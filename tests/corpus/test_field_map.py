import pytest

from thesis_factory.corpus.field_map import pagerank


def test_pagerank_ranks_most_cited_paper_first_and_ignores_outside_edges() -> None:
    ranks = pagerank(
        ["a", "b", "c"],
        [("a", "c"), ("b", "c"), ("c", "a"), ("a", "outside")],
    )

    assert max(ranks, key=ranks.get) == "c"
    assert sum(ranks.values()) == pytest.approx(1.0)
