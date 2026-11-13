"""One-owner Grok Bot / Dot message bridge. Python 3.11+, standard library only."""
import base64
import fcntl
import hashlib
import hmac
import html
import http.client
import ipaddress
import json
import os
import re
import secrets
import socket
import sqlite3
import ssl
import stat
import uuid
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit


def load_env(path=".env"):
    if Path(path).exists():
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.lstrip().startswith("#"):
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


def utc(epoch=None):
    return datetime.fromtimestamp(epoch or time.time(), timezone.utc).isoformat()


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def b64(value):
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def reply_id(mid, part_index=0):
    return "reply-" + digest(mid if part_index == 0 else mid + "|part|" + str(part_index))


class Rejected(Exception):
    pass



def upstream_error_summary(body, sensitive=()):
    """Bounded upstream diagnostic with credentials, URLs and opaque tokens removed."""
    value = body.decode("utf-8", errors="replace") if isinstance(body, bytes) else str(body)
    for item in sensitive:
        if item:
            value = value.replace(item, "[redacted]")
    value = re.sub(r"https?://[^\s\"<>]+", "[url]", value)
    value = re.sub(r"(?i)bearer\s+[^\s\"<>,}]+", "Bearer [redacted]", value)
    value = re.sub(r"[A-Za-z0-9_+/=-]{24,}", "[opaque]", value)
    return " ".join(value.split())[:800]



SAFE_ID = re.compile(r"[A-Za-z0-9._:-]{1,100}")
SEND_FIELDS = frozenset(("conversation_id", "message_id", "text", "reply_to", "final", "end_of_turn",
                         "recipient", "task_id", "parent_task_id", "delegation_id"))


def safe_id(value):
    return isinstance(value, str) and SAFE_ID.fullmatch(value) is not None


def strict_object(value, allowed, required=()):
    if not isinstance(value, dict) or set(value) - set(allowed) or set(required) - set(value):
        raise Rejected("Invalid request fields")


def fixed_https(url):
    if not isinstance(url, str) or not url or len(url) > 4096 or any(ord(c) < 33 for c in url):
        raise Rejected("Invalid fixed webhook URL")
    try:
        parsed = urlsplit(url)
        if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
                or parsed.port not in (None, 443) or parsed.fragment or not parsed.path.startswith("/")):
            raise ValueError()
    except (ValueError, TypeError):
        raise Rejected("Fixed webhook must use HTTPS port 443 without userinfo or fragment") from None
    return url


def load_bot_routes(path, reserved_keys, legacy_url=None):
    """Startup-only private registry. Invalid configuration fails before opening the database."""
    if not path:
        return {}
    route_path = Path(path)
    info = route_path.lstat()
    if (not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077
            or info.st_uid not in (0, os.geteuid()) or info.st_size > 262144):
        raise Rejected("BOT_ROUTES_FILE must be a private regular file owned by the service owner")
    # O_NOFOLLOW and fstat close the lstat/open symlink replacement window.
    fd = os.open(route_path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, "r", encoding="utf-8") as handle:
        current = os.fstat(handle.fileno())
        if ((current.st_dev, current.st_ino) != (info.st_dev, info.st_ino) or current.st_mode & 0o077
                or current.st_uid not in (0, os.geteuid())):
            raise Rejected("BOT_ROUTES_FILE changed while opening")
        raw = handle.read(262145)
    if len(raw.encode()) > 262144:
        raise Rejected("BOT_ROUTES_FILE too large")
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise Rejected("Duplicate registry field")
            result[key] = value
        return result
    data = json.loads(raw, object_pairs_hook=unique_pairs)
    strict_object(data, ("version", "bots"), ("version", "bots"))
    if type(data["version"]) is not int or data["version"] != 1 or not isinstance(data["bots"], list) or len(data["bots"]) > 64:
        raise Rejected("Unsupported bot registry")
    routes, identities = {}, set()
    def destination(url):
        parsed = urlsplit(url)
        return parsed.hostname.lower(), parsed.path or '/', parsed.query
    destinations = {destination(legacy_url)} if legacy_url else set()
    key_hashes = {digest(k) for k in reserved_keys if k}
    for value in data["bots"]:
        strict_object(value, ("id", "bot_uuid", "enabled", "webhook_url", "webhook_key", "send_key", "send_key_hash"),
                      ("id", "bot_uuid", "enabled"))
        bot, bot_uuid, enabled = value["id"], value["bot_uuid"], value["enabled"]
        if (not isinstance(bot, str) or not re.fullmatch(r"[a-z][a-z0-9._-]{0,63}", bot)
                or bot in ("dot", "grok", "admin") or bot in routes or type(enabled) is not bool):
            raise Rejected("Invalid or duplicate bot identity")
        try:
            if not isinstance(bot_uuid, str) or str(uuid.UUID(bot_uuid)) != bot_uuid or bot_uuid in identities:
                raise ValueError()
        except (ValueError, AttributeError):
            raise Rejected("Invalid or duplicate bot UUID") from None
        identities.add(bot_uuid)
        if "send_key" in value and "send_key_hash" in value:
            raise Rejected("Use send_key or send_key_hash, not both")
        key = value.get("send_key")
        key_hash = value.get("send_key_hash")
        if key is not None:
            if not isinstance(key, str) or len(key) < 40 or len(key) > 512 or any(ord(c) < 33 for c in key):
                raise Rejected("Bot send key must be a dedicated random credential")
            key_hash = digest(key)
        if key_hash is not None:
            if not isinstance(key_hash, str) or not re.fullmatch(r"[a-f0-9]{64}", key_hash) or key_hash in key_hashes:
                raise Rejected("Invalid or reused bot send key")
            key_hashes.add(key_hash)
        url, webhook_key = value.get("webhook_url"), value.get("webhook_key")
        if url is not None:
            fixed_https(url)
            target = destination(url)
            if target in destinations:
                raise Rejected('Each bot requires its own webhook URL')
            destinations.add(target)
        if webhook_key is not None and (not isinstance(webhook_key, str) or not 40 <= len(webhook_key) <= 512 or any(ord(c) < 33 for c in webhook_key)):
            raise Rejected("Invalid bot webhook key")
        if webhook_key is not None:
            webhook_hash = digest(webhook_key)
            if webhook_hash in key_hashes:
                raise Rejected('Each bot requires separate webhook and send credentials')
            key_hashes.add(webhook_hash)
        if enabled and (not url or not webhook_key or not key_hash):
            raise Rejected("Enabled bot requires a fixed webhook and dedicated credentials")
        route = {"id": bot, "bot_uuid": bot_uuid, "enabled": enabled, "webhook_url": url,
                 "webhook_key": webhook_key, "send_key_hash": key_hash}
        route["fingerprint"] = digest(encoded(route).decode())
        route['_sensitive'] = tuple(v for v in (key, key_hash, webhook_key, url) if v)
        routes[bot] = route
    return routes


