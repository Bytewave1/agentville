from agentville.world import World


def test_spawn_places_agents_on_distinct_free_tiles():
    world = World.with_dummies(count=5, seed=1)
    positions = {(a.x, a.y) for a in world.agents}
    assert len(world.agents) == 5
    assert len(positions) == 5


def test_agents_stay_inside_the_world_and_never_overlap():
    world = World.with_dummies(count=5, seed=7, width=6, height=6)
    for _ in range(200):
        world.step()
        positions = [(a.x, a.y) for a in world.agents]
        assert len(set(positions)) == len(positions)
        assert all(world.in_bounds(x, y) for x, y in positions)


def test_same_seed_gives_same_world():
    a = World.with_dummies(count=5, seed=42)
    b = World.with_dummies(count=5, seed=42)
    a.run(50)
    b.run(50)
    assert [(x.x, x.y) for x in a.agents] == [(x.x, x.y) for x in b.agents]


def test_tick_counter_advances():
    world = World.with_dummies(count=2, seed=3)
    world.run(4)
    assert world.tick == 4


def test_blocked_move_is_refused():
    world = World(width=2, height=1, seed=0)
    first = world.spawn("A")
    second = world.spawn("B")
    # Two agents on a 2x1 strip: whoever tries to walk into the other is blocked.
    target = "east" if first.x < second.x else "west"
    world.apply(first, target)
    assert (first.x, first.y) != (second.x, second.y)
    assert "blocked" in world.events[-1].text


def test_observation_lists_nearby_agents():
    world = World(width=10, height=10, seed=0)
    a = world.spawn("A")
    b = world.spawn("B")
    a.x, a.y, b.x, b.y = 2, 2, 3, 3
    assert world.observe(a).nearby == ["B"]
    b.x, b.y = 9, 9
    assert world.observe(a).nearby == []
