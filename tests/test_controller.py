"""Tests for GameState (the logic behind the window) - no display needed."""
from game.controller import GameState
from game.grid import Grid, WALL
from game.maps import make_unreachable_case


def test_click_goal_then_run_moves_npc_to_goal():
    s = GameState(Grid(8, 8))
    s.npcs[0].pos = s.npcs[0].start = (0, 0)
    s.select_npc(0)
    s.click_cell((5, 5))
    assert s.npc.goal == (5, 5)
    res = s.run_pathfinding()
    assert res.found
    for _ in range(100):
        s.step_all()
    assert s.npc.pos == (5, 5) and s.npc.arrived


def test_every_algorithm_selectable_and_runs():
    s = GameState(Grid(8, 8))
    s.npc.goal = (6, 6)
    for _ in s.algorithm_names:
        assert s.run_pathfinding().found
        s.cycle_algorithm()


def test_unreachable_goal_message_and_no_movement():
    grid, _, goal = make_unreachable_case()
    s = GameState(grid)
    s.npc.pos = s.npc.start = (0, 0)
    s.npc.goal = goal
    res = s.run_pathfinding()
    assert not res.found
    assert "NO PATH" in s.message
    s.step_all()
    assert s.npc.pos == (0, 0)


def test_clicking_wall_does_not_set_goal():
    g = Grid(5, 5)
    g.cells[2][2] = WALL
    s = GameState(g)
    s.click_cell((2, 2))
    assert s.npc.goal is None


def test_wall_edit_and_npc_protected():
    s = GameState(Grid(20, 20))
    npc_pos = s.npc.pos
    s.edit_wall(npc_pos)
    assert s.grid.is_walkable(npc_pos)            # cannot wall over an NPC
    s.edit_wall((10, 10))
    assert not s.grid.is_walkable((10, 10))


def test_comparison_returns_row_per_algorithm():
    s = GameState(Grid(8, 8))
    s.npc.goal = (7, 7)
    rows = s.run_comparison()
    assert [r["algorithm"] for r in rows] == s.algorithm_names


def test_quest_scheduling_through_controller():
    s = GameState(Grid(12, 12))
    for q in [(3, 3), (9, 2), (2, 9), (10, 10)]:
        s.toggle_quest(q)
    for method in ("hc", "sa"):
        res = s.schedule_quests(method)
        assert sorted(res.order) == sorted(s.quests)


def test_scheduling_needs_two_quests():
    s = GameState(Grid(6, 6))
    assert s.schedule_quests("sa") is None
