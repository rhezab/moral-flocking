"""Experiment viewer server. Serves only the viewer page, run files and dataset data
(never the repo root, which holds .env)."""
import json, sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUNS = ROOT / "experiments" / "runs"
DATA = ROOT / "moral-viewer" / "data.json"


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
            return self.send((HERE / "clusters.js").read_bytes(), "text/javascript; charset=utf-8")
        if path == "/api/items":
            return self.send((ROOT / "experiments" / "items.json").read_bytes(), "application/json")
        if path == "/data.json":
            return self.send(DATA.read_bytes(), "application/json")
        if path in ("/api/judgments", "/api/stances"):
            f = RUNS / ("judgments.jsonl" if path == "/api/judgments" else "stances.jsonl")
            lines = f.read_text().splitlines() if f.exists() else []
            return self.send(json.dumps([json.loads(l) for l in lines if l.strip()]).encode(), "application/json")
        if path == "/api/runs":
            records = []
            for f in sorted(RUNS.glob("*.jsonl")):
                if f.name in ("judgments.jsonl", "stances.jsonl"):
                    continue
                for i, line in enumerate(f.read_text().splitlines()):
                    if line.strip():
                        rec = json.loads(line)
                        rec["_file"], rec["_line"] = f.name, i
                        records.append(rec)
            return self.send(json.dumps(records).encode(), "application/json")
        self.send_error(404)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8008
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
