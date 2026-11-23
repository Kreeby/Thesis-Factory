"""Stage 3 input: group verified OPEN_QUESTION claims and count recurrence by distinct papers.

Deterministic given the embeddings (agglomerative clustering of verified-quote vectors). Clusters are
discovery candidates only: whether a quote states a real open question, and whether the
gap survives refutation, is decided by a separate review step.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

import numpy as np
from sklearn.cluster import AgglomerativeClustering

KIND = "OPEN_QUESTION"


def collect_open_questions(cards: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    items = []
    for card in cards:
        for claim in card.get("claims", []):
            if claim.get("kind") == KIND:
                items.append({
                    "paper_id": card["paper_id"],
                    "title": card.get("title", ""),
                    "statement": claim["statement"],
                    "quote": claim["quote"],
                    "address": claim["address"],
                })
    return items


def cluster_vectors(vectors: list[list[float]], distance_threshold: float) -> list[int]:
    """Label per vector: agglomerative clustering, cosine distance, average linkage."""
    # TF-IDF was tried first and grouped by shared words ("neural networks"), not by question.
    if len(vectors) < 2:
        return [0] * len(vectors)
    return [int(label) for label in AgglomerativeClustering(
        n_clusters=None, metric="cosine", linkage="average", distance_threshold=distance_threshold,
    ).fit_predict(np.asarray(vectors, dtype=float))]


def build_clusters(items: list[dict[str, Any]], labels: list[int]) -> list[dict[str, Any]]:
    """Clusters ordered by distinct papers (recurrence), then by claim count."""
    groups: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for item, label in zip(items, labels):
        groups[label].append(item)
    clusters = []
    for members in groups.values():
        papers = {m["paper_id"]: m["title"] for m in members}
        # one text can sit under several paper_ids (duplicate corpus records); count distinct texts
        texts = {m["address"]["artifact_sha256"] for m in members}
        clusters.append({
            "papers": len(texts), "claims": len(members), "paper_ids": len(papers),
            "paper_titles": papers, "members": members,
        })
    clusters.sort(key=lambda c: (-c["papers"], -c["claims"], c["members"][0]["quote"]))
    for number, cluster in enumerate(clusters, start=1):
        cluster["id"] = f"Q{number:04d}"
    return clusters
