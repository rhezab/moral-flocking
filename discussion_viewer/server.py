"""Discussion-experiment viewer server. Serves only the page, shared figure code and
experiment data (never the repo root, which holds .env)."""
import json, sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNS = ROOT / "experiments" / "runs"
SOURCES = lambda: sorted(p.name for p in RUNS.glob("discussion*.jsonl") if "dryrun" not in p.name)  # main + separate run files


def jsonl(path, keep=lambda r: True):
    if not path.exists():
        return []
    return [r for r in (json.loads(l) for l in path.read_text().splitlines() if l.strip()) if keep(r)]


class Handler(SimpleHTTPRequestHandler):
    def send(self, body, ctype):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            return self.send((HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
        if path == "/clusters.js":
            return self.send((ROOT / "experiments" / "viewer" / "clusters.js").read_bytes(), "text/javascript; charset=utf-8")
        if path == "/api/items":
            return self.send((ROOT / "experiments" / "items.json").read_bytes(), "application/json")
        if path == "/api/records":
            recs = []
            for src in SOURCES():
                part = jsonl(RUNS / src)
                for i, r in enumerate(part):
                    r["_ref"] = f"{src}:{i}"
                recs += part
            return self.send(json.dumps(recs).encode(), "application/json")
        if path in ("/api/judgments", "/api/stances"):
            stem = "judgments" if path == "/api/judgments" else "stances"
            srcs = tuple(s + ":" for s in SOURCES())
            mine = [r for f in sorted(RUNS.glob(stem + "*.jsonl")) for r in jsonl(f, lambda r: r["reply_ref"].startswith(srcs))]
            return self.send(json.dumps(mine).encode(), "application/json")
        self.send_error(404)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8009
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
