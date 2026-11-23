"""Verify every refutation quote verbatim against its source, then merge verdicts into review.json.

Quotes come from S2 abstracts (s2_citations_cache.json) or saved primary texts (sources/).
Any quote not found verbatim aborts the merge. Run from the repo root.
"""
import hashlib, json, shutil
from pathlib import Path

G = Path(".thesis-corpus/gaps")


def norm(s):
    return " ".join(s.split())


def main():
    spec = json.loads((G / "refutation_verdicts.json").read_text(encoding="utf-8"))
    cache = json.loads((G / "s2_citations_cache.json").read_text(encoding="utf-8"))
    papers = {}
    for v in cache.values():
        for p in v if isinstance(v, list) else []:
            papers.setdefault(norm(p["title"]).lower(), p)
    review_p = G / "review.json"
    review = json.loads(review_p.read_text(encoding="utf-8"))
    failures = []
    for gid, v in spec["verdicts"].items():
        assert v["refutation"] in spec["states"], (gid, v["refutation"])
        assert review["clusters"][gid]["verdict"] == "SPECIFIC_GAP", gid
        for e in v["evidence"]:
            if "lead" in e:
                e["verified"] = False  # pointer from a web search, no quote
                continue
            if "codex" in e:  # second-reviewer evidence: accepted only if verify_codex_quotes.py found it verbatim
                checked = json.loads((G / f"codex_review_{e['codex']}.checked.json").read_text(encoding="utf-8"))
                ok = any(x.get("check") == "VERIFIED" and x.get("doi_or_url") == e["url"] and x.get("quote") == e["quote"]
                         for x in checked["gaps"].get(gid, {}).get("evidence", []))
                if ok:
                    e.update(verified=True, where=f"Codex part {e['codex']}, fetched and matched by verify_codex_quotes.py")
                else:
                    failures.append((gid, e["url"], "codex quote not VERIFIED"))
                continue
            if "corpus_id" in e:  # abstract stored in the local corpus (S2 record copied from the Mac)
                import sqlite3
                db = sqlite3.connect("file:.thesis-corpus/corpus.sqlite?mode=ro", uri=True)
                r = db.execute("select title, year, doi, abstract from papers where paper_id = ?", (e["corpus_id"],)).fetchone()
                if not r:
                    failures.append((gid, e["corpus_id"], "not in corpus"))
                    continue
                text = r[3] or ""
                e.update(title=r[0], year=r[1], doi=r[2], paperId=e["corpus_id"], where="corpus.sqlite abstract (Semantic Scholar)")
            elif "s2_title" in e:
                key = norm(e["s2_title"]).lower()
                hits = [p for t, p in papers.items() if t.startswith(key[:60])]
                if len(hits) != 1:
                    failures.append((gid, e["s2_title"], f"{len(hits)} title matches"))
                    continue
                p = hits[0]
                text = p.get("abstract") or ""
                e.update(title=p["title"], year=p.get("year"), paperId=p.get("paperId"),
                         doi=(p.get("externalIds") or {}).get("DOI"), where="Semantic Scholar abstract")
            else:
                raw = (G / "sources" / e["file"]).read_bytes()
                text = raw.decode("utf-8", errors="replace")  # pdftotext emitted one Latin-1 byte (a name)
                e.update(sha256=hashlib.sha256(raw).hexdigest(), where=f"sources/{e['file']}")
            if norm(e["quote"]) not in norm(text):
                failures.append((gid, e.get("s2_title") or e.get("corpus_id") or e.get("file"), e["quote"][:60]))
            else:
                e["verified"] = True
    if failures:
        for f in failures:
            print("FAIL", *f)
        raise SystemExit(f"{len(failures)} quote(s) not verified; review.json unchanged")
    if not (G / "review.before-refutation.json").exists():  # keep the pre-refutation original
        shutil.copy(review_p, G / "review.before-refutation.json")
    for gid, v in spec["verdicts"].items():
        c = review["clusters"][gid]
        c["refutation"] = v["refutation"]
        c["crowded"] = v["crowded"]
        c["refutation_note"] = v["note"]
        c["refutation_evidence"] = v["evidence"]
    # keep keys added by later steps (e.g. second_review) on re-runs
    review["refutation"] = {**review.get("refutation", {}), **{k: spec[k] for k in ("reviewer", "method", "states", "crowded")}}
    review_p.write_text(json.dumps(review, ensure_ascii=False, indent=1), encoding="utf-8")
    n = sum(1 for v in spec["verdicts"].values() for e in v["evidence"] if e.get("verified"))
    print(f"merged {len(spec['verdicts'])} verdicts, {n} quotes verified")


if __name__ == "__main__":
    main()
