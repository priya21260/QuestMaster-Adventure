"""Hill Climbing and Simulated Annealing for QUEST SCHEDULING.

Problem: an NPC must visit several quest locations. In which ORDER should it
visit them so the total walking cost is smallest? (A small travelling-salesman
problem.) Walking cost between two locations comes from A* on the real map,
so walls and mud are respected.

A "state" is an ordering of quest locations. A "neighbour" swaps two of them.
  - Hill Climbing: keep swapping while it improves; stops at a local optimum.
  - Simulated Annealing: sometimes accepts a WORSE order (less often as the
    "temperature" cools), which lets it escape local optima.
"""
import math
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from algorithms.search import astar_manhattan
from game.grid import Grid, Pos

UNREACHABLE_PENALTY = 10_000


@dataclass
class ScheduleResult:
    algorithm: str
    order: List[Pos]
    cost: float
    iterations: int
    history: List[float]          # best cost over time (for charts)


def build_cost_table(grid: Grid, points: List[Pos]) -> Dict[Tuple[Pos, Pos], float]:
    """Walking cost between every pair of points (A*). Unreachable pairs get a big penalty."""
    table: Dict[Tuple[Pos, Pos], float] = {}
    for i, a in enumerate(points):
        for b in points[i + 1:]:
            res = astar_manhattan(grid, a, b)
            c = res.cost if res.found else UNREACHABLE_PENALTY
            table[(a, b)] = c
            table[(b, a)] = c
    return table


def tour_cost(start: Pos, order: List[Pos], table) -> float:
    total, cur = 0.0, start
    for p in order:
        total += table[(cur, p)]
        cur = p
    return total


def _prepare(grid: Grid, start: Pos, quests: List[Pos]):
    points = [start] + [q for q in quests if q != start]
    return points[1:], build_cost_table(grid, points)


def hill_climbing(grid: Grid, start: Pos, quests: List[Pos], seed: int = 0,
                  restarts: int = 5) -> ScheduleResult:
    """Steepest-ascent hill climbing (swap neighbourhood) with random restarts."""
    rng = random.Random(seed)
    items, table = _prepare(grid, start, quests)
    if len(items) < 2:
        return ScheduleResult("Hill Climbing", items, tour_cost(start, items, table), 0, [])
    best_order, best_cost, iterations, history = None, math.inf, 0, []
    for _ in range(restarts):
        order = items[:]
        rng.shuffle(order)
        cost = tour_cost(start, order, table)
        improved = True
        while improved:
            improved = False
            best_move, best_move_cost = None, cost
            for i in range(len(order)):
                for j in range(i + 1, len(order)):
                    cand = order[:]
                    cand[i], cand[j] = cand[j], cand[i]
                    c = tour_cost(start, cand, table)
                    iterations += 1
                    if c < best_move_cost:
                        best_move, best_move_cost = cand, c
            if best_move is not None:
                order, cost, improved = best_move, best_move_cost, True
        if cost < best_cost:
            best_order, best_cost = order, cost
        history.append(best_cost)
    return ScheduleResult("Hill Climbing", best_order, best_cost, iterations, history)


def simulated_annealing(grid: Grid, start: Pos, quests: List[Pos], seed: int = 0,
                        initial_temp: float = 50.0, cooling: float = 0.995,
                        min_temp: float = 0.01, max_iters: int = 20_000) -> ScheduleResult:
    """Simulated annealing with swap moves and geometric cooling."""
    rng = random.Random(seed)
    items, table = _prepare(grid, start, quests)
    if len(items) < 2:
        return ScheduleResult("Simulated Annealing", items, tour_cost(start, items, table), 0, [])
    order = items[:]
    rng.shuffle(order)
    cost = tour_cost(start, order, table)
    best_order, best_cost = order[:], cost
    temp, iterations, history = initial_temp, 0, []
    while temp > min_temp and iterations < max_iters:
        i, j = rng.sample(range(len(order)), 2)
        cand = order[:]
        cand[i], cand[j] = cand[j], cand[i]
        c = tour_cost(start, cand, table)
        delta = c - cost
        if delta < 0 or rng.random() < math.exp(-delta / temp):
            order, cost = cand, c
            if cost < best_cost:
                best_order, best_cost = order[:], cost
        temp *= cooling
        iterations += 1
        if iterations % 50 == 0:
            history.append(best_cost)
    return ScheduleResult("Simulated Annealing", best_order, best_cost, iterations, history)


def brute_force_optimum(grid: Grid, start: Pos, quests: List[Pos]) -> float:
    """Exact best cost by trying every order (only for small quest counts; used in tests)."""
    from itertools import permutations
    items, table = _prepare(grid, start, quests)
    return min(tour_cost(start, list(p), table) for p in permutations(items))
