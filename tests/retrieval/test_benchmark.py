import json
import re
from pathlib import Path

from thesis_factory.retrieval.evaluation import (
    RetrievalEvalCase,
)


BENCHMARK_PATH = (
        Path(__file__)
        .parents[2]
        / "evals"
        / "retrieval"
        / "baseline_v2.json"
)


def _benchmark() -> dict:
    return json.loads(
        BENCHMARK_PATH.read_text(
            encoding="utf-8"
        )
    )


def test_benchmark_cases_are_valid() -> None:
    raw = _benchmark()

    cases = tuple(
        RetrievalEvalCase.model_validate(
            case
        )
        for case in raw["cases"]
    )

    assert len(cases) == 12

    assert (
            len({
                case.id
                for case in cases
            })
            == len(cases)
    )

    target_count = sum(
        len(case.targets)
        for case in cases
    )

    assert target_count == 16


def test_benchmark_documents_are_pinned() -> None:
    raw = _benchmark()

    documents = raw["documents"]

    assert len(documents) == 2

    hashes = {
        document[
            "expected_artifact_sha256"
        ]
        for document in documents
    }

    assert len(hashes) == 2

    assert all(
        re.fullmatch(
            r"[0-9a-f]{64}",
            artifact_hash,
        )
        is not None
        for artifact_hash in hashes
    )