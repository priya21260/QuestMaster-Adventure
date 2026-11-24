# QuestMaster - Game NPC Pathfinding and Quest Knowledge Base

A 2D game where NPCs find paths with AI search algorithms, schedule quests with
constraint reasoning, answer questions from a knowledge base, and cooperate as
AI agents. Individual FAI project P51 (Gaming domain).

> Status: Phases 0-1 complete (setup, game environment, search algorithms). See `PROJECT_PROGRESS.md`.

## Setup

1. Install Python 3.10 or newer.
2. (Recommended) create a virtual environment:
   - Windows: `python -m venv venv` then `venv\Scripts\activate`
   - Mac/Linux: `python3 -m venv venv` then `source venv/bin/activate`
3. Install the packages needed so far (Phases 0-1):
   `pip install pygame networkx numpy matplotlib pandas pytest python-dotenv`
   (The full `requirements.txt` also lists LangChain, LangGraph, AutoGen, CrewAI and Streamlit; they are only needed from Phase 3-4 and are large, so install them later.)
4. Check your setup: `python check_environment.py` (only the Phase 1 items must be OK for now)
5. (Optional) copy `.env.example` to `.env` to enable LLM features. Not needed for basic mode.

## Run

- `python main.py` - opens the game window (needs pygame).
- `python main.py --demo` - text-only demo of pathfinding and quest scheduling.
- `python main.py --compare` - benchmark all algorithms on 30 maps; saves to `evaluation/results/`.
- `python -m pytest` - runs all tests.

## Game controls

| Input | Action |
|-------|--------|
| Left click | Select an NPC (click its circle) or set the destination for the selected NPC |
| Right click | Toggle a wall |
| M | Toggle mud (slow terrain, cost 3) under the mouse |
| Q | Mark/unmark a quest location under the mouse |
| TAB | Switch NPC |
| A / Left / Right | Change search algorithm |
| ENTER | Run pathfinding (the NPC then walks the path) |
| SPACE | Pause / resume walking |
| C | Compare all algorithms for the selected NPC and goal |
| S / H | Schedule quest order with Simulated Annealing / Hill Climbing |
| E | Show/hide explored cells |
| R | Reset |
| ESC | Quit |

## Folder guide

| Folder | Purpose |
|--------|---------|
| `config/` | Settings |
| `game/` | Grid map, NPCs, Pygame window |
| `algorithms/` | BFS, DFS, UCS, Greedy, A*, Hill Climbing, Simulated Annealing |
| `reasoning/` | CSP, FOL, Prolog, belief states |
| `knowledge_base/` | Game documents for NPC answers and RAG |
| `agents/` | NPC agents, tools, memory, guardrails |
| `frameworks/` | LangGraph, AutoGen, CrewAI |
| `learning/` | Q-learning, MARL |
| `evaluation/` | Benchmarks and test datasets |
| `ethics/` | Fairness and safety checks |
| `dashboard/` | Streamlit dashboard |
| `tests/` | Automated tests |
| `docs/` | Documentation and report |
