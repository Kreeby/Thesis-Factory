from itertools import count
from xml.etree.ElementTree import (
    Element,
    ParseError,
)

from defusedxml import ElementTree
from defusedxml.common import DefusedXmlException

from thesis_factory.artifacts.fetching import (
    ArtifactFormat,
    FetchedArtifact,
)
from thesis_factory.domain.document import (
    DocumentSectionKind,
    NormalizedDocument,
    NormalizedParagraph,
    NormalizedSection,
    SectionHeadingRole,
)


class GrobidTeiParser:
    def parse(
            self,
            artifact: FetchedArtifact,
    ) -> NormalizedDocument:
        if (
                artifact.format
                != ArtifactFormat.GROBID_XML
        ):
            raise ValueError(
                "artifact must be GROBID XML"
            )

        try:
            root = ElementTree.fromstring(
                artifact.content
            )
        except (
                ParseError,
                DefusedXmlException,
        ) as error:
            raise ValueError(
                "invalid GROBID XML"
            ) from error

        paragraph_counter = count(1)
        section_counter = count(1)

        title = _extract_title(
            root
        )

        sections: list[
            NormalizedSection
        ] = []

        abstract = _find_abstract(
            root
        )

        if abstract is not None:
            abstract_paragraphs = (
                _extract_descendant_paragraphs(
                    abstract,
                    paragraph_counter,
                )
            )

            if abstract_paragraphs:
                sections.append(
                    NormalizedSection(
                        ordinal=next(
                            section_counter
                        ),
                        kind=(
                            DocumentSectionKind
                            .ABSTRACT
                        ),
                        path=(
                            "Abstract",
                        ),
                        paragraphs=(
                            abstract_paragraphs
                        ),
                    )
                )

        sections.extend(
            _extract_body_sections(
                root,
                paragraph_counter=(
                    paragraph_counter
                ),
                section_counter=(
                    section_counter
                ),
            )
        )

        if not sections:
            raise ValueError(
                "GROBID document contains no usable paragraphs"
            )

        return NormalizedDocument(
            artifact_sha256=(
                artifact.sha256
            ),
            source_provider=(
                artifact.location.provider
            ),
            source_provider_id=(
                artifact.location
                .provider_work_id
            ),
            title=title,
            sections=tuple(
                sections
            ),
        )


def _extract_title(
        root: Element,
) -> str | None:
    title_stmt = (
        _find_first_descendant(
            root,
            "titlestmt",
        )
    )

    if title_stmt is None:
        return None

    fallback: str | None = None

    for element in title_stmt.iter():
        if (
                _local_name(element)
                != "title"
        ):
            continue

        text = _element_text(
            element
        )

        if text is None:
            continue

        if fallback is None:
            fallback = text

        title_type = (
            element.attrib.get("type")
        )

        if (
                isinstance(title_type, str)
                and title_type.casefold()
                == "main"
        ):
            return text

    return fallback


def _find_abstract(
        root: Element,
) -> Element | None:
    for element in root.iter():
        name = _local_name(
            element
        )

        if name == "abstract":
            return element

        if name != "div":
            continue

        div_type = (
            element.attrib.get("type")
        )

        if (
                isinstance(div_type, str)
                and div_type.casefold()
                == "abstract"
        ):
            return element

    return None


def _extract_body_sections(
        root: Element,
        *,
        paragraph_counter,
        section_counter,
) -> list[NormalizedSection]:
    text = _find_first_descendant(
        root,
        "text",
    )

    if text is None:
        return []

    # Standard GROBID:
    #
    # <TEI>
    #   <text>
    #     <body>
    #       <div>...</div>
    #
    # Older OpenAlex GROBID:
    #
    # <html>
    #   <body>
    #     <tei>
    #       <text>
    #         <div>...</div>
    #
    # In the older representation there is no TEI
    # <body> inside <text>.

    body = _find_direct_child(
        text,
        "body",
    )

    container = (
        body
        if body is not None
        else text
    )

    return _extract_root_sections(
        container,
        paragraph_counter=(
            paragraph_counter
        ),
        section_counter=(
            section_counter
        ),
    )


