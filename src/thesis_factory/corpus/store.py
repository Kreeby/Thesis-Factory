import json
import sqlite3
from array import array
from collections.abc import Iterable, Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


_SCHEMA = """
CREATE TABLE IF NOT EXISTS papers (
    paper_id TEXT PRIMARY KEY,
    doi TEXT,
    title TEXT NOT NULL,
    abstract TEXT,
    year INTEGER,
    venue TEXT,
    citation_count INTEGER,
    raw_json TEXT NOT NULL,
    fetched_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS papers_doi ON papers(doi);

-- Discovery provenance: which query surfaced which paper. Not evidence.
CREATE TABLE IF NOT EXISTS query_hits (
    query TEXT NOT NULL,
    paper_id TEXT NOT NULL,
    PRIMARY KEY (query, paper_id)
);

-- Resumable bulk-search state per query.
CREATE TABLE IF NOT EXISTS query_runs (
    query TEXT PRIMARY KEY,
    next_token TEXT,
    total INTEGER,
    fetched INTEGER NOT NULL DEFAULT 0,
    completed INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS embeddings (
    paper_id TEXT NOT NULL,
    model TEXT NOT NULL,
    vector BLOB,
    PRIMARY KEY (paper_id, model)
);

CREATE TABLE IF NOT EXISTS citations (
    citing_id TEXT NOT NULL,
    cited_id TEXT NOT NULL,
    PRIMARY KEY (citing_id, cited_id)
);

-- Marks papers whose references were requested, including empty results.
CREATE TABLE IF NOT EXISTS references_fetched (
    paper_id TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS screenings (
    paper_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    model TEXT NOT NULL,
    status TEXT NOT NULL,
    rationale TEXT NOT NULL,
    screened_at TEXT NOT NULL,
    PRIMARY KEY (paper_id, topic, model)
);
"""


def _now() -> str:
    return datetime.now(UTC).isoformat()


