import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


def response_for(path):
    route = urlsplit(path).path
    if route == "/":
        return 200, {"message": "Agentic SDLC workshop"}
    if route == "/healthz":
        return 200, {"status": "ok"}
    if route == "/version":
        return 200, {"version": os.environ.get("APP_VERSION", "local")}
    return 404, {"error": "not found"}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        status, payload = response_for(self.path)
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8080), Handler)
    print("Listening on port 8080", flush=True)
    server.serve_forever()
