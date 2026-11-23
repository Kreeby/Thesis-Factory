"""Build the Codex second-review package from review.json (blind part A, comparison part B)."""
import json
import sys
from pathlib import Path

G = Path(".thesis-corpus/gaps")
OUT = G / "codex_package"

RULES = """Rules (Thesis Factory AGENTS.md): do not invent papers, authors, DOIs, quotes or results.
Every evidence item needs a source you actually opened (URL or DOI) and a verbatim quote from it.
Separate facts from interpretation. Absence of results in one search is not proof of a gap.
Legal gaps: check against the final text of Regulation (EU) 2024/1689 and CJEU case law
(at least C-634/21 SCHUFA, 7 Dec 2023; C-203/22 Dun & Bradstreet Austria, 27 Feb 2025).
Budget: at most 40 web searches in total. Today is 2026-11-23."""

SCHEMA = """Output: one JSON file `codex_review_<A|B>.json`:
{"reviewer": "Codex <model>", "date": "...", "searches_used": N,
 "gaps": {"Q0004": {"refutation": "SURVIVED|REFUTED|CONTESTED", "crowded": true|false,
   "note": "one or two sentences", "evidence": [{"title": "...", "year": 2024,
   "doi_or_url": "...", "quote": "verbatim", "supports": "refutes|confirms_gap|partial"}]}}}
SURVIVED = no work found that closes the gap; REFUTED = a source closes it as stated;
CONTESTED = partly addressed or conflicting sources. crowded = active area with many papers."""


def main():
    review = json.loads((G / "review.json").read_text(encoding="utf-8"))
    gaps = {k: v for k, v in review["clusters"].items() if v.get("verdict") == "SPECIFIC_GAP"}
    # the package is the exact reviewer input of record; never overwrite it silently
    if OUT.exists() and any(OUT.iterdir()) and "--force" not in sys.argv:
        raise SystemExit(f"{OUT} already exists (reviewer input of record); pass --force to rebuild")
    OUT.mkdir(exist_ok=True)
    a = ["# Part A — blind second review of 23 candidate research gaps", "",
         "Thesis topic (owner-approved): *A Legally Grounded Empirical Evaluation of Explainable AI for Consumer Credit Scoring*.",
         "Each gap below was stated by the first reviewer from recurring author-stated open questions (verified quotes from papers read in full).",
         "Task per gap: (1) is the gap statement a fair reading of its quotes? (2) does a support paper ITSELF already do what its quote calls for (a prescription like 'a study must evaluate X' is not an open question if the same paper does X)? (3) try to REFUTE it: find work, especially later work, that closes it.", "",
         RULES, "", SCHEMA.replace("<A|B>", "A"), ""]
    for gid, g in gaps.items():
        a += [f"## {gid} · {g['theme']} · {g['papers']} distinct texts", f"**Gap:** {g['gap']}", ""]
        a += [f"- \"{s['quote']}\" — *{s['title']}*" for s in g["support"]] + [""]
    (OUT / "part_A_blind.md").write_text("\n".join(a), encoding="utf-8")

    b = ["# Part B — compare with the first reviewer (open only after Part A is saved)", "",
         review["refutation"]["method"], "",
         "Task: for each gap, say AGREE or DISAGREE with the verdict and why; check that each quoted source supports",
         "the use made of it (a real citation can still be misused); list missed work. Same rules and budget as Part A.", "",
         SCHEMA.replace("<A|B>", "B").replace('"note"', '"agree": true|false, "note"'), ""]
    for gid, g in gaps.items():
        b += [f"## {gid} · first reviewer: **{g['refutation']}**{' · crowded' if g['crowded'] else ''}",
              f"**Gap:** {g['gap']}", f"**Note:** {g['refutation_note']}", ""]
        for e in g["refutation_evidence"]:
            if e.get("lead"):
                b.append(f"- LEAD (not quote-verified): {e['lead']} — {e['url']}")
            else:
                ref = e.get("doi") or e.get("url") or e.get("paperId")
                b.append(f"- \"{e['quote']}\" — {e.get('title') or e.get('source')} ({e.get('year', '')}) {ref} [{e['where']}]")
        b.append("")
    (OUT / "part_B_compare.md").write_text("\n".join(b), encoding="utf-8")
    print("wrote", *(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
