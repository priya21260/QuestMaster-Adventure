"""The game map: a grid of cells.

Each cell is one of:
  - FLOOR (cost 1)  : normal walkable ground
  - MUD   (cost 3)  : walkable but slow (so cheapest path != shortest path)
  - WALL  (blocked) : obstacle, cannot be entered
NPCs move in 4 directions (up, down, left, right).
Positions are (row, col) tuples.
"""
from typing import Iterator, List, Tuple

Pos = Tuple[int, int]

FLOOR = 0
MUD = 1
WALL = 2

TERRAIN_COST = {FLOOR: 1, MUD: 3}


class Grid:
    def __init__(self, rows: int, cols: int, cells: List[List[int]] = None):
        self.rows = rows
        self.cols = cols
        self.cells = cells if cells is not None else [[FLOOR] * cols for _ in range(rows)]

    # --- queries ---
    def in_bounds(self, pos: Pos) -> bool:
        r, c = pos
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_walkable(self, pos: Pos) -> bool:
        return self.in_bounds(pos) and self.cells[pos[0]][pos[1]] != WALL

    def cost(self, pos: Pos) -> int:
        """Cost of ENTERING this cell."""
        return TERRAIN_COST[self.cells[pos[0]][pos[1]]]

    def neighbors(self, pos: Pos) -> Iterator[Pos]:
        r, c = pos
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nxt = (r + dr, c + dc)
            if self.is_walkable(nxt):
                yield nxt

    def walkable_cells(self) -> List[Pos]:
        return [(r, c) for r in range(self.rows) for c in range(self.cols)
                if self.cells[r][c] != WALL]

    # --- editing (used by the interactive map editor) ---
    def set_cell(self, pos: Pos, terrain: int) -> None:
        if self.in_bounds(pos):
            self.cells[pos[0]][pos[1]] = terrain

    def toggle_wall(self, pos: Pos) -> None:
        if self.in_bounds(pos):
            r, c = pos
            self.cells[r][c] = FLOOR if self.cells[r][c] == WALL else WALL

    def path_cost(self, path: List[Pos]) -> int:
        """Total cost of walking a path (cost of every cell entered after the start)."""
        return sum(self.cost(p) for p in path[1:])

    def to_networkx(self):
        """Build a NetworkX graph of the map (edge weight = cost of entering the target cell)."""
        import networkx as nx
        g = nx.DiGraph()
        g.add_nodes_from(self.walkable_cells())   # include isolated cells too
        for pos in self.walkable_cells():
            for nb in self.neighbors(pos):
                g.add_edge(pos, nb, weight=self.cost(nb))
        return g

    def copy(self) -> "Grid":
        return Grid(self.rows, self.cols, [row[:] for row in self.cells])
