"""Procedural terrain: lakes, beaches, meadows, forests and rocks.

Pure Python, no dependencies. The map is a list of strings, one character per tile.
The same seed always produces the same map.
"""

from __future__ import annotations

import math
import random

DEEP = "~"    # deep water
WATER = "w"   # shallow water
SAND = "s"    # beach
GRASS = "g"   # meadow
FOREST = "f"  # trees (blocks movement)
ROCK = "r"    # boulders (blocks movement)

WALKABLE = frozenset({SAND, GRASS})

# Characters for the console view (agents are drawn on top as letters).
ASCII = {DEEP: "~", WATER: "-", SAND: ":", GRASS: ".", FOREST: "^", ROCK: "o"}


def _smooth(t: float) -> float:
    return t * t * (3 - 2 * t)


def _value_noise(grid: list[list[float]], x: float, y: float) -> float:
    x0, y0 = int(math.floor(x)), int(math.floor(y))
    fx, fy = _smooth(x - x0), _smooth(y - y0)
    a, b = grid[y0][x0], grid[y0][x0 + 1]
    c, d = grid[y0 + 1][x0], grid[y0 + 1][x0 + 1]
    top = a + (b - a) * fx
    bottom = c + (d - c) * fx
    return top + (bottom - top) * fy


def _fractal(width: int, height: int, rng: random.Random, scale: float, octaves: int = 4) -> list[list[float]]:
    layers = []
    for octave in range(octaves):
        size = scale / (2**octave)
        grid = [
            [rng.random() for _ in range(int(width / size) + 3)]
            for _ in range(int(height / size) + 3)
        ]
        layers.append((size, grid, 0.5**octave))
    total = sum(amp for _, _, amp in layers)
    return [
        [
            sum(amp * _value_noise(grid, x / size, y / size) for size, grid, amp in layers) / total
            for x in range(width)
        ]
        for y in range(height)
    ]


def _quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, max(0, int(q * len(ordered))))]


def generate(width: int, height: int, seed: int | None = None) -> list[str]:
    """Return `height` strings of `width` tile characters."""
    rng = random.Random(seed)
    elevation = _fractal(width, height, rng, scale=16)
    moisture = _fractal(width, height, rng, scale=7, octaves=3)
    warp = _fractal(width, height, rng, scale=11, octaves=3)
    lakes = _fractal(width, height, rng, scale=9, octaves=3)

    # Stretch to 0..1, then pull the edges down so the world is an island with a
    # wobbly coastline. The warp noise bends the distance so the shore is not an oval.
    low = min(min(row) for row in elevation)
    high = max(max(row) for row in elevation)
    distances = [[0.0] * width for _ in range(height)]
    for y in range(height):
        for x in range(width):
            nx = (x + 0.5) / width * 2 - 1
            ny = (y + 0.5) / height * 2 - 1
            distance = math.sqrt(nx * nx + ny * ny) + 0.6 * (warp[y][x] - 0.5)
            distances[y][x] = distance
            border = min(x, y, width - 1 - x, height - 1 - y)
            stretched = (elevation[y][x] - low) / (high - low)
            elevation[y][x] = (
                stretched
                - 2.2 * max(0.0, distance - 0.4) ** 1.2
                - 0.8 * max(0, 3 - border)  # always sea at the very edge
            )

    flat = [v for row in elevation for v in row]
    deep_limit = _quantile(flat, 0.32)
    water_limit = _quantile(flat, 0.43)
    sand_limit = _quantile(flat, 0.47)
    rock_limit = _quantile(flat, 0.975)

    land_moisture = [
        moisture[y][x]
        for y in range(height)
        for x in range(width)
        if elevation[y][x] > sand_limit
    ]
    forest_limit = _quantile(land_moisture, 0.70) if land_moisture else 1.0

    grid = []
    for y in range(height):
        row = []
        for x in range(width):
            e = elevation[y][x]
            if e < deep_limit:
                row.append(DEEP)
            elif e < water_limit:
                row.append(WATER)
            elif e < sand_limit:
                row.append(SAND)
            elif e > rock_limit:
                row.append(ROCK)
            elif moisture[y][x] > forest_limit:
                row.append(FOREST)
            else:
                row.append(GRASS)
        grid.append(row)

    # Inland lakes: low spots in a separate noise field, but only well inside the island.
    inland = [
        lakes[y][x]
        for y in range(height)
        for x in range(width)
        if grid[y][x] in (GRASS, FOREST) and elevation[y][x] > sand_limit + 0.08
    ]
    if inland:
        lake_limit = _quantile(inland, 0.13)
        lake_deep = _quantile(inland, 0.05)
        for y in range(height):
            for x in range(width):
                if grid[y][x] in (GRASS, FOREST) and elevation[y][x] > sand_limit + 0.08:
                    if lakes[y][x] < lake_deep:
                        grid[y][x] = DEEP
                    elif lakes[y][x] < lake_limit:
                        grid[y][x] = WATER

    water = (DEEP, WATER)

    # Round off the blocky shapes: a tile follows the majority of its 8 neighbours.
    for _ in range(2):
        changes = []
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                wet = sum(
                    grid[y + dy][x + dx] in water
                    for dy in (-1, 0, 1)
                    for dx in (-1, 0, 1)
                    if dx or dy
                )
                here = grid[y][x]
                if here in water and wet <= 2:
                    changes.append((x, y, GRASS))
                elif here in (GRASS, FOREST, SAND) and wet >= 5:
                    changes.append((x, y, WATER))
        for x, y, tile in changes:
            grid[y][x] = tile

    # Beaches around every body of water, and no forest right on the shore.
    for y in range(height):
        for x in range(width):
            if grid[y][x] in (GRASS, FOREST):
                near = [
                    grid[ny][nx]
                    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
                    if 0 <= nx < width and 0 <= ny < height
                ]
                if any(t in water for t in near):
                    grid[y][x] = SAND

    return ["".join(row) for row in grid]


def largest_walkable_area(tiles: list[str]) -> set[tuple[int, int]]:
    """The biggest connected region agents can walk on (4-neighbour connectivity)."""
    height = len(tiles)
    width = len(tiles[0]) if height else 0
    seen: set[tuple[int, int]] = set()
    best: set[tuple[int, int]] = set()
    for sy in range(height):
        for sx in range(width):
            if (sx, sy) in seen or tiles[sy][sx] not in WALKABLE:
                continue
            region = {(sx, sy)}
            stack = [(sx, sy)]
            seen.add((sx, sy))
            while stack:
                x, y = stack.pop()
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if (
                        0 <= nx < width
                        and 0 <= ny < height
                        and (nx, ny) not in seen
                        and tiles[ny][nx] in WALKABLE
                    ):
                        seen.add((nx, ny))
                        region.add((nx, ny))
                        stack.append((nx, ny))
            if len(region) > len(best):
                best = region
    return best
