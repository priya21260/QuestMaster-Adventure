# QuestMaster - Project Progress

**Project:** P51 - QuestMaster: Game NPC Pathfinding and Quest Knowledge Base
**Mode:** Individual | **Last updated:** 2026-11-17

## Status summary

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Environment and project setup | Done, approved |
| 1 | Game environment and search algorithms | Done - awaiting your approval |
| 2 | Reasoning and knowledge representation | Not started |
| 3 | AI agents | Not started |
| 4 | AI frameworks (LangGraph, AutoGen, CrewAI) | Not started |
| 5 | Ethics and advanced concepts | Not started |
| 6 | Integration and testing | Not started |
| 7 | Final deliverables | Not started |

## Phase 1 - completed work

- `game/grid.py`: grid with FLOOR / MUD (cost 3) / WALL, neighbours, NetworkX export.
- `game/maps.py`: reproducible map generator, 30 test maps (goal always reachable), an unreachable-goal map, default demo map.
- `game/npc.py`: NPC with path following.
- `algorithms/search.py`: BFS, DFS, UCS, Greedy, A* with 2 heuristics (Manhattan, Euclidean). Unreachable/blocked goals handled.
- `algorithms/local_search.py`: Hill Climbing (with restarts) and Simulated Annealing for quest visiting order.
- `evaluation/compare_search.py`: benchmark (nodes expanded, time, path cost), saves CSV/Markdown/PNG to `evaluation/results/`.
- `game/controller.py`: game logic without drawing (selection, goals, wall/mud editing, pathfinding, comparison, quest scheduling).
- `game/ui.py`: Pygame window (map, 3 NPCs, click to set goal, algorithm choice, path + explored cells, walking animation, comparison table, quest scheduling).
- `main.py`: `--demo` (text), `--compare` (benchmark), or the window.
- `docs/ALGORITHMS.md` with measured results.

## Actual test results (build workspace, 2026-11-17)

- `python -m pytest`: **30 passed**.
  - A* (both heuristics) and UCS match NetworkX Dijkstra costs on 25 random maps each.
  - All 6 algorithms reach the goal on all 30 test maps (100%).
  - Unreachable, blocked and out-of-range goals handled by all algorithms.
  - Hill Climbing and Simulated Annealing give valid orders, are reproducible, and are within 25% of brute-force optimum on 6-quest problems.
  - Controller tests: click goal, run, walk to goal; unreachable goal; wall editing; comparison; scheduling.
- `python main.py --demo` and `python main.py --compare` ran successfully.

## NOT verified (honest limitations)

- **The Pygame window has not been seen running.** pygame is not installable in my workspace. I only ran `game/ui.py` against a mocked pygame (all 17 scripted input frames ran without errors) and checked its syntax. Real rendering and mouse behaviour must be confirmed on your computer. Please report anything that looks wrong.
- Genetic Algorithm not implemented (the spec allows Simulated Annealing OR Genetic Algorithm).
- Timing numbers are from one machine and vary a little between runs.

## Environment findings (build workspace)

- Not installed there: pygame, langchain, langgraph, autogen, crewai, streamlit, pyswip, SWI-Prolog. Later phases will state what I could and could not run.

## Pending

Phases 2-7 as listed in the project specification.
