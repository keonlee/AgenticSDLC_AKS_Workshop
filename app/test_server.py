import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import urlopen

from app.server import Handler, response_for


class ResponseTests(unittest.TestCase):
    def test_home(self):
        self.assertEqual(response_for("/"), (200, {"message": "Agentic SDLC workshop"}))

    def test_health(self):
        self.assertEqual(response_for("/healthz"), (200, {"status": "ok"}))

    def test_version(self):
        with patch.dict("os.environ", {"APP_VERSION": "test-sha"}):
            self.assertEqual(response_for("/version"), (200, {"version": "test-sha"}))

    def test_query_does_not_change_health_route(self):
        self.assertEqual(response_for("/healthz?probe=true")[0], 200)

    def test_unknown_route(self):
        self.assertEqual(response_for("/missing"), (404, {"error": "not found"}))


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def test_json_response(self):
        with urlopen(self.base_url + "/healthz", timeout=5) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers.get_content_type(), "application/json")
            self.assertEqual(json.load(response), {"status": "ok"})

    def test_http_not_found(self):
        with self.assertRaises(HTTPError) as error:
            urlopen(self.base_url + "/missing", timeout=5)
        self.assertEqual(error.exception.code, 404)
        self.assertEqual(json.load(error.exception), {"error": "not found"})
        error.exception.close()


if __name__ == "__main__":
    unittest.main()
