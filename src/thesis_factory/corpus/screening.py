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


def priority_plan(
        store: CorpusStore,
        pending: list[dict],
        *,
        topic: str,
        model: str,
        embedding_model: str,
        top_fraction: float,
        audit_size: int,
        seed: int = 0,
) -> dict:
    """Order pending broad-only papers for screening by predicted relevance.

    A logistic regression on SPECTER2 vectors, trained on the local model's own
    verdicts so far, ranks the papers. Returned groups, in screening order:
    ``no_abstract`` (no LLM call needed), ``no_embedding`` and ``top`` (screened
    in full), ``audit`` (random sample of the tail, to measure what the cut
    leaves behind). The rest of the tail stays unscreened and is reported.
    """

    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    from sklearn.model_selection import cross_val_predict

    vectors = {
        paper_id: np.asarray(vector, dtype=np.float32)
        for paper_id, vector in store.embeddings(embedding_model)
    }
    labels = [
        (paper_id, status != "NOT_RELEVANT")
        for paper_id, status in store.screenings(topic, model).items()
        if status != "INSUFFICIENT_EVIDENCE" and paper_id in vectors
    ]

    def matrix(ids: list[str]):
        x = np.stack([vectors[i] for i in ids])
        return x / np.linalg.norm(x, axis=1, keepdims=True)

    x_train = matrix([paper_id for paper_id, _ in labels])
    y_train = np.array([label for _, label in labels])
    classifier = LogisticRegression(max_iter=2000)
    cv_scores = cross_val_predict(classifier, x_train, y_train, cv=5, method="predict_proba")[:, 1]
    classifier.fit(x_train, y_train)

    no_abstract = [p["paper_id"] for p in pending if not (p["abstract"] or "").strip()]
    rest = [p["paper_id"] for p in pending if (p["abstract"] or "").strip()]
    no_embedding = [i for i in rest if i not in vectors]
    scored = [i for i in rest if i in vectors]
    scores = classifier.predict_proba(matrix(scored))[:, 1] if scored else []
    ranked = [i for _, i in sorted(zip(scores, scored), key=lambda t: (-t[0], t[1]))]

    cut = round(len(ranked) * top_fraction)
    tail = ranked[cut:]
    rng = np.random.default_rng(seed)
    audit = sorted(rng.choice(tail, size=min(audit_size, len(tail)), replace=False).tolist()) if tail else []

    order = np.argsort(-cv_scores)
    cv_recall = float(np.cumsum(y_train[order])[round(len(order) * top_fraction) - 1] / y_train.sum())

    return {
        "training_labels": len(labels),
        "training_positives": int(y_train.sum()),
        "cv_auc": round(float(roc_auc_score(y_train, cv_scores)), 4),
        "cv_recall_at_top_fraction": round(cv_recall, 4),
        "top_fraction": top_fraction,
        "seed": seed,
        "groups": {
            "no_abstract": no_abstract,
            "no_embedding": no_embedding,
            "top": ranked[:cut],
            "audit": audit,
        },
        "tail_unscreened": len(tail) - len(audit),
    }
