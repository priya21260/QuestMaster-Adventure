"""GameState: all game logic WITHOUT any drawing code.

The Pygame window (game/ui.py) only draws this state and forwards clicks to it.
Keeping logic separate makes it easy to test without a display.
"""
from typing import Dict, List, Optional

from algorithms.local_search import ScheduleResult, hill_climbing, simulated_annealing
from algorithms.search import ALGORITHMS, SearchResult
from evaluation.compare_search import compare_on_map
from game.grid import FLOOR, MUD, WALL, Grid, Pos
from game.maps import default_demo_map
from game.npc import NPC

NPC_COLORS = [(80, 160, 255), (255, 140, 60), (120, 220, 120)]


class GameState:
    def __init__(self, grid: Optional[Grid] = None):
        self.grid = grid or default_demo_map()
        self.npcs: List[NPC] = [
            NPC("Aria", (1, 1), NPC_COLORS[0]),
            NPC("Borin", (18, 18), NPC_COLORS[1]),
            NPC("Cael", (1, 18), NPC_COLORS[2]),
        ]
        self.selected = 0
        self.algorithm_names = list(ALGORITHMS.keys())
        self.algorithm_index = 0
        self.quests: List[Pos] = []
        self.schedule: Optional[ScheduleResult] = None
        self.comparison: List[dict] = []
        self.message = "Click an NPC cell, then click a destination. Press ENTER to run."
        self.show_explored = True
        self.pending_goal: Optional[Pos] = None

    # --- selection ---
    @property
    def npc(self) -> NPC:
        return self.npcs[self.selected]

    @property
    def algorithm(self) -> str:
        return self.algorithm_names[self.algorithm_index]

    def select_npc(self, index: int) -> None:
        self.selected = index % len(self.npcs)
        self.message = f"Selected {self.npc.name}."

    def cycle_algorithm(self, delta: int = 1) -> None:
        self.algorithm_index = (self.algorithm_index + delta) % len(self.algorithm_names)
        self.message = f"Algorithm: {self.algorithm}"

    # --- map interaction ---
    def npc_at(self, pos: Pos) -> Optional[int]:
        for i, n in enumerate(self.npcs):
            if n.pos == pos:
                return i
        return None

    def click_cell(self, pos: Pos) -> None:
        """Left click: select an NPC if clicked on one, otherwise set the destination."""
        if not self.grid.in_bounds(pos):
            return
        idx = self.npc_at(pos)
        if idx is not None:
            self.select_npc(idx)
            return
        if not self.grid.is_walkable(pos):
            self.message = "That cell is a wall - choose another destination."
            return
        self.npc.goal = pos
        self.npc.path, self.npc.path_index, self.npc.last_result = [], 0, None
        self.message = f"Goal for {self.npc.name} set to {pos}. Press ENTER to find a path."

    def edit_wall(self, pos: Pos) -> None:
        """Right click: toggle wall. Never walls over an NPC."""
        if self.grid.in_bounds(pos) and self.npc_at(pos) is None:
            self.grid.toggle_wall(pos)
            self._invalidate_paths()

    def edit_mud(self, pos: Pos) -> None:
        """Middle click / M key: toggle mud."""
        if self.grid.in_bounds(pos) and self.grid.cells[pos[0]][pos[1]] != WALL:
            cur = self.grid.cells[pos[0]][pos[1]]
            self.grid.set_cell(pos, FLOOR if cur == MUD else MUD)
            self._invalidate_paths()

    def _invalidate_paths(self) -> None:
        for n in self.npcs:
            n.path, n.path_index, n.last_result = [], 0, None

    # --- pathfinding ---
    def run_pathfinding(self) -> Optional[SearchResult]:
        npc = self.npc
        if npc.goal is None:
            self.message = "Set a destination first (click a cell)."
            return None
        start = npc.pos
        result = ALGORITHMS[self.algorithm](self.grid, start, npc.goal)
        npc.last_result = result
        if result.found:
            npc.set_path(result.path)
            self.message = (f"{self.algorithm}: path found - {result.steps} steps, cost "
                            f"{result.cost}, {result.nodes_expanded} nodes expanded, "
                            f"{result.time_ms:.2f} ms.")
        else:
            npc.path, npc.path_index = [], 0
            self.message = (f"{self.algorithm}: NO PATH - the goal {npc.goal} is unreachable "
                            f"({result.nodes_expanded} nodes expanded).")
        return result

    def run_comparison(self) -> List[dict]:
        npc = self.npc
        if npc.goal is None:
            self.message = "Set a destination first (click a cell)."
            return []
        self.comparison = compare_on_map(self.grid, npc.pos, npc.goal)
        self.message = "Comparison ready (table on the right)."
        return self.comparison

    def step_all(self) -> None:
        for n in self.npcs:
            n.step()

    # --- quest scheduling (Hill Climbing / Simulated Annealing) ---
    def toggle_quest(self, pos: Pos) -> None:
        if not self.grid.is_walkable(pos):
            return
        if pos in self.quests:
            self.quests.remove(pos)
        else:
            self.quests.append(pos)
        self.schedule = None
        self.message = f"{len(self.quests)} quest location(s) marked."

    def schedule_quests(self, method: str = "sa") -> Optional[ScheduleResult]:
        if len(self.quests) < 2:
            self.message = "Mark at least 2 quest locations first (press Q over a cell)."
            return None
        fn = simulated_annealing if method == "sa" else hill_climbing
        self.schedule = fn(self.grid, self.npc.pos, self.quests, seed=42)
        self.message = (f"{self.schedule.algorithm}: visit order cost {self.schedule.cost:.0f} "
                        f"(order: {len(self.schedule.order)} stops).")
        return self.schedule

    def reset(self) -> None:
        for n in self.npcs:
            n.reset()
        self.quests, self.schedule, self.comparison = [], None, []
        self.message = "Reset."
