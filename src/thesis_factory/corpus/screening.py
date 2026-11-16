"""Recall-first screening policy.

Papers surfaced by any core (topic-specific) query are kept without LLM
screening; only papers surfaced exclusively by broad method queries (SHAP,
LIME, ...) are screened by a local model. Measured on
evals/relevance/corpus_silver_v1.json before adoption.
"""

from thesis_factory.corpus.store import CorpusStore


def needs_screening(
        queries: set[str],
        broad_queries: set[str],
) -> bool:
    return bool(queries) and queries <= broad_queries


def included_papers(
        store: CorpusStore,
        *,
        broad_queries: set[str],
        topic: str,
        model: str,
) -> tuple[set[str], set[str]]:
    """Return (included, unscreened) paper ids.

    Unscreened broad-only papers are reported, never silently dropped or kept.
    """

    screenings = store.screenings(topic, model)
    included: set[str] = set()
    unscreened: set[str] = set()

    for paper_id, queries in store.paper_queries().items():
        if not needs_screening(queries, broad_queries):
            included.add(paper_id)
        elif paper_id not in screenings:
            unscreened.add(paper_id)
        elif screenings[paper_id] != "NOT_RELEVANT":
            included.add(paper_id)

    return included, unscreened
