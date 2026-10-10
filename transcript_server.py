"""Local bridge so an n8n that cannot run Python itself (for example n8n in Docker)
can still use YoutubeTranscript.py.

Start it before running the workflow and leave the window open:

    python transcript_server.py

n8n then calls   http://host.docker.internal:8765/transcript?video_id=<id>
and gets back exactly what YoutubeTranscript.py prints: one line of JSON.
"""
import json
import re
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# 127.0.0.1 keeps the bridge private to this computer; Docker Desktop still reaches it
# through host.docker.internal. The Dockerfile passes 0.0.0.0 as the first argument.
HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = 8765
SCRIPT = Path(__file__).with_name("YoutubeTranscript.py")
VIDEO_ID = re.compile(r"[A-Za-z0-9_-]{5,20}")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/health":
            return self._send(200, json.dumps({"status": "ok"}))
        if url.path != "/transcript":
            return self._send(404, json.dumps({"status": "error", "message": "unknown path"}))

        video_id = parse_qs(url.query).get("video_id", [""])[0]
        if not VIDEO_ID.fullmatch(video_id):
            return self._send(200, json.dumps({"status": "error", "video_id": video_id, "message": "invalid video id"}))

        # Run the script the same way n8n's Execute Command node would. It always prints one
        # JSON line, also on failure, so answer 200 either way and let the workflow filter.
        result = subprocess.run(
            [sys.executable, str(SCRIPT), video_id],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        body = result.stdout.strip() or json.dumps(
            {
                "status": "error",
                "video_id": video_id,
                "message": result.stderr.strip()[-500:] or "no output from YoutubeTranscript.py",
            }
        )
        self._send(200, body)

    def _send(self, code, body):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    print(f"Transcript bridge listening on http://{HOST}:{PORT}  (Ctrl+C to stop)")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
