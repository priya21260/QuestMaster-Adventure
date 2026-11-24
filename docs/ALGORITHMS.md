# ALGORITHMS.md - Search and Optimisation in QuestMaster

All code is in `algorithms/search.py` and `algorithms/local_search.py`.
Map rules: 4-direction movement; FLOOR costs 1, MUD costs 3, WALL is blocked.

## 1. Path-finding (find a route from start to goal)

| Algorithm | Idea (simple words) | Finds shortest in steps? | Finds cheapest in cost? | Uses |
|---|---|---|---|---|
| BFS | Explore all cells 1 step away, then 2 steps, ... (a queue) | Yes | No (ignores mud) | queue |
| DFS | Go as deep as possible, back up when stuck (a stack) | No | No | stack |
| UCS | Always expand the cell with the lowest cost so far | No guarantee | Yes | priority queue on g |
| Greedy Best-First | Always expand the cell that *looks* closest to the goal | No | No | priority queue on h |
| A* | Expand lowest (cost so far + estimate to goal) | - | Yes (if heuristic is admissible) | priority queue on g+h |

### Heuristics for A* (two required)
- **Manhattan** `|dr|+|dc|` - exact distance if there were no walls/mud on a 4-direction grid.
- **Euclidean** straight-line distance - always <= Manhattan, so it is also admissible but less informed, so A* expands more nodes with it.

Both never overestimate (the cheapest cell costs 1), so A* returns the optimal path with either.

### Unreachable goals
If the open list becomes empty without reaching the goal, the algorithm returns `found=False`, an empty path and cost `None`. A blocked or out-of-range start/goal is also handled safely. The UI shows "NO PATH" and the NPC does not move.

## 2. Quest scheduling (choose the order of quest locations)
Problem: visit several quest spots in the cheapest total walking cost. Pairwise costs come from A* on the real map. A state is an ordering; a move swaps two stops.

- **Hill Climbing** - repeatedly take the best improving swap; stops at a local optimum. Run with 5 random restarts to reduce bad luck.
- **Simulated Annealing** - may accept a worse order with probability `exp(-delta/T)`; `T` cools geometrically (x0.995), so early it explores and late it settles.

Tests check both against brute-force optimum on 6-quest problems.

## 3. Measured comparison (30 test maps, reproducible)
Generated with `python main.py --compare`; files are in `evaluation/results/`.
Maps are 20x20, wall density rising 10%-30%, goal always reachable. Timings are from one machine and vary slightly between runs; node counts and costs are deterministic.

| algorithm | success_rate | avg_nodes_expanded | avg_time_ms | avg_path_cost | optimal_rate |
|---|---|---|---|---|---|
| BFS | 1.0 | 143.633 | 0.151 | 17.533 | 0.4 |
| DFS | 1.0 | 154.5 | 0.173 | 94.2 | 0.0 |
| UCS | 1.0 | 138.567 | 0.223 | 15.667 | 1.0 |
| Greedy | 1.0 | 17.633 | 0.027 | 18.267 | 0.333 |
| A* (manhattan) | 1.0 | 46.0 | 0.081 | 15.667 | 1.0 |
| A* (euclidean) | 1.0 | 59.833 | 0.111 | 15.667 | 1.0 |

(`optimal_rate` = share of maps where the path cost equals the best cost found by any algorithm on that map.)

### What the numbers show
- UCS and both A* variants are always optimal in cost; A* does it with about a third of UCS's expanded nodes.
- Manhattan beats Euclidean on this grid (fewer nodes) because it is the tighter estimate.
- Greedy is fastest and expands the fewest nodes but is optimal on only a third of maps.
- DFS always finds a path but a very poor one (average cost about 6x optimal).
- BFS expands about as many nodes as UCS here but ignores mud, so it is optimal on only 40% of maps.

## 4. Limitations
- Timings of sub-millisecond runs are noisy (median of 5 runs is used).
- Results apply to this map style (random obstacles, 20x20), not to all maps.
- Quest scheduling is checked against brute force only for small problems (6 quests).
