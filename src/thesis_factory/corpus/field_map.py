"""Deterministic field map: embedding clusters, term labels and citation centrality.

No LLM is involved; every number is reproducible from the corpus database.
"""

from collections import Counter
from typing import Any

import numpy as np
from scipy import sparse
from sklearn.cluster import MiniBatchKMeans
from sklearn.feature_extraction.text import TfidfVectorizer

from thesis_factory.corpus.build import SPECTER_V2
from thesis_factory.corpus.store import CorpusStore


def pagerank(
        node_ids: list[str],
        edges: list[tuple[str, str]],
        *,
        damping: float = 0.85,
        iterations: int = 100,
        tolerance: float = 1e-10,
) -> dict[str, float]:
    """PageRank over citation edges restricted to ``node_ids`` (citing -> cited)."""

    index = {node: i for i, node in enumerate(node_ids)}
    pairs = [
        (index[a], index[b])
        for a, b in edges
        if a in index and b in index and a != b
    ]
    n = len(node_ids)

    if n == 0:
        return {}

    rows = np.array([p[1] for p in pairs], dtype=np.int64)
    cols = np.array([p[0] for p in pairs], dtype=np.int64)
    out_degree = np.bincount(cols, minlength=n).astype(float)
    weights = 1.0 / out_degree[cols] if pairs else np.array([])
    transition = sparse.csr_matrix((weights, (rows, cols)), shape=(n, n))
    dangling = out_degree == 0

    rank = np.full(n, 1.0 / n)

    for _ in range(iterations):
        updated = (
            damping * (transition @ rank + rank[dangling].sum() / n)
            + (1 - damping) / n
        )

        if np.abs(updated - rank).sum() < tolerance:
            rank = updated
            break

        rank = updated

    return dict(zip(node_ids, rank.tolist()))


def build_field_map(
        store: CorpusStore,
        *,
        clusters: int | None = None,
        top_papers: int = 10,
        top_terms: int = 8,
        seed: int = 0,
        only: set[str] | None = None,
) -> dict[str, Any]:
    embedded = [
        (paper_id, vector)
        for paper_id, vector in store.embeddings(SPECTER_V2)
        if only is None or paper_id in only
    ]

    if len(embedded) < 2:
        raise ValueError("field map needs at least two embedded papers")

    paper_ids = [paper_id for paper_id, _ in embedded]
    matrix = np.array([vector for _, vector in embedded], dtype=np.float32)
    matrix /= np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-12

    k = clusters or int(min(40, max(2, round((len(paper_ids) / 50) ** 0.5))))
    labels = MiniBatchKMeans(
        n_clusters=k,
        random_state=seed,
        n_init=3,
        batch_size=4096,
    ).fit_predict(matrix)

    papers = {paper["paper_id"]: paper for paper in store.papers()}
    titles = [papers[pid]["title"] for pid in paper_ids]
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=2,
        max_features=50000,
    )
    tfidf = vectorizer.fit_transform(titles)
    vocabulary = np.array(vectorizer.get_feature_names_out())

    centrality = pagerank(paper_ids, store.citations())

    result = []

    for cluster in range(k):
        members = [i for i, label in enumerate(labels) if label == cluster]

        if not members:
            continue

        term_scores = np.asarray(tfidf[members].mean(axis=0)).ravel()
        member_ids = [paper_ids[i] for i in members]
        ranked = sorted(
            member_ids,
            key=lambda pid: (-centrality[pid], pid),
        )[:top_papers]
        years = Counter(
            papers[pid]["year"] for pid in member_ids if papers[pid]["year"]
        )

        result.append({
            "cluster": cluster,
            "size": len(members),
            "terms": vocabulary[np.argsort(-term_scores)[:top_terms]].tolist(),
            "years": dict(sorted(years.items())),
            "central_papers": [
                {
                    "paper_id": pid,
                    "title": papers[pid]["title"],
                    "year": papers[pid]["year"],
                    "doi": papers[pid]["doi"],
                    "citation_count": papers[pid]["citation_count"],
                    "pagerank": round(centrality[pid], 8),
                }
                for pid in ranked
            ],
        })

    result.sort(key=lambda item: -item["size"])

    return {
        "embedding_model": SPECTER_V2,
        "papers_mapped": len(paper_ids),
        "clusters": result,
        "method": (
            f"MiniBatchKMeans(k={k}, seed={seed}) on L2-normalised SPECTER2; "
            "TF-IDF title terms; PageRank on in-corpus citation edges"
        ),
    }


def render_markdown(field_map: dict[str, Any]) -> str:
    lines = [
        "# Field map",
        "",
        f"Papers mapped: {field_map['papers_mapped']}. Method: {field_map['method']}.",
        "Discovery artifact only: clusters and centrality are not evidence of claims.",
        "",
    ]

    for cluster in field_map["clusters"]:
        lines += [
            f"## Cluster {cluster['cluster']} — {cluster['size']} papers",
            "",
            f"Terms: {', '.join(cluster['terms'])}",
            "",
        ]
        lines += [
            f"- {paper['title']} ({paper['year']}), citations {paper['citation_count']}"
            for paper in cluster["central_papers"]
        ]
        lines.append("")

    return "\n".join(lines)
