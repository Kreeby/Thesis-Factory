import numpy as np

from thesis_factory.corpus.priority import priority_scores


def test_relevance_follows_facet_similarity_and_momentum_favours_recent() -> None:
    vectors = {
        "core": np.array([1.0, 0.0]),
        "near": np.array([0.9, 0.1]),
        "far": np.array([0.0, 1.0]),
        "old": np.array([0.8, 0.2]),
    }
    cited = {"old": 10, "near": 4}
    years = {"core": 2020, "near": 2026, "far": 2020, "old": 2000}

    scores = priority_scores(vectors, {"credit": {"core"}}, cited, years, current_year=2026)

    assert scores["far"]["relevance"] == min(s["relevance"] for s in scores.values())
    assert scores["old"]["influence"] > scores["near"]["influence"]
    # 4 citations in its first year beat 10 spread over 27 years.
    assert scores["near"]["momentum"] > scores["old"]["momentum"]
    assert all(0 < s["score"] <= 100 and s["facet"] == "credit" for s in scores.values())