def public_post(url, payload, headers):
    """Resolve once; pin a public IP while preserving hostname TLS validation. No redirects."""
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise Rejected("HTTPS destination required")
    if parsed.port not in (None, 443):
        raise Rejected("Outbound HTTPS must use port 443")
    addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
    if not addresses:
        raise Rejected("No destination address")
    for item in addresses:
        address = ipaddress.ip_address(item[4][0])
        if not (address.ipv4_mapped if hasattr(address, "ipv4_mapped") and address.ipv4_mapped else address).is_global:
            raise Rejected("Non-public destination blocked")
    family, kind, proto, _, address = addresses[0]
    connection = http.client.HTTPSConnection(parsed.hostname, 443, timeout=10, context=ssl.create_default_context())
    def pinned_connect(*_args, **_kwargs):
        sock = socket.socket(family, kind, proto)
        sock.settimeout(10)
        try:
            sock.connect(address)
            return sock
        except BaseException:
            sock.close()
            raise
    connection._create_connection = pinned_connect
    body = encoded(payload)
    if len(body) > 262144:
        raise Rejected("Payload too large")
    try:
        connection.request("POST", parsed.path + ("?" + parsed.query if parsed.query else ""), body,
                           {"Content-Type": "application/json", **headers})
        response = connection.getresponse()
        return response.status, response.read(262145)
    finally:
        connection.close()


