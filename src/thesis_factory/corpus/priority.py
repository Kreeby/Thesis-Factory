"""Graded deep-reading priority for every paper: transparent percentiles, no LLM."""

import re
from collections.abc import Mapping

import numpy as np
from scipy.stats import rankdata

# shortcut: fixed hand-set weights, revisit once candidate research questions exist (then score per question).
WEIGHTS = {"relevance": 0.5, "influence": 0.25, "momentum": 0.25}


def _percentile(values: np.ndarray) -> np.ndarray:
    return rankdata(values, method="average") / len(values) * 100


def priority_scores(
        vectors: Mapping[str, np.ndarray],
        facets: Mapping[str, set[str]],
        cited: Mapping[str, int],
        years: Mapping[str, int | None],
        *,
        current_year: int,
) -> dict[str, dict[str, float | str]]:
    """Score each paper with a vector, every component a 0-100 percentile over the scored set.

    relevance: max cosine to a facet centroid (facet = papers whose titles match it);
    influence: citations from included papers; momentum: the same per year since publication,
    so recent papers are not ranked out merely for being new.
    """

    ids = sorted(vectors)
    matrix = np.stack([vectors[p] for p in ids]).astype(np.float64)
    matrix /= np.linalg.norm(matrix, axis=1, keepdims=True)
    index = {p: i for i, p in enumerate(ids)}
    names = [f for f in facets if any(p in index for p in facets[f])]
    centroids = np.stack([matrix[[index[p] for p in facets[f] if p in index]].mean(axis=0) for f in names])
    centroids /= np.linalg.norm(centroids, axis=1, keepdims=True)
    similarity = matrix @ centroids.T

    counts = np.array([cited.get(p, 0) for p in ids], dtype=np.float64)
    age = np.array([max(1, current_year - (years.get(p) or current_year) + 1) for p in ids])
    parts = {
        "relevance": _percentile(similarity.max(axis=1)),
        "influence": _percentile(counts),
        "momentum": _percentile(counts / age),
    }
    score = sum(WEIGHTS[k] * parts[k] for k in WEIGHTS)
    nearest = similarity.argmax(axis=1)

    return {
        p: {
            **{k: round(float(parts[k][i]), 1) for k in parts},
            "score": round(float(score[i]), 1),
            "facet": names[nearest[i]],
        }
        for i, p in enumerate(ids)
    }


SURVEY = re.compile(r"\b(survey|review|overview|meta-analysis|taxonomy|state of the art)\b", re.I)


def select_round1(
        scored: Mapping[str, Mapping],
        *,
        central: int,
        surveys: int,
        frontier: int,
        frontier_from: int,
) -> dict[str, list[tuple[str, str]]]:
    """Field-map reading list before any research question exists: per facet, (paper_id, stratum).

    Per facet: survey, the top-scoring reviews (each compresses many papers), and frontier,
    papers since ``frontier_from`` ranked by relevance + momentum, where open problems are
    stated. Then central: the ``central`` top-scoring papers overall, so a crowded facet does
    not lose landmark papers to a fixed quota. Screen status is ignored on purpose: the local
    screen drops foundational general work.
    """

    by_score = sorted(scored, key=lambda p: (-scored[p]["score"], p))
    strata = [
        ("survey", surveys, [p for p in by_score if SURVEY.search(scored[p]["title"])]),
        ("frontier", frontier, sorted(
            (p for p in scored if (scored[p]["year"] or 0) >= frontier_from),
            key=lambda p: (-(scored[p]["relevance"] + scored[p]["momentum"]), p),
        )),
    ]
    taken: set[str] = set()
    picked: dict[str, list[tuple[str, str]]] = {}

    for facet in sorted({s["facet"] for s in scored.values()}):
        picked[facet] = []
        for stratum, quota, ranked in strata:
            chosen = [p for p in ranked if scored[p]["facet"] == facet and p not in taken][:quota]
            picked[facet] += [(p, stratum) for p in chosen]
            taken.update(chosen)

    for p in [p for p in by_score if p not in taken][:central]:
        picked[scored[p]["facet"]].append((p, "central"))

    return picked
