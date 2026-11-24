"""Tests for the benchmark module."""
from evaluation.compare_search import benchmark, summarise, to_markdown


def test_benchmark_covers_30_maps_and_all_algorithms():
    df = benchmark(30)
    assert df["map"].nunique() == 30
    assert df["algorithm"].nunique() == 6
    assert df["found"].all()          # target: 100% of reachable goals reached


def test_summary_claims_hold():
    s = summarise(benchmark(30)).set_index("algorithm")
    assert s.loc["UCS", "optimal_rate"] == 1.0
    assert s.loc["A* (manhattan)", "optimal_rate"] == 1.0
    assert s.loc["A* (manhattan)", "avg_nodes_expanded"] < s.loc["UCS", "avg_nodes_expanded"]
    assert "| algorithm |" in to_markdown(s.reset_index())
