"""HTTP server for /metrics and Kubernetes probes.

Liveness (/healthz): main loop touched the heartbeat recently.
Readiness (/ready): last successful metrics scrape was recent.
"""

from __future__ import annotations

import os
import socket
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import structlog
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, generate_latest

DEFAULT_MAX_AGE = 300
logger = structlog.get_logger(__name__)


class HealthState:
    """Tracks main-loop heartbeat and last successful scrape."""

    def __init__(self, max_age: float = DEFAULT_MAX_AGE) -> None:
        self.max_age = max_age
        self._heartbeat = 0.0
        self._last_success = 0.0

    def touch(self) -> None:
        """Record that the main loop is still running."""
        self._heartbeat = time.monotonic()

    def mark_success(self) -> None:
        """Record a successful metrics scrape."""
        now = time.monotonic()
        self._heartbeat = now
        self._last_success = now

    def is_alive(self) -> bool:
        return (
            self._heartbeat > 0 and (time.monotonic() - self._heartbeat) < self.max_age
        )

    def is_ready(self) -> bool:
        return (
            self._last_success > 0
            and (time.monotonic() - self._last_success) < self.max_age
        )


class _Handler(BaseHTTPRequestHandler):
    health: HealthState

    def log_message(self, format: str, *args: object) -> None:
        logger.debug(format % args, client=self.address_string())

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        if path == "/healthz":
            if type(self).health.is_alive():
                self._respond(200, b"ok\n")
            else:
                self._respond(503, b"heartbeat stale\n")
        elif path == "/ready":
            if type(self).health.is_ready():
                self._respond(200, b"ok\n")
            else:
                self._respond(503, b"not ready\n")
        elif path == "/metrics":
            self.send_response(200)
            self.send_header("Content-Type", CONTENT_TYPE_LATEST)
            self.end_headers()
            self.wfile.write(generate_latest(REGISTRY))
        else:
            self.send_error(404)

    def _respond(self, code: int, body: bytes) -> None:
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)


class _Server(ThreadingHTTPServer):
    """Serve on IPv6 as well as IPv4 wherever the kernel has IPv6.

    ThreadingHTTPServer inherits address_family = AF_INET, so ("", port) binds
    0.0.0.0 only. On an IPv6-only cluster that leaves the pod unreachable at its
    own address and the httpGet probes are refused forever; on a dual-stack one
    the IPv6 half is dark. With AF_INET6 and the Linux default
    net.ipv6.bindv6only=0 the same socket serves both families.
    /proc/net/if_inet6 is absent exactly when IPv6 is compiled out or disabled at
    boot, where an AF_INET6 socket cannot be created at all.
    """

    address_family = (
        socket.AF_INET6 if os.path.exists("/proc/net/if_inet6") else socket.AF_INET
    )


def start_server(port: int, max_age: float = DEFAULT_MAX_AGE) -> HealthState:
    health = HealthState(max_age=max_age)
    _Handler.health = health
    server = _Server(("", port), _Handler)
    Thread(target=server.serve_forever, daemon=True).start()
    return health
