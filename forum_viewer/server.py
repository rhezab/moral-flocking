"""Forum viewer: the public discussion transcripts, round by round.
Same data API as the discussion viewer; serves its own page."""
import sys
from http.server import HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "discussion_viewer"))
import server as base  # noqa: E402

HERE = Path(__file__).resolve().parent


class Handler(base.Handler):
    def do_GET(self):
        if self.path.split("?")[0] in ("/", "/index.html"):
            return self.send((HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
        return super().do_GET()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8011
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
