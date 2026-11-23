"""Candidate works that may close each SPECIFIC_GAP (discovery only, not evidence).

Sources: (1) Semantic Scholar papers citing the gap's support papers, published no earlier
than the support paper; (2) verified quotes in local cards of *other* papers.
Both filtered by hand-set theme keywords. Run from the repo root:
  ./scripts/uv run python scripts/gap_refutation_candidates.py
"""
import json, re, sys
from pathlib import Path


from thesis_factory.integrations.semantic_scholar.client import SemanticScholarClient

G = Path(".thesis-corpus/gaps")
THEME_KW = {  # shortcut: hand-set keyword filters, recall-limited; semantic search needs the Mac corpus
    "counterfactual-quality": r"counterfactual.*(evaluat|benchmark|quality|plausib|user study|human)|(evaluat|benchmark).*counterfactual",
    "xai-evaluation": r"(evaluat|benchmark|metric|faithful|ground.?truth).*(explanation|explainab|xai|attribution)|(explanation|xai|attribution).*(evaluat|benchmark|metric|faithful)",
    "fairness-metrics": r"fairness.*(metric|measure|select|choos|incompatib|trade|varian|stabil)",
    "joint-tradeoff": r"(fair|explain).*(profit|accura|performance|trade).*credit|credit.*(fair|explain).*(trade|profit|performance)",
    "counterfactual-robustness": r"(robust|stabl|manipulat).*(counterfactual|recourse)|(counterfactual|recourse).*(robust|stabl|manipulat)",
    "xai-human-evaluation": r"(user study|human.subject|human.grounded|end.user|lay).*(explanation|xai)|(explanation|xai).*(user study|human evaluation|end.user)",
    "legal-automated-decision": r"(article 22|art\. 22|solely automated|automated decision|schufa|human in the loop|human oversight)",
    "legal-ai-act-high-risk": r"(ai act|artificial intelligence act|2024/1689).*(high.risk|credit|creditworth)|(high.risk).*(ai act)",
    "xai-law-bridge": r"(explanation|xai|explainab).*(legal|law|gdpr|ai act|regulat)|(legal|gdpr|ai act|regulat).*(explanation|xai|explainab)",
    "bias-mitigation-benchmark": r"(bias|fairness).*(mitigat|benchmark|debias).*|(benchmark).*(fair)",
    "legal-right-to-explanation": r"right to (an )?explanation|meaningful information|article 15|art\. 15|trade secret",
    "causal-explanations": r"causal.*(counterfactual|recourse)|(counterfactual|recourse).*causal|immutab",
    "xai-in-credit": r"(credit|lend|loan).*(explain|xai|shap|lime|interpret)|(explain|xai|shap|lime).*(credit|lend|loan)",
    "explanation-tailoring": r"(tailor|personali|stakeholder|audience|user.centr|recipient).*(explanation)|(explanation).*(tailor|personali|stakeholder|audience)",
}
CARD_KINDS = {"FINDING", "XAI_METHOD", "EVALUATION_METRIC", "LEGAL_CLAIM", "MODEL"}


def main():
    review = json.loads((G / "review.json").read_text(encoding="utf-8"))
    index = json.loads(Path(".thesis-corpus/fulltext/index.json").read_text(encoding="utf-8"))
    sha2pid = {v["sha256"]: k for k, v in index.items() if v.get("sha256")}
    cards = [json.loads(p.read_text(encoding="utf-8")) for p in Path(".thesis-corpus/cards").glob("*.json")]
    gaps = {k: v for k, v in review["clusters"].items() if v.get("verdict") == "SPECIFIC_GAP"}

    cache_p = G / "s2_citations_cache.json"
    cache = json.loads(cache_p.read_text(encoding="utf-8")) if cache_p.exists() else {}
    s2 = SemanticScholarClient(max_retries=4)
    pids = sorted({sha2pid[s["address"]["artifact_sha256"]] for g in gaps.values() for s in g["support"]
                   if s["address"]["artifact_sha256"] in sha2pid})
    meta = {p: m for p, m in zip(pids, s2.batch(pids, fields="title,year,citationCount")) if m}
    for pid in pids:
        if pid in cache:
            continue
        try:
            page = s2._request("GET", f"/graph/v1/paper/{pid}/citations",
                               params={"fields": "title,year,citationCount,externalIds,abstract", "limit": 1000})
            cache[pid] = [c["citingPaper"] for c in page.get("data", []) if c.get("citingPaper", {}).get("title")]
        except Exception as e:  # record, keep going: one failed seed must not stop the rest
            cache[pid] = {"error": str(e)[:200]}
        cache_p.write_text(json.dumps(cache), encoding="utf-8")

    out = {}
    for gid, g in gaps.items():
        kw = re.compile(THEME_KW[g["theme"]], re.I)
        own = {s["address"]["artifact_sha256"] for s in g["support"]}
        seeds = [sha2pid[s] for s in own if s in sha2pid]
        min_year = min((meta.get(p, {}).get("year") or 0) for p in seeds) if seeds else 0
        cites = {}
        for p in seeds:
            for c in cache.get(p, []) if isinstance(cache.get(p), list) else []:
                text = f"{c['title']} {c.get('abstract') or ''}"
                if (c.get("year") or 0) >= min_year and kw.search(text):
                    e = cites.setdefault(c.get("paperId"), {**{k: c.get(k) for k in ("title", "year", "citationCount", "externalIds", "abstract")}, "cites_seeds": 0})
                    e["cites_seeds"] += 1
        ranked = sorted(cites.values(), key=lambda c: (-c["cites_seeds"], -(c["citationCount"] or 0)))[:10]
        local = [{"title": cd["title"], "kind": cl["kind"], "quote": cl["quote"], "address": cl["address"]}
                 for cd in cards if cd["artifact_sha256"] not in own
                 for cl in cd["claims"] if cl["kind"] in CARD_KINDS and kw.search(cl["quote"])]
        out[gid] = {"theme": g["theme"], "gap": g["gap"], "seeds": [meta.get(p, {"paperId": p}) for p in seeds],
                    "seed_errors": [p for p in seeds if isinstance(cache.get(p), dict)],
                    "citing_candidates": ranked, "local_quotes": local[:15], "local_quote_total": len(local)}
    (G / "refutation_candidates.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for gid, o in out.items():
        print(gid, o["theme"], "seeds", len(o["seeds"]), "err", len(o["seed_errors"]), "citing", len(o["citing_candidates"]), "local", o["local_quote_total"])


if __name__ == "__main__":
    main()
