"""A tiny local web server so you can use the agent from a browser.

Run:   .\\.venv\\Scripts\\python.exe server.py
Open:  http://127.0.0.1:8000

It uses only Python's built-in http.server and listens on 127.0.0.1, so it is
reachable from THIS computer only. Your API key stays on the server side and is
never sent to the browser.
"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import markdown

from agent import run_agent
from prompts import build_report_prompt
from report import generate_report

HOST, PORT = "127.0.0.1", 8000
PAGE = (Path(__file__).parent / "web" / "index.html").read_bytes()


def to_html(text):
    return markdown.markdown(text, extensions=["tables"])


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body, content_type="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self._send(200, PAGE, "text/html")
        else:
            self._send(404, {"error": "Not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
            calls = []

            if self.path == "/api/ask":
                question = (data.get("question") or "").strip()
                if not question:
                    return self._send(400, {"error": "Please type a question."})
                answer = run_agent(question, on_tool_call=lambda s, n, i: calls.append(f"step {s}: {n}"))
                return self._send(200, {"html": to_html(answer), "calls": calls})

            if self.path == "/api/report":
                md_path, html_path = generate_report()
                text = md_path.read_text(encoding="utf-8")
                return self._send(200, {"html": to_html(text), "saved": str(html_path), "calls": []})

            self._send(404, {"error": "Not found"})
        except Exception as error:  # show problems (e.g. expired key) in the page
            self._send(500, {"error": f"{type(error).__name__}: {error}"})


if __name__ == "__main__":
    print(f"Agent running at http://{HOST}:{PORT}  (press Ctrl+C to stop)")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
