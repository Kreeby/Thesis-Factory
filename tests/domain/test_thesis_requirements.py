import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from thesis_factory.domain.thesis_requirements import (
    RequirementAuthority,
    RequirementCategory,
    RequirementLevel,
    RequirementScope,
    ThesisRequirementSet,
)


ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

REQUIREMENTS_PATH = (
        ROOT
        / "config"
        / "requirements"
        / "elte_ik_msc.json"
)


def _load() -> ThesisRequirementSet:
    raw = json.loads(
        REQUIREMENTS_PATH.read_text(
            encoding="utf-8"
        )
    )

    return (
        ThesisRequirementSet
        .model_validate(
            raw
        )
    )


def test_elute_requirement_set_validates() -> None:
    requirement_set = _load()

    assert (
            requirement_set.id
            == "elte-ik-msc-v1"
    )

    assert (
            requirement_set.source_sha256
            == (
                "129d548384f437e2eb3b4fdee15a8471"
                "371b2b664cf86b3400b34790d12f72d5"
            )
    )


def test_core_topic_researchability_constraints_exist() -> None:
    requirement_set = _load()

    by_id = {
        requirement.id: requirement
        for requirement
        in requirement_set.requirements
    }

    assert (
            by_id[
                "systematic-research"
            ].level
            == RequirementLevel.REQUIRED
    )

    assert (
            by_id[
                "systematic-research"
            ].authority
            == (
                RequirementAuthority
                .FACULTY_REQUIREMENT
            )
    )

    assert (
            by_id[
                "experimental-software-work"
            ].category
            == RequirementCategory.ENGINEERING
    )

    assert (
            by_id[
                "validation"
            ].category
            == RequirementCategory.VALIDATION
    )

    assert (
            by_id[
                "results-based-contribution"
            ].category
            == RequirementCategory.CONTRIBUTION
    )


def test_eit_prototype_is_scoped_to_eit() -> None:
    requirement_set = _load()

    prototype = next(
        requirement
        for requirement
        in requirement_set.requirements
        if (
                requirement.id
                == "eit-prototype"
        )
    )

    assert prototype.scopes == (
        RequirementScope.EIT,
    )


def test_ai_policy_remains_explicitly_unknown() -> None:
    requirement_set = _load()

    question_ids = {
        question.id
        for question
        in requirement_set.open_questions
    }

    assert (
            "ai-assistance-policy"
            in question_ids
    )


def test_duplicate_requirement_ids_are_rejected() -> None:
    requirement_set = _load()

    raw = (
        requirement_set
        .model_dump(
            mode="json"
        )
    )

    raw[
        "requirements"
    ].append(
        raw[
            "requirements"
        ][0]
    )

    with pytest.raises(
            ValidationError,
            match=(
                    "requirement ids "
                    "must be unique"
            ),
    ):
        ThesisRequirementSet.model_validate(
            raw
        )