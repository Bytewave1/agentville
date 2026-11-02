import json
import threading
import urllib.request

from agentville.server import make_server
from agentville.world import World


def _start(tick_seconds=3600.0):
    world = World.with_dummies(count=3, seed=5)
    httpd, sim = make_server(world, port=0, tick_seconds=tick_seconds)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{httpd.server_address[1]}"
    return httpd, sim, base


def test_snapshot_contains_world_data():
    world = World.with_dummies(count=3, seed=5)
    world.run(2)
    snap = world.snapshot()
    assert snap["tick"] == 2
    assert len(snap["agents"]) == 3
    assert {"name", "x", "y"} <= snap["agents"][0].keys()
    assert snap["events"]


def test_server_serves_page_and_state():
    httpd, sim, base = _start()
    try:
        page = urllib.request.urlopen(base + "/").read().decode()
        assert "Agentville" in page
        state = json.loads(urllib.request.urlopen(base + "/api/state").read())
        assert len(state["agents"]) == 3
        assert state["paused"] is False
    finally:
        sim.stop()
        httpd.shutdown()
        httpd.server_close()


def test_pause_toggles():
    httpd, sim, base = _start()
    try:
        req = urllib.request.Request(base + "/api/pause", method="POST")
        assert json.loads(urllib.request.urlopen(req).read())["paused"] is True
        state = json.loads(urllib.request.urlopen(base + "/api/state").read())
        assert state["paused"] is True
    finally:
        sim.stop()
        httpd.shutdown()
        httpd.server_close()


def test_unknown_path_is_404():
    httpd, sim, base = _start()
    try:
        try:
            urllib.request.urlopen(base + "/nope")
            raise AssertionError("expected 404")
        except urllib.error.HTTPError as err:
            assert err.code == 404
    finally:
        sim.stop()
        httpd.shutdown()
        httpd.server_close()
