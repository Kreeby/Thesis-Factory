from collections.abc import Callable

from thesis_factory.corpus.store import CorpusStore
from thesis_factory.integrations.semantic_scholar.client import (
    SemanticScholarClient,
)


SPECTER_V2 = "specter_v2"

Progress = Callable[[str], None]


def collect_query(
        client: SemanticScholarClient,
        store: CorpusStore,
        query: str,
        *,
        max_papers: int,
        year: str | None = None,
        progress: Progress = print,
) -> int:
    """Fetch up to ``max_papers`` for ``query``, resuming a prior run."""

    if max_papers < 1:
        raise ValueError("max_papers must be positive")

    state = store.query_run(query)

    if state and (state["completed"] or state["fetched"] >= max_papers):
        progress(f"skip (already fetched {state['fetched']}): {query}")
        return state["fetched"]

    fetched = store.query_hit_count(query)
    token = state["next_token"] if state else None

    for papers, next_token, total in client.search_bulk_pages(
            query,
            token=token,
            year=year,
    ):
        truncated = len(papers) > max_papers - fetched
        store.upsert_papers(papers[:max_papers - fetched], query=query)
        # Count distinct hits so a re-fetched page is not double-counted.
        fetched = store.query_hit_count(query)
        completed = next_token is None and not truncated
        store.save_query_run(
            query,
            # A truncated page is re-fetched on resume so its tail is not lost.
            next_token=token if truncated else next_token,
            total=total,
            fetched=fetched,
            completed=completed,
        )
        token = next_token
        progress(f"{fetched}/{min(total, max_papers)} {query}")

        if completed or fetched >= max_papers:
            break

    return fetched


def enrich_embeddings(
        client: SemanticScholarClient,
        store: CorpusStore,
        *,
        limit: int,
        chunk_size: int = 500,
        progress: Progress = print,
) -> int:
    ids = store.papers_missing_embedding(SPECTER_V2)[:limit]

    for start in range(0, len(ids), chunk_size):
        chunk = ids[start:start + chunk_size]
        items = client.batch(chunk, fields="embedding.specter_v2")

        for paper_id, item in zip(chunk, items):
            vector = ((item or {}).get("embedding") or {}).get("vector")
            store.put_embedding(paper_id, SPECTER_V2, vector)

        progress(f"embeddings {start + len(chunk)}/{len(ids)}")

    return len(ids)


def enrich_references(
        client: SemanticScholarClient,
        store: CorpusStore,
        *,
        limit: int,
        chunk_size: int = 500,
        progress: Progress = print,
) -> int:
    ids = store.papers_missing_references()[:limit]

    for start in range(0, len(ids), chunk_size):
        chunk = ids[start:start + chunk_size]
        items = client.batch(chunk, fields="references.paperId")

        for paper_id, item in zip(chunk, items):
            store.put_references(
                paper_id,
                (
                    ref["paperId"]
                    for ref in (item or {}).get("references") or []
                    if ref.get("paperId")
                ),
            )

        progress(f"references {start + len(chunk)}/{len(ids)}")

    return len(ids)
