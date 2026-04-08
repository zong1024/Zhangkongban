import json
import threading
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn


HOST = "0.0.0.0"
PORT = 8765


STATE = {
    "command_id": 0,
    "signal": "",
    "source": "idle",
    "updated_at": "",
    "reports": [],
}
LOCK = threading.Lock()


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def append_report(event, payload):
    with LOCK:
        STATE["reports"].append(
            {
                "time": now_text(),
                "event": event,
                "payload": payload,
            }
        )
        STATE["reports"] = STATE["reports"][-30:]


def set_command(signal, source):
    with LOCK:
        STATE["command_id"] += 1
        STATE["signal"] = str(signal)
        STATE["source"] = source
        STATE["updated_at"] = now_text()


def snapshot_state():
    with LOCK:
        return {
            "command_id": STATE["command_id"],
            "signal": STATE["signal"],
            "source": STATE["source"],
            "updated_at": STATE["updated_at"],
            "reports": list(STATE["reports"]),
        }


INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Topic 3 Local Server</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; background: #f6f7fb; color: #18202a; }
    .wrap { max-width: 920px; margin: 0 auto; }
    h1 { margin-bottom: 8px; }
    .hint { color: #526172; margin-bottom: 20px; }
    .grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }
    .card { background: #fff; border-radius: 14px; padding: 18px; box-shadow: 0 8px 30px rgba(10, 20, 40, 0.08); }
    .buttons { display: flex; flex-wrap: wrap; gap: 10px; }
    button { border: 0; border-radius: 10px; padding: 12px 16px; font-size: 15px; cursor: pointer; }
    .split { background: #1d4ed8; color: #fff; }
    .red { background: #dc2626; color: #fff; }
    .green { background: #16a34a; color: #fff; }
    .blue { background: #2563eb; color: #fff; }
    .sensor { background: #d97706; color: #fff; }
    .clear { background: #374151; color: #fff; }
    code, pre { background: #0f172a; color: #e2e8f0; border-radius: 10px; }
    pre { padding: 14px; overflow: auto; min-height: 220px; }
    .row { margin: 8px 0; }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Topic 3 Local Server</h1>
    <div class="hint">Hotspot: zr / zongrui2 | Server port: 8765</div>
    <div class="grid">
      <div class="card">
        <h2>Send Signal</h2>
        <div class="buttons">
          <button class="split" onclick="sendSignal('split')">X = split</button>
          <button class="red" onclick="sendSignal('2')">X = 2 red</button>
          <button class="green" onclick="sendSignal('3')">X = 3 green</button>
          <button class="blue" onclick="sendSignal('4')">X = 4 blue</button>
          <button class="sensor" onclick="sendSignal('sensor')">extra sensor</button>
          <button class="clear" onclick="sendSignal('clear')">clear</button>
        </div>
        <div class="row" id="current"></div>
      </div>
      <div class="card">
        <h2>Board Reports</h2>
        <pre id="reports">waiting...</pre>
      </div>
    </div>
  </div>
  <script>
    async function sendSignal(signal) {
      await fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ signal, source: 'web' })
      });
      await refresh();
    }

    async function refresh() {
      const res = await fetch('/api/state');
      const data = await res.json();
      document.getElementById('current').textContent =
        `command_id=${data.command_id} signal=${data.signal || '-'} source=${data.source} updated=${data.updated_at || '-'}`;
      document.getElementById('reports').textContent =
        JSON.stringify(data.reports, null, 2);
    }

    refresh();
    setInterval(refresh, 1000);
  </script>
</body>
</html>
"""


class Topic3Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self._send_html(INDEX_HTML)
            return
        if self.path == "/api/state":
            self._send_json(snapshot_state())
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_POST(self):
        if self.path == "/api/command":
            payload = self._read_json()
            signal = payload.get("signal", "")
            source = payload.get("source", "web")
            set_command(signal, source)
            append_report("command", payload)
            self._send_json({"ok": True, "command_id": STATE["command_id"]})
            return
        if self.path == "/api/report":
            payload = self._read_json()
            append_report(payload.get("event", "report"), payload.get("payload"))
            self._send_json({"ok": True})
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    def _send_json(self, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html):
        body = html.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))


def main():
    print("Topic 3 server starting on http://%s:%s" % (HOST, PORT))
    print("Hotspot: zr / zongrui2")
    server = ThreadingHTTPServer((HOST, PORT), Topic3Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
