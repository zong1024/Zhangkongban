import json
import threading
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn


HOST = "0.0.0.0"
PORT = 8766


STATE = {
    "latest_detection": None,
    "help_active": False,
    "help_reply": "",
    "help_payload": None,
    "logs": [],
}
LOCK = threading.Lock()

LABELS = {
    "person": {"label_cn": "人", "message": "前方有人"},
    "chair": {"label_cn": "椅子", "message": "前方有椅子"},
    "table": {"label_cn": "桌子", "message": "前方有桌子"},
    "status": {"label_cn": "在线", "message": "设备在线"},
    "unknown": {"label_cn": "未知", "message": "未知障碍"},
}


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def append_log(event_type, payload):
    with LOCK:
        STATE["logs"].append(
            {
                "time": now_text(),
                "event": event_type,
                "payload": payload,
            }
        )
        STATE["logs"] = STATE["logs"][-80:]


def enrich_payload(payload):
    payload = dict(payload or {})
    category = str(payload.get("category", "")).strip().lower()
    obstacle = str(payload.get("obstacle", "")).strip().lower()

    if category in LABELS:
        payload.setdefault("label_cn", LABELS[category]["label_cn"])
        payload.setdefault("message", LABELS[category]["message"])

    if obstacle in LABELS:
        payload.setdefault("obstacle_label_cn", LABELS[obstacle]["label_cn"])

    return payload


def set_detection(payload):
    with LOCK:
        payload = enrich_payload(payload)
        payload["server_time"] = now_text()
        STATE["latest_detection"] = payload


def set_help(payload):
    with LOCK:
        payload = enrich_payload(payload)
        payload["server_time"] = now_text()
        STATE["help_reply"] = ""
        STATE["help_active"] = True
        STATE["help_payload"] = payload


def ack_help():
    with LOCK:
        STATE["help_reply"] = "0"
        STATE["help_active"] = False


def reset_help():
    with LOCK:
        STATE["help_reply"] = ""
        STATE["help_active"] = False
        STATE["help_payload"] = None


def snapshot_state():
    with LOCK:
        return {
            "latest_detection": STATE["latest_detection"],
            "help_active": STATE["help_active"],
            "help_reply": STATE["help_reply"],
            "help_payload": STATE["help_payload"],
            "logs": list(STATE["logs"]),
        }


