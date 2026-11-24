"""Map generation. All maps are reproducible from a seed."""
import random
from typing import List, Optional, Tuple

from game.grid import Grid, FLOOR, MUD, WALL, Pos


def generate_map(rows: int = 20, cols: int = 20, wall_density: float = 0.22,
                 mud_density: float = 0.10, seed: int = 0) -> Grid:
    """Random map. The same seed always gives the same map."""
    rng = random.Random(seed)
    grid = Grid(rows, cols)
    for r in range(rows):
        for c in range(cols):
            x = rng.random()
            if x < wall_density:
                grid.cells[r][c] = WALL
            elif x < wall_density + mud_density:
                grid.cells[r][c] = MUD
    return grid


def pick_start_goal(grid: Grid, seed: int = 0) -> Tuple[Pos, Pos]:
    """Pick two different walkable cells (they may or may not be connected)."""
    rng = random.Random(seed)
    cells = grid.walkable_cells()
    start, goal = rng.sample(cells, 2)
    return start, goal


def reachable_cells(grid: Grid, start: Pos) -> set:
    """All cells reachable from start (plain flood fill, used to build/validate test maps)."""
    seen = {start}
    stack = [start]
    while stack:
        cur = stack.pop()
        for nb in grid.neighbors(cur):
            if nb not in seen:
                seen.add(nb)
                stack.append(nb)
    return seen


def build_test_maps(count: int = 30, rows: int = 20, cols: int = 20
                    ) -> List[Tuple[Grid, Pos, Pos]]:
    """Build `count` test cases (grid, start, goal) where the goal IS reachable.

    Used for the 'NPC reaches reachable goals on 30 test maps' target.
    Wall density grows with the map number so the set mixes easy and hard maps.
    """
    cases = []
    seed = 1000
    while len(cases) < count:
        density = 0.10 + 0.20 * (len(cases) / max(1, count - 1))  # 0.10 .. 0.30
        grid = generate_map(rows, cols, wall_density=density, seed=seed)
        seed += 1
        cells = grid.walkable_cells()
        if len(cells) < 2:
            continue
        rng = random.Random(seed)
        start = rng.choice(cells)
        region = sorted(reachable_cells(grid, start) - {start})
        if len(region) < 10:   # too cramped to be an interesting test
            continue
        goal = rng.choice(region)
        cases.append((grid, start, goal))
    return cases


def make_unreachable_case(rows: int = 12, cols: int = 12) -> Tuple[Grid, Pos, Pos]:
    """A hand-built map where the goal is sealed inside walls."""
    grid = Grid(rows, cols)
    goal = (rows // 2, cols // 2)
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        grid.cells[goal[0] + dr][goal[1] + dc] = WALL
    return grid, (0, 0), goal


def default_demo_map() -> Grid:
    """The map the game starts with: fixed, so every demo looks the same."""
    grid = generate_map(20, 20, wall_density=0.20, mud_density=0.10, seed=7)
    for pos in ((1, 1), (18, 18), (1, 18), (18, 1), (10, 10)):
        grid.cells[pos[0]][pos[1]] = FLOOR   # keep key spots walkable
    return grid
