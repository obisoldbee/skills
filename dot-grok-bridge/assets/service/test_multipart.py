import unittest
from test_bridge import BridgeTests
from bridge import Rejected


class MultipartTests(BridgeTests):
    def start(self):
        self.send(1)
        self.b.claim('grok', 'm1')

    def part(self, index, text, end=False, final=False):
        return self.b.callback_reply('m1', {'part_index': index, 'text': text,
                                           'end_of_turn': end, 'final': final})

    def test_multiple_parts_then_next_round(self):
        self.start()
        a = self.part(0, 'first')
        self.assertFalse(a['end_of_turn'])
        self.b.claim('dot', a['id'])
        with self.assertRaisesRegex(Rejected, 'turn is still open'):
            self.b.send('dot', {'conversation_id': 'test', 'message_id': 'early',
                               'reply_to': a['id'], 'text': 'too soon'})
        self.b.finish('dot', a['id'])
        self.assertEqual(self.b.history('test')['conversation']['state'], 'active')
        b = self.part(1, 'second', end=True)
        self.b.claim('dot', b['id'])
        self.b.finish('dot', b['id'])
        c = self.b.send('dot', {'conversation_id': 'test', 'message_id': 'next',
                               'reply_to': b['id'], 'text': 'follow-up'})
        self.assertEqual(c['recipient'], 'grok')

    def test_retry_order_and_final_seal(self):
        self.start()
        with self.assertRaises(Rejected):
            self.part(1, 'out of order')
        a = self.part(0, 'first')
        self.assertTrue(self.part(0, 'first')['duplicate'])
        with self.assertRaises(Rejected):
            self.part(0, 'changed')
        with self.assertRaises(Rejected):
            self.part(1, 'invalid final', final=True)
        b = self.part(1, 'last', end=True, final=True)
        self.b.claim('dot', b['id'])
        with self.assertRaisesRegex(Rejected, 'Earlier reply parts'):
            self.b.finish('dot', b['id'])
        self.b.claim('dot', a['id'])
        self.b.finish('dot', a['id'])
        self.b.finish('dot', b['id'])
        self.assertEqual(self.b.history('test')['conversation']['state'], 'completed')
        with self.assertRaises(Rejected):
            self.part(2, 'late', end=True)

    def test_closed_turn_cannot_continue(self):
        self.start()
        self.part(0, 'done', end=True)
        with self.assertRaises(Rejected):
            self.part(1, 'not part of the same turn', end=True)

    def test_parts_do_not_consume_turn_budget(self):
        self.start()
        for i in range(10):
            self.part(i, str(i), end=i == 9)
        self.assertEqual(len(self.b.history('test')['messages']), 11)

    def test_part_bounds_and_claim(self):
        self.send(1)
        with self.assertRaises(Rejected):
            self.part(0, 'unclaimed')
        self.b.claim('grok', 'm1')
        for bad in (-1, True, 1.5, '1', 16):
            with self.assertRaises(Rejected):
                self.part(bad, 'bad index')


if __name__ == '__main__':
    unittest.main()
