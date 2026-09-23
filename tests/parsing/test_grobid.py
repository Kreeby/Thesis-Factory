import hashlib

import pytest

from thesis_factory.artifacts.fetching import (
    ArtifactFormat,
    FetchedArtifact,
)
from thesis_factory.domain.document import (
    DocumentSectionKind,
    SectionHeadingRole,
)
from thesis_factory.domain.source_text import (
    SourceTextLocation,
    SourceTextLocationKind,
)
from thesis_factory.parsing.grobid import (
    GrobidTeiParser,
)


def _artifact(
        content: bytes,
        *,
        artifact_format: ArtifactFormat = (
                ArtifactFormat.GROBID_XML
        ),
) -> FetchedArtifact:
    location_kind = (
        SourceTextLocationKind
        .OPENALEX_GROBID_XML
        if (
                artifact_format
                == ArtifactFormat.GROBID_XML
        )
        else (
            SourceTextLocationKind
            .OPENALEX_PDF
        )
    )

    location = SourceTextLocation(
        kind=location_kind,
        url=(
            "https://example.org/artifact"
        ),
        provider="openalex",
        provider_work_id=(
            "https://openalex.org/W123"
        ),
        is_open_access=True,
    )

    return FetchedArtifact(
        location=location,
        format=artifact_format,
        content=content,
        sha256=hashlib.sha256(
            content
        ).hexdigest(),
        content_length=len(
            content
        ),
        response_content_type=None,
    )


def test_parses_standard_namespaced_grobid() -> None:
    content = b"""
    <TEI xmlns="http://www.tei-c.org/ns/1.0">
        <teiHeader>
            <fileDesc>
                <titleStmt>
                    <title
                        level="a"
                        type="main"
                    >
                        Example Credit Risk Paper
                    </title>
                </titleStmt>
            </fileDesc>

            <profileDesc>
                <abstract>
                    <p>
                        This paper studies
                        machine learning
                        for credit risk.
                    </p>
                </abstract>
            </profileDesc>
        </teiHeader>

        <text>
            <body>
                <div>
                    <head>
                        1 Introduction
                    </head>

                    <p>
                        Credit risk modelling is
                        an important problem.
                    </p>

                    <div>
                        <head>
                            1.1 Background
                        </head>

                        <p>
                            Earlier approaches used
                            statistical models.
                        </p>
                    </div>
                </div>

                <div>
                    <head>
                        2 Methodology
                    </head>

                    <p xml:id="p-method">
                        We compare
                        <ref>gradient boosting</ref>
                        with logistic regression.
                    </p>
                </div>
            </body>
        </text>
    </TEI>
    """

    document = (
        GrobidTeiParser()
        .parse(
            _artifact(content)
        )
    )

    assert (
            document.normalization_version
            == "grobid-tei-v1"
    )

    assert (
            document.title
            == "Example Credit Risk Paper"
    )

    assert len(
        document.sections
    ) == 4

    abstract = (
        document.sections[0]
    )

    assert (
            abstract.kind
            == DocumentSectionKind.ABSTRACT
    )

    assert abstract.path == (
        "Abstract",
    )

    assert (
            abstract.paragraphs[0]
            .ordinal
            == 1
    )

    introduction = (
        document.sections[1]
    )

    assert introduction.path == (
        "1 Introduction",
    )

    background = (
        document.sections[2]
    )

    assert background.path == (
        "1 Introduction",
        "1.1 Background",
    )

    methodology = (
        document.sections[3]
    )

    assert methodology.path == (
        "2 Methodology",
    )

    paragraph = (
        methodology.paragraphs[0]
    )

    assert (
            paragraph.ordinal
            == 4
    )

    assert paragraph.text == (
        "We compare gradient boosting "
        "with logistic regression."
    )

    assert (
            paragraph.source_xml_id
            == "p-method"
    )


def test_parses_legacy_openalex_grobid_shape() -> None:
    content = b"""
    <html>
        <body>
            <tei>
                <text>
                    <div>
                        <head>
                            Introduction
                        </head>

                        <p>
                            Legacy OpenAlex
                            paragraph.
                        </p>
                    </div>

                    <div>
                        <head>
                            Results
                        </head>

                        <p>
                            Legacy result.
                        </p>
                    </div>
                </text>
            </tei>
        </body>
    </html>
    """

    document = (
        GrobidTeiParser()
        .parse(
            _artifact(content)
        )
    )

    assert len(
        document.sections
    ) == 2

    assert (
            document.sections[0].path
            == ("Introduction",)
    )

    assert (
            document.sections[0]
            .paragraphs[0]
            .text
            == "Legacy OpenAlex paragraph."
    )

    assert (
            document.sections[1].path
            == ("Results",)
    )


def test_parses_direct_body_paragraphs() -> None:
    content = b"""
    <TEI>
        <text>
            <body>
                <head>Introduction</head>

                <p>
                    First paragraph.
                </p>

                <p>
                    Second paragraph.
                </p>
            </body>
        </text>
    </TEI>
    """

    document = (
        GrobidTeiParser()
        .parse(
            _artifact(content)
        )
    )

    assert len(
        document.sections
    ) == 1

    section = (
        document.sections[0]
    )

    assert section.path == (
        "Introduction",
    )

    assert [
               paragraph.text
               for paragraph
               in section.paragraphs
           ] == [
               "First paragraph.",
               "Second paragraph.",
           ]


def test_rejects_non_grobid_artifact() -> None:
    content = (
        b"%PDF-1.7\n"
        b"example"
    )

    with pytest.raises(
            ValueError,
            match=(
                    "artifact must be "
                    "GROBID XML"
            ),
    ):
        (
            GrobidTeiParser()
            .parse(
                _artifact(
                    content,
                    artifact_format=(
                        ArtifactFormat.PDF
                    ),
                )
            )
        )


def test_rejects_invalid_or_empty_grobid() -> None:
    with pytest.raises(
            ValueError,
            match="invalid GROBID XML",
    ):
        (
            GrobidTeiParser()
            .parse(
                _artifact(
                    b"<TEI><broken>"
                )
            )
        )

    with pytest.raises(
            ValueError,
            match=(
                    "contains no usable paragraphs"
            ),
    ):
        (
            GrobidTeiParser()
            .parse(
                _artifact(
                    b"<TEI><text><body /></text></TEI>"
                )
            )
        )

def test_identifies_table_heading_role() -> None:
    content = b"""
    <TEI>
        <text>
            <body>
                <div>
                    <head>Table 2: Model performance</head>

                    <p>
                        Notes: Own calculation.
                    </p>

                    <p>
                        We then compare the models
                        using another dataset.
                    </p>
                </div>
            </body>
        </text>
    </TEI>
    """

    document = (
        GrobidTeiParser()
        .parse(
            _artifact(content)
        )
    )

    section = (
        document.sections[0]
    )

    assert (
            section.kind
            == DocumentSectionKind.BODY
    )

    assert (
            section.heading_role
            == SectionHeadingRole.TABLE
    )

    assert len(
        section.paragraphs
    ) == 2


def test_identifies_figure_heading_role() -> None:
    content = b"""
    <TEI>
        <text>
            <body>
                <div>
                    <head>
                        Figure 1: Decision tree
                    </head>

                    <p>
                        Notes: Example figure.
                    </p>
                </div>
            </body>
        </text>
    </TEI>
    """

    document = (
        GrobidTeiParser()
        .parse(
            _artifact(content)
        )
    )

    section = (
        document.sections[0]
    )

    assert (
            section.kind
            == DocumentSectionKind.BODY
    )

    assert (
            section.heading_role
            == SectionHeadingRole.FIGURE
    )
