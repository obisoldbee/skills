import time
import unittest
from unittest.mock import patch
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

    def test_delayed_part_preserves_retry_before_final_reply(self):
        self.b.send('grok', {'conversation_id': 'test', 'message_id': 'first',
                             'text': 'first part', 'end_of_turn': False})
        self.b.send('grok', {'conversation_id': 'test', 'message_id': 'last',
                             'reply_to': 'first', 'text': 'last part'})
        final = {'conversation_id': 'test', 'message_id': 'final', 'reply_to': 'last',
                 'text': 'received both', 'final': True}
        now = time.time()
        with patch.object(self.b, 'event_post', side_effect=[(503, b''), (200, b''), (200, b'')]), \
                patch('bridge.time.time', return_value=now) as clock:
            self.b.dispatch_one()
            self.b.dispatch_one()
            self.assertEqual(self.b.message('first')['status'], 'queued')
            self.assertTrue(self.b.claim('dot', 'last')['claimed'])
            self.b.finish('dot', 'last')
            with self.assertRaisesRegex(Rejected, 'Earlier reply parts'):
                self.b.send('dot', final)
            self.assertIsNone(self.b.message('final'))
            self.assertEqual(self.b.history('test')['conversation']['state'], 'active')
            clock.return_value = now + 3
            self.assertTrue(self.b.dispatch_one())
        self.assertEqual(self.b.message('first')['attempts'], 2)
        self.assertTrue(self.b.claim('dot', 'first')['claimed'])
        self.b.finish('dot', 'first')
        self.b.send('dot', final)
        self.b.dispatch_one()
        self.b.claim('grok', 'final')
        self.b.finish('grok', 'final')
        history = self.b.history('test')
        self.assertEqual(history['conversation']['state'], 'completed')
        self.assertTrue(all(m['received_at'] and m['processed_at'] and m['status'] != 'stopped'
                            for m in history['messages']))

    def test_existing_final_cannot_close_with_a_gap_for_other_recipient(self):
        first = self.b.send('grok', {'conversation_id': 'test', 'message_id': 'first',
                                     'text': 'part one', 'end_of_turn': False})
        self.b.send('grok', {'conversation_id': 'test', 'message_id': 'last',
                             'reply_to': first['id'], 'text': 'part two'})
        self.b.claim('dot', 'last')
        self.b.send('dot', {'conversation_id': 'test', 'message_id': 'old-final',
                            'reply_to': 'last', 'text': 'receipt'})
        # A previous service version could already have persisted this final.
        self.b.db.execute("UPDATE messages SET final=1 WHERE id='old-final'")
        self.b.claim('grok', 'old-final')
        with self.assertRaisesRegex(Rejected, 'Earlier reply parts'):
            self.b.finish('grok', 'old-final')
        self.assertIsNone(self.b.message('old-final')['processed_at'])
        self.b.claim('dot', 'first')
        self.b.finish('dot', 'first')
        self.b.finish('grok', 'old-final')
        self.assertEqual(self.b.history('test')['conversation']['state'], 'completed')

    def test_only_the_open_outgoing_turn_can_still_be_in_flight(self):
        def send(actor, mid, parent=None, **flags):
            return self.b.send(actor, {'conversation_id': 'test', 'message_id': mid,
                                       'text': mid, 'reply_to': parent, **flags})
        send('grok', 'old-first', end_of_turn=False)
        send('grok', 'old-last', 'old-first')
        self.b.claim('dot', 'old-last')
        send('dot', 'question', 'old-last')
        self.b.claim('grok', 'question')
        send('grok', 'new-first', 'question', end_of_turn=False)
        with self.assertRaisesRegex(Rejected, 'Earlier reply parts'):
            send('grok', 'new-last', 'new-first', final=True)
        self.b.claim('dot', 'old-first')
        self.b.finish('dot', 'old-first')
        self.assertTrue(send('grok', 'new-last', 'new-first', final=True)['final'])

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
