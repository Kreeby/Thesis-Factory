import hashlib
import json
import time
from html.parser import HTMLParser
from urllib.parse import urlsplit

import httpx
from defusedxml import ElementTree

from thesis_factory.domain.primary_source import (
    PrimarySourceDocument,
    PrimarySourceParagraph,
)


class PrimarySourceFetchError(
    ValueError
):
    pass


_RETRYABLE_STATUS = {
    408,
    429,
    500,
    502,
    503,
    504,
}


class PrimarySourceFetcher:
    def __init__(
        self,
        *,
        max_bytes: int = 8 * 1024 * 1024,
        retry_attempts: int = 3,
        retry_backoff_seconds: float = 0.5,
        sleep_fn=time.sleep,
        http_client: httpx.Client | None = None,
    ) -> None:
        if max_bytes < 1:
            raise ValueError(
                "max_bytes must be positive"
            )

        if retry_attempts < 1:
            raise ValueError(
                "retry_attempts must be positive"
            )

        if retry_backoff_seconds < 0:
            raise ValueError(
                "retry_backoff_seconds must "
                "not be negative"
            )

        self._max_bytes = max_bytes
        self._retry_attempts = (
            retry_attempts
        )
        self._retry_backoff_seconds = (
            retry_backoff_seconds
        )
        self._sleep_fn = sleep_fn

        self._http_client = (
            http_client
            or httpx.Client(
                timeout=45.0,
                follow_redirects=True,
                headers={
                    "User-Agent": (
                        "ThesisFactory/0.1 "
                        "primary-source-verifier"
                    ),
                },
            )
        )

        self._owns_client = (
            http_client is None
        )

    def fetch(
        self,
        *,
        url: str,
        title: str | None = None,
    ) -> PrimarySourceDocument:
        response = self._get_with_retry(
            url
        )

        content = response.content

        if not content:
            raise PrimarySourceFetchError(
                "primary-source response is empty"
            )

        if len(content) > self._max_bytes:
            raise PrimarySourceFetchError(
                "primary-source response exceeds "
                "the maximum size"
            )

        content_type = (
            response.headers.get(
                "content-type",
                "",
            )
            .split(
                ";",
                1,
            )[0]
            .strip()
            .casefold()
        )

        paragraphs = _normalize_content(
            content,
            content_type=content_type,
        )

        if not paragraphs:
            raise PrimarySourceFetchError(
                "primary-source page produced "
                "no usable text"
            )

        digest = hashlib.sha256(
            content
        ).hexdigest()

        final_url = str(
            response.url
            or url
        )

        host = (
            urlsplit(
                final_url
            ).hostname
            or ""
        ).casefold()

        return PrimarySourceDocument(
            artifact_sha256=digest,
            source_url=final_url,
            source_host=host,
            title=title,
            paragraphs=tuple(
                PrimarySourceParagraph(
                    ordinal=index,
                    text=text,
                )
                for index, text
                in enumerate(
                    paragraphs,
                    start=1,
                )
            ),
        )

    def _get_with_retry(
        self,
        url: str,
    ) -> httpx.Response:
        last_error: Exception | None = None

        headers = _request_headers(
            url
        )

        for attempt in range(
            1,
            self._retry_attempts + 1,
        ):
            try:
                response = (
                    self._http_client.get(
                        url,
                        headers=headers,
                    )
                )
            except httpx.TimeoutException as error:
                last_error = error

                if (
                    attempt
                    < self._retry_attempts
                ):
                    self._sleep(
                        attempt
                    )
                    continue

                raise PrimarySourceFetchError(
                    "primary-source fetch timed out "
                    f"for {_safe_url(url)}"
                ) from error

            if not response.is_error:
                return response

            if (
                response.status_code
                in _RETRYABLE_STATUS
                and attempt
                < self._retry_attempts
            ):
                self._sleep(
                    attempt
                )
                continue

            raise PrimarySourceFetchError(
                "primary-source fetch failed "
                f"with HTTP {response.status_code} "
                f"for {_safe_url(url)}"
            )

        raise PrimarySourceFetchError(
            "primary-source fetch failed "
            f"for {_safe_url(url)}"
        ) from last_error

    def _sleep(
        self,
        attempt: int,
    ) -> None:
        self._sleep_fn(
            self._retry_backoff_seconds
            * attempt
        )

    def close(self) -> None:
        if self._owns_client:
            self._http_client.close()


