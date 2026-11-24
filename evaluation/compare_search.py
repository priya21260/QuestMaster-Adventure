"""Compare all search algorithms: nodes expanded, execution time, path cost.

Run:  python -m evaluation.compare_search
Writes results to evaluation/results/ (CSV, Markdown table, PNG chart).
Numbers are measured on this machine; timings vary slightly between runs.
"""
import statistics
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from algorithms.search import ALGORITHMS
from game.grid import Grid, Pos
from game.maps import build_test_maps

RESULTS_DIR = Path(__file__).resolve().parent / "results"


def compare_on_map(grid: Grid, start: Pos, goal: Pos, repeats: int = 5) -> List[dict]:
    """Run every algorithm on one map. Time = median of `repeats` runs."""
    rows = []
    for name, algo in ALGORITHMS.items():
        times = []
        res = None
        for _ in range(repeats):
            res = algo(grid, start, goal)
            times.append(res.time_ms)
        rows.append({
            "algorithm": name,
            "found": res.found,
            "path_cost": res.cost,
            "steps": res.steps,
            "nodes_expanded": res.nodes_expanded,
            "time_ms": statistics.median(times),
        })
    return rows


def benchmark(num_maps: int = 30) -> pd.DataFrame:
    """Full per-map results on the standard 30 test maps."""
    records = []
    for i, (grid, start, goal) in enumerate(build_test_maps(num_maps)):
        for row in compare_on_map(grid, start, goal):
            row["map"] = i
            records.append(row)
    return pd.DataFrame(records)


def summarise(df: pd.DataFrame) -> pd.DataFrame:
    """One row per algorithm: averages over all maps, plus success and optimality rates."""
    optimal = df.groupby("map")["path_cost"].transform("min")
    df = df.assign(is_optimal=(df["path_cost"] == optimal) & df["found"])
    out = df.groupby("algorithm", sort=False).agg(
        success_rate=("found", "mean"),
        avg_nodes_expanded=("nodes_expanded", "mean"),
        avg_time_ms=("time_ms", "mean"),
        avg_path_cost=("path_cost", "mean"),
        optimal_rate=("is_optimal", "mean"),
    ).round(3)
    return out.reset_index()


def to_markdown(summary: pd.DataFrame) -> str:
    cols = list(summary.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in summary.iterrows():
        lines.append("| " + " | ".join(str(r[c]) for c in cols) + " |")
    return "\n".join(lines)


def save_chart(summary: pd.DataFrame, path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    for ax, col, title in zip(
            axes,
            ["avg_nodes_expanded", "avg_time_ms", "avg_path_cost"],
            ["Avg nodes expanded", "Avg time (ms)", "Avg path cost"]):
        ax.barh(summary["algorithm"], summary[col], color="#4f8ef7")
        ax.set_title(title)
        ax.invert_yaxis()
    fig.suptitle("Search algorithm comparison (30 test maps)")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def run_and_save() -> pd.DataFrame:
    RESULTS_DIR.mkdir(exist_ok=True)
    df = benchmark(30)
    summary = summarise(df)
    df.to_csv(RESULTS_DIR / "search_per_map.csv", index=False)
    summary.to_csv(RESULTS_DIR / "search_summary.csv", index=False)
    (RESULTS_DIR / "search_summary.md").write_text(to_markdown(summary) + "\n", encoding="utf-8")
    save_chart(summary, RESULTS_DIR / "search_comparison.png")
    return summary


if __name__ == "__main__":
    s = run_and_save()
    print(to_markdown(s))
    print(f"\nSaved to {RESULTS_DIR}")
