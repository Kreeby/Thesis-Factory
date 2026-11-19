import numpy as np

from thesis_factory.corpus.priority import priority_scores, select_round1


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


def test_round1_quotas_per_facet_and_central_by_overall_score() -> None:
    def paper(score, year, facet, title="A study", rel=50, mom=50):
        return {"score": score, "year": year, "facet": facet, "title": title, "relevance": rel, "momentum": mom}

    scored = {
        "s1": paper(90, 2015, "a", "A survey of credit XAI"),
        "s2": paper(10, 2015, "a", "A review of nothing"),
        "new": paper(20, 2025, "a", rel=99, mom=99),
        "top": paper(95, 2010, "a"),
        "b1": paper(50, 2025, "b"),
        "b2": paper(40, 2010, "b"),
    }

    picked = select_round1(scored, central=1, surveys=1, frontier=1, frontier_from=2024)

    assert picked["a"] == [("s1", "survey"), ("new", "frontier"), ("top", "central")]
    # b2 loses the single central slot to a's higher-scoring paper.
    assert picked["b"] == [("b1", "frontier")]
