from thesis_factory.reading.gaps import build_clusters, cluster_vectors, collect_open_questions


def _card(paper_id, *quotes, kind="OPEN_QUESTION"):
    address = {"artifact_sha256": "x", "normalization_version": "v", "paragraph_ordinal": 0, "start_char": 0, "end_char": 1}
    return {
        "paper_id": paper_id, "title": f"title {paper_id}",
        "claims": [{"kind": kind, "statement": q, "quote": q, "address": address} for q in quotes],
    }


def test_recurrence_counts_distinct_papers_not_claims():
    cards = [
        _card("p1", "counterfactuals A", "counterfactuals B"),
        _card("p2", "counterfactuals C"),
        _card("p3", "gdpr A"),
        _card("p4", "gdpr B"),
        _card("p5", "irrelevant finding", kind="FINDING"),
    ]
    items = collect_open_questions(cards)
    assert len(items) == 5  # the FINDING is not collected

    # two well-separated directions stand in for two topics
    vectors = [[1, 0.05], [1, 0.0], [1, -0.05], [0.05, 1], [0, 1]]
    clusters = build_clusters(items, cluster_vectors(vectors, distance_threshold=0.3))

    top = clusters[0]
    assert top["id"] == "Q0001"
    assert top["papers"] == 2 and top["claims"] == 3  # p1 twice counts once
    assert set(top["paper_titles"]) == {"p1", "p2"}
    assert set(clusters[1]["paper_titles"]) == {"p3", "p4"}
    assert len(clusters) == 2


def test_single_vector_gets_one_label():
    assert cluster_vectors([[1.0, 0.0]], distance_threshold=0.3) == [0]
    assert cluster_vectors([], distance_threshold=0.3) == []
