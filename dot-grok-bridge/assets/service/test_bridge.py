"""Focused invariants only. These tests are NOT real-agent acceptance."""
import json
import os
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from bridge import Bridge, Rejected, reply_id, public_post


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.calls = []
        def transport(url, payload, headers):
            self.calls.append((url, payload, headers))
            if payload.get("type") == "verification":
                return 200, json.dumps({"challenge": payload["challenge"]}).encode()
            return 200, b"{}"
        self.env = patch.dict(os.environ, {"GROK_WEBHOOK_URL": "https://bot.example/trigger", "GROK_WEBHOOK_KEY": "test-only", "CALLBACK_HOSTS": "callback.example"})
        self.env.start()
        self.b = Bridge(self.tmp.name+"/test.sqlite", "https://bridge.example", "a"*48, "g"*48, transport)
        self.b.subscribe({"name": "message.created", "arguments": {"recipient": "dot"}, "delivery": {"mode": "webhook", "url": "https://callback.example/events", "secret": "whsec_"+"YWJj"*8}})

    def tearDown(self):
        self.b.close()
        self.env.stop()
        self.tmp.cleanup()

    def send(self, n, final=False):
        sender = "dot" if n % 2 else "grok"
        args = {"conversation_id": "test", "message_id": f"m{n}", "text": f"test-only-{n}", "final": final}
        if n > 1:
            args["reply_to"] = f"m{n-1}"
        return self.b.send(sender, args), args

    def test_duplicate_delivery_and_claim_beyond_four_rounds(self):
        for n in range(1, 13):
            msg, args = self.send(n)
            self.assertTrue(self.b.send(msg["sender"], args)["duplicate"])
            self.assertTrue(self.b.dispatch_one())
            self.assertFalse(self.b.dispatch_one())
            self.assertTrue(self.b.claim(msg["recipient"], msg["id"])["claimed"])
            self.assertFalse(self.b.claim(msg["recipient"], msg["id"])["claimed"])
        self.assertEqual(len(self.calls), 13)  # verification + exactly 12 deliveries
        self.send(13)

    def test_realistic_final_receipt_has_separate_completion(self):
        for n in range(1, 4):
            msg, _ = self.send(n, final=n == 3)
            self.b.dispatch_one()
            self.b.claim(msg["recipient"], msg["id"])
        self.b.finish("grok", "m3")
        history = self.b.history("test")
        self.assertEqual(history["conversation"]["state"], "completed")
        self.assertEqual(history["messages"][-1]["status"], "completed")
        with self.assertRaises(Rejected):
            self.send(4)

    def test_event_wakeup_without_payload_receives_only_once(self):
        self.send(1)
        self.b.dispatch_one()
        self.b.claim('grok', 'm1')
        self.send(2)
        self.assertFalse(self.b.receive('dot')['claimed'])
        self.b.dispatch_one()
        received = self.b.receive('dot')
        self.assertTrue(received['claimed'])
        self.assertEqual(received['id'], 'm2')
        self.assertFalse(self.b.receive('dot')['claimed'])

    def test_ambiguous_grok_timeout_is_not_retried(self):
        self.send(1)
        def timeout(*_args):
            raise TimeoutError()
        self.b.post = timeout
        self.b.dispatch_one()
        self.assertEqual(self.b.message("m1")["status"], "delivery_unknown")
        self.assertFalse(self.b.dispatch_one())

    def test_stop_expiration_and_reply_fork_prevention(self):
        self.send(1)
        with self.assertRaises(Rejected):
            self.send(2)  # never claimed
        self.b.stop("test")
        self.assertFalse(self.b.dispatch_one())
        self.assertEqual(self.b.message("m1")["status"], "stopped")
        with self.assertRaises(Rejected):
            self.b.claim("grok", "m1")

    def test_transport_receipt_is_not_agent_receipt(self):
        self.send(1)
        self.b.dispatch_one()
        msg = self.b.message("m1")
        self.assertEqual(msg["status"], "routine_accepted")
        self.assertIsNone(msg["received_at"])
        self.assertIsNone(msg["processed_at"])

    def test_second_subscription_cannot_hijack_original_conversation(self):
        self.send(1)
        original=self.b.db.execute('SELECT subscription_id FROM conversations').fetchone()[0]
        with self.assertRaisesRegex(Rejected,'original Dot'):
            self.b.subscribe({'name':'message.created','arguments':{'recipient':'dot'},'delivery':{'mode':'webhook','url':'https://callback.example/another-chat','secret':'whsec_'+'YWJj'*8}})
        self.b.claim('grok','m1')
        self.send(2)
        self.assertEqual(self.b.db.execute("SELECT subscription_id FROM messages WHERE id='m2'").fetchone()[0],original)

    def test_expired_original_cannot_fall_back_to_new_subscription(self):
        self.send(1)
        self.b.claim('grok','m1')
        self.b.db.execute('UPDATE subscriptions SET expires=0')
        with self.assertRaisesRegex(Rejected,'Original Dot'):
            self.send(2)

    def test_long_id_reply_and_collision_resistance(self):
        for length in (1,94,95,100):
            mid='m'*length
            self.assertLessEqual(len(reply_id(mid)),100)
            self.assertEqual(reply_id(mid),reply_id(mid))
        self.assertNotEqual(reply_id('m'*99+'a'),reply_id('m'*99+'b'))
        mid='m'*100
        self.b.send('dot',{'conversation_id':'long','message_id':mid,'text':'x'})
        self.b.claim('grok',mid)
        msg=self.b.send('grok',{'conversation_id':'long','message_id':reply_id(mid),'reply_to':mid,'text':'answer','final':True})
        self.assertEqual(msg['recipient'],'dot')
        with self.assertRaises(Rejected):
            self.b.send('dot',{'conversation_id':'bad','message_id':'m'*101,'text':'x'})

    def test_only_one_concurrent_claim(self):
        self.send(1)
        with ThreadPoolExecutor(max_workers=8) as pool:
            claimed=list(pool.map(lambda _:self.b.claim('grok','m1')['claimed'],range(20)))
        self.assertEqual(sum(claimed),1)

    def test_second_process_connection_fails_closed(self):
        with self.assertRaisesRegex(Rejected,'Only one bridge'):
            Bridge(self.tmp.name+'/test.sqlite','https://bridge.example','a'*48,'g'*48)

    def test_lease_expiry_does_not_repeat_external_work(self):
        self.send(1);self.b.claim('grok','m1')
        self.b.db.execute('UPDATE messages SET claim_deadline=0')
        self.b.expire()
        self.assertEqual(self.b.message('m1')['status'],'processing_unknown')
        self.assertFalse(self.b.claim('grok','m1')['claimed'])
        self.assertFalse(self.b.dispatch_one())

    def test_restart_preserves_unknown_claims_and_binding(self):
        self.send(1);self.b.claim('grok','m1')
        self.b.close()
        self.b=Bridge(self.tmp.name+'/test.sqlite','https://bridge.example','a'*48,'g'*48)
        self.assertEqual(self.b.message('m1')['status'],'processing_unknown')
        self.assertFalse(self.b.claim('grok','m1')['claimed'])
        self.assertIsNotNone(self.b.db.execute('SELECT * FROM binding').fetchone())

    def test_daily_cap_preserves_idempotent_retry(self):
        with patch.dict(os.environ,{'MAX_MESSAGES_PER_DAY':'1'}):
            _,args=self.send(1)
            self.assertTrue(self.b.send('dot',args)['duplicate'])
            self.b.claim('grok','m1')
            with self.assertRaisesRegex(Rejected,'Daily'):
                self.send(2)

    def test_private_callback_address_is_rejected_before_connect(self):
        with patch('socket.getaddrinfo',return_value=[(2,1,6,'',('127.0.0.1',443))]):
            with self.assertRaisesRegex(Rejected,'Non-public'):
                public_post('https://callback.example/path',{}, {})


if __name__ == "__main__":
    unittest.main()
