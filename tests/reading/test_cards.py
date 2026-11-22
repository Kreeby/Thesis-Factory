from thesis_factory.domain.document import (
    DocumentSectionKind,
    NormalizedDocument,
    NormalizedParagraph,
    NormalizedSection,
)
from thesis_factory.reading.cards import ChunkClaims, build_card

SHA = "a" * 64


class FakeReasoner:
    def __init__(self, replies):
        self.replies = list(replies)

    def generate(self, *, system, prompt, output_model):
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return output_model.model_validate(reply)


def _document() -> NormalizedDocument:
    texts = ["SHAP was applied to a gradient boosting model on 10,000 loans.", "Explanations were unstable across seeds."]
    return NormalizedDocument(
        artifact_sha256=SHA,
        source_provider="openalex",
        source_provider_id="https://openalex.org/W1",
        sections=(
            NormalizedSection(
                ordinal=1,
                kind=DocumentSectionKind.BODY,
                path=("Results",),
                paragraphs=tuple(NormalizedParagraph(ordinal=i, text=t) for i, t in enumerate(texts, 1)),
            ),
        ),
    )


def test_only_exact_quotes_survive_and_get_addresses() -> None:
    claims = [
        {"kind": "XAI_METHOD", "statement": "Uses SHAP.", "paragraph": 1, "quote": "SHAP was applied to a gradient boosting model"},
        {"kind": "FINDING", "statement": "Unstable.", "paragraph": 2, "quote": "Explanations were very unstable"},
        {"kind": "DATASET", "statement": "10k loans.", "paragraph": 9, "quote": "a gradient boosting model on 10,000 loans"},
    ]
    card = build_card(FakeReasoner([{"claims": claims}]), _document(), paper_id="p", artifact_sha256=SHA)

    assert card["stats"] == {"proposed": 3, "verified": 1, "rejected": 2, "failed_chunks": 0}
    address = card["claims"][0]["address"]
    assert (address["paragraph_ordinal"], address["start_char"], address["end_char"]) == (1, 0, 45)
    assert {r["reason"] for r in card["rejected"]} == {"quote not an exact substring", "paragraph outside chunk"}


def test_echoed_prompt_question_is_rejected() -> None:
    # Regression: qwen3 sometimes returns the prompt's question as the statement (7/271 in the Windows trial).
    claims = [{"kind": "OPEN_QUESTION", "statement": "What open questions do the authors suggest? ",
               "paragraph": 2, "quote": "Explanations were unstable"}]
    card = build_card(FakeReasoner([{"claims": claims}]), _document(), paper_id="p", artifact_sha256=SHA)

    assert card["stats"]["verified"] == 0
    assert card["rejected"][0]["reason"] == "statement is a question"


def test_failed_chunk_is_counted_not_fatal() -> None:
    card = build_card(FakeReasoner([RuntimeError("truncated"), {"claims": []}]), _document(), paper_id="p",
                      artifact_sha256=SHA, max_chars=70)

    assert card["stats"]["failed_chunks"] == 1
    assert ChunkClaims.model_json_schema()["properties"]["claims"]["maxItems"] == 12
