import json
from pathlib import Path

import pytest

from thesis_factory.domain.thesis_requirements import (
    RequirementLevel,
    RequirementScope,
    ThesisRequirementSet,
)
from thesis_factory.domain.topic_researchability import (
    RequirementAssessmentStatus,
    ResearchabilityDimension,
    ResearchabilityDimensionAssessment,
    ResearchabilityDimensionStatus,
    TopicResearchabilityStatus,
    UniversityFitStatus,
    UniversityRequirementAssessment,
    build_topic_researchability_report,
    evaluate_university_fit,
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


def _requirement_set(
) -> ThesisRequirementSet:
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


def _assessment(
        requirement_id: str,
        status: (
                RequirementAssessmentStatus
        ),
) -> UniversityRequirementAssessment:
    return UniversityRequirementAssessment(
        requirement_id=(
            requirement_id
        ),
        status=status,
        rationale=(
            f"Assessment for "
            f"{requirement_id}."
        ),
    )


def _positive_assessments(
        requirement_set: (
                ThesisRequirementSet
        ),
        *,
        scopes: tuple[
            RequirementScope,
            ...,
        ],
) -> tuple[
    UniversityRequirementAssessment,
    ...,
]:
    scope_set = set(
        scopes
    )

    return tuple(
        _assessment(
            requirement.id,
            (
                RequirementAssessmentStatus
                .SATISFIED
            ),
        )
        for requirement
        in requirement_set.requirements
        if (
                set(requirement.scopes)
                & scope_set
                and requirement.level
                in {
                    RequirementLevel.REQUIRED,
                    RequirementLevel.EXPECTED,
                }
        )
    )


def _passing_university_fit():
    requirement_set = (
        _requirement_set()
    )

    scopes = (
        RequirementScope.MSC,
    )

    return evaluate_university_fit(
        topic=(
            "Explainable machine learning "
            "for credit risk"
        ),
        requirement_set=(
            requirement_set
        ),
        active_scopes=scopes,
        assessments=(
            _positive_assessments(
                requirement_set,
                scopes=scopes,
            )
        ),
    )


def test_all_required_and_expected_constraints_can_pass() -> None:
    requirement_set = (
        _requirement_set()
    )

    scopes = (
        RequirementScope.MSC,
    )

    result = evaluate_university_fit(
        topic=(
            "Explainable machine learning "
            "for credit risk"
        ),
        requirement_set=(
            requirement_set
        ),
        active_scopes=scopes,
        assessments=(
            _positive_assessments(
                requirement_set,
                scopes=scopes,
            )
        ),
    )

    assert (
            result.status
            == UniversityFitStatus.PASS
    )

    assert (
            result.blocking_requirement_ids
            == ()
    )

    assert (
            result.unknown_required_requirement_ids
            == ()
    )

    assert (
            result.concern_requirement_ids
            == ()
    )


def test_unsatisfied_required_constraint_fails() -> None:
    requirement_set = (
        _requirement_set()
    )

    scopes = (
        RequirementScope.MSC,
    )

    assessments = list(
        _positive_assessments(
            requirement_set,
            scopes=scopes,
        )
    )

    assessments = [
        (
            _assessment(
                item.requirement_id,
                (
                    RequirementAssessmentStatus
                    .UNSATISFIED
                ),
            )
            if (
                    item.requirement_id
                    == "systematic-research"
            )
            else item
        )
        for item in assessments
    ]

    result = evaluate_university_fit(
        topic="Example topic",
        requirement_set=(
            requirement_set
        ),
        active_scopes=scopes,
        assessments=tuple(
            assessments
        ),
    )

    assert (
            result.status
            == UniversityFitStatus.FAIL
    )

    assert (
            "systematic-research"
            in result.blocking_requirement_ids
    )


def test_missing_required_constraint_is_unknown() -> None:
    requirement_set = (
        _requirement_set()
    )

    result = evaluate_university_fit(
        topic="Example topic",
        requirement_set=(
            requirement_set
        ),
        active_scopes=(
            RequirementScope.MSC,
        ),
    )

    assert (
            result.status
            == UniversityFitStatus.UNKNOWN
    )

    assert (
            "systematic-research"
            in (
                result
                .unknown_required_requirement_ids
            )
    )


def test_unsatisfied_expected_constraint_creates_concern() -> None:
    requirement_set = (
        _requirement_set()
    )

    scopes = (
        RequirementScope.MSC,
    )

    assessments = list(
        _positive_assessments(
            requirement_set,
            scopes=scopes,
        )
    )

    assessments = [
        (
            _assessment(
                item.requirement_id,
                (
                    RequirementAssessmentStatus
                    .UNSATISFIED
                ),
            )
            if (
                    item.requirement_id
                    == "experimental-software-work"
            )
            else item
        )
        for item in assessments
    ]

    result = evaluate_university_fit(
        topic="Example topic",
        requirement_set=(
            requirement_set
        ),
        active_scopes=scopes,
        assessments=tuple(
            assessments
        ),
    )

    assert (
            result.status
            == UniversityFitStatus.CONCERNS
    )

    assert (
            result.blocking_requirement_ids
            == ()
    )

    assert (
            result.unknown_required_requirement_ids
            == ()
    )

    assert (
            "experimental-software-work"
            in result.concern_requirement_ids
    )


def test_eit_scope_activates_eit_prototype_requirement() -> None:
    requirement_set = (
        _requirement_set()
    )

    msc_scopes = (
        RequirementScope.MSC,
    )

    msc_result = evaluate_university_fit(
        topic="Example topic",
        requirement_set=(
            requirement_set
        ),
        active_scopes=msc_scopes,
        assessments=(
            _positive_assessments(
                requirement_set,
                scopes=msc_scopes,
            )
        ),
    )

    assert (
            "eit-prototype"
            not in {
                item.requirement.id
                for item
                in msc_result.requirements
            }
    )

    eit_scopes = (
        RequirementScope.MSC,
        RequirementScope.EIT,
    )

    eit_result = evaluate_university_fit(
        topic="Example topic",
        requirement_set=(
            requirement_set
        ),
        active_scopes=eit_scopes,
        assessments=(
            _positive_assessments(
                requirement_set,
                scopes=(
                    RequirementScope.MSC,
                ),
            )
        ),
    )

    assert (
            eit_result.status
            == UniversityFitStatus.UNKNOWN
    )

    assert (
            "eit-prototype"
            in (
                eit_result
                .unknown_required_requirement_ids
            )
    )


def test_rejects_assessment_for_inapplicable_requirement() -> None:
    requirement_set = (
        _requirement_set()
    )

    with pytest.raises(
            ValueError,
            match="not applicable",
    ):
        evaluate_university_fit(
            topic="Example topic",
            requirement_set=(
                requirement_set
            ),
            active_scopes=(
                RequirementScope.MSC,
            ),
            assessments=(
                _assessment(
                    "eit-prototype",
                    (
                        RequirementAssessmentStatus
                        .SATISFIED
                    ),
                ),
            ),
        )


def test_rejects_duplicate_assessment_ids() -> None:
    requirement_set = (
        _requirement_set()
    )

    assessment = _assessment(
        "systematic-research",
        (
            RequirementAssessmentStatus
            .SATISFIED
        ),
    )

    with pytest.raises(
            ValueError,
            match="must be unique",
    ):
        evaluate_university_fit(
            topic="Example topic",
            requirement_set=(
                requirement_set
            ),
            active_scopes=(
                RequirementScope.MSC,
            ),
            assessments=(
                assessment,
                assessment,
            ),
        )


def test_report_remains_unknown_when_other_dimensions_are_unassessed() -> None:
    report = (
        build_topic_researchability_report(
            university_fit=(
                _passing_university_fit()
            ),
        )
    )

    assert (
            report.status
            == TopicResearchabilityStatus.UNKNOWN
    )

    assert (
            ResearchabilityDimension
            .UNIVERSITY_FIT
            not in report.unknown_dimensions
    )

    assert (
            ResearchabilityDimension.LITERATURE
            in report.unknown_dimensions
    )

    assert (
            ResearchabilityDimension.DATASET
            in report.unknown_dimensions
    )


def test_failed_university_fit_blocks_topic() -> None:
    requirement_set = (
        _requirement_set()
    )

    university_fit = (
        evaluate_university_fit(
            topic="Literature review only",
            requirement_set=(
                requirement_set
            ),
            active_scopes=(
                RequirementScope.MSC,
            ),
            assessments=(
                _assessment(
                    "systematic-research",
                    (
                        RequirementAssessmentStatus
                        .UNSATISFIED
                    ),
                ),
            ),
        )
    )

    report = (
        build_topic_researchability_report(
            university_fit=(
                university_fit
            ),
        )
    )

    assert (
            report.status
            == (
                TopicResearchabilityStatus
                .NOT_RESEARCHABLE
            )
    )

    assert (
            ResearchabilityDimension
            .UNIVERSITY_FIT
            in report.blocking_dimensions
    )


def test_report_becomes_researchable_when_every_dimension_passes() -> None:
    university_fit = (
        _passing_university_fit()
    )

    assessments = tuple(
        ResearchabilityDimensionAssessment(
            dimension=dimension,
            status=(
                ResearchabilityDimensionStatus
                .PASS
            ),
            rationale=(
                f"{dimension.value} passed."
            ),
        )
        for dimension
        in ResearchabilityDimension
        if (
                dimension
                != (
                    ResearchabilityDimension
                    .UNIVERSITY_FIT
                )
        )
    )

    report = (
        build_topic_researchability_report(
            university_fit=(
                university_fit
            ),
            assessments=assessments,
        )
    )

    assert (
            report.status
            == (
                TopicResearchabilityStatus
                .RESEARCHABLE
            )
    )

    assert (
            report.blocking_dimensions
            == ()
    )

    assert (
            report.unknown_dimensions
            == ()
    )

    assert (
            report.concern_dimensions
            == ()
    )


def test_concern_requires_human_review_when_everything_else_is_known() -> None:
    university_fit = (
        _passing_university_fit()
    )

    assessments = tuple(
        ResearchabilityDimensionAssessment(
            dimension=dimension,
            status=(
                (
                    ResearchabilityDimensionStatus
                    .CONCERNS
                )
                if (
                        dimension
                        == (
                            ResearchabilityDimension
                            .CONTRIBUTION
                        )
                )
                else (
                    ResearchabilityDimensionStatus
                    .PASS
                )
            ),
            rationale=(
                f"Assessment for "
                f"{dimension.value}."
            ),
        )
        for dimension
        in ResearchabilityDimension
        if (
                dimension
                != (
                    ResearchabilityDimension
                    .UNIVERSITY_FIT
                )
        )
    )

    report = (
        build_topic_researchability_report(
            university_fit=(
                university_fit
            ),
            assessments=assessments,
        )
    )

    assert (
            report.status
            == (
                TopicResearchabilityStatus
                .HUMAN_REVIEW_REQUIRED
            )
    )

    assert report.concern_dimensions == (
        ResearchabilityDimension.CONTRIBUTION,
    )


def test_report_rejects_duplicate_dimensions() -> None:
    university_fit = (
        _passing_university_fit()
    )

    assessment = (
        ResearchabilityDimensionAssessment(
            dimension=(
                ResearchabilityDimension
                .LITERATURE
            ),
            status=(
                ResearchabilityDimensionStatus
                .PASS
            ),
            rationale="Literature is sufficient.",
        )
    )

    with pytest.raises(
            ValueError,
            match="must be unique",
    ):
        build_topic_researchability_report(
            university_fit=(
                university_fit
            ),
            assessments=(
                assessment,
                assessment,
            ),
        )


def test_report_rejects_manual_university_fit_dimension() -> None:
    university_fit = (
        _passing_university_fit()
    )

    with pytest.raises(
            ValueError,
            match="must not be supplied",
    ):
        build_topic_researchability_report(
            university_fit=(
                university_fit
            ),
            assessments=(
                ResearchabilityDimensionAssessment(
                    dimension=(
                        ResearchabilityDimension
                        .UNIVERSITY_FIT
                    ),
                    status=(
                        ResearchabilityDimensionStatus
                        .PASS
                    ),
                    rationale=(
                        "Attempted override."
                    ),
                ),
            ),
        )