def _request_headers(
    url: str,
) -> dict[
    str,
    str,
]:
    host = (
        urlsplit(
            url
        ).hostname
        or ""
    ).casefold()

    if (
        host == "publications.europa.eu"
        or host.endswith(
            ".publications.europa.eu"
        )
    ):
        return {
            "Accept": (
                "application/xhtml+xml,"
                "text/html;q=0.9"
            ),
            "Accept-Language": "eng",
            "Accept-Max-Cs-Size": (
                str(
                    64
                    * 1024
                    * 1024
                )
            ),
        }

    return {
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml,text/xml,"
            "application/json,text/plain;q=0.9,"
            "*/*;q=0.5"
        ),
        "Accept-Language": "en",
    }


def _normalize_content(
    content: bytes,
    *,
    content_type: str,
) -> tuple[
    str,
    ...,
]:
    stripped = content.lstrip()
    lower_prefix = stripped[
        :300
    ].lower()

    if (
        content_type
        in {
            "application/xml",
            "text/xml",
            "application/akn+xml",
        }
        or stripped.startswith(
            b"<?xml"
        )
    ):
        return _xml_blocks(
            content
        )

    if (
        content_type
        in {
            "text/html",
            "application/xhtml+xml",
            "",
        }
        or lower_prefix.startswith(
            b"<!doctype html"
        )
        or lower_prefix.startswith(
            b"<html"
        )
    ):
        text = content.decode(
            "utf-8",
            errors="replace",
        )

        parser = _BlockTextParser()
        parser.feed(
            text
        )
        parser.close()

        return _unique(
            parser.paragraphs
        )

    if (
        content_type
        in {
            "text/plain",
            "text/csv",
        }
    ):
        text = content.decode(
            "utf-8",
            errors="replace",
        )

        return _unique(
            _plain_blocks(
                text
            )
        )

    if (
        content_type
        == "application/json"
    ):
        payload = json.loads(
            content.decode(
                "utf-8"
            )
        )

        values: list[
            str
        ] = []

        _collect_json_strings(
            payload,
            values,
        )

        return _unique(
            values
        )

    if (
        content_type
        == "application/pdf"
        or content.startswith(
            b"%PDF-"
        )
    ):
        raise PrimarySourceFetchError(
            "PDF primary sources are not "
            "supported by this executor yet"
        )

    raise PrimarySourceFetchError(
        "unsupported primary-source "
        f"content type: {content_type or 'unknown'}"
    )


_XML_BLOCK_TAGS = {
    "p",
    "np",
    "txt",
    "alinea",
    "parag",
    "paragraph",
    "para",
    "point",
    "item",
    "recital",
    "heading",
    "title",
    "ti.art",
    "sti.art",
    "ti.section",
    "ti.chapter",
}


def _xml_blocks(
    content: bytes,
) -> tuple[
    str,
    ...,
]:
    root = ElementTree.fromstring(
        content
    )

    values: list[
        str
    ] = []

    for element in root.iter():
        tag = element.tag

        if not isinstance(
            tag,
            str,
        ):
            continue

        local = (
            tag.rsplit(
                "}",
                1,
            )[-1]
            .casefold()
        )

        if local not in _XML_BLOCK_TAGS:
            continue

        text = " ".join(
            " ".join(
                element.itertext()
            ).split()
        )

        if len(text) >= 8:
            values.append(
                text
            )

    unique = _unique(
        values
    )

    if len(unique) >= 3:
        return unique

    full_text = " ".join(
        " ".join(
            root.itertext()
        ).split()
    )

    return _unique(
        _chunk_text(
            full_text,
            max_chars=1200,
        )
    )


