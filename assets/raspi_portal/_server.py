"""Minimal HTTP captive-portal server (stdlib only)."""

import http.server
import queue
import threading
import urllib.parse

# ---------------------------------------------------------------------------
# HTML pages
# ---------------------------------------------------------------------------

_PORTAL_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PiKaraoke WiFi Setup</title>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:sans-serif;background:#111;color:#eee;
          display:flex;align-items:center;justify-content:center;
          min-height:100vh;padding:20px}}
    .card{{background:#222;border-radius:12px;padding:32px;
           width:100%;max-width:420px}}
    h1{{color:#e91e63;margin-bottom:8px;font-size:1.6rem}}
    p{{color:#aaa;margin-bottom:20px;line-height:1.5}}
    label{{display:block;margin-bottom:4px;font-size:.9rem;color:#ccc}}
    input{{width:100%;padding:10px 12px;font-size:1rem;
           border:1px solid #444;border-radius:6px;
           background:#333;color:#eee;margin-bottom:16px}}
    button{{width:100%;padding:13px;background:#e91e63;color:#fff;
            border:none;font-size:1rem;border-radius:6px;
            cursor:pointer;font-weight:bold}}
    button:active{{background:#c2185b}}
    .err{{color:#ff5252;margin-bottom:12px;font-size:.9rem}}
  </style>
</head>
<body>
  <div class="card">
    <h1>&#127908; PiKaraoke Setup</h1>
    <p>Enter your home WiFi credentials so this Pi can connect to your network.</p>
    {error_block}
    <form method="POST" action="/connect">
      <label for="ssid">WiFi Name (SSID)</label>
      <input id="ssid" type="text" name="ssid"
             autocomplete="off" autocorrect="off"
             autocapitalize="none" spellcheck="false" required>
      <label for="pw">Password</label>
      <input id="pw" type="password" name="password"
             autocomplete="current-password">
      <button type="submit">Connect &amp; Reboot</button>
    </form>
  </div>
</body>
</html>"""

_CONFIRM_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Connecting…</title>
  <style>
    body{{font-family:sans-serif;background:#111;color:#eee;
          display:flex;align-items:center;justify-content:center;
          min-height:100vh;text-align:center;padding:20px}}
    h1{{color:#4caf50;margin-bottom:16px}}
    p{{color:#aaa;line-height:1.6}}
    strong{{color:#eee}}
  </style>
</head>
<body>
  <div>
    <h1>&#10003; Done!</h1>
    <p>Connecting to <strong>{ssid}</strong>&hellip;</p>
    <p>The Pi will reboot in <strong>10 seconds</strong>.</p>
    <p style="margin-top:16px"><em>You can close this page.<br>
    PiKaraoke will start automatically once it is back online.</em></p>
  </div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------

class _PortalHandler(http.server.BaseHTTPRequestHandler):
    # Injected before the server thread starts; shared across all requests.
    _result_queue: "queue.Queue[tuple[str, str]]" = None  # type: ignore[assignment]

    # ------------------------------------------------------------------ GET
    def do_GET(self):
        # Redirect everything that isn't "/" so Android/iOS captive-portal
        # probes land on the form page instead of returning a 404.
        if self.path not in ("/", "/index.html"):
            self._redirect("/")
            return
        self._send_html(200, self._portal_page())

    # ----------------------------------------------------------------- POST
    def do_POST(self):
        if self.path != "/connect":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        params = urllib.parse.parse_qs(raw, keep_blank_values=True)

        ssid = params.get("ssid", [""])[0].strip()
        password = params.get("password", [""])[0]  # keep spaces; allow blank

        if not ssid:
            self._send_html(200, self._portal_page(error="WiFi name cannot be empty."))
            return

        # Send confirmation page *before* putting to queue so the response
        # is fully written before the main thread tears down the hotspot.
        self._send_html(200, _CONFIRM_HTML.format(ssid=ssid))
        self.wfile.flush()

        self._result_queue.put((ssid, password))

    # ---------------------------------------------------------------- utils
    def _portal_page(self, error: str = "") -> str:
        block = f'<p class="err">{error}</p>' if error else ""
        return _PORTAL_HTML.format(error_block=block)

    def _send_html(self, code: int, body: str):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _redirect(self, location: str):
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    def log_message(self, fmt, *args):  # suppress default stderr noise
        print(f"[PORTAL] {fmt % args}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_server(
    host: str, port: int
) -> "tuple[http.server.HTTPServer, queue.Queue[tuple[str, str]]]":
    """Start the portal HTTP server in a daemon thread.

    Returns (server, result_queue).  The caller blocks on result_queue.get()
    until the user submits the WiFi form.
    """
    result_queue: "queue.Queue[tuple[str, str]]" = queue.Queue()
    _PortalHandler._result_queue = result_queue

    server = http.server.HTTPServer((host, port), _PortalHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server, result_queue


def stop_server(server: http.server.HTTPServer):
    server.shutdown()
