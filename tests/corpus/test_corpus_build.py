from thesis_factory.corpus.build import (
    SPECTER_V2,
    collect_query,
    enrich_embeddings,
    enrich_references,
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
