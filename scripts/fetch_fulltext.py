"""Fetch OpenAlex GROBID full text for the reading list, within the free daily allowance.

Work lookups by DOI are free; each GROBID download costs USD 0.01 of the
USD 1/day free allowance. The run stops at --max-downloads or when the
remaining free allowance reported by OpenAlex drops below --reserve-usd.
It never spends prepaid funds. Resumable: finished papers are skipped.
"""

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx

API = "https://api.openalex.org"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reading-list", type=Path, default=Path("config/reading/credit_xai_reading_list_v2.json"))
    parser.add_argument("--out", type=Path, default=Path(".thesis-corpus/fulltext"))
    parser.add_argument("--max-downloads", type=int, default=90)
    parser.add_argument("--reserve-usd", type=float, default=0.05)
    parser.add_argument("--days", type=int, default=1, help="keep going across daily resets, at most this many days")
    args = parser.parse_args()

    for day in range(args.days):
        reset_in = run_once(args)
        if reset_in is None:
            return 0
        if day + 1 < args.days:
            print(f"waiting {reset_in // 60} min for the free allowance to reset", flush=True)
            # Wall-clock deadline: a single long sleep does not advance while the Mac sleeps.
            deadline = time.time() + reset_in + 120
            while (remaining := deadline - time.time()) > 0:
                time.sleep(min(remaining, 300))
    return 0


def get(client: httpx.Client, url: str, params: dict) -> httpx.Response | None:
    """GET, or None on a transient server/network failure; the paper stays pending for the next pass."""

    try:
        response = client.get(url, params=params)
    except httpx.TransportError as error:
        print(f"network error, skipping for now: {type(error).__name__}", flush=True)
        return None
    if response.status_code >= 500:
        print(f"server error {response.status_code}, skipping for now", flush=True)
        return None
    return response


def run_once(args) -> int | None:
    """One pass; returns seconds until allowance reset if stopped by the cap, else None."""

    key = os.environ.get("OPENALEX_API_KEY")
    if not key:
        raise SystemExit("OPENALEX_API_KEY is not set")

    args.out.mkdir(parents=True, exist_ok=True)
    index_path = args.out / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {}
    reading = json.loads(args.reading_list.read_text(encoding="utf-8"))
    papers = [p for facet in reading["facets"].values() for p in facet["papers"]]
    downloads = 0
    skipped = 0
    reset_in = None

    def save() -> None:
        tmp = index_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(index, indent=1), encoding="utf-8")
        tmp.replace(index_path)

    with httpx.Client(timeout=60, follow_redirects=True) as client:
        for paper in papers:
            pid = paper["paper_id"]
            entry = index.get(pid, {})

            if entry.get("status") in {"fetched", "no_doi", "no_grobid"}:
                continue
            if not paper["doi"]:
                index[pid] = {"status": "no_doi"}
                save()
                continue

            if "work_id" not in entry:
                response = get(client, f"{API}/works/doi:{paper['doi']}",
                               {"select": "id,has_content,content_urls,open_access", "api_key": key})
                if response is None:
                    skipped += 1
                    continue
                if response.status_code == 404:
                    index[pid] = {"status": "no_grobid", "reason": "doi not in OpenAlex"}
                    save()
                    continue
                response.raise_for_status()
                work = response.json()
                entry = {
                    "work_id": work["id"],
                    "grobid_url": (work.get("content_urls") or {}).get("grobid_xml"),
                    "oa_url": (work.get("open_access") or {}).get("oa_url"),
                }
                if not (work.get("has_content") or {}).get("grobid_xml") or not entry["grobid_url"]:
                    entry["status"] = "no_grobid"
                index[pid] = entry
                save()
                if entry.get("status") == "no_grobid":
                    continue

            if downloads >= args.max_downloads:
                reset_in = reset_in or 3600
                break

            response = get(client, entry["grobid_url"], {"api_key": key})
            if response is None:
                skipped += 1
                continue
            remaining = float(response.headers.get("x-ratelimit-remaining-usd", "0"))
            reset_in = int(response.headers.get("x-ratelimit-reset", "3600"))
            if response.status_code == 429:
                print("free allowance exhausted (429)", flush=True)
                break
            response.raise_for_status()
            content = response.content
            if not content.lstrip().startswith(b"<"):
                index[pid] = {**entry, "status": "bad_content"}
                save()
                continue

            sha = hashlib.sha256(content).hexdigest()
            (args.out / f"{sha}.tei.xml").write_bytes(content)
            index[pid] = {
                **entry,
                "status": "fetched",
                "sha256": sha,
                "bytes": len(content),
                "fetched_at": datetime.now(UTC).isoformat(),
            }
            save()
            downloads += 1
            print(f"{downloads} fetched {pid} (free allowance left ${remaining:.2f})", flush=True)

            if remaining < args.reserve_usd:
                print("free allowance nearly used; stopping until reset", flush=True)
                break
            time.sleep(0.5)
        else:
            reset_in = 3600 if skipped else None  # retry transient failures in an hour

    statuses = {}
    for entry in index.values():
        statuses[entry.get("status", "pending")] = statuses.get(entry.get("status", "pending"), 0) + 1
    print(f"downloads this run {downloads}; index: {statuses} of {len(papers)} papers", flush=True)
    return reset_in


if __name__ == "__main__":
    sys.exit(main())