class CorpusStore:
    """Local, topic-independent paper cache reusable across theses."""

    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path)
        self._db.executescript(_SCHEMA)

    def close(self) -> None:
        self._db.close()

    def upsert_papers(
            self,
            papers: Iterable[dict[str, Any]],
            *,
            query: str | None = None,
    ) -> int:
        count = 0

        with self._db:
            for paper in papers:
                paper_id = paper.get("paperId")
                title = (paper.get("title") or "").strip()

                # S2 occasionally returns records without id or title; skip them.
                if not paper_id or not title:
                    continue

                doi = (paper.get("externalIds") or {}).get("DOI")
                self._db.execute(
                    """
                    INSERT INTO papers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(paper_id) DO UPDATE SET
                        doi=excluded.doi, title=excluded.title,
                        abstract=COALESCE(excluded.abstract, papers.abstract),
                        year=excluded.year, venue=excluded.venue,
                        citation_count=excluded.citation_count,
                        raw_json=excluded.raw_json,
                        fetched_at=excluded.fetched_at
                    """,
                    (
                        paper_id,
                        doi.lower() if doi else None,
                        title,
                        paper.get("abstract"),
                        paper.get("year"),
                        paper.get("venue"),
                        paper.get("citationCount"),
                        json.dumps(paper, sort_keys=True),
                        _now(),
                    ),
                )

                if query is not None:
                    self._db.execute(
                        "INSERT OR IGNORE INTO query_hits VALUES (?, ?)",
                        (query, paper_id),
                    )

                count += 1

        return count

    def query_hit_count(self, query: str) -> int:
        return self._db.execute(
            "SELECT COUNT(*) FROM query_hits WHERE query = ?",
            (query,),
        ).fetchone()[0]

    def query_run(self, query: str) -> dict[str, Any] | None:
        row = self._db.execute(
            "SELECT next_token, total, fetched, completed "
            "FROM query_runs WHERE query = ?",
            (query,),
        ).fetchone()

        if row is None:
            return None

        return {
            "next_token": row[0],
            "total": row[1],
            "fetched": row[2],
            "completed": bool(row[3]),
        }

    def save_query_run(
            self,
            query: str,
            *,
            next_token: str | None,
            total: int,
            fetched: int,
            completed: bool,
    ) -> None:
        with self._db:
            self._db.execute(
                "INSERT OR REPLACE INTO query_runs VALUES (?, ?, ?, ?, ?, ?)",
                (query, next_token, total, fetched, int(completed), _now()),
            )

    def papers_missing_embedding(self, model: str) -> list[str]:
        return [
            row[0]
            for row in self._db.execute(
                "SELECT paper_id FROM papers WHERE paper_id NOT IN "
                "(SELECT paper_id FROM embeddings WHERE model = ?) "
                "ORDER BY paper_id",
                (model,),
            )
        ]

    def put_embedding(
            self,
            paper_id: str,
            model: str,
            vector: list[float] | None,
    ) -> None:
        # NULL vector records "S2 has no embedding" so it is not re-requested.
        blob = array("f", vector).tobytes() if vector else None

        with self._db:
            self._db.execute(
                "INSERT OR REPLACE INTO embeddings VALUES (?, ?, ?)",
                (paper_id, model, blob),
            )

    def embeddings(self, model: str) -> Iterator[tuple[str, array]]:
        for paper_id, blob in self._db.execute(
                "SELECT paper_id, vector FROM embeddings "
                "WHERE model = ? AND vector IS NOT NULL ORDER BY paper_id",
                (model,),
        ):
            vector = array("f")
            vector.frombytes(blob)
            yield paper_id, vector

    def papers_missing_references(self) -> list[str]:
        return [
            row[0]
            for row in self._db.execute(
                "SELECT paper_id FROM papers WHERE paper_id NOT IN "
                "(SELECT paper_id FROM references_fetched) ORDER BY paper_id"
            )
        ]

    def put_references(
            self,
            paper_id: str,
            cited_ids: Iterable[str],
    ) -> None:
        with self._db:
            self._db.executemany(
                "INSERT OR IGNORE INTO citations VALUES (?, ?)",
                ((paper_id, cited) for cited in cited_ids),
            )
            self._db.execute(
                "INSERT OR IGNORE INTO references_fetched VALUES (?)",
                (paper_id,),
            )

    def citations(self) -> list[tuple[str, str]]:
        return self._db.execute(
            "SELECT citing_id, cited_id FROM citations"
        ).fetchall()

    def papers(self) -> list[dict[str, Any]]:
        rows = self._db.execute(
            "SELECT paper_id, doi, title, abstract, year, venue, "
            "citation_count FROM papers ORDER BY paper_id"
        )
        keys = (
            "paper_id", "doi", "title", "abstract",
            "year", "venue", "citation_count",
        )
        return [dict(zip(keys, row)) for row in rows]

    def paper_queries(self) -> dict[str, set[str]]:
        hits: dict[str, set[str]] = {}

        for query, paper_id in self._db.execute(
                "SELECT query, paper_id FROM query_hits"
        ):
            hits.setdefault(paper_id, set()).add(query)

        return hits

    def unscreened_papers(
            self,
            topic: str,
            model: str,
    ) -> list[dict[str, Any]]:
        screened = {
            row[0]
            for row in self._db.execute(
                "SELECT paper_id FROM screenings "
                "WHERE topic = ? AND model = ?",
                (topic, model),
            )
        }
        return [
            paper
            for paper in self.papers()
            if paper["paper_id"] not in screened
        ]

    def put_screening(
            self,
            paper_id: str,
            *,
            topic: str,
            model: str,
            status: str,
            rationale: str,
    ) -> None:
        with self._db:
            self._db.execute(
                "INSERT OR REPLACE INTO screenings VALUES (?, ?, ?, ?, ?, ?)",
                (paper_id, topic, model, status, rationale, _now()),
            )

    def screenings(
            self,
            topic: str,
            model: str,
    ) -> dict[str, str]:
        return dict(
            self._db.execute(
                "SELECT paper_id, status FROM screenings "
                "WHERE topic = ? AND model = ?",
                (topic, model),
            ).fetchall()
        )

    def counts(self) -> dict[str, int]:
        tables = (
            "papers", "query_hits", "embeddings",
            "citations", "screenings",
        )
        counts = {
            table: self._db.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]
            for table in tables
        }
        counts["papers_with_abstract"] = self._db.execute(
            "SELECT COUNT(*) FROM papers WHERE abstract IS NOT NULL "
            "AND TRIM(abstract) != ''"
        ).fetchone()[0]
        return counts
