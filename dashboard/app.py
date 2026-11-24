
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from game.controller import GameState
from algorithms.search import ALGORITHMS


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="QuestMaster",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =====================================================
# RESPONSIVE LIGHT / DARK THEME STYLING
# =====================================================

st.markdown("""
<style>

/* Main application */
.stApp {
    background-color: var(--background-color);
    color: var(--text-color);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--secondary-background-color);
}

/* Headings */
h1, h2, h3, h4 {
    color: var(--text-color) !important;
}

/* General text */
p, li, label {
    color: var(--text-color);
}

/* Metrics */
div[data-testid="stMetric"] {
    background-color: var(--secondary-background-color);
    padding: 15px;
    border-radius: 12px;
}

/* Metric text */
[data-testid="stMetricLabel"],
[data-testid="stMetricValue"] {
    color: var(--text-color) !important;
}

/* Input labels */
.stTextInput label,
.stNumberInput label,
.stSelectbox label,
.stMultiSelect label {
    color: var(--text-color) !important;
}

/* Text and number input */
.stTextInput input,
.stNumberInput input {
    color: var(--text-color) !important;
    background-color: var(--secondary-background-color) !important;
}

/* Select box */
.stSelectbox div[data-baseweb="select"] {
    color: var(--text-color);
}

/* Dropdown options */
[role="option"] {
    color: var(--text-color) !important;
}

/* Buttons */
.stButton button {
    border-radius: 10px;
    font-weight: 600;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 10px;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    color: var(--text-color);
}

/* Captions */
.stCaption {
    color: var(--text-color);
    opacity: 0.85;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# GAME STATE
# =====================================================

if "game" not in st.session_state:
    st.session_state.game = GameState()

game = st.session_state.game


# =====================================================
# HEADER
# =====================================================

st.title("⚔️ QUESTMASTER")

st.caption(
    "Intelligent NPC Pathfinding & Quest Optimization"
)

st.markdown(
    "Explore the world, navigate NPCs, optimize quests "
    "and compare intelligent search algorithms."
)


# =====================================================
# SIDEBAR - GAME CONTROLS
# =====================================================

st.sidebar.title("🎮 Game Controls")

npc_names = [npc.name for npc in game.npcs]

selected_name = st.sidebar.selectbox(
    "Select your NPC",
    npc_names,
    index=game.selected
)

selected_index = npc_names.index(selected_name)

game.select_npc(selected_index)

algorithm_names = list(ALGORITHMS.keys())

selected_algorithm = st.sidebar.selectbox(
    "Pathfinding algorithm",
    algorithm_names,
    index=game.algorithm_index
)

game.algorithm_index = algorithm_names.index(
    selected_algorithm
)

st.sidebar.divider()

st.sidebar.markdown("### 🧭 Destination")

npc = game.npc

goal_row = st.sidebar.number_input(
    "Destination row",
    min_value=0,
    max_value=game.grid.rows - 1,
    value=npc.goal[0] if npc.goal else game.grid.rows - 2,
    key="goal_row"
)

goal_col = st.sidebar.number_input(
    "Destination column",
    min_value=0,
    max_value=game.grid.cols - 1,
    value=npc.goal[1] if npc.goal else 1,
    key="goal_col"
)

if st.sidebar.button(
    "📍 Set Destination",
    width="stretch"
):
    game.click_cell(
        (int(goal_row), int(goal_col))
    )
    st.rerun()


if st.sidebar.button(
    "🔍 Find Path",
    width="stretch"
):
    game.run_pathfinding()
    st.rerun()


if st.sidebar.button(
    "📊 Compare Algorithms",
    width="stretch"
):
    game.run_comparison()
    st.rerun()


st.sidebar.divider()

st.sidebar.markdown("### 🚶 NPC Movement")


if st.sidebar.button(
    "Move One Step",
    width="stretch"
):
    if npc.step():
        game.message = (
            f"{npc.name} moved to {npc.pos}."
        )
    else:
        game.message = "No further movement available."

    st.rerun()


if st.sidebar.button(
    "Reset Game",
    width="stretch"
):
    game.reset()
    st.rerun()


# =====================================================
# MAIN DASHBOARD
# =====================================================

left, right = st.columns([1.7, 1])


# =====================================================
# ADVENTURE MAP
# =====================================================

with left:

    st.subheader("🗺️ Adventure Map")

    st.markdown(
        "🟩 Floor  |  🟫 Mud  |  ⬛ Wall  |  "
        "🔵 NPC  |  ⭐ Quest  |  🟨 Path"
    )

    fig, ax = plt.subplots(figsize=(9, 8))

    colors = [
        "#b8d9a5",
        "#a87845",
        "#253044"
    ]

    cmap = ListedColormap(colors)

    ax.imshow(
        game.grid.cells,
        cmap=cmap,
        vmin=0,
        vmax=2
    )

    # Grid lines

    ax.set_xticks(range(game.grid.cols))
    ax.set_yticks(range(game.grid.rows))

    ax.set_xticks(
        [x - 0.5 for x in range(game.grid.cols + 1)],
        minor=True
    )

    ax.set_yticks(
        [y - 0.5 for y in range(game.grid.rows + 1)],
        minor=True
    )

    ax.grid(
        which="minor",
        color="#64748b",
        linewidth=0.5
    )

    # Quest locations

    for quest in game.quests:

        ax.scatter(
            quest[1],
            quest[0],
            marker="*",
            s=180,
            color="gold"
        )

    # Scheduled quest route

    if game.schedule:

        order = game.schedule.order

        if order:

            ax.plot(
                [p[1] for p in order],
                [p[0] for p in order],
                color="yellow",
                linestyle="--",
                linewidth=2
            )

    # NPC paths

    for character in game.npcs:

        if character.path:

            path = character.path[
                character.path_index:
            ]

            if len(path) > 0:

                ax.plot(
                    [p[1] for p in path],
                    [p[0] for p in path],
                    color="#facc15",
                    linewidth=2
                )

    # NPC characters

    for character in game.npcs:

        color = tuple(
            c / 255 for c in character.color
        )

        ax.scatter(
            character.pos[1],
            character.pos[0],
            s=180,
            color=[color],
            edgecolors="white",
            linewidths=1.5
        )

        ax.text(
            character.pos[1],
            character.pos[0] - 0.3,
            character.name,
            color="white",
            fontsize=8,
            ha="center",
            fontweight="bold"
        )

    # Destination

    if npc.goal:

        ax.scatter(
            npc.goal[1],
            npc.goal[0],
            marker="X",
            color="red",
            s=150
        )

    ax.set_title(
        "QuestMaster World Map",
        color="white"
    )

    ax.tick_params(colors="white")

    fig.patch.set_facecolor("#172338")
    ax.set_facecolor("#172338")

    st.pyplot(fig)

    plt.close(fig)


# =====================================================
# NPC INFORMATION
# =====================================================

with right:

    st.subheader("🧙 NPC Information")

    npc = game.npc

    st.metric(
        "Selected NPC",
        npc.name
    )

    st.metric(
        "Current Position",
        str(npc.pos)
    )

    st.metric(
        "Destination",
        str(npc.goal or "Not set")
    )

    st.divider()

    st.subheader("📈 Pathfinding Results")

    result = npc.last_result

    if result:

        col1, col2 = st.columns(2)

        col1.metric(
            "Steps",
            result.steps
        )

        col2.metric(
            "Path Cost",
            result.cost
        )

        col1.metric(
            "Nodes Expanded",
            result.nodes_expanded
        )

        col2.metric(
            "Execution Time",
            f"{result.time_ms:.3f} ms"
        )

        st.success(
            "Path found successfully!"
            if result.found
            else "No path found."
        )

    else:

        st.info(
            "Set a destination and run pathfinding."
        )

    st.divider()

    st.subheader("📜 Game Status")

    st.info(game.message)


# =====================================================
# ALGORITHM COMPARISON
# =====================================================

st.divider()

st.subheader(
    "📊 Algorithm Performance Comparison"
)

if game.comparison:

    st.dataframe(
        game.comparison,
        width="stretch",
        hide_index=True
    )

else:

    st.info(
        "Select a destination and click Compare Algorithms."
    )


# =====================================================
# QUEST SCHEDULING
# =====================================================

st.divider()

st.subheader("⭐ Quest Scheduling")

st.write(
    "Choose multiple locations on the map using their "
    "coordinates and calculate an optimized visiting order."
)

q1, q2, q3 = st.columns(3)


with q1:

    quest_row = st.number_input(
        "Quest row",
        min_value=0,
        max_value=game.grid.rows - 1,
        value=5,
        key="quest_row"
    )


with q2:

    quest_col = st.number_input(
        "Quest column",
        min_value=0,
        max_value=game.grid.cols - 1,
        value=5,
        key="quest_col"
    )


with q3:

    st.write("")
    st.write("")

    if st.button(
        "⭐ Add / Remove Quest",
        width="stretch"
    ):

        game.toggle_quest(
            (int(quest_row), int(quest_col))
        )

        st.rerun()


if game.quests:

    st.write(
        "Marked quest locations:",
        game.quests
    )


method = st.selectbox(
    "Optimization method",
    ["sa", "hc"],
    format_func=lambda x: (
        "Simulated Annealing"
        if x == "sa"
        else "Hill Climbing"
    )
)


if st.button(
    "🚀 Optimize Quest Route",
    width="stretch"
):

    game.schedule_quests(method)
    st.rerun()


if game.schedule:

    st.success("Quest route optimized!")

    st.write(
        "Algorithm:",
        game.schedule.algorithm
    )

    st.write(
        "Total route cost:",
        game.schedule.cost
    )

    st.write(
        "Visit order:",
        game.schedule.order
    )


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.caption(
    "QUESTMASTER | Intelligent Game AI | "
    "Pathfinding • Optimization • NPC Navigation"
)
