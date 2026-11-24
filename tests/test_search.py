"""Tests for grid, maps and search algorithms."""
import networkx as nx
import pytest

from algorithms.search import ALGORITHMS, astar, bfs, ucs
from game.grid import Grid, MUD, WALL
from game.maps import build_test_maps, make_unreachable_case, generate_map, pick_start_goal


def _valid_path(grid, path, start, goal):
    assert path[0] == start and path[-1] == goal
    for a, b in zip(path, path[1:]):
        assert abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1, "path jumps"
        assert grid.is_walkable(b), "path walks through a wall"


def test_open_grid_all_algorithms_find_path():
    g = Grid(5, 5)
    for name, algo in ALGORITHMS.items():
        r = algo(g, (0, 0), (4, 4))
        assert r.found, name
        _valid_path(g, r.path, (0, 0), (4, 4))


def test_start_equals_goal():
    g = Grid(3, 3)
    for name, algo in ALGORITHMS.items():
        r = algo(g, (1, 1), (1, 1))
        assert r.found and r.path == [(1, 1)] and r.cost == 0, name


def test_unreachable_goal_handled_by_all():
    g, s, t = make_unreachable_case()
    for name, algo in ALGORITHMS.items():
        r = algo(g, s, t)
        assert r.found is False and r.path == [] and r.cost is None, name


def test_blocked_goal_or_start_does_not_crash():
    g = Grid(4, 4)
    g.cells[3][3] = WALL
    for algo in ALGORITHMS.values():
        assert algo(g, (0, 0), (3, 3)).found is False
        assert algo(g, (3, 3), (0, 0)).found is False
        assert algo(g, (0, 0), (9, 9)).found is False   # out of bounds


def test_ucs_prefers_cheap_detour_over_mud():
    g = Grid(3, 3)
    for c in range(3):
        g.cells[1][c] = MUD            # the whole middle row is mud
    # Every route from top to bottom must cross mud; UCS cost must equal Dijkstra's.
    r = ucs(g, (0, 0), (2, 0))
    assert r.cost == 3 + 1
    gx = g.to_networkx()
    assert r.cost == nx.dijkstra_path_length(gx, (0, 0), (2, 0))


def test_bfs_fewest_steps_ucs_lowest_cost():
    # Straight route along the middle row is 4 steps but crosses 3 mud cells (cost 3+3+3+1=10).
    # Detour via the top row is 6 steps but costs only 6.
    g = Grid(3, 5)
    for c in (1, 2, 3):
        g.cells[1][c] = MUD
    r_bfs = bfs(g, (1, 0), (1, 4))
    r_ucs = ucs(g, (1, 0), (1, 4))
    assert r_bfs.steps <= r_ucs.steps          # BFS: fewest steps
    assert r_ucs.cost <= r_bfs.cost            # UCS: lowest cost
    assert r_ucs.cost < r_bfs.cost             # and here they really differ


@pytest.mark.parametrize("heur", ["manhattan", "euclidean"])
def test_astar_optimal_matches_dijkstra_on_random_maps(heur):
    for seed in range(25):
        g = generate_map(15, 15, 0.25, 0.15, seed=seed)
        s, t = pick_start_goal(g, seed)
        r = astar(g, s, t, heur)
        gx = g.to_networkx()
        if nx.has_path(gx, s, t):
            assert r.found
            assert r.cost == nx.dijkstra_path_length(gx, s, t), f"seed {seed}"
        else:
            assert not r.found


def test_ucs_optimal_matches_dijkstra_on_random_maps():
    for seed in range(25):
        g = generate_map(15, 15, 0.25, 0.15, seed=100 + seed)
        s, t = pick_start_goal(g, seed)
        r = ucs(g, s, t)
        gx = g.to_networkx()
        if nx.has_path(gx, s, t):
            assert r.cost == nx.dijkstra_path_length(gx, s, t)


def test_30_test_maps_every_reachable_goal_is_reached_by_every_algorithm():
    """Project target: NPC reaches reachable goals on 100% of 30 test maps."""
    cases = build_test_maps(30)
    assert len(cases) == 30
    for i, (g, s, t) in enumerate(cases):
        for name, algo in ALGORITHMS.items():
            r = algo(g, s, t)
            assert r.found, f"map {i} algorithm {name} failed"
            _valid_path(g, r.path, s, t)


def test_astar_expands_no_more_than_ucs():
    cases = build_test_maps(30)
    for g, s, t in cases:
        assert astar(g, s, t, "manhattan").nodes_expanded <= ucs(g, s, t).nodes_expanded + 1