class Bridge:
    def __init__(self, db_path, base_url, admin_key, grok_key, post=public_post, routes_file=None):
        self.base = base_url.rstrip("/")
        self.admin_key, self.grok_key, self.post = admin_key, grok_key, post
        self.lock = threading.RLock()
        self.public_limits = {}
        self.routes = load_bot_routes(routes_file if routes_file is not None else os.getenv("BOT_ROUTES_FILE"),
                                      (admin_key, grok_key, os.getenv('GROK_WEBHOOK_KEY')), os.getenv('GROK_WEBHOOK_URL'))
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.instance_lock = open(str(db_path) + '.lock', 'a')
        try:
            fcntl.flock(self.instance_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.instance_lock.close()
            raise Rejected('Only one bridge process may use this database') from None
        self.db = sqlite3.connect(db_path, check_same_thread=False, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript("""
          CREATE TABLE IF NOT EXISTS conversations(id TEXT PRIMARY KEY,state TEXT,expires REAL);
          CREATE TABLE IF NOT EXISTS messages(
            id TEXT PRIMARY KEY,conversation_id TEXT,sender TEXT,recipient TEXT,text TEXT,
            reply_to TEXT UNIQUE,sent_at TEXT,received_at TEXT,processed_at TEXT,status TEXT,
            final INTEGER,attempts INTEGER DEFAULT 0,next_attempt REAL DEFAULT 0,
            delivery_url TEXT,subscription_id TEXT,callback_token_hash TEXT,error TEXT);
          CREATE TABLE IF NOT EXISTS audit(seq INTEGER PRIMARY KEY,at TEXT,message_id TEXT,stage TEXT,detail TEXT);
          CREATE TABLE IF NOT EXISTS subscriptions(id TEXT PRIMARY KEY,url TEXT,secret TEXT,old_secret TEXT,
            rotate_until REAL,expires REAL,active INTEGER);
          CREATE TABLE IF NOT EXISTS clients(id TEXT PRIMARY KEY,redirects TEXT);
          CREATE TABLE IF NOT EXISTS codes(hash TEXT PRIMARY KEY,client TEXT,redirect TEXT,challenge TEXT,expires REAL);
          CREATE TABLE IF NOT EXISTS tokens(hash TEXT PRIMARY KEY,client TEXT,kind TEXT,expires REAL);
          CREATE TABLE IF NOT EXISTS binding(slot INTEGER PRIMARY KEY CHECK(slot=1),subscription_id TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS bot_identities(id TEXT PRIMARY KEY,bot_uuid TEXT UNIQUE NOT NULL);
          CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY,parent_task_id TEXT,created_at TEXT);
          CREATE TABLE IF NOT EXISTS delegations(id TEXT PRIMARY KEY,conversation_id TEXT UNIQUE,task_id TEXT,recipient TEXT);

        """)
        for table, column, kind in [('conversations','subscription_id','TEXT'),('messages','claim_deadline','REAL'),
                                    ('messages','end_of_turn','INTEGER NOT NULL DEFAULT 1'),
                                    ('conversations','bot_id',"TEXT NOT NULL DEFAULT 'grok'"),
                                    ('conversations','task_id','TEXT'),('conversations','parent_task_id','TEXT'),
                                    ('conversations','delegation_id','TEXT'),('messages','task_id','TEXT'),
                                    ('messages','parent_task_id','TEXT'),('messages','delegation_id','TEXT'),
                                    ('messages','route_fingerprint','TEXT')]:
            if column not in [r[1] for r in self.db.execute('PRAGMA table_info('+table+')')]:
                self.db.execute('ALTER TABLE '+table+' ADD COLUMN '+column+' '+kind)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            # Legacy conversations are addressable as root tasks without rewriting their
            # old nullable metadata or changing idempotency of already stored messages.
            self.db.execute('INSERT OR IGNORE INTO tasks(id,parent_task_id,created_at) SELECT id,NULL,? FROM conversations WHERE task_id IS NULL', (utc(),))
            for bot, route in self.routes.items():
                identity = self.db.execute('SELECT bot_uuid FROM bot_identities WHERE id=?', (bot,)).fetchone()
                reused = self.db.execute('SELECT id FROM bot_identities WHERE bot_uuid=?', (route['bot_uuid'],)).fetchone()
                if (identity and identity['bot_uuid'] != route['bot_uuid']) or (reused and reused['id'] != bot):
                    raise Rejected('Bot identity binding cannot be replaced; use a new bot id and UUID')
                self.db.execute('INSERT OR IGNORE INTO bot_identities VALUES(?,?)', (bot, route['bot_uuid']))
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK')
            self.db.close()
            self.instance_lock.close()
            raise
        # Never automatically re-trigger a Bot after a process dies during its POST.
        self.db.execute("UPDATE messages SET status='delivery_unknown',error='service restarted during POST' WHERE status='dispatching' AND recipient!='dot'")
        self.db.execute("UPDATE messages SET status='queued' WHERE status='dispatching' AND recipient='dot'")
        self.db.execute("UPDATE messages SET status='processing_unknown',error='process restarted after claim' WHERE status='agent_processing'")

    def close(self):
        self.db.close()
        self.instance_lock.close()

    def audit(self, mid, stage, detail=""):
        self.db.execute("INSERT INTO audit(at,message_id,stage,detail) VALUES(?,?,?,?)", (utc(), mid, stage, detail))

    def message(self, mid):
        row = self.db.execute("SELECT * FROM messages WHERE id=?", (mid,)).fetchone()
        return {k: bool(row[k]) if k in ("final", "end_of_turn") else row[k] for k in ("id", "conversation_id", "sender", "recipient", "text", "reply_to",
                                    "sent_at", "received_at", "processed_at", "status", "final", "end_of_turn", "attempts", "error", "task_id", "parent_task_id", "delegation_id")} if row else None

    def expire(self):
        self.db.execute("UPDATE conversations SET state='expired' WHERE state='active' AND expires<?", (time.time(),))
        self.db.execute("UPDATE messages SET status='expired' WHERE status='queued' AND conversation_id IN (SELECT id FROM conversations WHERE state='expired')")
        self.db.execute("UPDATE messages SET status='processing_unknown',error='claim lease expired; inspect before recovery' WHERE status='agent_processing' AND claim_deadline<?", (time.time(),))
        self.db.execute('DELETE FROM codes WHERE expires<?',(time.time(),))
        self.db.execute('DELETE FROM tokens WHERE expires<?',(time.time(),))

    def bot_route(self, actor):
        if not isinstance(actor, str):
            return None
        if actor == 'grok':
            route = {'id': 'grok', 'enabled': True, 'webhook_url': os.getenv('GROK_WEBHOOK_URL'),
                     'webhook_key': os.getenv('GROK_WEBHOOK_KEY')}
            route['fingerprint'] = digest(encoded(route).decode())
            return route
        return self.routes.get(actor)

    def bot_enabled(self, actor):
        route = self.bot_route(actor)
        return bool(route and route['enabled'])

    def check_conversation_actor(self, actor, conv):
        if actor == 'admin':
            return
        if actor == 'dot' or (self.bot_enabled(actor) and conv['bot_id'] == actor):
            return
        raise Rejected('Conversation not accessible to this agent')

    def bind_task(self, actor, task_id, parent_task_id):
        if task_id is None:
            return
        if task_id == parent_task_id:
            raise Rejected('Task parent cycle')
        existing = self.db.execute('SELECT parent_task_id FROM tasks WHERE id=?', (task_id,)).fetchone()
        if existing:
            if existing['parent_task_id'] != parent_task_id:
                raise Rejected('Task parent binding is immutable')
            if actor != 'dot' and not self.db.execute('SELECT 1 FROM conversations WHERE (task_id=? OR (task_id IS NULL AND id=?)) AND bot_id=?', (task_id, task_id, actor)).fetchone():
                raise Rejected('Task not accessible to this agent')
        if parent_task_id is not None:
            if not existing and actor != 'dot' and not self.db.execute('SELECT 1 FROM conversations WHERE (task_id=? OR (task_id IS NULL AND id=?)) AND bot_id=?', (parent_task_id, parent_task_id, actor)).fetchone():
                raise Rejected('Parent task not accessible to this agent')
            seen, ancestor = {task_id}, parent_task_id
            while ancestor is not None:
                if ancestor in seen or len(seen) > 256:
                    raise Rejected('Task parent cycle or depth limit')
                seen.add(ancestor)
                parent = self.db.execute('SELECT parent_task_id FROM tasks WHERE id=?', (ancestor,)).fetchone()
                if not parent:
                    raise Rejected('Parent task must already exist')
                ancestor = parent['parent_task_id']
        if not existing:
            self.db.execute('INSERT INTO tasks VALUES(?,?,?)', (task_id, parent_task_id, utc()))

    def send(self, sender, args):
        with self.lock:
            strict_object(args, SEND_FIELDS, ("message_id", "conversation_id", "text"))
            if sender != 'dot' and not self.bot_enabled(sender):
                raise Rejected('Unknown or disabled sender')
            self.expire()
            mid, cid, text = (args.get(k) for k in ("message_id", "conversation_id", "text"))
            if not all(safe_id(v) for v in (mid, cid)):
                raise Rejected("Use stable, non-secret message_id and conversation_id, 1..100 safe characters")
            if not isinstance(text, str) or not text.strip() or len(text.encode()) > 16000:
                raise Rejected("text must contain 1..16000 UTF-8 bytes")
            final = args.get("final", False)
            if not isinstance(final, bool):
                raise Rejected("final must be boolean")
            end_of_turn = args.get("end_of_turn", True)
            if not isinstance(end_of_turn, bool) or (final and not end_of_turn):
                raise Rejected("end_of_turn must be boolean; final requires end_of_turn=true")
            parent_id = args.get("reply_to")
            if parent_id is not None and not safe_id(parent_id):
                raise Rejected("Invalid reply_to")
            conv = self.db.execute("SELECT * FROM conversations WHERE id=?", (cid,)).fetchone()
            if conv:
                self.check_conversation_actor(sender, conv)
            for field in ('recipient', 'task_id', 'parent_task_id', 'delegation_id'):
                if field in args and not safe_id(args[field]):
                    raise Rejected('Invalid recipient, task or delegation identifier')
            bot = conv['bot_id'] if conv else (args.get('recipient', 'grok') if sender == 'dot' else sender)
            recipient = bot if sender == 'dot' else 'dot'
            if args.get('recipient', recipient) != recipient or not self.bot_enabled(bot):
                raise Rejected("Unknown, disabled or mismatched recipient")
            task_id = args.get('task_id', conv['task_id'] if conv else cid)
            task_binding = self.db.execute('SELECT parent_task_id FROM tasks WHERE id=?', (task_id,)).fetchone() if task_id else None
            parent_task_id = args.get('parent_task_id', conv['parent_task_id'] if conv else (task_binding['parent_task_id'] if task_binding else None))
            delegation_id = args.get('delegation_id', conv['delegation_id'] if conv else None)
            for value in (task_id, parent_task_id, delegation_id):
                if value is not None and not safe_id(value):
                    raise Rejected("Invalid task or delegation identifier")
            if parent_task_id is not None and task_id is None:
                raise Rejected("parent_task_id requires task_id")
            if conv and (task_id, parent_task_id, delegation_id) != (conv['task_id'], conv['parent_task_id'], conv['delegation_id']):
                raise Rejected("Conversation task binding is immutable")
            existing = self.message(mid)
            if existing:
                if (existing["conversation_id"], existing["sender"], existing["recipient"], existing["text"], existing["reply_to"], existing["final"], existing["end_of_turn"], existing["task_id"], existing["parent_task_id"], existing["delegation_id"]) != (cid, sender, recipient, text, parent_id, final, end_of_turn, task_id, parent_task_id, delegation_id):
                    raise Rejected("message_id conflict")
                self.audit(mid, "duplicate_suppressed")
                return {**existing, "duplicate": True}
            parent = self.message(parent_id) if parent_id else None
            if conv:
                if conv["state"] != "active":
                    raise Rejected("Conversation " + conv["state"])
                last = self.db.execute("SELECT id FROM messages WHERE conversation_id=? ORDER BY rowid DESC LIMIT 1", (cid,)).fetchone()
                if not parent or parent["conversation_id"] != cid or last["id"] != parent_id:
                    raise Rejected("Reply must reference latest message in this conversation")
                if parent['sender'] == sender:
                    if parent['end_of_turn']:
                        raise Rejected("Sender's turn is already closed")
                else:
                    if not parent['end_of_turn']:
                        raise Rejected("Sender's turn is still open; acknowledge this part and wait")
                    if parent["received_at"] is None:
                        raise Rejected("claim_message before replying")
                    if parent['status'] == 'processing_unknown':
                        raise Rejected("Previous processing is unknown; inspect before recovery")
                if parent["final"]:
                    raise Rejected("Final message must be completed, not replied to")
                if final:
                    # A reply acknowledges its claimed parent in the transaction below.
                    # An outgoing multipart final can still carry the last part to its recipient.
                    pending = self.db.execute(
                        "SELECT 1 FROM messages WHERE conversation_id=? AND id!=? AND processed_at IS NULL "
                        "AND rowid <= (SELECT MAX(rowid) FROM messages WHERE conversation_id=? AND recipient=?) "
                        "LIMIT 1", (cid, parent_id, cid, sender),
                    ).fetchone()
                    if pending:
                        raise Rejected("Earlier reply parts must be acknowledged before sending final")
                count = self.db.execute("SELECT count(*) FROM messages WHERE conversation_id=? AND end_of_turn=1", (cid,)).fetchone()[0]
                turn_limit = int(os.getenv('MAX_COMPLETED_TURNS', '0'))
                if turn_limit and count >= turn_limit:
                    self.audit(parent_id, "round_limit_rejected", mid)
                    raise Rejected("Configured completed-turn limit reached")
            elif parent_id:
                raise Rejected("Unknown conversation")
            binding = self.db.execute('SELECT subscription_id FROM binding WHERE slot=1').fetchone()
            sid = conv['subscription_id'] if conv else (binding[0] if binding else None)
            sub = self.db.execute("SELECT * FROM subscriptions WHERE id=? AND active=1 AND expires>?", (sid,time.time())).fetchone()
            if not sub:
                raise Rejected("Original Dot subscription must be active")
            day = utc()[:10]
            count = self.db.execute('SELECT count(*) FROM messages WHERE sent_at>=?',(day,)).fetchone()[0]
            daily_limit = int(os.getenv('MAX_MESSAGES_PER_DAY', '0'))
            if daily_limit and count >= daily_limit:
                raise Rejected('Daily message limit reached')
            pages = self.db.execute('PRAGMA page_count').fetchone()[0]
            size = self.db.execute('PRAGMA page_size').fetchone()[0]
            if pages*size >= 32*1024*1024:
                raise Rejected('Database size limit reached; operator maintenance required')
            route = self.bot_route(bot)
            if not route or not route['webhook_url'] or not route['webhook_key']:
                raise Rejected("Bot webhook is not configured")
            self.db.execute("BEGIN IMMEDIATE")
            try:
                if not conv:
                    self.bind_task(sender, task_id, parent_task_id)
                    if delegation_id is not None:
                        previous = self.db.execute("SELECT conversation_id FROM delegations WHERE id=?", (delegation_id,)).fetchone()
                        if previous:
                            raise Rejected("delegation_id already assigned")
                        self.db.execute("INSERT INTO delegations VALUES(?,?,?,?)", (delegation_id, cid, task_id, recipient))
                    self.db.execute("INSERT INTO conversations(id,state,expires,subscription_id,bot_id,task_id,parent_task_id,delegation_id) VALUES(?,?,?,?,?,?,?,?)", (cid, "active", time.time() + int(os.getenv("CONVERSATION_TIMEOUT_SECONDS", "604800")),sid,bot,task_id,parent_task_id,delegation_id))
                self.db.execute("INSERT INTO messages(id,conversation_id,sender,recipient,text,reply_to,sent_at,status,final,delivery_url,subscription_id,end_of_turn,task_id,parent_task_id,delegation_id,route_fingerprint) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                                (mid, cid, sender, recipient, text, parent_id, utc(), "queued", int(final), sub["url"], sub["id"], int(end_of_turn),task_id,parent_task_id,delegation_id,route['fingerprint'] if recipient != 'dot' else None))
                if parent and parent['sender'] != sender:
                    self.db.execute("UPDATE messages SET processed_at=?,status='replied' WHERE id=?", (utc(), parent_id))
                    self.audit(parent_id, "agent_replied", mid)
                self.db.execute("UPDATE conversations SET expires=? WHERE id=?", (time.time() + int(os.getenv("CONVERSATION_TIMEOUT_SECONDS", "604800")), cid))
                self.audit(mid, "service_received")
                self.db.execute("COMMIT")
            except BaseException:
                self.db.execute("ROLLBACK")
                raise
            return self.message(mid)

    def callback_actor(self, message):
        actor = message['recipient']
        route = self.bot_route(actor)
        if (not route or not route['enabled'] or actor == 'dot'
                or (message['route_fingerprint'] is None and actor != 'grok')
                or (message['route_fingerprint'] is not None and message['route_fingerprint'] != route['fingerprint'])):
            raise Rejected('Callback route was disabled or changed; operator review required')
        return actor

    def callback_reply(self, incoming_id, args):
        """Sequential reply parts share one scoped callback; retries retain stable IDs."""
        with self.lock:
            index = args.get('part_index', 0)
            if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < 16:
                raise Rejected('part_index must be an integer in 0..15')
            raw_message = self.db.execute('SELECT * FROM messages WHERE id=?', (incoming_id,)).fetchone()
            if raw_message:
                self.callback_actor(raw_message)
            incoming = self.message(incoming_id)
            if not incoming or not self.bot_enabled(incoming['recipient']) or not incoming['received_at']:
                raise Rejected('Claim this Grok message before replying')
            if incoming['final'] or not incoming['end_of_turn']:
                raise Rejected('Cannot reply to final or unfinished incoming turn')
            if index == 15 and not args.get('end_of_turn', True):
                raise Rejected('The sixteenth part must end the turn')
            return self.send(incoming['recipient'], {'conversation_id': incoming['conversation_id'],
                'message_id': reply_id(incoming_id, index),
                'reply_to': incoming_id if index == 0 else reply_id(incoming_id, index-1),
                'text': args.get('text'), 'final': args.get('final', False),
                'end_of_turn': args.get('end_of_turn', True)})

    def receive(self, sender):
        with self.lock:
            if sender != 'dot' and not self.bot_enabled(sender):
                raise Rejected('Unknown or disabled agent')
            self.expire()
            row = self.db.execute("SELECT m.id FROM messages m JOIN conversations c ON c.id=m.conversation_id WHERE m.recipient=? AND m.received_at IS NULL AND m.status IN ('dispatching','event_accepted') AND c.state='active' ORDER BY m.rowid LIMIT 1", (sender,)).fetchone()
            return self.claim(sender, row[0]) if row else {"claimed": False, "reason": "no_pending_message"}

    def claim(self, sender, mid):
        with self.lock:
            if not safe_id(mid):
                raise Rejected('Invalid message identifier')
            if sender != 'dot' and not self.bot_enabled(sender):
                raise Rejected('Unknown or disabled agent')
            self.expire()
            msg = self.message(mid)
            if not msg or msg["recipient"] != sender:
                raise Rejected("Message not addressed to this agent")
            conv = self.db.execute("SELECT state FROM conversations WHERE id=?", (msg["conversation_id"],)).fetchone()
            if conv["state"] not in ("active", "completed"):
                raise Rejected("Conversation " + conv["state"])
            if msg["received_at"]:
                self.audit(mid, "duplicate_claim_suppressed")
                return {**msg, "claimed": False, "reason": "already_claimed"}
            self.db.execute('BEGIN IMMEDIATE')
            try:
                changed=self.db.execute("UPDATE messages SET received_at=?,status='agent_processing',claim_deadline=? WHERE id=? AND received_at IS NULL", (utc(), time.time()+int(os.getenv("CLAIM_TIMEOUT_SECONDS", "86400")), mid)).rowcount
                if not changed:
                    self.db.execute('ROLLBACK')
                    return {**self.message(mid),'claimed':False,'reason':'already_claimed'}
                self.audit(mid, "agent_claimed")
                self.db.execute('COMMIT')
            except BaseException:
                if self.db.in_transaction:self.db.execute('ROLLBACK')
                raise
            return {**self.message(mid), "claimed": True}

    def finish(self, sender, mid):
        with self.lock:
            if not safe_id(mid):
                raise Rejected('Invalid message identifier')
            if sender != 'dot' and not self.bot_enabled(sender):
                raise Rejected('Unknown or disabled agent')
            msg = self.message(mid)
            if not msg or msg["recipient"] != sender or not msg["received_at"]:
                raise Rejected("Only recipient of a claimed message can acknowledge it")
            if msg['final']:
                pending = self.db.execute(
                    "SELECT 1 FROM messages WHERE conversation_id=? AND id!=? AND processed_at IS NULL LIMIT 1",
                    (msg['conversation_id'], mid),
                ).fetchone()
                if pending:
                    raise Rejected('Earlier reply parts must be acknowledged before completing the conversation')
            self.db.execute("UPDATE messages SET status='completed',processed_at=? WHERE id=?", (utc(), mid))
            if msg['final']:
                self.db.execute("UPDATE conversations SET state='completed' WHERE id=? AND state='active'", (msg["conversation_id"],))
            self.audit(mid, "agent_completed")
            return self.message(mid)

    def stop(self, cid, actor='admin'):
        with self.lock:
            if not safe_id(cid):
                raise Rejected('Invalid conversation identifier')
            conv = self.db.execute("SELECT * FROM conversations WHERE id=?", (cid,)).fetchone()
            if conv:
                self.check_conversation_actor(actor, conv)
            elif actor != 'admin' and actor != 'dot' and not self.bot_enabled(actor):
                raise Rejected('Unknown or disabled agent')
            self.db.execute("UPDATE conversations SET state='stopped' WHERE id=? AND state='active'", (cid,))
            self.db.execute("UPDATE messages SET status='stopped' WHERE conversation_id=? AND status='queued'", (cid,))
            self.audit(None, "conversation_stopped", cid)
            return {"conversation_id": cid, "stopped": True}

    def history(self, cid, actor='admin'):
        with self.lock:
            if not safe_id(cid):
                raise Rejected('Invalid conversation identifier')
            self.expire()
            conv = self.db.execute("SELECT * FROM conversations WHERE id=?", (cid,)).fetchone()
            if conv:
                self.check_conversation_actor(actor, conv)
            elif actor != 'admin' and actor != 'dot' and not self.bot_enabled(actor):
                raise Rejected('Unknown or disabled agent')
            ids = self.db.execute("SELECT id FROM messages WHERE conversation_id=? ORDER BY rowid", (cid,)).fetchall()
            audit = self.db.execute("SELECT * FROM audit WHERE message_id IN (SELECT id FROM messages WHERE conversation_id=?) OR (stage='conversation_stopped' AND detail=?) ORDER BY seq", (cid, cid)).fetchall()
            return {"conversation": dict(conv) if conv else None, "messages": [self.message(r[0]) for r in ids], "audit": [dict(r) for r in audit]}

    def event_post(self, sub, payload, eid):
        body = encoded(payload)
        timestamp = str(int(time.time()))
        signatures = []
        keys = [sub["secret"]]
        if sub["old_secret"] and sub["rotate_until"] > time.time():
            keys.append(sub["old_secret"])
        for secret in keys:
            key = base64.b64decode(secret.removeprefix("whsec_"), validate=True)
            signature = base64.b64encode(hmac.new(key, eid.encode()+b"."+timestamp.encode()+b"."+body, hashlib.sha256).digest()).decode()
            signatures.append("v1," + signature)
        return self.post(sub["url"], payload, {"webhook-id": eid, "webhook-timestamp": timestamp,
                         "webhook-signature": " ".join(signatures), "X-MCP-Subscription-Id": sub["id"]})

    def subscribe(self, params):
        delivery = params.get("delivery", {})
        if params.get("name") != "message.created" or params.get("arguments") != {"recipient": "dot"} or delivery.get("mode") != "webhook":
            raise Rejected("Subscribe to message.created with recipient=dot and webhook delivery")
        url, secret = delivery.get("url", ""), delivery.get("secret", "")
        callback_host = urlsplit(url).hostname
        if callback_host and re.fullmatch(r"[a-zA-Z0-9.-]{1,253}", callback_host):
            print("subscription callback host", callback_host, flush=True)
        hosts = os.getenv("CALLBACK_HOSTS", "").split(",")
        if callback_host not in hosts:
            print("subscription rejected: callback host not configured", flush=True)
            raise Rejected("Callback host not configured: " + str(urlsplit(url).hostname))
        try:
            if not secret.startswith("whsec_") or not 24 <= len(base64.b64decode(secret[6:], validate=True)) <= 64:
                raise ValueError()
        except (ValueError, TypeError):
            raise Rejected("Invalid signing secret") from None
        sid = "sub_" + digest("dot|" + url + "|message.created|recipient=dot")[:32]
        with self.lock:
            bound=self.db.execute('SELECT subscription_id FROM binding WHERE slot=1').fetchone()
            if bound and bound[0]!=sid:
                print('subscription rejected: original binding mismatch', flush=True)
                raise Rejected('Bridge is bound to the original Dot subscription; explicit operator rebind required')
        challenge = secrets.token_urlsafe(32)
        sub = {"id": sid, "url": url, "secret": secret, "old_secret": None, "rotate_until": 0}
        status, response = self.event_post(sub, {"type": "verification", "challenge": challenge}, "verify_" + secrets.token_hex(16))
        try:
            verified = 200 <= status < 300 and hmac.compare_digest(json.loads(response).get("challenge", ""), challenge)
        except (ValueError, TypeError):
            verified = False
        if not verified:
            print("subscription rejected: callback verification failed", status, flush=True)
            raise Rejected("Callback verification failed")
        ttl = params.get("ttlMs", 86400000)
        if ttl is not None and (not isinstance(ttl, int) or isinstance(ttl, bool) or ttl <= 0):
            raise Rejected("Invalid ttlMs")
        expires = time.time() + min(86400, (ttl / 1000 if ttl is not None else 86400))
        with self.lock:
            bound=self.db.execute('SELECT subscription_id FROM binding WHERE slot=1').fetchone()
            if bound and bound[0]!=sid:
                raise Rejected('Original Dot binding changed during verification')
            old = self.db.execute("SELECT secret FROM subscriptions WHERE id=?", (sid,)).fetchone()
            self.db.execute("INSERT OR REPLACE INTO subscriptions VALUES(?,?,?,?,?,?,1)",
                            (sid, url, secret, old[0] if old and old[0] != secret else None, time.time()+300, expires))
            self.audit(None, "dot_subscription_verified", sid)
            self.db.execute('INSERT OR IGNORE INTO binding VALUES(1,?)',(sid,))
        return {"id": sid, "refreshBefore": utc(expires), "cursor": None, "truncated": False}

    def dispatch_one(self):
        with self.lock:
            self.expire()
            row = self.db.execute("SELECT * FROM messages WHERE status='queued' AND next_attempt<=? ORDER BY rowid LIMIT 1", (time.time(),)).fetchone()
            if not row:
                return False
            mid = row["id"]
            conv = self.db.execute("SELECT state FROM conversations WHERE id=?", (row["conversation_id"],)).fetchone()
            if conv[0] != "active":
                self.db.execute("UPDATE messages SET status='stopped' WHERE id=?", (mid,))
                return True
            sub = self.db.execute("SELECT * FROM subscriptions WHERE id=? AND active=1 AND expires>?", (row["subscription_id"], time.time())).fetchone()
            if not sub:
                self.db.execute("UPDATE messages SET status='failed',error='Dot subscription unavailable' WHERE id=?", (mid,))
                return True
            route = None
            if row['recipient'] != 'dot':
                route = self.bot_route(row['recipient'])
                if (not route or not route['enabled'] or not route['webhook_url'] or not route['webhook_key']
                        or (row['route_fingerprint'] is None and row['recipient'] != 'grok')
                        or (row['route_fingerprint'] is not None and row['route_fingerprint'] != route['fingerprint'])):
                    self.db.execute("UPDATE messages SET status='failed',error='Bot route unavailable or changed; operator review required' WHERE id=?", (mid,))
                    self.audit(mid, 'route_changed_or_disabled')
                    return True
            self.db.execute("UPDATE messages SET status='dispatching',attempts=attempts+1 WHERE id=?", (mid,))
            self.audit(mid, "dispatch_started")
            message = self.message(mid)
            payload = {k: message[k] for k in ("id", "conversation_id", "sender", "recipient", "text", "reply_to", "sent_at", "final", "end_of_turn")}
            for field in ('task_id', 'parent_task_id', 'delegation_id'):
                if message[field] is not None:
                    payload[field] = message[field]
            if row["recipient"] != "dot":
                token = secrets.token_urlsafe(32)
                self.db.execute("UPDATE messages SET callback_token_hash=? WHERE id=?", (digest(token), mid))
                payload["callback_url"] = self.base + "/grok/" + token
                payload["reply_message_id"] = reply_id(mid)
        # No lock across network I/O: Agent callbacks may arrive while POST is pending.
        status, error, diagnostic = None, None, None
        try:
            if row["recipient"] != "dot":
                status, response_body = self.post(route['webhook_url'], payload,
                                      {"Authorization": "Bearer " + route['webhook_key']})
                if not 200 <= status < 300:
                    diagnostic = upstream_error_summary(response_body, (
                        self.admin_key, self.grok_key, route['webhook_key'], route['webhook_url'],
                        route.get('send_key_hash'), payload["callback_url"], token, payload["text"], *route.get('_sensitive', ())))
            else:
                status, _ = self.event_post(sub, {"eventId": mid, "name": "message.created",
                                                  "timestamp": row["sent_at"], "data": payload, "cursor": None}, mid)
        except (OSError, http.client.HTTPException, Rejected) as exc:
            error = type(exc).__name__
        with self.lock:
            if diagnostic is not None:
                self.audit(mid, "grok_upstream_rejected", str(status) + " " + diagnostic)
            current = self.message(mid)
            if current["status"] != "dispatching":
                self.audit(mid, "delivery_response_after_agent_callback", str(status))
                return True
            if status and 200 <= status < 300:
                state = "routine_accepted" if row["recipient"] != "dot" else "event_accepted"
                self.audit(mid, state, str(status))
            elif row["recipient"] == "dot" and (status is None or status == 429 or status >= 500) and current["attempts"] < 3:
                state = "queued"
            else:
                state = "delivery_unknown" if row["recipient"] != "dot" and status is None else "failed"
                self.audit(mid, state, error or str(status))
            self.db.execute("UPDATE messages SET status=?,error=?,next_attempt=? WHERE id=?",
                            (state, error or (str(status) if state in ("failed", "queued") else None), time.time()+2**current["attempts"], mid))
        return True

    def bearer(self, token):
        if not isinstance(token, str) or not token or len(token) > 512:
            return None
        if token and hmac.compare_digest(token, self.admin_key):
            return "admin"
        if token and hmac.compare_digest(token, self.grok_key):
            return "grok"
        token_hash = digest(token)
        for actor, route in self.routes.items():
            if route['enabled'] and route['send_key_hash'] and hmac.compare_digest(token_hash, route['send_key_hash']):
                return actor
        with self.lock:
            row = self.db.execute("SELECT 1 FROM tokens WHERE hash=? AND kind='access' AND expires>?", (token_hash, time.time())).fetchone()
        return "dot" if row else None

    def allow_public(self, endpoint, limit):
        with self.lock:
            window = int(time.time() // 60)
            old_window, count = self.public_limits.get(endpoint, (window, 0))
            count = count if old_window == window else 0
            self.public_limits[endpoint] = (window, count+1)
            return count < limit


def schema(properties, required):
    return {"type": "object", "properties": properties, "required": required, "additionalProperties": False}


STRING = {"type": "string"}
TOOLS = [
    ("send_message", "Send to an enabled registered bot by optional recipient (default grok; replies retain the conversation recipient). Every conversation is bilateral with Dot. Optional task_id and existing parent_task_id associate child work; delegation_id prevents duplicate delegation. Use stable IDs. In an existing conversation, reply_to must reference its latest message. When replying to the other agent, first claim that incoming message and wait for end_of_turn=true. When continuing your own multipart turn, reference your previous outgoing message whose end_of_turn=false; do not claim your own outgoing message. Set end_of_turn=true only on the last part. Collaborate on owner-assigned tasks: delegate, execute with existing tools, clarify and deliver without per-message approval. No fixed turn limit; idle sessions expire after 7 days. Privacy disclosure or payment needs owner approval. Before replying final=true, check this conversation for unprocessed earlier parts on either side. Wait for the original message IDs to be delivered and processed. final=true ends the conversation; it is not merely end-of-turn.", schema({"conversation_id": STRING, "message_id": STRING, "text": STRING, "reply_to": STRING, "final": {"type": "boolean"}, "end_of_turn": {"type": "boolean"}, "recipient": STRING, "task_id": STRING, "parent_task_id": STRING, "delegation_id": STRING}, ["conversation_id", "message_id", "text"])),
    ("claim_message", "Claim an incoming message before understanding/replying. On event wakeup with missing payload, message_id='' atomically receives the oldest delivered Dot message. If claimed=false, stop. Never poll on a schedule.", schema({"message_id": STRING}, ["message_id"])),
    ("complete_message", "Acknowledge a claimed message. With end_of_turn=false, process this part and wait before replying. Non-final acknowledgments keep the conversation active. A final acknowledgment completes the conversation only after earlier parts are acknowledged.", schema({"message_id": STRING}, ["message_id"])),
    ("stop_conversation", "Stop queued delivery and future replies. An already running Agent cannot be forcibly cancelled.", schema({"conversation_id": STRING}, ["conversation_id"])),
    ("get_conversation", "Read messages and stage timestamps. Transport acceptance is not proof an Agent read or understood a message.", schema({"conversation_id": STRING}, ["conversation_id"])),
]
EVENT = {"name": "message.created", "description": "A message from an authorized registered Bot for Dot.", "delivery": ["webhook"],
         "inputSchema": schema({"recipient": {"type": "string", "enum": ["dot"]}}, ["recipient"]),
         "payloadSchema": schema({"id": STRING, "conversation_id": STRING, "sender": STRING, "recipient": STRING,
                                   "text": STRING, "reply_to": {"type": ["string", "null"]}, "sent_at": STRING, "final": {"type": "boolean"}, "end_of_turn": {"type": "boolean"}, "task_id": STRING, "parent_task_id": STRING, "delegation_id": STRING},
                                  ["id", "conversation_id", "sender", "recipient", "text", "reply_to", "sent_at", "final"])}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def setup(self):
        super().setup()
        self.connection.settimeout(15)

    def log_message(self, *_args):
        pass  # Paths may contain scoped callback tokens or OAuth codes.

    def respond(self, value, status=200, headers=None, content_type="application/json"):
        body = encoded(value) if content_type == "application/json" else value.encode()
        self.send_response(status)
        for key, val in {"Content-Type": content_type, "Content-Length": str(len(body)), "Cache-Control": "no-store",
                         "X-Content-Type-Options": "nosniff", "Referrer-Policy": "no-referrer", **(headers or {})}.items():
            self.send_header(key, val)
        self.end_headers()
        self.wfile.write(body)

    @property
    def bridge(self):
        return self.server.bridge

    def body(self):
        size = int(self.headers.get("Content-Length", "0"))
        if size < 0 or size > 32768:
            raise Rejected("Request too large")
        return self.rfile.read(size)

    def identity(self):
        auth = self.headers.get("Authorization", "")
        return self.bridge.bearer(auth[7:]) if auth.startswith("Bearer ") else None

    def oauth_params(self, params):
        b = self.bridge
        client = b.db.execute("SELECT redirects FROM clients WHERE id=?", (params.get("client_id"),)).fetchone()
        if not client or params.get("redirect_uri") not in json.loads(client[0]):
            raise Rejected("Invalid client or redirect")
        if params.get("response_type") != "code" or params.get("code_challenge_method") != "S256" or not re.fullmatch(r"[A-Za-z0-9_-]{43}", params.get("code_challenge", "")):
            raise Rejected("Authorization code + S256 required")
        if params.get("resource") != b.base + "/mcp" or params.get("scope", "bridge") != "bridge":
            raise Rejected("Invalid resource or scope")

    def do_GET(self):
        b, path = self.bridge, urlsplit(self.path).path
        if path.startswith('/.well-known/') or path == '/mcp':
            print('discovery GET', path, flush=True)
        try:
            if path == "/health":
                if self.identity() != 'admin':
                    return self.respond({'error':'Unauthorized'},401)
                return self.respond({"service": "grok-dot-bridge", "version": "0.2.0-pilot"})
            if path.startswith("/.well-known/oauth-protected-resource"):
                return self.respond({"resource": b.base+"/mcp", "authorization_servers": [b.base], "scopes_supported": ["bridge"]})
            if path == "/.well-known/oauth-authorization-server":
                return self.respond({"issuer": b.base, "authorization_endpoint": b.base+"/authorize", "token_endpoint": b.base+"/token",
                                     "registration_endpoint": b.base+"/register", "response_types_supported": ["code"],
                                     "grant_types_supported": ["authorization_code", "refresh_token"], "token_endpoint_auth_methods_supported": ["none"],
                                     "code_challenge_methods_supported": ["S256"], "scopes_supported": ["bridge"], "authorization_response_iss_parameter_supported": True})
            if path == "/authorize":
                params = {k: v[0] for k, v in parse_qs(urlsplit(self.path).query).items()}
                with b.lock:
                    self.oauth_params(params)
                fields = "".join('<input type="hidden" name="'+html.escape(k, quote=True)+'" value="'+html.escape(v, quote=True)+'">' for k, v in params.items())
                return self.respond('<!doctype html><title>Connect message bridge</title><h1>Connect your Dot</h1><p>This grants communication access only to your Grok Bot / Dot bridge.</p><form method="post" action="/authorize">'+fields+'<label>Bridge owner key <input type="password" name="owner_key" required autocomplete="off"></label><button>Connect</button></form>',
                                    content_type="text/html; charset=utf-8", headers={"Content-Security-Policy": "default-src 'none'; form-action 'self' https://"+urlsplit(params["redirect_uri"]).hostname+"; frame-ancestors 'none'"})
            if path.startswith("/conversations/") and self.identity():
                return self.respond(b.history(path.rsplit("/", 1)[1], self.identity()))
            if path == "/mcp":
                if self.identity() != "dot":
                    return self.respond({"error": "Unauthorized"}, 401, {"WWW-Authenticate": 'Bearer resource_metadata="'+b.base+'/.well-known/oauth-protected-resource", scope="bridge"'})
                return self.respond({"error": "Use POST"}, 405)
            return self.respond({"error": "Not found"}, 404)
        except (Rejected, ValueError, TypeError):
            return self.respond({"error": "Invalid request"}, 400)

    def do_POST(self):
        b, path = self.bridge, urlsplit(self.path).path
        self.connection.settimeout(15)
        try:
            if not b.allow_public('all_post',120):
                return self.respond({'error':'Rate limited'},429)
            raw = self.body()
            if path in ("/authorize", "/token"):
                args = {k: v[0] for k, v in parse_qs(raw.decode()).items()}
            else:
                args = json.loads(raw)
                if not isinstance(args, dict):
                    raise Rejected("JSON object required")
            if path == "/register":
                if not b.allow_public('register', 10):
                    return self.respond({"error": "Rate limited"}, 429)
                redirects = args.get("redirect_uris", [])
                hosts = os.getenv("OAUTH_REDIRECT_HOSTS", "chatgpt.com,chat.openai.com").split(",")
                if not redirects or len(redirects) > 5 or any(urlsplit(u).scheme != "https" or urlsplit(u).hostname not in hosts or urlsplit(u).username or urlsplit(u).fragment for u in redirects):
                    raise Rejected("Redirect URI not allowed")
                client = secrets.token_urlsafe(24)
                with b.lock:
                    b.db.execute("INSERT INTO clients VALUES(?,?)", (client, json.dumps(redirects)))
                return self.respond({"client_id": client, "redirect_uris": redirects, "token_endpoint_auth_method": "none",
                                     "grant_types": ["authorization_code", "refresh_token"], "response_types": ["code"]}, 201)
            if path == "/authorize":
                if not b.allow_public('authorize', 10):
                    return self.respond({"error": "Rate limited"}, 429)
                with b.lock:
                    self.oauth_params(args)
                    if not hmac.compare_digest(args.get("owner_key", ""), b.admin_key):
                        raise Rejected("Owner key invalid")
                    code = secrets.token_urlsafe(32)
                    b.db.execute("INSERT INTO codes VALUES(?,?,?,?,?)", (digest(code), args["client_id"], args["redirect_uri"], args["code_challenge"], time.time()+120))
                query = {"code": code, "state": args.get("state", ""), "iss": b.base}
                return self.respond({}, 303, {"Location": args["redirect_uri"] + ("&" if "?" in args["redirect_uri"] else "?") + urlencode(query)})
            if path == "/token":
                with b.lock:
                    if args.get("resource") != b.base+"/mcp":
                        raise Rejected("Wrong resource")
                    client = args.get("client_id")
                    if args.get("grant_type") == "authorization_code":
                        code = b.db.execute("SELECT * FROM codes WHERE hash=?", (digest(args.get("code", "")),)).fetchone()
                        if not code or code["expires"] < time.time() or code["client"] != client or code["redirect"] != args.get("redirect_uri") or not hmac.compare_digest(code["challenge"], b64(hashlib.sha256(args.get("code_verifier", "").encode()).digest())):
                            raise Rejected("Invalid grant")
                        b.db.execute("DELETE FROM codes WHERE hash=?", (code["hash"],))
                    elif args.get("grant_type") == "refresh_token":
                        token = b.db.execute("SELECT * FROM tokens WHERE hash=? AND kind='refresh' AND expires>?", (digest(args.get("refresh_token", "")), time.time())).fetchone()
                        if not token or token["client"] != client:
                            raise Rejected("Invalid refresh token")
                        b.db.execute("DELETE FROM tokens WHERE hash=?", (token["hash"],))
                    else:
                        raise Rejected("Unsupported grant")
                    access, refresh = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
                    b.db.executemany("INSERT INTO tokens VALUES(?,?,?,?)", [(digest(access), client, "access", time.time()+3600), (digest(refresh), client, "refresh", time.time()+2592000)])
                return self.respond({"access_token": access, "refresh_token": refresh, "token_type": "Bearer", "expires_in": 3600, "scope": "bridge"})
            who = self.identity()
            if path == '/mcp':
                method_label = args.get('method', '')
                if isinstance(method_label, str) and re.fullmatch(r'[a-zA-Z/._-]{1,80}', method_label):
                    print('mcp', method_label, 'authenticated' if who else 'unauthenticated', flush=True)
            if path.startswith("/grok/"):
                token_hash = digest(path.rsplit("/", 1)[1])
                with b.lock:
                    msg = b.db.execute("SELECT * FROM messages WHERE callback_token_hash=?", (token_hash,)).fetchone()
                    if not msg:
                        return self.respond({"error": "Unauthorized"}, 401)
                    action = args.get("action")
                    strict_object(args, ("action", "text", "part_index", "final", "end_of_turn"), ("action",))
                    if action in ('claim', 'complete') and set(args) != {'action'}:
                        raise Rejected('Unexpected callback fields')
                    actor = b.callback_actor(msg)
                    if action == "claim":
                        result = b.claim(actor, msg["id"])
                    elif action == "complete":
                        result = b.finish(actor, msg["id"])
                    elif action == "reply":
                        result = b.callback_reply(msg['id'], args)
                    else:
                        raise Rejected("action must be claim/reply/complete")
                return self.respond(result)
            if not who:
                return self.respond({"error": "Unauthorized"}, 401, {"WWW-Authenticate": 'Bearer resource_metadata="'+b.base+'/.well-known/oauth-protected-resource", scope="bridge"'})
            if path == '/admin/revoke' and who=='admin':
                with b.lock:
                    b.db.execute('DELETE FROM tokens')
                    b.db.execute('DELETE FROM codes')
                    b.db.execute('UPDATE subscriptions SET active=0')
                    b.db.execute("UPDATE conversations SET state='stopped' WHERE state='active'")
                    b.db.execute("UPDATE messages SET status='stopped' WHERE status='queued'")
                return self.respond({'revoked':True})
            if path == "/messages" and (who == 'dot' or b.bot_enabled(who)):
                return self.respond(b.send(who, args))
            if path == "/stop":
                strict_object(args, ('conversation_id',), ('conversation_id',))
                return self.respond(b.stop(args["conversation_id"], who))
            if path != "/mcp" or who != "dot":
                return self.respond({"error": "Forbidden"}, 403)
            request_id = args.get("id")
            method, params = args.get("method"), args.get("params", {})
            try:
                if not isinstance(params, dict):
                    raise Rejected('MCP params must be an object')
                if method == "server/discover":
                    result = {"resultType": "complete", "supportedVersions": ["2026-07-28"], "capabilities": {"tools": {}, "events": {}}, "serverInfo": {"name": "grok-dot-bridge", "version": "0.1.0"}}
                elif method == "initialize":
                    result = {"protocolVersion": "2026-07-28", "capabilities": {"tools": {}, "events": {}}, "serverInfo": {"name": "grok-dot-bridge", "version": "0.1.0"}}
                elif method in ("ping", "notifications/initialized"):
                    result = {}
                elif method == "tools/list":
                    result = {"tools": [{"name": name, "description": description, "inputSchema": spec,
                                          "annotations": {"readOnlyHint": name == "get_conversation", "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
                                          "securitySchemes": [{"type": "oauth2", "scopes": ["bridge"]}]} for name, description, spec in TOOLS]}
                elif method == "events/list":
                    result = {"events": [EVENT]}
                elif method == "events/subscribe":
                    result = b.subscribe(params)
                elif method == "events/unsubscribe":
                    if params.get("name") != "message.created" or params.get("arguments") != {"recipient": "dot"}:
                        raise Rejected("Invalid subscription")
                    with b.lock:
                        b.db.execute("UPDATE subscriptions SET active=0 WHERE url=?", (params.get("delivery", {}).get("url"),))
                    result = {}
                elif method == "tools/call":
                    name, arguments = params.get("name"), params.get("arguments", {})
                    spec = next((s for n, _, s in TOOLS if n == name), None)
                    if not spec or not isinstance(arguments, dict) or set(arguments) - set(spec["properties"]) or set(spec["required"]) - set(arguments):
                        raise Rejected("Invalid tool arguments")
                    for field, value in arguments.items():
                        expected = spec['properties'][field].get('type')
                        if (expected == 'string' and not isinstance(value, str)) or (expected == 'boolean' and type(value) is not bool):
                            raise Rejected('Invalid tool argument type')
                    if name == "send_message":
                        value = b.send("dot", arguments)
                    elif name == "claim_message":
                        value = b.receive("dot") if arguments["message_id"] == "" else b.claim("dot", arguments["message_id"])
                    elif name == "complete_message":
                        value = b.finish("dot", arguments["message_id"])
                    elif name == "stop_conversation":
                        value = b.stop(arguments["conversation_id"], "dot")
                    else:
                        value = b.history(arguments["conversation_id"], "dot")
                    result = {"content": [{"type": "text", "text": encoded(value).decode()}], "isError": False}
                else:
                    return self.respond({"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Method not found"}})
                if request_id is None:
                    return self.respond({}, 202)
                return self.respond({"jsonrpc": "2.0", "id": request_id, "result": result})
            except (Rejected, OSError, ValueError, TypeError) as exc:
                if method == 'events/subscribe':
                    print('subscription error class', type(exc).__name__, flush=True)
                code = -32015 if method == "events/subscribe" else -32602
                return self.respond({"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": str(exc) if isinstance(exc, Rejected) else type(exc).__name__}})
        except (Rejected, KeyError, ValueError, TypeError):
            return self.respond({"error": "Invalid request"}, 400)


class LimitedServer(ThreadingHTTPServer):
    daemon_threads = True
    def __init__(self,*args,**kwargs):
        self.slots=threading.BoundedSemaphore(16)
        super().__init__(*args,**kwargs)

    def process_request(self,request,client_address):
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try:
            super().process_request(request,client_address)
        except BaseException:
            self.slots.release()
            raise

    def process_request_thread(self,request,client_address):
        try:
            super().process_request_thread(request,client_address)
        finally:
            self.slots.release()


def run():
    load_env()
    os.umask(0o077)
    admin, grok = os.getenv("ADMIN_KEY", ""), os.getenv("GROK_KEY", "")
    if len(admin) < 40 or len(grok) < 40 or admin == grok:
        raise SystemExit("Set different random ADMIN_KEY/GROK_KEY (at least 40 characters) in private .env")
    base = os.environ["PUBLIC_BASE_URL"]
    if urlsplit(base).scheme != "https":
        raise SystemExit("PUBLIC_BASE_URL must be HTTPS")
    bridge = Bridge(os.getenv("DB_PATH", "data/bridge.sqlite3"), base, admin, grok)
    server = LimitedServer((os.getenv("BIND_HOST", "127.0.0.1"), int(os.getenv("PORT", "8787"))), Handler)
    server.bridge = bridge
    def worker():
        while True:
            try:
                if not bridge.dispatch_one():
                    time.sleep(0.5)
            except Exception as exc:
                # Only exception class: never log URLs, credentials, or response bodies.
                print("delivery_worker:", type(exc).__name__, flush=True)
                time.sleep(1)
    threading.Thread(target=worker, daemon=True).start()
    print("grok-dot-bridge listening", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    run()
