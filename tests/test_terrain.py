from agentville import terrain


def test_same_seed_same_map():
    assert terrain.generate(40, 30, 5) == terrain.generate(40, 30, 5)


def test_different_seed_different_map():
    assert terrain.generate(40, 30, 5) != terrain.generate(40, 30, 6)


def test_map_has_requested_size_and_known_tiles():
    tiles = terrain.generate(50, 30, 1)
    assert len(tiles) == 30
    assert all(len(row) == 50 for row in tiles)
    assert set("".join(tiles)) <= set(terrain.ASCII)


def test_map_has_water_beach_meadow_and_forest():
    text = "".join(terrain.generate(64, 40, 42))
    for kind in (terrain.DEEP, terrain.WATER, terrain.SAND, terrain.GRASS, terrain.FOREST):
        assert kind in text


def test_edges_are_sea():
    tiles = terrain.generate(64, 40, 42)
    edge = set(tiles[0]) | set(tiles[-1]) | {row[0] for row in tiles} | {row[-1] for row in tiles}
    assert edge == {terrain.DEEP}


def test_there_is_a_big_walkable_landmass():
    tiles = terrain.generate(64, 40, 42)
    assert len(terrain.largest_walkable_area(tiles)) > 400
