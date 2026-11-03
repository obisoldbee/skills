import os,time,unittest
from unittest.mock import patch
from test_bridge import BridgeTests
from bridge import Rejected

class CollaborationTests(BridgeTests):
    def test_long_work_survives_old_fifteen_minute_and_five_minute_limits(self):
        self.send(1)
        started=time.time()
        self.b.claim('grok','m1')
        with patch('bridge.time.time',return_value=started+1800):
            self.b.expire()
            self.assertEqual(self.b.message('m1')['status'],'agent_processing')
            self.send(2)
            expires=self.b.history('test')['conversation']['expires']
            self.assertGreater(expires,started+604800)

    def test_more_than_one_hundred_messages(self):
        for n in range(1,105):
            msg,_=self.send(n)
            self.b.claim(msg['recipient'],msg['id'])
        self.assertEqual(len(self.b.history('test')['messages']),104)

    def test_optional_operator_turn_limit(self):
        with patch.dict(os.environ,{'MAX_COMPLETED_TURNS':'2'}):
            for n in range(1,3):
                msg,_=self.send(n)
                self.b.claim(msg['recipient'],msg['id'])
            with self.assertRaisesRegex(Rejected,'Configured completed-turn'):
                self.send(3)

if __name__=='__main__': unittest.main()
