"""A tiny web server: keeps the world ticking and serves the browser viewer.

Only the standard library is used, so there is nothing extra to install.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import resources

from .world import World


class Simulation:
    """Runs the world in a background thread, one tick every `tick_seconds`."""

    def __init__(self, world: World, tick_seconds: float = 1.0) -> None:
        self.world = world
        self.tick_seconds = tick_seconds
        self.paused = False
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _loop(self) -> None:
        while not self._stop.wait(self.tick_seconds):
            if not self.paused:
                with self._lock:
                    self.world.step()

    def snapshot(self) -> dict:
        with self._lock:
            data = self.world.snapshot()
        data["paused"] = self.paused
        data["tick_seconds"] = self.tick_seconds
        return data


def _index_html() -> bytes:
    return resources.files("agentville").joinpath("web", "index.html").read_bytes()


def make_server(
    world: World, host: str = "127.0.0.1", port: int = 8000, tick_seconds: float = 1.0
) -> tuple[ThreadingHTTPServer, Simulation]:
    sim = Simulation(world, tick_seconds)

    class Handler(BaseHTTPRequestHandler):
        def _send(self, status: int, body: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802 (stdlib naming)
            path = self.path.split("?", 1)[0]
            if path in ("/", "/index.html"):
                self._send(200, _index_html(), "text/html; charset=utf-8")
            elif path == "/api/map":
                self._send(200, json.dumps(world.map_data()).encode(), "application/json")
            elif path == "/api/state":
                body = json.dumps(sim.snapshot()).encode()
                self._send(200, body, "application/json")
            else:
                self._send(404, b"not found", "text/plain; charset=utf-8")

        def do_POST(self) -> None:  # noqa: N802
            if self.path == "/api/pause":
                sim.paused = not sim.paused
                self._send(200, json.dumps({"paused": sim.paused}).encode(), "application/json")
            else:
                self._send(404, b"not found", "text/plain; charset=utf-8")

        def log_message(self, format: str, *args) -> None:  # keep the console quiet
            pass

    httpd = ThreadingHTTPServer((host, port), Handler)
    return httpd, sim


def serve(world: World, host: str = "127.0.0.1", port: int = 8000, tick_seconds: float = 1.0) -> None:
    httpd, sim = make_server(world, host, port, tick_seconds)
    sim.start()
    print(f"Agentville läuft auf http://{host}:{httpd.server_address[1]}  (Strg+C zum Beenden)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        sim.stop()
        httpd.server_close()
