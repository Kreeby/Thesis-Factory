from thesis_factory.corpus.build import (
    SPECTER_V2,
    collect_query,
    enrich_embeddings,
    enrich_references,
    snowball_backward,
)
from thesis_factory.corpus.store import CorpusStore


def _paper(paper_id: str, **extra) -> dict:
    return {
        "paperId": paper_id,
        "title": f"Title {paper_id}",
        "abstract": "An abstract.",
        "externalIds": {"DOI": f"10.1/{paper_id.upper()}"},
        **extra,
    }


class _FakeClient:
    def __init__(self, pages=None, batch_items=None):
        self.pages = pages or []
        self.batch_items = batch_items or {}
        self.search_tokens = []
        self.batch_calls = []

    def search_bulk_pages(self, query, *, token=None, year=None):
        self.search_tokens.append(token)
        start = 0 if token is None else int(token)
        for index in range(start, len(self.pages)):
            next_token = str(index + 1) if index + 1 < len(self.pages) else None
            yield self.pages[index], next_token, 5

    def batch(self, ids, *, fields):
        self.batch_calls.append((tuple(ids), fields))
        return [self.batch_items.get(i) for i in ids]


def _store(tmp_path) -> CorpusStore:
    return CorpusStore(tmp_path / "corpus.sqlite")


def test_collect_caps_papers_and_resumes_from_saved_token(tmp_path) -> None:
    store = _store(tmp_path)
    pages = [[_paper("a"), _paper("b")], [_paper("c"), _paper("d")], [_paper("e")]]
    client = _FakeClient(pages)

    assert collect_query(client, store, "q", max_papers=3, progress=lambda _: None) == 3
    assert store.query_run("q")["next_token"] == "1"  # truncated page is re-fetched

    assert collect_query(client, store, "q", max_papers=5, progress=lambda _: None) == 5
    assert client.search_tokens == [None, "1"]
    assert store.query_run("q")["completed"] is True
    assert store.counts()["papers"] == 5
    assert store.counts()["query_hits"] == 5



def test_doi_is_normalized_and_abstract_not_erased(tmp_path) -> None:
    store = _store(tmp_path)
    store.upsert_papers([_paper("a")])
    store.upsert_papers([_paper("a", abstract=None)])

    paper = store.papers()[0]
    assert paper["doi"] == "10.1/a"
    assert paper["abstract"] == "An abstract."


def test_embeddings_store_vectors_and_mark_missing(tmp_path) -> None:
    store = _store(tmp_path)
    store.upsert_papers([_paper("a"), _paper("b")])
    client = _FakeClient(
        batch_items={"a": {"embedding": {"model": "specter_v2", "vector": [0.5, 1.0]}}}
    )

    enrich_embeddings(client, store, limit=10, progress=lambda _: None)
    enrich_embeddings(client, store, limit=10, progress=lambda _: None)

    assert len(client.batch_calls) == 1
    vectors = dict(store.embeddings(SPECTER_V2))
    assert list(vectors) == ["a"]
    assert list(vectors["a"]) == [0.5, 1.0]


def test_references_build_citation_edges_once(tmp_path) -> None:
    store = _store(tmp_path)
    store.upsert_papers([_paper("a"), _paper("b")])
    client = _FakeClient(
        batch_items={"a": {"references": [{"paperId": "b"}, {"paperId": None}]}}
    )

    enrich_references(client, store, limit=10, progress=lambda _: None)
    enrich_references(client, store, limit=10, progress=lambda _: None)

    assert store.citations() == [("a", "b")]
    assert len(client.batch_calls) == 1


def test_only_broad_only_papers_are_screened_and_unscreened_are_reported(tmp_path) -> None:
    from thesis_factory.corpus.screening import included_papers

    store = _store(tmp_path)
    store.upsert_papers([_paper("core")], query="credit")
    store.upsert_papers([_paper("core"), _paper("noise"), _paper("xai"), _paper("todo")], query="shap")
    for paper_id, status in [("noise", "NOT_RELEVANT"), ("xai", "UNCERTAIN")]:
        store.put_screening(paper_id, topic="t", model="m", status=status, rationale="r")

    included, unscreened = included_papers(store, broad_queries={"shap"}, topic="t", model="m")

    assert included == {"core", "xai"}
    assert unscreened == {"todo"}


