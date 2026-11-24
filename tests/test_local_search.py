"""Tests for Hill Climbing and Simulated Annealing quest scheduling."""
import random

from algorithms.local_search import (brute_force_optimum, hill_climbing,
                                     simulated_annealing, build_cost_table, tour_cost)
from game.maps import generate_map


def _setup(seed=3, n=6):
    g = generate_map(15, 15, 0.15, 0.05, seed=seed)
    cells = g.walkable_cells()
    rng = random.Random(seed)
    pts = rng.sample(cells, n + 1)
    return g, pts[0], pts[1:]


def test_results_are_valid_permutations():
    g, start, quests = _setup()
    for fn in (hill_climbing, simulated_annealing):
        r = fn(g, start, quests, seed=1)
        assert sorted(r.order) == sorted(quests)


def test_reported_cost_matches_recomputed_cost():
    g, start, quests = _setup()
    table = build_cost_table(g, [start] + quests)
    for fn in (hill_climbing, simulated_annealing):
        r = fn(g, start, quests, seed=1)
        assert r.cost == tour_cost(start, r.order, table)


def test_close_to_optimal_on_small_problems():
    for seed in range(5):
        g, start, quests = _setup(seed=seed, n=6)
        best = brute_force_optimum(g, start, quests)
        hc = hill_climbing(g, start, quests, seed=1, restarts=10)
        sa = simulated_annealing(g, start, quests, seed=1)
        assert hc.cost <= best * 1.25 + 1, f"HC seed {seed}"
        assert sa.cost <= best * 1.25 + 1, f"SA seed {seed}"


def test_reproducible_with_same_seed():
    g, start, quests = _setup()
    a = simulated_annealing(g, start, quests, seed=5)
    b = simulated_annealing(g, start, quests, seed=5)
    assert a.order == b.order and a.cost == b.cost


def test_single_and_empty_quest_lists():
    g, start, quests = _setup()
    assert hill_climbing(g, start, quests[:1]).order == quests[:1]
    assert simulated_annealing(g, start, []).order == []
