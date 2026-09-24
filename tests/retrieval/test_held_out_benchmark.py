import json
import re
from collections import Counter
from pathlib import Path

from thesis_factory.retrieval.evaluation import (
    RetrievalEvalCase,
    RetrievalEvalScope,
    RetrievalQueryStyle,
)


ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

HELD_OUT_PATH = (
    ROOT
    / "evals"
    / "retrieval"
    / "held_out_v1.json"
)

BASELINE_PATH = (
    ROOT
    / "evals"
    / "retrieval"
    / "baseline_v2.json"
)


def _load(
        path: Path,
) -> dict:
    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def test_held_out_benchmark_shape_is_frozen() -> None:
    raw = _load(
        HELD_OUT_PATH
    )

    cases = tuple(
        RetrievalEvalCase.model_validate(
            case
        )
        for case
        in raw["cases"]
    )

    assert (
        raw["name"]
        == "credit-risk-four-paper-held-out-v1"
    )

    assert raw["top_k"] == 5
    assert len(cases) == 12

    assert (
        len({
            case.id
            for case
            in cases
        })
        == 12
    )

    assert (
        sum(
            len(case.targets)
            for case
            in cases
        )
        == 16
    )

    assert Counter(
        case.query_style
        for case
        in cases
    ) == {
        RetrievalQueryStyle.LEXICAL: 5,
        RetrievalQueryStyle.PARAPHRASE: 7,
    }

    assert Counter(
        case.scope
        for case
        in cases
    ) == {
        RetrievalEvalScope.SINGLE_DOCUMENT: 8,
        RetrievalEvalScope.SOURCE_SELECTION: 2,
        RetrievalEvalScope.CROSS_DOCUMENT: 2,
    }


def test_held_out_documents_are_new_and_pinned() -> None:
    held_out = _load(
        HELD_OUT_PATH
    )

    baseline = _load(
        BASELINE_PATH
    )

    documents = held_out[
        "documents"
    ]

    assert len(documents) == 4

    hashes = {
        document[
            "expected_artifact_sha256"
        ]
        for document
        in documents
    }

    assert len(hashes) == 4

    assert all(
        re.fullmatch(
            r"[0-9a-f]{64}",
            artifact_hash,
        )
        is not None
        for artifact_hash
        in hashes
    )

    baseline_hashes = {
        document[
            "expected_artifact_sha256"
        ]
        for document
        in baseline["documents"]
    }

    assert (
        hashes
        .isdisjoint(
            baseline_hashes
        )
    )

    held_out_dois = {
        document["doi"]
        for document
        in documents
    }

    baseline_dois = {
        document["doi"]
        for document
        in baseline["documents"]
    }

    assert (
        held_out_dois
        .isdisjoint(
            baseline_dois
        )
    )


def test_held_out_selection_did_not_use_retrievers() -> None:
    raw = _load(
        HELD_OUT_PATH
    )

    protocol = raw[
        "selection_protocol"
    ]

    assert (
        protocol[
            "retrieval_systems_used_for_selection"
        ]
        == []
    )

    assert protocol[
        "queries"
    ] == [
        "consumer credit scoring machine learning",
        "corporate default prediction machine learning",
        "alternative data credit scoring",
        "explainable machine learning credit risk",
    ]

    document_queries = [
        document[
            "selection_query"
        ]
        for document
        in raw["documents"]
    ]

    assert document_queries == (
        protocol["queries"]
    )


def test_every_target_points_only_to_held_out_documents() -> None:
    raw = _load(
        HELD_OUT_PATH
    )

    held_out_hashes = {
        document[
            "expected_artifact_sha256"
        ]
        for document
        in raw["documents"]
    }

    cases = tuple(
        RetrievalEvalCase.model_validate(
            case
        )
        for case
        in raw["cases"]
    )

    target_hashes = {
        unit.artifact_sha256
        for case
        in cases
        for target
        in case.targets
        for unit
        in target.acceptable_units
    }

    assert target_hashes
    assert (
        target_hashes
        <= held_out_hashes
    )
