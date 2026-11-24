"""Path-finding search algorithms.

Every algorithm has the same signature:  algo(grid, start, goal) -> SearchResult
so the UI and the benchmark can treat them all the same way.

  BFS     - explores level by level; fewest STEPS (ignores terrain cost)
  DFS     - dives deep first; finds *a* path, usually not a good one
  UCS     - always expands the cheapest-so-far node; optimal COST
  Greedy  - always expands the node that looks closest to the goal; fast, not optimal
  A*      - UCS + heuristic (cost so far + estimate to goal); optimal if heuristic is admissible
"""
import heapq
import time
from collections import deque
from dataclasses import dataclass, field
from itertools import count
from typing import Callable, Dict, List, Optional

from game.grid import Grid, Pos


@dataclass
class SearchResult:
    algorithm: str
    found: bool
    path: List[Pos] = field(default_factory=list)
    cost: Optional[int] = None        # total terrain cost of the path (None if not found)
    nodes_expanded: int = 0
    time_ms: float = 0.0
    explored: List[Pos] = field(default_factory=list)   # expansion order (for visualisation)

    @property
    def steps(self) -> int:
        return max(0, len(self.path) - 1)


# ---------------------------------------------------------------- heuristics
def manhattan(a: Pos, b: Pos) -> int:
    """|dr| + |dc|. Admissible: the cheapest cell costs 1, so real cost >= this."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def euclidean(a: Pos, b: Pos) -> float:
    """Straight-line distance. Admissible, but weaker (smaller) than Manhattan on a 4-direction grid."""
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


HEURISTICS: Dict[str, Callable[[Pos, Pos], float]] = {
    "manhattan": manhattan,
    "euclidean": euclidean,
}


# ---------------------------------------------------------------- helpers
def _rebuild(parents: Dict[Pos, Optional[Pos]], goal: Pos) -> List[Pos]:
    path = []
    cur: Optional[Pos] = goal
    while cur is not None:
        path.append(cur)
        cur = parents[cur]
    path.reverse()
    return path


def _finish(name: str, grid: Grid, parents, goal: Pos, found: bool,
            expanded: List[Pos], t0: float) -> SearchResult:
    elapsed = (time.perf_counter() - t0) * 1000
    if found:
        path = _rebuild(parents, goal)
        return SearchResult(name, True, path, grid.path_cost(path), len(expanded), elapsed, expanded)
    return SearchResult(name, False, [], None, len(expanded), elapsed, expanded)


def _invalid(name: str, grid: Grid, start: Pos, goal: Pos) -> Optional[SearchResult]:
    """Handle blocked/out-of-range start or goal without crashing."""
    if not grid.is_walkable(start) or not grid.is_walkable(goal):
        return SearchResult(name, False)
    return None


# ---------------------------------------------------------------- algorithms
def bfs(grid: Grid, start: Pos, goal: Pos) -> SearchResult:
    name = "BFS"
    bad = _invalid(name, grid, start, goal)
    if bad:
        return bad
    t0 = time.perf_counter()
    parents: Dict[Pos, Optional[Pos]] = {start: None}
    queue = deque([start])
    expanded: List[Pos] = []
    while queue:
        cur = queue.popleft()
        expanded.append(cur)
        if cur == goal:
            return _finish(name, grid, parents, goal, True, expanded, t0)
        for nb in grid.neighbors(cur):
            if nb not in parents:
                parents[nb] = cur
                queue.append(nb)
    return _finish(name, grid, parents, goal, False, expanded, t0)


def dfs(grid: Grid, start: Pos, goal: Pos) -> SearchResult:
    name = "DFS"
    bad = _invalid(name, grid, start, goal)
    if bad:
        return bad
    t0 = time.perf_counter()
    parents: Dict[Pos, Optional[Pos]] = {}
    stack = [(start, None)]
    expanded: List[Pos] = []
    while stack:
        cur, parent = stack.pop()
        if cur in parents:
            continue
        parents[cur] = parent
        expanded.append(cur)
        if cur == goal:
            return _finish(name, grid, parents, goal, True, expanded, t0)
        for nb in grid.neighbors(cur):
            if nb not in parents:
                stack.append((nb, cur))
    return _finish(name, grid, parents, goal, False, expanded, t0)


def ucs(grid: Grid, start: Pos, goal: Pos) -> SearchResult:
    name = "UCS"
    bad = _invalid(name, grid, start, goal)
    if bad:
        return bad
    t0 = time.perf_counter()
    tie = count()   # tie-breaker so the heap never compares positions
    best: Dict[Pos, int] = {start: 0}
    parents: Dict[Pos, Optional[Pos]] = {start: None}
    heap = [(0, next(tie), start)]
    closed = set()
    expanded: List[Pos] = []
    while heap:
        g, _, cur = heapq.heappop(heap)
        if cur in closed:
            continue
        closed.add(cur)
        expanded.append(cur)
        if cur == goal:
            return _finish(name, grid, parents, goal, True, expanded, t0)
        for nb in grid.neighbors(cur):
            ng = g + grid.cost(nb)
            if nb not in best or ng < best[nb]:
                best[nb] = ng
                parents[nb] = cur
                heapq.heappush(heap, (ng, next(tie), nb))
    return _finish(name, grid, parents, goal, False, expanded, t0)


def greedy(grid: Grid, start: Pos, goal: Pos, heuristic: str = "manhattan") -> SearchResult:
    name = "Greedy"
    bad = _invalid(name, grid, start, goal)
    if bad:
        return bad
    h = HEURISTICS[heuristic]
    t0 = time.perf_counter()
    tie = count()
    parents: Dict[Pos, Optional[Pos]] = {start: None}
    heap = [(h(start, goal), next(tie), start)]
    closed = set()
    expanded: List[Pos] = []
    while heap:
        _, _, cur = heapq.heappop(heap)
        if cur in closed:
            continue
        closed.add(cur)
        expanded.append(cur)
        if cur == goal:
            return _finish(name, grid, parents, goal, True, expanded, t0)
        for nb in grid.neighbors(cur):
            if nb not in parents:
                parents[nb] = cur
                heapq.heappush(heap, (h(nb, goal), next(tie), nb))
    return _finish(name, grid, parents, goal, False, expanded, t0)


def astar(grid: Grid, start: Pos, goal: Pos, heuristic: str = "manhattan") -> SearchResult:
    name = f"A* ({heuristic})"
    bad = _invalid(name, grid, start, goal)
    if bad:
        return bad
    h = HEURISTICS[heuristic]
    t0 = time.perf_counter()
    tie = count()
    best: Dict[Pos, int] = {start: 0}
    parents: Dict[Pos, Optional[Pos]] = {start: None}
    heap = [(h(start, goal), next(tie), 0, start)]
    closed = set()
    expanded: List[Pos] = []
    while heap:
        _, _, g, cur = heapq.heappop(heap)
        if cur in closed:
            continue
        closed.add(cur)
        expanded.append(cur)
        if cur == goal:
            return _finish(name, grid, parents, goal, True, expanded, t0)
        for nb in grid.neighbors(cur):
            ng = g + grid.cost(nb)
            if nb not in best or ng < best[nb]:
                best[nb] = ng
                parents[nb] = cur
                heapq.heappush(heap, (ng + h(nb, goal), next(tie), ng, nb))
    return _finish(name, grid, parents, goal, False, expanded, t0)


def astar_manhattan(grid: Grid, start: Pos, goal: Pos) -> SearchResult:
    return astar(grid, start, goal, "manhattan")


def astar_euclidean(grid: Grid, start: Pos, goal: Pos) -> SearchResult:
    return astar(grid, start, goal, "euclidean")


# Registry used by the UI and the benchmark (order = display order)
ALGORITHMS: Dict[str, Callable[[Grid, Pos, Pos], SearchResult]] = {
    "BFS": bfs,
    "DFS": dfs,
    "UCS": ucs,
    "Greedy": greedy,
    "A* (manhattan)": astar_manhattan,
    "A* (euclidean)": astar_euclidean,
}
