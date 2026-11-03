import unittest
from bridge import upstream_error_summary
class DiagnosticTests(unittest.TestCase):
    def test_redaction(self):
        result=upstream_error_summary(b'{"error":"failed", "key":"short-secret", "url":"https://example.org/private/token", "auth":"Bearer abcdef", "opaque":"abcdefghijklmnopqrstuvwxy0123456789"}',('short-secret',))
        for secret in ('short-secret','https://','abcdef','abcdefghijklmnopqrstuvwxy0123456789'):
            self.assertNotIn(secret,result)
        self.assertIn('failed',result)
    def test_bounded_and_malformed(self):
        self.assertLessEqual(len(upstream_error_summary(b'error '*1000+b'\xff')),800)
    def test_error_preserved(self):
        self.assertIn('quota exceeded',upstream_error_summary(b'{"error":"quota exceeded"}'))
if __name__=='__main__':unittest.main()
