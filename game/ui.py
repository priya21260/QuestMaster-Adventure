"""Pygame window for QuestMaster (Phase 1).

Controls (also shown in the side panel):
  Left click   select NPC / set destination for the selected NPC
  Right click  toggle wall          M  toggle mud under mouse
  Q            mark/unmark quest location under mouse
  TAB          next NPC             A / Left / Right   change algorithm
  ENTER        run pathfinding      SPACE  play/pause walking
  C            compare algorithms   S  schedule quests (Simulated Annealing)
  H            schedule quests (Hill Climbing)
  E            show/hide explored cells   R  reset    ESC  quit
"""
import pygame

from config import settings
from game.controller import GameState
from game.grid import MUD, WALL

PANEL_W = 380
STATUS_H = 56

BG = (24, 26, 32)
FLOOR_C = (226, 222, 205)
MUD_C = (150, 115, 70)
WALL_C = (58, 62, 76)
GRID_LINE = (200, 196, 180)
EXPLORED_C = (170, 205, 245)
PATH_C = (255, 215, 0)
GOAL_C = (230, 60, 60)
QUEST_C = (160, 90, 220)
PANEL_BG = (36, 39, 48)
TEXT = (235, 235, 240)
MUTED = (150, 155, 170)
ACCENT = (79, 142, 247)

HELP_LINES = [
    "Left click: select NPC / set goal",
    "Right click: wall   M: mud   Q: quest spot",
    "TAB: next NPC   A/<-/->: algorithm",
    "ENTER: find path   SPACE: play/pause",
    "C: compare   S: schedule (SA)   H: (Hill)",
    "E: explored cells   R: reset   ESC: quit",
]


