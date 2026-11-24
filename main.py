"""QuestMaster entry point.

  python main.py             open the game window (needs pygame)
  python main.py --demo      text-only demo, no window needed
  python main.py --compare   run the algorithm comparison on 30 maps and save tables/chart
"""
import argparse
import sys

from config import settings


def demo() -> None:
    """Prints pathfinding and quest scheduling results without any window."""
    from algorithms.search import ALGORITHMS
    from game.controller import GameState
    from game.maps import make_unreachable_case

    state = GameState()
    npc = state.npc
    goal = (18, 1)
    print(f"Map {state.grid.rows}x{state.grid.cols}. {npc.name} at {npc.pos} -> goal {goal}\n")
    print(f"{'algorithm':<16}{'found':>6}{'steps':>7}{'cost':>6}{'nodes':>7}{'ms':>9}")
    for name, algo in ALGORITHMS.items():
        r = algo(state.grid, npc.pos, goal)
        print(f"{name:<16}{str(r.found):>6}{r.steps:>7}{str(r.cost):>6}{r.nodes_expanded:>7}{r.time_ms:>9.3f}")

    g, s, t = make_unreachable_case()
    r = ALGORITHMS["A* (manhattan)"](g, s, t)
    print(f"\nUnreachable test: goal {t} sealed by walls -> found={r.found} (handled without crashing)")

    state.quests = [(5, 5), (15, 3), (3, 15), (16, 16)]
    state.quests = [q for q in state.quests if state.grid.is_walkable(q)]
    for method in ("hc", "sa"):
        res = state.schedule_quests(method)
        if res:
            print(f"{res.algorithm}: visit order {res.order} total cost {res.cost:.0f}")


def main() -> int:
    parser = argparse.ArgumentParser(description="QuestMaster")
    parser.add_argument("--demo", action="store_true", help="text-only demo")
    parser.add_argument("--compare", action="store_true", help="run algorithm comparison")
    args = parser.parse_args()

    print("QuestMaster - Game NPC Pathfinding and Quest Knowledge Base")
    print(f"LLM mode: {'on' if settings.llm_available() else 'off (basic mode)'}")

    if args.compare:
        from evaluation.compare_search import run_and_save, to_markdown
        print(to_markdown(run_and_save()))
        return 0
    if args.demo:
        demo()
        return 0
    try:
        from game import ui
    except ImportError:
        print("\npygame is not installed, so the window cannot open.\n"
              "Install it with:  pip install pygame\n"
              "Meanwhile you can run:  python main.py --demo")
        return 1
    ui.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
