"""Local preview server for the report pages (this folder only, 127.0.0.1, UTF-8, no caching).

usage: python serve.py [PORT]
"""
import functools, http.server, sys
from pathlib import Path


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".html": "text/html; charset=utf-8", ".json": "application/json; charset=utf-8",
                      ".md": "text/plain; charset=utf-8"}

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8012
    handler = functools.partial(Handler, directory=str(Path(__file__).resolve().parent))
    http.server.ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()