def _extract_root_sections(
        container: Element,
        *,
        paragraph_counter,
        section_counter,
) -> list[NormalizedSection]:
    result: list[
        NormalizedSection
    ] = []

    current_heading: str | None = None
    pending_paragraphs: list[
        NormalizedParagraph
    ] = []

    def flush_pending() -> None:
        nonlocal pending_paragraphs

        if not pending_paragraphs:
            return

        path = (
            (current_heading,)
            if current_heading
            else ("Body",)
        )

        result.append(
            NormalizedSection(
                ordinal=next(
                    section_counter
                ),
                kind=(
                    DocumentSectionKind
                    .BODY
                ),
                path=path,
                paragraphs=tuple(
                    pending_paragraphs
                ),
            )
        )

        pending_paragraphs = []

    for child in container:
        name = _local_name(
            child
        )

        if name == "head":
            flush_pending()

            current_heading = (
                _element_text(
                    child
                )
            )

            continue

        if name == "p":
            text = _element_text(
                child
            )

            if text is not None:
                pending_paragraphs.append(
                    _paragraph_from_element(
                        child,
                        paragraph_counter,
                    )
                )

            continue

        if name == "div":
            flush_pending()

            result.extend(
                _extract_div_sections(
                    child,
                    parent_path=(),
                    paragraph_counter=(
                        paragraph_counter
                    ),
                    section_counter=(
                        section_counter
                    ),
                )
            )

    flush_pending()

    return result


def _extract_div_sections(
        div: Element,
        *,
        parent_path: tuple[str, ...],
        paragraph_counter,
        section_counter,
) -> list[NormalizedSection]:
    result: list[
        NormalizedSection
    ] = []

    heading = _direct_heading(
        div
    )

    if heading is not None:
        current_path = (
            *parent_path,
            heading,
        )
    elif parent_path:
        current_path = parent_path
    else:
        current_path = (
            "Body",
        )

    direct_paragraphs: list[
        NormalizedParagraph
    ] = []

    for child in div:
        if (
                _local_name(child)
                != "p"
        ):
            continue

        text = _element_text(
            child
        )

        if text is None:
            continue

        direct_paragraphs.append(
            _paragraph_from_element(
                child,
                paragraph_counter,
            )
        )

    if direct_paragraphs:
        result.append(
            NormalizedSection(
                ordinal=next(
                    section_counter
                ),
                kind=(
                    DocumentSectionKind
                    .BODY
                ),
                heading_role=(
                    _section_heading_role(
                        heading
                    )
                ),
                path=current_path,
                paragraphs=tuple(
                    direct_paragraphs
                ),
            )
        )

    for child in div:
        if (
                _local_name(child)
                != "div"
        ):
            continue

        result.extend(
            _extract_div_sections(
                child,
                parent_path=current_path,
                paragraph_counter=(
                    paragraph_counter
                ),
                section_counter=(
                    section_counter
                ),
            )
        )

    return result


def _extract_descendant_paragraphs(
        element: Element,
        paragraph_counter,
) -> tuple[
    NormalizedParagraph,
    ...
]:
    result: list[
        NormalizedParagraph
    ] = []

    for descendant in element.iter():
        if (
                _local_name(descendant)
                != "p"
        ):
            continue

        text = _element_text(
            descendant
        )

        if text is None:
            continue

        result.append(
            _paragraph_from_element(
                descendant,
                paragraph_counter,
            )
        )

    return tuple(
        result
    )


def _paragraph_from_element(
        element: Element,
        paragraph_counter,
) -> NormalizedParagraph:
    text = _element_text(
        element
    )

    if text is None:
        raise ValueError(
            "paragraph contains no usable text"
        )

    xml_id = (
            element.attrib.get(
                (
                    "{http://www.w3.org/"
                    "XML/1998/namespace}id"
                )
            )
            or element.attrib.get(
        "xml:id"
    )
    )

    return NormalizedParagraph(
        ordinal=next(
            paragraph_counter
        ),
        text=text,
        source_xml_id=xml_id,
    )


def _direct_heading(
        element: Element,
) -> str | None:
    for child in element:
        if (
                _local_name(child)
                != "head"
        ):
            continue

        return _element_text(
            child
        )

    return None


def _find_direct_child(
        element: Element,
        name: str,
) -> Element | None:
    normalized_name = (
        name.casefold()
    )

    for child in element:
        if (
                _local_name(child)
                == normalized_name
        ):
            return child

    return None


def _find_first_descendant(
        element: Element,
        name: str,
) -> Element | None:
    normalized_name = (
        name.casefold()
    )

    for descendant in element.iter():
        if (
                _local_name(descendant)
                == normalized_name
        ):
            return descendant

    return None


def _element_text(
        element: Element,
) -> str | None:
    text = " ".join(
        " ".join(
            element.itertext()
        ).split()
    )

    return text or None


def _local_name(
        element: Element,
) -> str:
    tag = element.tag

    if not isinstance(tag, str):
        return ""

    return (
        tag
        .rsplit("}", 1)[-1]
        .rsplit(":", 1)[-1]
        .casefold()
    )

def _section_heading_role(
        heading: str | None,
) -> SectionHeadingRole:
    if heading is None:
        return SectionHeadingRole.STANDARD

    normalized = (
        heading
        .strip()
        .casefold()
    )

    if normalized.startswith(
            "table "
    ):
        return SectionHeadingRole.TABLE

    if normalized.startswith(
            "figure "
    ):
        return SectionHeadingRole.FIGURE

    return SectionHeadingRole.STANDARD