INDEX_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>导盲杖本地服务端</title>
  <style>
    :root {
      --bg: #eef2f7;
      --card: #ffffff;
      --ink: #102033;
      --muted: #5b6b7a;
      --line: #d7dee7;
      --blue: #1d4ed8;
      --red: #dc2626;
      --green: #15803d;
      --amber: #d97706;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      padding: 24px;
      background: linear-gradient(180deg, #f8fafc 0%, var(--bg) 100%);
      color: var(--ink);
      font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
    }
    .wrap {
      max-width: 1100px;
      margin: 0 auto;
    }
    h1 {
      margin: 0 0 10px;
      font-size: 28px;
    }
    .hint {
      margin-bottom: 18px;
      color: var(--muted);
    }
    .grid {
      display: grid;
      gap: 16px;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    }
    .card {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 16px 40px rgba(16, 32, 51, 0.08);
    }
    h2 {
      margin: 0 0 12px;
      font-size: 20px;
    }
    .metric {
      margin: 8px 0;
      color: var(--muted);
    }
    .value {
      margin-top: 8px;
      font-size: 24px;
      font-weight: 700;
      color: var(--ink);
    }
    .buttons {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-top: 14px;
    }
    button {
      border: 0;
      border-radius: 12px;
      padding: 12px 16px;
      color: #fff;
      font-size: 15px;
      cursor: pointer;
    }
    .ack { background: var(--green); }
    .reset { background: var(--red); }
    .refresh { background: var(--blue); }
    .pill {
      display: inline-block;
      padding: 4px 10px;
      border-radius: 999px;
      background: #e5eefc;
      color: #1e3a8a;
      font-size: 13px;
      margin-top: 6px;
    }
    pre {
      margin: 0;
      min-height: 340px;
      padding: 14px;
      border-radius: 14px;
      background: #09111f;
      color: #dce8ff;
      overflow: auto;
      white-space: pre-wrap;
      word-break: break-word;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>导盲杖本地服务端</h1>
    <div class="hint">热点建议：zr / zongrui2 | 本机端口：8766 | 收到求助后点击“发送 0 确认”</div>
    <div class="grid">
      <div class="card">
        <h2>最新障碍物</h2>
        <div class="metric">板端每次识别到障碍物后都会上传到这里</div>
        <div class="value" id="obstacleText">等待数据</div>
        <div class="metric" id="obstacleMeta">-</div>
        <div class="pill" id="obstacleTime">-</div>
      </div>
      <div class="card">
        <h2>求助状态</h2>
        <div class="value" id="helpState">未触发</div>
        <div class="metric" id="helpMeta">-</div>
        <div class="pill" id="helpReply">reply = ""</div>
        <div class="buttons">
          <button class="ack" onclick="ackHelp()">发送 0 确认</button>
          <button class="reset" onclick="resetHelp()">重置求助</button>
          <button class="refresh" onclick="refresh()">刷新</button>
        </div>
      </div>
      <div class="card" style="grid-column: 1 / -1;">
        <h2>事件日志</h2>
        <pre id="logs">waiting...</pre>
      </div>
    </div>
  </div>
  <script>
    async function callApi(path, body) {
      const res = await fetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body || {})
      });
      return await res.json();
    }

    async function ackHelp() {
      await callApi('/api/help/ack', { source: 'web' });
      await refresh();
    }

    async function resetHelp() {
      await callApi('/api/help/reset', { source: 'web' });
      await refresh();
    }

    async function refresh() {
      const res = await fetch('/api/state');
      const data = await res.json();

      const det = data.latest_detection || {};
      const help = data.help_payload || {};

      document.getElementById('obstacleText').textContent =
        det.message || det.label_cn || det.category || '等待数据';
      document.getElementById('obstacleMeta').textContent =
        '类别=' + (det.category || '-') + '  置信度=' + (det.score == null ? '-' : det.score);
      document.getElementById('obstacleTime').textContent =
        '上传时间：' + (det.server_time || '-');

      document.getElementById('helpState').textContent =
        data.help_reply === '0' ? '已确认到场' : (data.help_active ? '正在求助' : '未触发');
      document.getElementById('helpMeta').textContent =
        '队伍=' + (help.team_id || '-') + '  位置=' + (help.location || '-') +
        '  障碍物=' + (help.obstacle_label_cn || help.obstacle || '-');
      document.getElementById('helpReply').textContent =
        'reply = "' + (data.help_reply || '') + '"';
      document.getElementById('logs').textContent =
        JSON.stringify(data.logs, null, 2);
    }

    refresh();
    setInterval(refresh, 1000);
  </script>
</body>
</html>
"""


class BlindCaneHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send_html(INDEX_HTML)
            return
        if self.path == "/api/state":
            self._send_json(snapshot_state())
            return
        self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def do_POST(self):
        if self.path == "/api/recognition":
            payload = self._read_json()
            set_detection(payload)
            append_log("recognition", payload)
            self._send_json({"ok": True})
            return
        if self.path == "/api/help":
            payload = self._read_json()
            set_help(payload)
            append_log("help", payload)
            self._send_json({"ok": True, "reply": snapshot_state()["help_reply"]})
            return
        if self.path == "/api/help/ack":
            payload = self._read_json()
            ack_help()
            append_log("help_ack", payload)
            self._send_json({"ok": True, "reply": "0"})
            return
        if self.path == "/api/help/reset":
            payload = self._read_json()
            reset_help()
            append_log("help_reset", payload)
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
    print("Blind cane server starting on http://%s:%s" % (HOST, PORT))
    print("Hotspot suggestion: zr / zongrui2")
    server = ThreadingHTTPServer((HOST, PORT), BlindCaneHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