def _chunk_text(
    text: str,
    *,
    max_chars: int,
) -> list[
    str
]:
    if not text:
        return []

    words = text.split()

    chunks: list[
        str
    ] = []

    current: list[
        str
    ] = []

    current_length = 0

    for word in words:
        extra = (
            len(word)
            + (
                1
                if current
                else 0
            )
        )

        if (
            current
            and current_length + extra
            > max_chars
        ):
            chunks.append(
                " ".join(
                    current
                )
            )
            current = []
            current_length = 0

        current.append(
            word
        )

        current_length += extra

    if current:
        chunks.append(
            " ".join(
                current
            )
        )

    return chunks


class _BlockTextParser(
    HTMLParser
):
    _BLOCK_TAGS = {
        "article",
        "blockquote",
        "dd",
        "div",
        "dt",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "li",
        "p",
        "pre",
        "section",
        "td",
        "th",
    }

    _IGNORED_TAGS = {
        "script",
        "style",
        "noscript",
        "svg",
        "canvas",
    }

    def __init__(
        self,
    ) -> None:
        super().__init__(
            convert_charrefs=True
        )

        self.paragraphs: list[
            str
        ] = []

        self._parts: list[
            str
        ] = []

        self._ignored_depth = 0

    def handle_starttag(
        self,
        tag,
        attrs,
    ) -> None:
        normalized = (
            tag.casefold()
        )

        if (
            normalized
            in self._IGNORED_TAGS
        ):
            self._ignored_depth += 1
            return

        if (
            self._ignored_depth == 0
            and normalized
            in self._BLOCK_TAGS
        ):
            self._flush()

    def handle_endtag(
        self,
        tag,
    ) -> None:
        normalized = (
            tag.casefold()
        )

        if (
            normalized
            in self._IGNORED_TAGS
        ):
            if self._ignored_depth > 0:
                self._ignored_depth -= 1
            return

        if (
            self._ignored_depth == 0
            and normalized
            in self._BLOCK_TAGS
        ):
            self._flush()

    def handle_data(
        self,
        data,
    ) -> None:
        if self._ignored_depth > 0:
            return

        if data.strip():
            self._parts.append(
                data
            )

    def close(
        self,
    ) -> None:
        super().close()
        self._flush()

    def _flush(
        self,
    ) -> None:
        if not self._parts:
            return

        normalized = " ".join(
            " ".join(
                self._parts
            ).split()
        )

        self._parts = []

        if (
            len(normalized) >= 2
        ):
            self.paragraphs.append(
                normalized
            )


def _plain_blocks(
    text: str,
) -> list[
    str
]:
    blocks = []

    for raw in text.splitlines():
        normalized = " ".join(
            raw.split()
        )

        if len(normalized) >= 2:
            blocks.append(
                normalized
            )

    return blocks


def _collect_json_strings(
    value,
    result: list[
        str
    ],
) -> None:
    if isinstance(
        value,
        str,
    ):
        normalized = " ".join(
            value.split()
        )

        if len(normalized) >= 8:
            result.append(
                normalized
            )

        return

    if isinstance(
        value,
        list,
    ):
        for item in value:
            _collect_json_strings(
                item,
                result,
            )
        return

    if isinstance(
        value,
        dict,
    ):
        for item in value.values():
            _collect_json_strings(
                item,
                result,
            )


def _unique(
    values,
) -> tuple[
    str,
    ...,
]:
    result: list[
        str
    ] = []

    seen: set[
        str
    ] = set()

    for value in values:
        normalized = " ".join(
            value.split()
        )

        if (
            not normalized
            or normalized in seen
        ):
            continue

        seen.add(
            normalized
        )
        result.append(
            normalized
        )

    return tuple(
        result
    )


def _safe_url(
    url: str,
) -> str:
    parsed = urlsplit(
        url
    )

    return (
        f"{parsed.scheme}://"
        f"{parsed.netloc}"
        f"{parsed.path}"
    )
