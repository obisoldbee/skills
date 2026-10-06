"""Offline redirect transport test: no sockets, synthetic credentials only."""
import importlib.util
import io
import unittest
import urllib.error
import urllib.request
from email.message import Message
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = ['scripts/providers/agnes_vision.py', 'scripts/providers/minimax_m3_course_audio.py', 'scripts/providers/minimax_m3_course_video.py']

class RedirectTests(unittest.TestCase):
    def test_authenticated_post_never_follows_redirect(self):
        real_builder = urllib.request.build_opener
        for index, relative in enumerate(PROVIDERS):
            spec = importlib.util.spec_from_file_location(f"redirect_provider_{index}", ROOT / relative)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for code in (301, 302, 303, 307, 308):
                for location in ("https://other.invalid/collect", "http://source.invalid/plain", "https://source.invalid/next"):
                    with self.subTest(provider=relative, code=code, location=location):
                        sent = []
                        class Transport(urllib.request.HTTPSHandler):
                            def https_open(self, request):
                                sent.append(request)
                                headers = Message()
                                headers["Location"] = location
                                response = urllib.response.addinfourl(io.BytesIO(b""), headers, request.full_url, code)
                                response.msg = "Redirect"
                                return response
                        def builder(*handlers):
                            return real_builder(urllib.request.ProxyHandler({}), Transport(), *handlers)
                        request = urllib.request.Request("https://source.invalid/generate", data=b"{}",
                            headers={"Authorization": "Bearer synthetic", "X-Api-Key": "synthetic"})
                        with mock.patch.object(module.urllib.request, "build_opener", side_effect=builder), \
                             mock.patch("socket.create_connection", side_effect=AssertionError("network forbidden")):
                            with self.assertRaises(urllib.error.HTTPError) as raised:
                                module.authenticated_urlopen(request, timeout=1)
                        raised.exception.close()
                        self.assertEqual(code, raised.exception.code)
                        self.assertEqual(["https://source.invalid/generate"], [r.full_url for r in sent])
                        self.assertEqual("POST", sent[0].get_method())

if __name__ == "__main__":
    unittest.main()
