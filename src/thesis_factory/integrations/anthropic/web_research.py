from anthropic import Anthropic

from thesis_factory.domain.web_research import (
    WebCitation,
    WebResearchPacket,
)
from thesis_factory.integrations.anthropic.client_factory import (
    create_anthropic_client,
)


class WebResearchError(
    RuntimeError
):
    pass


class AnthropicWebResearcher:
    def __init__(
        self,
        *,
        model: str,
        client: Anthropic | None = None,
        max_tokens: int = 3000,
        max_search_uses: int = 4,
        max_continuations: int = 1,
    ) -> None:
        if max_tokens < 1:
            raise ValueError(
                "max_tokens must be positive"
            )

        if max_search_uses < 1:
            raise ValueError(
                "max_search_uses must be positive"
            )

        if max_continuations < 0:
            raise ValueError(
                "max_continuations must not be negative"
            )

        self._model = model
        self._client = (
            client
            or create_anthropic_client()
        )
        self._max_tokens = max_tokens
        self._max_search_uses = (
            max_search_uses
        )
        self._max_continuations = (
            max_continuations
        )

    def research(
        self,
        *,
        approved_topic: str,
        objective: str,
    ) -> WebResearchPacket:
        normalized_topic = " ".join(
            approved_topic.split()
        )
        normalized_objective = " ".join(
            objective.split()
        )

        if not normalized_topic:
            raise ValueError(
                "approved_topic must not be empty"
            )

        if not normalized_objective:
            raise ValueError(
                "objective must not be empty"
            )

        prompt = (
            "Research the following objective for an "
            "MSc thesis proposal.\n\n"
            "<approved_topic>"
            f"{normalized_topic}"
            "</approved_topic>\n"
            "<research_objective>"
            f"{normalized_objective}"
            "</research_objective>\n\n"
            "Search the web as needed. Prefer primary, "
            "authoritative, peer-reviewed, or official "
            "sources over summaries. Distinguish source "
            "facts from your interpretation. Do not choose "
            "a dataset, method, metric, baseline, research "
            "gap, or contribution merely because it seems "
            "plausible. Surface competing candidates and "
            "limitations when evidence is mixed. Cite every "
            "externally checkable factual statement. "
            "This response is discovery material only; "
            "nothing in it will be treated as verified "
            "evidence until separately checked."
        )

        tools = [
            {
                "type": (
                    "web_search_20250305"
                ),
                "name": "web_search",
                "max_uses": (
                    self._max_search_uses
                ),
            }
        ]

        messages: list[
            dict[str, object]
        ] = [
            {
                "role": "user",
                "content": prompt,
            }
        ]

        text_parts: list[str] = []
        raw_citations: list[
            tuple[
                str,
                str | None,
                str,
            ]
        ] = []

        response = None

        for attempt in range(
            self._max_continuations + 1
        ):
            response = (
                self._client.messages.create(
                    model=self._model,
                    max_tokens=self._max_tokens,
                    tools=tools,
                    messages=messages,
                )
            )

            response_text, response_citations = (
                _extract_response_material(
                    response.content
                )
            )

            text_parts.extend(
                response_text
            )
            raw_citations.extend(
                response_citations
            )

            if (
                response.stop_reason
                != "pause_turn"
            ):
                break

            if (
                attempt
                >= self._max_continuations
            ):
                raise WebResearchError(
                    "web research exceeded "
                    "continuation budget"
                )

            messages.append(
                {
                    "role": "assistant",
                    "content": response.content,
                }
            )

        if response is None:
            raise WebResearchError(
                "web research returned no response"
            )

        narrative = " ".join(
            part.strip()
            for part in text_parts
            if part.strip()
        )

        if not narrative:
            raise WebResearchError(
                "web research returned no narrative"
            )

        unique_raw_citations = (
            _deduplicate_citations(
                raw_citations
            )
        )

        if not unique_raw_citations:
            raise WebResearchError(
                "web research returned "
                "no source citations"
            )

        citations = tuple(
            WebCitation(
                citation_id=f"c{index}",
                url=url,
                title=title,
                cited_text=cited_text,
            )
            for index, (
                url,
                title,
                cited_text,
            )
            in enumerate(
                unique_raw_citations,
                start=1,
            )
        )

        return WebResearchPacket(
            objective=normalized_objective,
            narrative=narrative,
            citations=citations,
        )


def _extract_response_material(
    content,
) -> tuple[
    list[str],
    list[
        tuple[
            str,
            str | None,
            str,
        ]
    ],
]:
    text_parts: list[str] = []
    citations: list[
        tuple[
            str,
            str | None,
            str,
        ]
    ] = []

    for block in content:
        if (
            getattr(
                block,
                "type",
                None,
            )
            != "text"
        ):
            continue

        text = getattr(
            block,
            "text",
            None,
        )

        if isinstance(text, str):
            text_parts.append(
                text
            )

        for citation in (
            getattr(
                block,
                "citations",
                None,
            )
            or ()
        ):
            if (
                getattr(
                    citation,
                    "type",
                    None,
                )
                != (
                    "web_search_result_location"
                )
            ):
                continue

            url = getattr(
                citation,
                "url",
                None,
            )
            cited_text = getattr(
                citation,
                "cited_text",
                None,
            )

            if (
                not isinstance(url, str)
                or not url.strip()
                or not isinstance(
                    cited_text,
                    str,
                )
                or not cited_text.strip()
            ):
                continue

            title = getattr(
                citation,
                "title",
                None,
            )

            citations.append(
                (
                    url,
                    (
                        title
                        if isinstance(
                            title,
                            str,
                        )
                        else None
                    ),
                    cited_text,
                )
            )

    return (
        text_parts,
        citations,
    )


def _deduplicate_citations(
    citations: list[
        tuple[
            str,
            str | None,
            str,
        ]
    ],
) -> tuple[
    tuple[
        str,
        str | None,
        str,
    ],
    ...,
]:
    seen: set[
        tuple[str, str]
    ] = set()

    result: list[
        tuple[
            str,
            str | None,
            str,
        ]
    ] = []

    for (
        url,
        title,
        cited_text,
    ) in citations:
        identity = (
            url,
            cited_text,
        )

        if identity in seen:
            continue

        seen.add(
            identity
        )
        result.append(
            (
                url,
                title,
                cited_text,
            )
        )

    return tuple(
        result
    )
