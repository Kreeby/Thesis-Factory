from types import SimpleNamespace

import pytest

from thesis_factory.integrations.anthropic.web_research import (
    AnthropicWebResearcher,
    WebResearchError,
)


def _response(
    *,
    stop_reason="end_turn",
    text="Research result.",
    url="https://example.org/source",
    cited_text="Source evidence.",
):
    citation = SimpleNamespace(
        type="web_search_result_location",
        url=url,
        title="Example Source",
        cited_text=cited_text,
    )

    block = SimpleNamespace(
        type="text",
        text=text,
        citations=[citation],
    )

    return SimpleNamespace(
        stop_reason=stop_reason,
        content=[block],
    )


class FakeMessages:
    def __init__(self, responses):
        self.responses = list(
            responses
        )
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(
            kwargs
        )
        return self.responses.pop(0)


class FakeClient:
    def __init__(self, responses):
        self.messages = FakeMessages(
            responses
        )


def test_web_research_returns_provider_citations() -> None:
    client = FakeClient(
        [_response()]
    )

    researcher = AnthropicWebResearcher(
        model="test-model",
        client=client,
        max_search_uses=3,
    )

    packet = researcher.research(
        approved_topic="Approved topic",
        objective="Find candidate datasets.",
    )

    assert (
        packet.objective
        == "Find candidate datasets."
    )
    assert len(packet.citations) == 1
    assert (
        packet.citations[0].citation_id
        == "c1"
    )
    assert (
        str(packet.citations[0].url)
        == "https://example.org/source"
    )

    call = client.messages.calls[0]

    assert call["tools"] == [
        {
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 3,
        }
    ]


def test_web_research_assigns_deterministic_ids() -> None:
    client = FakeClient(
        [
            SimpleNamespace(
                stop_reason="end_turn",
                content=[
                    SimpleNamespace(
                        type="text",
                        text="Research.",
                        citations=[
                            SimpleNamespace(
                                type=(
                                    "web_search_result_location"
                                ),
                                url="https://example.org/a",
                                title="A",
                                cited_text="Evidence A.",
                            ),
                            SimpleNamespace(
                                type=(
                                    "web_search_result_location"
                                ),
                                url="https://example.org/b",
                                title="B",
                                cited_text="Evidence B.",
                            ),
                        ],
                    )
                ],
            )
        ]
    )

    packet = AnthropicWebResearcher(
        model="test-model",
        client=client,
    ).research(
        approved_topic="Topic",
        objective="Objective",
    )

    assert [
        citation.citation_id
        for citation in packet.citations
    ] == ["c1", "c2"]


def test_web_research_handles_bounded_pause_turn() -> None:
    client = FakeClient(
        [
            _response(
                stop_reason="pause_turn",
                text="Part one.",
            ),
            _response(
                text="Part two.",
            ),
        ]
    )

    researcher = AnthropicWebResearcher(
        model="test-model",
        client=client,
        max_continuations=1,
    )

    packet = researcher.research(
        approved_topic="Topic",
        objective="Objective",
    )

    assert (
        "Part one."
        in packet.narrative
    )
    assert (
        "Part two."
        in packet.narrative
    )
    assert (
        len(client.messages.calls)
        == 2
    )


def test_web_research_rejects_missing_citations() -> None:
    response = SimpleNamespace(
        stop_reason="end_turn",
        content=[
            SimpleNamespace(
                type="text",
                text="Uncited result.",
                citations=[],
            )
        ],
    )

    researcher = AnthropicWebResearcher(
        model="test-model",
        client=FakeClient(
            [response]
        ),
    )

    with pytest.raises(
        WebResearchError,
        match="no source citations",
    ):
        researcher.research(
            approved_topic="Topic",
            objective="Objective",
        )


def test_web_research_enforces_continuation_budget() -> None:
    researcher = AnthropicWebResearcher(
        model="test-model",
        client=FakeClient(
            [
                _response(
                    stop_reason="pause_turn",
                )
            ]
        ),
        max_continuations=0,
    )

    with pytest.raises(
        WebResearchError,
        match="continuation budget",
    ):
        researcher.research(
            approved_topic="Topic",
            objective="Objective",
        )
