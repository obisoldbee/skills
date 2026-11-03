"""Isolated fake-credential/fake-transport tests. Only HTTP loopback; no provider I/O."""
import copy
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import threading
import time
import unittest
from http.client import HTTPConnection
from urllib.parse import urlsplit
from unittest.mock import patch
import bridge


class MultiBotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)
        self.calls = []
        self.registry = {'version': 1, 'bots': [self.bot('artist', '1'), self.bot('swe', '2')]}
        self.write_registry()
        self.env = patch.dict(os.environ, {'BOT_ROUTES_FILE': str(self.path/'routes.json'),
            'GROK_WEBHOOK_URL': 'https://legacy.example/hook', 'GROK_WEBHOOK_KEY': 'l'*48,
            'CALLBACK_HOSTS': 'dot.example'})
        self.env.start()
        self.b = self.open()
        self.b.subscribe({'name':'message.created','arguments':{'recipient':'dot'}, 'delivery':{
            'mode':'webhook','url':'https://dot.example/events','secret':'whsec_'+'YWJj'*8}})
        self.b.db.execute('INSERT INTO tokens VALUES(?,?,?,?)', (bridge.digest('dot-key'),'client','access',time.time()+10000))
        self.server = bridge.LimitedServer(('127.0.0.1', 0), bridge.Handler)
        self.server.bridge = self.b
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.b.close()
        self.env.stop()
        self.tmp.cleanup()

    @staticmethod
    def bot(name, digit):
        return {'id':name, 'bot_uuid':f'{digit*8}-{digit*4}-4{digit*3}-8{digit*3}-{digit*12}',
            'enabled':True, 'webhook_url':f'https://{name}.example/hook',
            'webhook_key':name+'-webhook-key-'+'w'*48, 'send_key':name+'-send-key-'+'s'*48}

    def write_registry(self):
        file = self.path/'routes.json'
        file.write_text(json.dumps(self.registry))
        file.chmod(0o600)

    def post(self, url, payload, headers):
        self.calls.append((url, payload, headers))
        if payload.get('type') == 'verification':
            return 200, json.dumps({'challenge':payload['challenge']}).encode()
        return 200, b'{}'

    def open(self):
        return bridge.Bridge(str(self.path/'test.sqlite'), 'https://bridge.example', 'a'*48, 'g'*48, self.post)

    def reopen(self):
        self.b.close()
        self.b = self.open()
        self.server.bridge = self.b

    def req(self, path, data=None, key=None):
        connection = HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        headers = {'Content-Type':'application/json'}
        if key:
            headers['Authorization'] = 'Bearer '+key
        connection.request('POST' if data is not None else 'GET', path, json.dumps(data) if data is not None else None, headers)
        response = connection.getresponse()
        value = response.status, json.loads(response.read())
        connection.close()
        return value

    def send(self, cid='c1', mid='m1', sender='dot', **extra):
        return self.b.send(sender, {'conversation_id':cid,'message_id':mid,'text':'work','recipient':'artist' if sender=='dot' else 'dot',**extra})

    def test_route_registry_strict_private_and_fail_closed(self):
        key = self.registry['bots'][0]['send_key']
        self.assertEqual(self.b.bearer(key), 'artist')
        cases = []
        for field, value in [('id','grok'),('id','Dot'),('bot_uuid','no-uuid'),('enabled',1),
                ('webhook_url','http://artist.example/hook'),('webhook_url','https://artist.example:8443/hook'),
                ('webhook_url','https://username@artist.example/hook'),('webhook_url','https://artist.example/hook#fragment'),
                ('send_key','short'),('send_key','g'*48),('webhook_key','short')]:
            candidate=copy.deepcopy(self.registry)
            candidate['bots'][0][field]=value
            cases.append(candidate)
        candidate=copy.deepcopy(self.registry);candidate['bots'][0]['unknown']='x';cases.append(candidate)
        candidate=copy.deepcopy(self.registry);candidate['bots'][1]['send_key']=key;cases.append(candidate)
        candidate=copy.deepcopy(self.registry);candidate['bots'][1]['bot_uuid']=candidate['bots'][0]['bot_uuid'];cases.append(candidate)
        candidate=copy.deepcopy(self.registry);candidate['bots'][0]['send_key_hash']=bridge.digest(key);cases.append(candidate)
        candidate=copy.deepcopy(self.registry);candidate['bots'][1]['webhook_url']=candidate['bots'][0]['webhook_url'];cases.append(candidate)
        candidate=copy.deepcopy(self.registry);candidate['bots'][1]['webhook_key']=candidate['bots'][0]['webhook_key'];cases.append(candidate)
        candidate=copy.deepcopy(self.registry);candidate['bots'][1]['send_key']=candidate['bots'][0]['webhook_key'];cases.append(candidate)
        candidate=copy.deepcopy(self.registry);candidate['bots'][0]['webhook_url']='https://legacy.example:443/hook';cases.append(candidate)
        for candidate in cases:
            with self.subTest(candidate=cases.index(candidate)):
                file=self.path/'invalid.json';file.write_text(json.dumps(candidate));file.chmod(0o600)
                with self.assertRaises(bridge.Rejected):
                    bridge.load_bot_routes(str(file), ('g'*48,'a'*48), 'https://legacy.example/hook')
        file=self.path/'routes.json';file.chmod(0o644)
        with self.assertRaises(bridge.Rejected):bridge.load_bot_routes(str(file),())
        file.chmod(0o600)
        link=self.path/'link.json';link.symlink_to(file)
        with self.assertRaises(bridge.Rejected):bridge.load_bot_routes(str(link),())
        file=self.path/'duplicate.json';file.write_text('{"version":1,"version":1,"bots":[]}');file.chmod(0o600)
        with self.assertRaises(bridge.Rejected):bridge.load_bot_routes(str(file),())

    def test_default_route_compatibility_and_unknown_never_falls_back(self):
        legacy=self.b.send('dot',{'conversation_id':'legacy','message_id':'legacy1','text':'legacy'})
        self.assertEqual(legacy['recipient'],'grok')
        self.assertTrue(self.b.dispatch_one())
        self.assertEqual(self.calls[-1][0], 'https://legacy.example/hook')
        for recipient in ('unknown','dot','admin'):
            with self.assertRaises(bridge.Rejected):self.send(cid=recipient,mid=recipient,recipient=recipient)
        self.b.db.execute("INSERT INTO conversations(id,state,expires,bot_id) VALUES('bad','active',?,'missing')",(time.time()+1000,))
        self.b.db.execute("INSERT INTO messages(id,conversation_id,recipient,status,next_attempt,subscription_id) SELECT 'unknown','bad','missing','queued',0,id FROM subscriptions LIMIT 1")
        before=len(self.calls)
        self.assertTrue(self.b.dispatch_one())
        self.assertEqual(len(self.calls),before)
        self.assertEqual(self.b.message('unknown')['status'],'failed')

    def test_http_mcp_and_identity_isolation(self):
        artist=self.registry['bots'][0]['send_key'];swe=self.registry['bots'][1]['send_key']
        rpc={'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'send_message','arguments':{
            'conversation_id':'c1','message_id':'m1','text':'draw','recipient':'artist','task_id':'task1','delegation_id':'d1'}}}
        status,body=self.req('/mcp',rpc,'dot-key')
        self.assertEqual(status,200);self.assertNotIn('error',body)
        self.assertEqual(self.req('/mcp',{'method':'tools/list'},artist)[0],403)
        self.assertEqual(self.req('/conversations/c1',key=artist)[0],200)
        self.assertEqual(self.req('/conversations/c1',key=swe)[0],400)
        self.assertEqual(self.req('/stop',{'conversation_id':'c1'},swe)[0],400)
        self.assertEqual(self.b.history('c1')['conversation']['state'],'active')
        self.assertEqual(self.req('/conversations/c1',key='g'*48)[0],400)
        for field in ('sender','webhook_url','delivery_url','callback_token'):
            self.assertEqual(self.req('/messages',{'conversation_id':'x','message_id':'x','text':'work',field:'dot'},artist)[0],400)
        self.assertEqual(self.req('/messages',{'conversation_id':'bad-target','message_id':'bad-target','text':'x','recipient':'swe'},artist)[0],400)
        self.assertEqual(self.req('/stop',{'conversation_id':'c1'},'a'*48)[0],200)

    def test_scoped_callback_identity_multipart_and_final(self):
        self.send(task_id='task1',delegation_id='delegate1')
        self.b.dispatch_one()
        delivered=self.calls[-1]
        self.assertEqual(delivered[0],'https://artist.example/hook')
        self.assertEqual(delivered[1]['recipient'],'artist')
        callback=urlsplit(delivered[1]['callback_url']).path
        self.assertEqual(self.req(callback,{'action':'claim','sender':'swe'})[0],400)
        self.assertEqual(self.req(callback,{'action':'claim'})[0],200)
        first={'action':'reply','text':'part1','part_index':0,'end_of_turn':False}
        code,part=self.req(callback,first)
        self.assertEqual(code,200);self.assertEqual(part['sender'],'artist');self.assertEqual(part['recipient'],'dot')
        self.assertEqual(part['task_id'],'task1')
        self.assertTrue(self.req(callback,first)[1]['duplicate'])
        self.assertEqual(self.req(callback,{**first,'recipient':'swe'})[0],400)
        final={'action':'reply','text':'part2','part_index':1,'final':True}
        code,part=self.req(callback,final)
        self.assertEqual(code,200);self.assertEqual(part['sender'],'artist')
        self.b.dispatch_one();self.b.dispatch_one()
        incoming=self.b.receive('dot');self.b.finish('dot',incoming['id'])
        incoming=self.b.receive('dot');self.b.finish('dot',incoming['id'])
        self.assertEqual(self.b.history('c1')['conversation']['state'],'completed')
        self.assertEqual(self.req(callback,final)[1]['duplicate'],True)
        with self.assertRaises(bridge.Rejected):self.send(mid='m-next',reply_to=part['id'])

    def test_bot_initiates_to_original_dot_and_dot_reply_returns_same_bot(self):
        artist=self.registry['bots'][0]['send_key']
        status,body=self.req('/messages',{'conversation_id':'artist-first','message_id':'artist1','text':'question'},artist)
        self.assertEqual(status,200);self.assertEqual(body['sender'],'artist');self.assertEqual(body['recipient'],'dot')
        self.b.dispatch_one()
        self.assertEqual(self.calls[-1][0],'https://dot.example/events')
        self.b.receive('dot')
        reply=self.b.send('dot',{'conversation_id':'artist-first','message_id':'dot-response','reply_to':'artist1','text':'answer'})
        self.assertEqual(reply['recipient'],'artist')
        self.b.dispatch_one();self.assertEqual(self.calls[-1][0],'https://artist.example/hook')
        with self.assertRaises(bridge.Rejected):self.b.send('swe',{'conversation_id':'artist-first','message_id':'hijack','reply_to':'dot-response','text':'x'})

    def test_dot_mcp_multipart_uses_latest_outgoing_without_self_claim(self):
        def rpc(name, arguments):
            status, body = self.req('/mcp', {'jsonrpc':'2.0', 'id':1,
                'method':'tools/call', 'params':{'name':name, 'arguments':arguments}}, 'dot-key')
            self.assertEqual(status, 200)
            return body

        def accepted(name, arguments):
            body = rpc(name, arguments)
            self.assertNotIn('error', body)
            return json.loads(body['result']['content'][0]['text'])

        artist = self.registry['bots'][0]['send_key']
        cid, incoming = 'dot-multipart', 'multipart-question'
        status, _ = self.req('/messages', {'conversation_id':cid,
            'message_id':incoming, 'text':'Review in two parts'}, artist)
        self.assertEqual(status, 200)
        self.b.dispatch_one()

        first = {'conversation_id':cid, 'message_id':'dot-part-1',
            'reply_to':incoming, 'text':'First review part', 'end_of_turn':False, 'final':False}
        self.assertIn('claim_message before replying', rpc('send_message', first)['error']['message'])
        self.assertIsNone(self.b.message(first['message_id']))
        self.assertTrue(accepted('claim_message', {'message_id':incoming})['claimed'])
        part1 = accepted('send_message', first)
        self.assertIsNone(part1['received_at'])

        # Outgoing messages cannot be claimed by their sender, and continuation must not need one.
        own_claim = rpc('claim_message', {'message_id':part1['id']})
        self.assertIn('Message not addressed to this agent', own_claim['error']['message'])
        early = {'conversation_id':cid, 'message_id':'artist-too-early',
            'reply_to':part1['id'], 'text':'Reply before turn ends'}
        self.assertEqual(self.req('/messages', early, artist)[0], 400)
        self.assertIsNone(self.b.message(early['message_id']))

        second = {'conversation_id':cid, 'message_id':'dot-part-2',
            'reply_to':incoming, 'text':'Last review part', 'end_of_turn':True, 'final':False}
        stale = rpc('send_message', second)
        self.assertIn('Reply must reference latest message', stale['error']['message'])
        self.assertIsNone(self.b.message(second['message_id']))
        second['reply_to'] = part1['id']
        part2 = accepted('send_message', second)
        self.assertEqual(part2['reply_to'], part1['id'])
        self.assertIsNone(self.b.message(part1['id'])['received_at'])
        self.assertTrue(accepted('send_message', second)['duplicate'])

        closed = rpc('send_message', {'conversation_id':cid, 'message_id':'dot-late-part',
            'reply_to':part2['id'], 'text':'Extra part after turn closed'})
        self.assertIn("Sender's turn is already closed", closed['error']['message'])
        self.assertIsNone(self.b.message('dot-late-part'))
        followup = {'conversation_id':cid, 'message_id':'artist-followup',
            'reply_to':part2['id'], 'text':'Follow-up after both parts'}
        self.assertEqual(self.req('/messages', followup, artist)[0], 400)
        self.assertIsNone(self.b.message(followup['message_id']))

        for expected_id in (part1['id'], part2['id']):
            self.b.dispatch_one()
            payload = self.calls[-1][1]
            self.assertEqual(payload['id'], expected_id)
            callback = urlsplit(payload['callback_url']).path
            self.assertTrue(self.req(callback, {'action':'claim'})[1]['claimed'])
            self.assertEqual(self.req(callback, {'action':'complete'})[0], 200)
        status, reply = self.req('/messages', followup, artist)
        self.assertEqual(status, 200)
        self.assertEqual(reply['sender'], 'artist')
        self.assertEqual(reply['recipient'], 'dot')

    def test_task_dedupe_delegation_unique_and_cycle_rejection(self):
        original=self.send(task_id='root-task',delegation_id='root-delegate')
        self.assertTrue(self.send(task_id='root-task',delegation_id='root-delegate')['duplicate'])
        for change in ({'recipient':'swe'},{'task_id':'different'},{'delegation_id':'different'}):
            values = {'task_id':'root-task','delegation_id':'root-delegate'} | change
            with self.assertRaises(bridge.Rejected):
                self.send(**values)
        child=self.send(cid='child',mid='child1',recipient='swe',task_id='child-task',parent_task_id='root-task',delegation_id='child-delegate')
        self.assertEqual(child['parent_task_id'],'root-task')
        continued=self.send(cid='child-continuation',mid='cc1',sender='swe',task_id='child-task')
        self.assertEqual(continued['parent_task_id'],'root-task')
        explicit=self.send(cid='child-followup',mid='cf1',sender='swe',task_id='child-task',parent_task_id='root-task')
        self.assertEqual(explicit['parent_task_id'],'root-task')
        with self.assertRaisesRegex(bridge.Rejected,'delegation_id'):
            self.send(cid='repeat',mid='repeat1',task_id='rollback-task',delegation_id='child-delegate')
        self.assertIsNone(self.b.db.execute("SELECT 1 FROM tasks WHERE id='rollback-task'").fetchone())
        with self.assertRaises(bridge.Rejected):self.send(cid='self',mid='self1',task_id='self',parent_task_id='self')
        with self.assertRaises(bridge.Rejected):self.send(cid='missing-parent',mid='mp',task_id='mp',parent_task_id='absent')
        with self.assertRaises(bridge.Rejected):self.send(cid='stranger',mid='stranger1',sender='swe',task_id='stranger-task',parent_task_id='root-task')
        self.b.db.execute("UPDATE tasks SET parent_task_id='child-task' WHERE id='root-task'")
        with self.assertRaisesRegex(bridge.Rejected,'cycle'):
            self.send(cid='cycle',mid='cycle1',task_id='other',parent_task_id='root-task')
        for field in ('recipient','task_id','parent_task_id','delegation_id'):
            with self.assertRaises(bridge.Rejected):self.send(cid='null-'+field,mid='null-'+field,**{field:None})

    def test_route_pin_disable_restart_and_scoped_epoch(self):
        self.send();self.b.dispatch_one()
        callback=urlsplit(self.calls[-1][1]['callback_url']).path
        self.send(cid='pending',mid='pending1')
        self.registry['bots'][0]['webhook_url']='https://artist-new.example/hook'
        self.write_registry();self.reopen()
        before=len(self.calls);self.b.dispatch_one()
        self.assertEqual(len(self.calls),before)
        self.assertEqual(self.b.message('pending1')['status'],'failed')
        self.assertEqual(self.req(callback,{'action':'claim'})[0],400)
        self.send(cid='disabled',mid='disabled1')
        self.registry['bots'][0]['enabled']=False;self.write_registry();self.reopen()
        self.assertIsNone(self.b.bearer(self.registry['bots'][0]['send_key']))
        self.b.dispatch_one();self.assertEqual(self.b.message('disabled1')['status'],'failed')
        self.registry['bots'][0]['enabled']=True;self.write_registry();self.reopen()
        self.send(cid='restart',mid='restart1')
        self.b.db.execute("UPDATE messages SET status='dispatching' WHERE id='restart1'")
        self.reopen();self.assertEqual(self.b.message('restart1')['status'],'delivery_unknown')
        self.assertFalse(self.b.dispatch_one())

    def test_bot_uuid_and_slug_cannot_be_reassigned_after_restart(self):
        self.send()
        self.b.close()
        self.registry['bots'][0]['bot_uuid']='33333333-3333-4333-8333-333333333333'
        self.write_registry()
        with self.assertRaisesRegex(bridge.Rejected,'identity binding'):
            self.open()
        self.registry['bots'][0]['bot_uuid']='11111111-1111-4111-8111-111111111111'
        self.registry['bots'][0]['id']='new-slug'
        self.write_registry()
        with self.assertRaisesRegex(bridge.Rejected,'identity binding'):
            self.open()
        self.registry['bots'][0]['id']='artist';self.write_registry()
        self.b=self.open();self.server.bridge=self.b

    def test_bot_timeout_302_and_diagnostic_never_retry_or_leak(self):
        self.send()
        self.b.post=lambda *_args: (_ for _ in ()).throw(TimeoutError())
        self.b.dispatch_one();self.assertEqual(self.b.message('m1')['status'],'delivery_unknown')
        self.assertFalse(self.b.dispatch_one())
        self.send(cid='redirect',mid='redirect1')
        count=[]
        def reject(url,payload,headers):
            count.append(url)
            bot=self.registry['bots'][0]
            return 302, (' '.join([bot['webhook_url'],bot['webhook_key'],bot['send_key'],payload['callback_url'],payload['text']])).encode()
        self.b.post=reject
        self.b.dispatch_one();self.assertEqual(len(count),1)
        self.assertEqual(self.b.message('redirect1')['status'],'failed')
        history=json.dumps(self.b.history('redirect'))
        for secret in (self.registry['bots'][0]['send_key'],self.registry['bots'][0]['webhook_key'],self.registry['bots'][0]['webhook_url']):
            self.assertNotIn(secret,history)
        self.assertFalse(self.b.dispatch_one())

    def test_old_database_append_migration_preserves_oauth_and_original_queue(self):
        # Drop additive tables/columns by constructing the original schema in a separate fake database.
        path=str(self.path/'old.sqlite')
        old=sqlite3.connect(path)
        old.executescript('''CREATE TABLE conversations(id TEXT PRIMARY KEY,state TEXT,expires REAL,subscription_id TEXT);
          CREATE TABLE messages(id TEXT PRIMARY KEY,conversation_id TEXT,sender TEXT,recipient TEXT,text TEXT,
            reply_to TEXT UNIQUE,sent_at TEXT,received_at TEXT,processed_at TEXT,status TEXT,final INTEGER,
            attempts INTEGER DEFAULT 0,next_attempt REAL DEFAULT 0,delivery_url TEXT,subscription_id TEXT,callback_token_hash TEXT,error TEXT,
            claim_deadline REAL,end_of_turn INTEGER NOT NULL DEFAULT 1);
          CREATE TABLE tokens(hash TEXT PRIMARY KEY,client TEXT,kind TEXT,expires REAL);
          CREATE TABLE binding(slot INTEGER PRIMARY KEY CHECK(slot=1),subscription_id TEXT NOT NULL);
          CREATE TABLE subscriptions(id TEXT PRIMARY KEY,url TEXT,secret TEXT,old_secret TEXT,rotate_until REAL,expires REAL,active INTEGER);''')
        sub=self.b.db.execute('SELECT * FROM subscriptions').fetchone()
        old.execute('INSERT INTO subscriptions VALUES(?,?,?,?,?,?,?)',tuple(sub))
        old.execute('INSERT INTO binding VALUES(1,?)',(sub['id'],))
        old.execute('INSERT INTO tokens VALUES(?,?,?,?)',(bridge.digest('legacy-dot'),'legacy','access',time.time()+1000))
        old.execute("INSERT INTO conversations VALUES('old','active',?,?)",(time.time()+1000,sub['id']))
        old.execute("INSERT INTO messages(id,conversation_id,sender,recipient,text,status,subscription_id) VALUES('old1','old','dot','grok','legacy','queued',?)",(sub['id'],))
        old.commit();old.close()
        migrated=bridge.Bridge(path,'https://bridge.example','a'*48,'g'*48,self.post)
        try:
            self.assertEqual(migrated.bearer('legacy-dot'),'dot')
            self.assertEqual(migrated.history('old')['conversation']['bot_id'],'grok')
            migrated.dispatch_one();self.assertEqual(self.calls[-1][0],'https://legacy.example/hook')
            migrated.claim('grok','old1')
            result=migrated.callback_reply('old1',{'text':'answer'})
            self.assertEqual(result['recipient'],'dot');self.assertIsNone(result['task_id'])
            self.assertTrue(migrated.callback_reply('old1',{'text':'answer'})['duplicate'])
            child=migrated.send('dot',{'conversation_id':'legacy-child','message_id':'legacy-child1','text':'child',
                'recipient':'artist','task_id':'legacy-child-task','parent_task_id':'old','delegation_id':'legacy-child-delegate'})
            self.assertEqual(child['parent_task_id'],'old')
        finally:migrated.close()


if __name__ == '__main__': unittest.main()
