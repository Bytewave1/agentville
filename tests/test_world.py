from agentville.world import World


def test_spawn_places_agents_on_distinct_free_tiles():
    world = World.with_dummies(count=5, seed=1)
    positions = {(a.x, a.y) for a in world.agents}
    assert len(world.agents) == 5
    assert len(positions) == 5


def test_agents_stay_inside_the_world_and_never_overlap():
    world = World.with_dummies(count=5, seed=7, width=6, height=6, generate_terrain=False)
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


def test_agents_only_walk_on_walkable_tiles():
    from agentville import terrain

    world = World.with_dummies(count=12, seed=3)
    for _ in range(150):
        world.step()
        for agent in world.agents:
            assert world.tile_at(agent.x, agent.y) in terrain.WALKABLE


def test_water_and_trees_block_movement():
    from agentville import terrain

    world = World(width=3, height=1, seed=0, tiles=[terrain.GRASS + terrain.WATER + terrain.FOREST])
    agent = world.spawn("A")
    assert (agent.x, agent.y) == (0, 0)
    assert world.observe(agent).open == ()
    world.apply(agent, "east")
    assert (agent.x, agent.y) == (0, 0)
    assert "blocked" in world.events[-1].text


def test_observation_open_directions_skip_blocked_tiles():
    from agentville import terrain

    tiles = [terrain.GRASS * 3, terrain.GRASS + terrain.GRASS + terrain.WATER, terrain.GRASS * 3]
    world = World(width=3, height=3, seed=0, tiles=tiles)
    agent = world.spawn("A")
    agent.x, agent.y = 1, 1
    assert set(world.observe(agent).open) == {"north", "south", "west"}
