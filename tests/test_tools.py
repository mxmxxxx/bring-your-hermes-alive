import contextlib
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from tools.doctor import CheckError, check, normalize_url, stream_text
from tools.init_env import create_config


class ConfigTests(unittest.TestCase):
    def test_private_unique_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory) / 'a.env', Path(directory) / 'b.env'
            create_config(a)
            create_config(b, 8643)
            original = a.read_text()
            self.assertIn('API_SERVER_HOST=127.0.0.1', original)
            self.assertNotEqual(original.split('API_SERVER_KEY=')[1], b.read_text().split('API_SERVER_KEY=')[1])
            with self.assertRaises(FileExistsError):
                create_config(a)
            self.assertEqual(original, a.read_text())
            if os.name != 'nt':
                self.assertEqual(stat.S_IMODE(a.stat().st_mode), 0o600)

    def test_invalid_port(self):
        with self.assertRaises(ValueError):
            create_config('unused', 0)


class ProtocolTests(unittest.TestCase):
    def test_urls(self):
        self.assertEqual(normalize_url('https://example.test'), 'https://example.test/v1')
        self.assertEqual(normalize_url('http://[::1]:8642/v1/'), 'http://[::1]:8642/v1')
        for url in ('http://remote.test/v1', 'https://u:p@example.test/v1',
                    'https://example.test/v1?key=secret', 'https://example.test/chat/completions',
                    'https://example.test:bad/v1', 'https://example.test/v1#secret'):
            with self.subTest(url=url), self.assertRaises(CheckError):
                normalize_url(url)

    def test_sse_progress_and_unicode(self):
        stream = (': heartbeat\n\nevent: hermes.tool.progress\ndata: {}\n\n'
                  'data: {"choices":[{"delta":{"content":"你好"}}]}\n\n'
                  'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}\n\n'
                  'data: [DONE]\n\n')
        self.assertEqual(''.join(stream_text(stream.encode().splitlines(keepends=True))), '你好')

    def test_truncation_and_errors(self):
        for stream in ('data: {}\n\n', 'data: INVALID\n\n', 'data: {"error":{}}\n\n'):
            with self.subTest(stream=stream), self.assertRaises(CheckError):
                list(stream_text(stream.splitlines(keepends=True)))


class HTTPTests(unittest.TestCase):
    def test_end_to_end_and_redirect(self):
        seen = []

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                seen.append(self.headers.get('Authorization'))
                if self.path.startswith('/redirect/'):
                    self.send_response(302)
                    self.send_header('Location', '/v1/models')
                    self.end_headers()
                    return
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{"data":[{"id":"test-model"}]}')

            def do_POST(self):
                seen.append(self.headers.get('Authorization'))
                data = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream' if data['stream'] else 'application/json')
                self.end_headers()
                if data['stream']:
                    self.wfile.write(b'data: {"choices":[{"delta":{"content":"hello"}}]}\n\ndata: [DONE]\n\n')
                else:
                    self.wfile.write(b'{"choices":[{"message":{"content":"hello"}}]}')

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                check(base + '/v1', 'test-secret', chat=True, stream=True)
            self.assertEqual(seen, ['Bearer test-secret'] * 3)
            self.assertNotIn('test-secret', output.getvalue())
            self.assertNotIn('hello', output.getvalue())
            before = len(seen)
            with self.assertRaises(CheckError):
                check(base + '/redirect/v1', 'test-secret')
            self.assertEqual(len(seen), before + 1)  # Redirect target was not requested.
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == '__main__':
    unittest.main()
