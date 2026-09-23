import pytest
from pydantic import ValidationError

from thesis_factory.research.literature_search_planning import (
    LiteratureSearchPlan,
    LiteratureSearchPlanner,
    LiteratureSearchTask,
)


class FakeReasoner:
    def __init__(
            self,
            result: LiteratureSearchPlan,
    ) -> None:
        self.result = result
        self.calls: list[dict[str, object]] = []

    def generate(
            self,
            *,
            system: str,
            prompt: str,
            output_model: type[LiteratureSearchPlan],
    ) -> LiteratureSearchPlan:
        self.calls.append(
            {
                "system": system,
                "prompt": prompt,
                "output_model": output_model,
            }
        )

        return self.result


def test_planner_generates_bounded_search_plan() -> None:
    plan = LiteratureSearchPlan(
        tasks=(
            LiteratureSearchTask(
                objective=(
                    "Find empirical studies of machine learning "
                    "for consumer credit default prediction."
                ),
                query=(
                    "consumer credit default "
                    "machine learning"
                ),
            ),
            LiteratureSearchTask(
                objective=(
                    "Find work on explainable machine learning "
                    "for credit-risk decisions."
                ),
                query=(
                    "explainable machine learning "
                    "credit risk"
                ),
            ),
        )
    )

    reasoner = FakeReasoner(plan)
    planner = LiteratureSearchPlanner(reasoner)

    result = planner.plan(
        topic="machine learning credit risk"
    )

    assert result == plan
    assert len(result.tasks) == 2

    assert len(reasoner.calls) == 1

    call = reasoner.calls[0]

    assert call["output_model"] is LiteratureSearchPlan
    assert (
            "<candidate_topic>"
            "machine learning credit risk"
            "</candidate_topic>"
            in call["prompt"]
    )


def test_empty_topic_does_not_call_reasoner() -> None:
    reasoner = FakeReasoner(
        LiteratureSearchPlan(
            tasks=(
                LiteratureSearchTask(
                    objective="Example objective",
                    query="example query",
                ),
            )
        )
    )

    planner = LiteratureSearchPlanner(reasoner)

    with pytest.raises(
            ValueError,
            match="topic must not be empty",
    ):
        planner.plan(topic="   ")

    assert reasoner.calls == []


def test_plan_rejects_more_than_five_tasks() -> None:
    tasks = tuple(
        LiteratureSearchTask(
            objective=f"Objective {index}",
            query=f"query {index}",
        )
        for index in range(6)
    )

    with pytest.raises(ValidationError):
        LiteratureSearchPlan(
            tasks=tasks
        )


def test_plan_rejects_duplicate_queries() -> None:
    with pytest.raises(
            ValidationError,
            match="search queries must be unique",
    ):
        LiteratureSearchPlan(
            tasks=(
                LiteratureSearchTask(
                    objective="First angle",
                    query="credit risk machine learning",
                ),
                LiteratureSearchTask(
                    objective="Second angle",
                    query="Credit Risk Machine Learning",
                ),
            )
        )


def test_task_rejects_blank_query() -> None:
    with pytest.raises(ValidationError):
        LiteratureSearchTask(
            objective="Find relevant literature",
            query="   ",
        )