def run() -> None:
    pygame.init()
    state = GameState()
    cell = settings.CELL_SIZE
    grid_w, grid_h = state.grid.cols * cell, state.grid.rows * cell
    screen = pygame.display.set_mode((grid_w + PANEL_W, grid_h + STATUS_H))
    pygame.display.set_caption("QuestMaster - NPC Pathfinding")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas,menlo,dejavusansmono,arial", 15)
    small = pygame.font.SysFont("consolas,menlo,dejavusansmono,arial", 13)
    big = pygame.font.SysFont("arial", 20, bold=True)

    playing = True
    step_ms = 140
    last_step = pygame.time.get_ticks()

    def cell_at(mouse):
        x, y = mouse
        if x < 0 or y < 0 or x >= grid_w or y >= grid_h:
            return None
        return (y // cell, x // cell)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = cell_at(event.pos)
                if pos is not None:
                    if event.button == 1:
                        state.click_cell(pos)
                    elif event.button == 3:
                        state.edit_wall(pos)
                    elif event.button == 2:
                        state.edit_mud(pos)
            elif event.type == pygame.KEYDOWN:
                key = event.key
                mouse_cell = cell_at(pygame.mouse.get_pos())
                if key == pygame.K_ESCAPE:
                    running = False
                elif key == pygame.K_TAB:
                    state.select_npc(state.selected + 1)
                elif key in (pygame.K_a, pygame.K_RIGHT):
                    state.cycle_algorithm(1)
                elif key == pygame.K_LEFT:
                    state.cycle_algorithm(-1)
                elif key == pygame.K_RETURN:
                    state.run_pathfinding()
                    playing = True
                elif key == pygame.K_SPACE:
                    playing = not playing
                elif key == pygame.K_c:
                    state.run_comparison()
                elif key == pygame.K_s:
                    state.schedule_quests("sa")
                elif key == pygame.K_h:
                    state.schedule_quests("hc")
                elif key == pygame.K_e:
                    state.show_explored = not state.show_explored
                elif key == pygame.K_r:
                    state.reset()
                elif key == pygame.K_m and mouse_cell:
                    state.edit_mud(mouse_cell)
                elif key == pygame.K_q and mouse_cell:
                    state.toggle_quest(mouse_cell)

        now = pygame.time.get_ticks()
        if playing and now - last_step >= step_ms:
            state.step_all()
            last_step = now

        # ------------------------------------------------ draw map
        screen.fill(BG)
        grid = state.grid
        explored = set()
        if state.show_explored and state.npc.last_result is not None:
            explored = set(state.npc.last_result.explored)
        for r in range(grid.rows):
            for c in range(grid.cols):
                t = grid.cells[r][c]
                color = WALL_C if t == WALL else MUD_C if t == MUD else FLOOR_C
                if (r, c) in explored and t != WALL:
                    color = EXPLORED_C
                rect = pygame.Rect(c * cell, r * cell, cell, cell)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, GRID_LINE, rect, 1)

        # paths of all NPCs (selected NPC highlighted)
        for i, n in enumerate(state.npcs):
            if len(n.path) > 1:
                pts = [(p[1] * cell + cell // 2, p[0] * cell + cell // 2) for p in n.path]
                pygame.draw.lines(screen, PATH_C if i == state.selected else n.color, False,
                                  pts, 4 if i == state.selected else 2)

        # quests
        for k, q in enumerate(state.quests):
            cx, cy = q[1] * cell + cell // 2, q[0] * cell + cell // 2
            pygame.draw.polygon(screen, QUEST_C, [(cx, cy - 11), (cx + 10, cy), (cx, cy + 11), (cx - 10, cy)])
        if state.schedule:
            for k, q in enumerate(state.schedule.order, 1):
                label = small.render(str(k), True, (255, 255, 255))
                screen.blit(label, (q[1] * cell + cell // 2 - 4, q[0] * cell + cell // 2 - 7))

        # goals
        for i, n in enumerate(state.npcs):
            if n.goal:
                gx, gy = n.goal[1] * cell, n.goal[0] * cell
                pygame.draw.rect(screen, GOAL_C if i == state.selected else n.color,
                                 (gx + 6, gy + 6, cell - 12, cell - 12), 3)

        # NPCs
        for i, n in enumerate(state.npcs):
            cx, cy = n.pos[1] * cell + cell // 2, n.pos[0] * cell + cell // 2
            pygame.draw.circle(screen, n.color, (cx, cy), cell // 2 - 3)
            pygame.draw.circle(screen, (255, 255, 255) if i == state.selected else (20, 20, 20),
                               (cx, cy), cell // 2 - 3, 3 if i == state.selected else 1)
            screen.blit(small.render(n.name[0], True, (10, 10, 10)), (cx - 4, cy - 7))

        # ------------------------------------------------ side panel
        px = grid_w
        pygame.draw.rect(screen, PANEL_BG, (px, 0, PANEL_W, grid_h + STATUS_H))
        y = 12
        screen.blit(big.render("QuestMaster", True, ACCENT), (px + 14, y)); y += 32
        screen.blit(font.render(f"NPC: {state.npc.name}", True, TEXT), (px + 14, y)); y += 22
        screen.blit(font.render(f"Algorithm: {state.algorithm}", True, TEXT), (px + 14, y)); y += 22
        goal = state.npc.goal
        screen.blit(font.render(f"Goal: {goal if goal else '-'}", True, TEXT), (px + 14, y)); y += 26

        res = state.npc.last_result
        screen.blit(font.render("Last result", True, ACCENT), (px + 14, y)); y += 20
        if res is None:
            screen.blit(small.render("(none yet)", True, MUTED), (px + 14, y)); y += 18
        elif res.found:
            for line in (f"steps: {res.steps}   cost: {res.cost}",
                         f"nodes expanded: {res.nodes_expanded}",
                         f"time: {res.time_ms:.3f} ms"):
                screen.blit(small.render(line, True, TEXT), (px + 14, y)); y += 18
        else:
            screen.blit(small.render("NO PATH (unreachable)", True, GOAL_C), (px + 14, y)); y += 18
        y += 8

        if state.comparison:
            screen.blit(font.render("Comparison", True, ACCENT), (px + 14, y)); y += 20
            screen.blit(small.render(f"{'algorithm':<16}{'cost':>5}{'nodes':>7}{'ms':>8}", True, MUTED), (px + 14, y)); y += 16
            for row in state.comparison:
                cost = row["path_cost"] if row["found"] else "-"
                line = f"{row['algorithm']:<16}{str(cost):>5}{row['nodes_expanded']:>7}{row['time_ms']:>8.3f}"
                screen.blit(small.render(line, True, TEXT), (px + 14, y)); y += 16
            y += 8

        if state.schedule:
            screen.blit(font.render("Quest schedule", True, ACCENT), (px + 14, y)); y += 20
            screen.blit(small.render(f"{state.schedule.algorithm}: cost {state.schedule.cost:.0f}",
                                     True, TEXT), (px + 14, y)); y += 18
            y += 6

        y = grid_h + STATUS_H - 6 * 16 - 10 if grid_h + STATUS_H > 330 else y
        for line in HELP_LINES:
            screen.blit(small.render(line, True, MUTED), (px + 14, y)); y += 16

        # status bar
        pygame.draw.rect(screen, (18, 20, 25), (0, grid_h, grid_w, STATUS_H))
        msg = state.message
        screen.blit(small.render(msg[:90], True, TEXT), (10, grid_h + 8))
        if len(msg) > 90:
            screen.blit(small.render(msg[90:180], True, TEXT), (10, grid_h + 26))

        pygame.display.flip()
        clock.tick(settings.FPS)

    pygame.quit()