def test_priority_plan_ranks_by_learned_relevance_and_audits_the_tail(tmp_path) -> None:
    from thesis_factory.corpus.screening import priority_plan

    store = _store(tmp_path)
    papers = []
    for i in range(40):
        relevant = i % 4 == 0
        paper_id = f"p{i:02d}"
        store.put_embedding(paper_id, "e", [1.0, 0.1 * (i % 3)] if relevant else [0.1 * (i % 3), 1.0])
        if i < 20:
            store.put_screening(paper_id, topic="t", model="m",
                                status="RELEVANT" if relevant else "NOT_RELEVANT", rationale="r")
        else:
            papers.append({"paper_id": paper_id, "abstract": "a"})
    papers.append({"paper_id": "bare", "abstract": None})

    plan = priority_plan(store, papers, topic="t", model="m", embedding_model="e",
                         top_fraction=0.25, audit_size=3)

    groups = plan["groups"]
    assert groups["no_abstract"] == ["bare"]
    assert set(groups["top"]) == {"p20", "p24", "p28", "p32", "p36"}
    assert len(groups["audit"]) == 3 and not set(groups["audit"]) & set(groups["top"])
    assert plan["tail_unscreened"] == 12


def test_rejects_cited_by_included_papers_are_rescued(tmp_path) -> None:
    from thesis_factory.corpus.screening import policy_included

    store = _store(tmp_path)
    store.upsert_papers([_paper("a"), _paper("b")], query="credit")
    store.upsert_papers([_paper("classic"), _paper("noise")], query="shap")
    for paper_id in ("classic", "noise"):
        store.put_screening(paper_id, topic="t", model="m", status="NOT_RELEVANT", rationale="r")
    store.put_references("a", ["classic", "noise"])
    store.put_references("b", ["classic"])
    config = {"broad_queries": ["shap"], "screening_topic": "t", "rescue_min_citations": 2}

    included, unscreened, rescued = policy_included(store, config, model="m")

    assert rescued == {"classic"}
    assert included == {"a", "b", "classic"}
    assert unscreened == set()


def test_no_abstract_paper_dropped_only_by_title_only_not_relevant(tmp_path) -> None:
    from thesis_factory.corpus.screening import included_papers

    store = _store(tmp_path)
    store.upsert_papers([_paper("bare_noise"), _paper("bare_maybe"), _paper("bare_todo")], query="shap")
    for paper_id in ("bare_noise", "bare_maybe", "bare_todo"):
        store.put_screening(paper_id, topic="t", model="m", status="INSUFFICIENT_EVIDENCE", rationale="r")
    store.put_screening("bare_noise", topic="t", model="m:title-only", status="NOT_RELEVANT", rationale="r")
    store.put_screening("bare_maybe", topic="t", model="m:title-only", status="UNCERTAIN", rationale="r")

    included, _ = included_papers(store, broad_queries={"shap"}, topic="t", model="m")

    assert included == {"bare_maybe", "bare_todo"}


def test_backward_snowball_adds_cited_outsiders_for_screening_not_rescue(tmp_path) -> None:
    from thesis_factory.corpus.screening import policy_included

    store = _store(tmp_path)
    store.upsert_papers([_paper("a"), _paper("b")], query="credit")
    store.upsert_papers([_paper("rejected")], query="shap")
    store.put_screening("rejected", topic="t", model="m", status="NOT_RELEVANT", rationale="r")
    store.put_references("a", ["out1", "out2", "gone"])
    store.put_references("b", ["out1", "gone"])
    store.put_references("rejected", ["out2"])
    client = _FakeClient(batch_items={"out1": _paper("out1")})

    added = snowball_backward(client, store, included={"a", "b"}, min_citations=2, query="snowball", progress=lambda _: None)

    # out2 has one included citer; "gone" is unknown to S2.
    assert added == 1
    assert client.batch_calls[0][0] == ("gone", "out1")
    config = {
        "broad_queries": ["shap", "snowball"], "screening_topic": "t",
        "rescue_min_citations": 2, "snowball_query": "snowball",
    }
    included, unscreened, rescued = policy_included(store, config, model="m")
    assert unscreened == {"out1"}
    assert rescued == set()
