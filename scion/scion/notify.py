"""Webhook notifications (FR-RV-10, FR-OP-05; ADR-18).

Events are posted as JSON to every configured URL from a background thread, with a few retries.
Delivery is best effort: a slow or failing webhook never blocks the request that caused the event.
The payload carries a ``text`` field, so chat systems that accept Slack-style webhooks can show it.
"""
from __future__ import annotations

import json
import queue
import threading
import time
import urllib.request
from collections import Counter


class Notifier:
    def __init__(self, urls_for, attempts: int = 3, timeout: float = 5.0):
        """``urls_for(repo)`` returns the webhook URLs for a repository's events."""
        self.urls_for, self.attempts, self.timeout = urls_for, attempts, timeout
        self.counters: Counter = Counter()
        self._q: queue.Queue = queue.Queue(maxsize=10_000)
        self._thread = threading.Thread(target=self._run, daemon=True, name="notify")
        self._thread.start()

    def __call__(self, event: str, repo: str, payload: dict) -> None:
        urls = self.urls_for(repo)
        if not urls:
            return
        cr = payload.get("cr", {})
        text = f"[{repo}] {event}: CR {cr.get('id')} \"{cr.get('title', '')}\" by {cr.get('author')} ({cr.get('state')})" \
            if cr else f"[{repo}] {event}"
        body = json.dumps({"event": event, "repo": repo, "text": text, **payload}).encode()
        for url in urls:
            try:
                self._q.put_nowait((url, body))
            except queue.Full:
                self.counters["dropped"] += 1

    def _run(self) -> None:
        while True:
            url, body = self._q.get()
            for attempt in range(self.attempts):
                try:
                    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
                    with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                        resp.read()
                    self.counters["delivered"] += 1
                    break
                except (OSError, ValueError):
                    time.sleep(0.2 * 2 ** attempt)
            else:
                self.counters["failed"] += 1
            self._q.task_done()

    def flush(self, timeout: float = 10.0) -> bool:
        """Wait until every queued event has been tried (for tests and shutdown)."""
        deadline = time.time() + timeout
        while self._q.unfinished_tasks and time.time() < deadline:
            time.sleep(0.01)
        return not self._q.unfinished_tasks
