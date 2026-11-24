"""NPC (non-player character) with position, a path to follow and a step method."""
from typing import List, Optional

from game.grid import Pos


class NPC:
    def __init__(self, name: str, start: Pos, color=(80, 160, 255)):
        self.name = name
        self.pos = start
        self.start = start
        self.color = color
        self.goal: Optional[Pos] = None
        self.path: List[Pos] = []
        self.path_index = 0          # index in path of the NPC's current cell
        self.last_result = None      # SearchResult from the most recent pathfinding

    def set_path(self, path: List[Pos]) -> None:
        """Give the NPC a path (list of cells starting at its current position)."""
        self.path = list(path)
        self.path_index = 0
        if self.path:
            self.pos = self.path[0]

    @property
    def arrived(self) -> bool:
        return bool(self.path) and self.path_index >= len(self.path) - 1

    def step(self) -> bool:
        """Move one cell along the path. Returns True if the NPC moved."""
        if not self.path or self.arrived:
            return False
        self.path_index += 1
        self.pos = self.path[self.path_index]
        return True

    def reset(self) -> None:
        self.pos = self.start
        self.path = []
        self.path_index = 0
        self.goal = None
        self.last_result = None
