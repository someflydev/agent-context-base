from __future__ import annotations

import json
import os
import time
from collections import Counter
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


HOST = "0.0.0.0"
PORT = 8765
JOBS_FILE = Path(os.environ.get("JOBS_FILE", "/fixtures/jobs-large.json"))
EVENTS_FILE = Path(os.environ.get("EVENTS_FILE", "/fixtures/events-large.json"))


def _load_json(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _load_jobs() -> list[dict]:
    return _load_json(JOBS_FILE)


def _load_events() -> list[dict]:
    events = _load_json(EVENTS_FILE)
    return sorted(events, key=lambda event: (event["timestamp"], event["event_id"]))


def _job_stats(jobs: list[dict]) -> dict[str, object]:
    counts = Counter(job["status"] for job in jobs)
    return {
        "total_jobs": len(jobs),
        "statuses": dict(counts),
    }


class JobAPIHandler(BaseHTTPRequestHandler):
    server_version = "TaskFlowFixtureAPI/0.1"

    def _send_json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_sse(self) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        for event in _load_events():
            payload = json.dumps(event, ensure_ascii=False)
            self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
            self.wfile.flush()
            time.sleep(0.05)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        parts = [part for part in parsed.path.split("/") if part]

        if parsed.path == "/jobs":
            self._send_json(_load_jobs())
            return
        if len(parts) == 2 and parts[0] == "jobs":
            job_id = parts[1]
            for job in _load_jobs():
                if job["id"] == job_id:
                    self._send_json(job)
                    return
            self._send_json({"error": f"unknown job {job_id}"}, status=HTTPStatus.NOT_FOUND)
            return
        if parsed.path == "/events":
            self._send_sse()
            return
        if parsed.path == "/stats":
            self._send_json(_job_stats(_load_jobs()))
            return

        self._send_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), JobAPIHandler)
    print(f"Serving fixture-backed job API on http://{HOST}:{PORT}")
    server.serve_forever()
