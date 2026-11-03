"""Offline routing identities; all health delivery is mocked."""
import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch
import service_health
from report_common import page_text, parse_space_id, validate_space_id


class BrowserIdentityTests(unittest.TestCase):
    def run_cli(self, page, identity=None):
        argv = ['service_health.py', '--phase', 'unknown', '--page', page,
                '--chat-id', 'oc_offline_fixture']
        if identity is not None:
            argv += ['--space-id', identity]
        output, error = io.StringIO(), io.StringIO()
        with patch('sys.argv', argv), patch.object(service_health, 'observe',
                return_value={'status': 'not_triggered', 'transition': None}) as observe:
            with redirect_stdout(output), redirect_stderr(error):
                try:
                    result = service_health.main()
                except SystemExit as exc:
                    result = exc.code
        return result, observe, output.getvalue(), error.getvalue()

    def test_legacy_ego_integer_still_accepts_and_formats(self):
        result, observe, _, _ = self.run_cli('closed', '37')
        self.assertEqual(result, 0)
        self.assertEqual(observe.call_args.kwargs['page'], '已关闭（空间 37）')
        self.assertEqual(parse_space_id('37'), 37)
        self.assertEqual(page_text({'status': 'preserved', 'space_id': 37}), '已保留（空间 37）')

    def test_ego_missing_or_negative_identity_fails_before_observation(self):
        for identity in (None, '-1'):
            result, observe, _, _ = self.run_cli('closed', identity)
            self.assertEqual(result, 2)
            observe.assert_not_called()

    def test_actual_non_ego_identifiers_pass_created_page_statuses(self):
        for identity in ('tabbit:tab:42', 'edge:tab:abc', 'system-browser:tab:7',
                         'harness-browser:tab:9'):
            for status in ('closed', 'preserved', 'unconfirmed'):
                result, observe, _, _ = self.run_cli(status, identity)
                self.assertEqual(result, 0)
                self.assertIn('页面 ' + identity, observe.call_args.kwargs['page'])
                self.assertEqual(parse_space_id(identity), identity)

    def test_missing_non_ego_identifier_cannot_be_normalized_to_zero(self):
        for status in ('closed', 'preserved', 'unconfirmed'):
            result, observe, _, _ = self.run_cli(status)
            self.assertEqual(result, 2)
            observe.assert_not_called()

    def test_not_created_accepts_only_no_identity(self):
        result, observe, _, _ = self.run_cli('not_created')
        self.assertEqual(result, 0)
        self.assertEqual(observe.call_args.kwargs['page'], '未创建')
        for identity in ('37', 'tabbit:tab:42'):
            result, observe, _, _ = self.run_cli('not_created', identity)
            self.assertEqual(result, 2)
            observe.assert_not_called()
            with self.assertRaises(ValueError):
                page_text({'status': 'not_created', 'space_id': parse_space_id(identity)})

    def test_renderer_accepts_non_ego_anomaly_and_keeps_normal_five_line_label(self):
        self.assertEqual(page_text({'status': 'unconfirmed', 'space_id': 'edge:tab:abc'}),
                         '关闭未确认（页面 edge:tab:abc）')
        self.assertEqual(page_text({'status': 'closed', 'space_id': 'tabbit:tab:42'}), '已关闭')

    def test_identity_rejects_malformed_values_even_for_closed_page(self):
        for identity in (True, -1, '', '42', 'unknown:tab:42', 'tabbit:tab:',
                         'tabbit:tab:two words', 'edge:tab:bad\nline', 'edge:tab:```'):
            with self.subTest(identity=repr(identity)):
                with self.assertRaises(ValueError):
                    validate_space_id(identity)
                with self.assertRaises(ValueError):
                    page_text({'status': 'closed', 'space_id': identity})

    def test_bad_cli_identity_never_calls_health_or_sender(self):
        for identity in ('other:tab:4', 'tabbit:tab:', 'tabbit:tab:two words'):
            result, observe, _, _ = self.run_cli('closed', identity)
            self.assertEqual(result, 2)
            observe.assert_not_called()


if __name__ == '__main__':
    unittest.main()
