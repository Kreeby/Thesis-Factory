"""Corpus pass for refutation (discovery only, not evidence): for each SPECIFIC_GAP,
(1) corpus papers citing its support papers (full local graph) matching the theme keywords;
(2) SPECTER2 nearest neighbours of the support-paper centroid (keyword match reported, not required).
Both restricted to year >= earliest support paper. Run from the repo root."""
import json, sqlite3, sys
from pathlib import Path

import numpy as np

G = Path(".thesis-corpus/gaps")

from gap_refutation_candidates import THEME_KW  # same keyword filters as the S2 pass (scripts/ is on sys.path)
import re


def main():
    review = json.loads((G / "review.json").read_text(encoding="utf-8"))
    index = json.loads(Path(".thesis-corpus/fulltext/index.json").read_text(encoding="utf-8"))
    sha2pid = {v["sha256"]: k for k, v in index.items() if v.get("sha256")}
    db = sqlite3.connect("file:.thesis-corpus/corpus.sqlite?mode=ro", uri=True)
    meta = {r[0]: r[1:] for r in db.execute("select paper_id,title,abstract,year,citation_count,doi from papers")}
    ids, vecs = [], []
    for pid, blob in db.execute("select paper_id,vector from embeddings where model='specter_v2' and vector is not null"):
        ids.append(pid); vecs.append(np.frombuffer(blob, dtype=np.float32))
    M = np.vstack(vecs); M /= np.linalg.norm(M, axis=1, keepdims=True)
    row = {p: i for i, p in enumerate(ids)}
    years = np.array([meta[p][2] or 0 for p in ids])

    out = {}
    for gid, g in review["clusters"].items():
        if g.get("verdict") != "SPECIFIC_GAP":
            continue
        kw = re.compile(THEME_KW[g["theme"]], re.I)
        seeds = sorted({sha2pid[s["address"]["artifact_sha256"]] for s in g["support"] if s["address"]["artifact_sha256"] in sha2pid})
        miny = min((meta.get(p, (None,) * 5)[2] or 0) for p in seeds) if seeds else 0

        def card(p, **extra):
            t, a, y, cc, doi = meta[p]
            return {"paperId": p, "title": t, "year": y, "citationCount": cc, "doi": doi,
                    "keyword_match": bool(kw.search(f"{t} {a or ''}")), **extra}

        q = ",".join("?" * len(seeds))
        citing = {}
        for c, in db.execute(f"select citing_id from citations where cited_id in ({q})", seeds) if seeds else []:
            citing[c] = citing.get(c, 0) + 1
        graph = [card(p, cites_seeds=n) for p, n in citing.items()
                 if p in meta and (meta[p][2] or 0) >= miny and p not in seeds]
        graph = [c for c in graph if c["keyword_match"]]
        graph.sort(key=lambda c: (-c["cites_seeds"], -(c["citationCount"] or 0)))

        sv = [row[p] for p in seeds if p in row]
        near = []
        if sv:
            cen = M[sv].mean(0); cen /= np.linalg.norm(cen)
            sim = M @ cen
            sim[years < miny] = -1
            for i in np.argsort(-sim)[:40]:
                if ids[i] not in seeds:
                    near.append(card(ids[i], cosine=round(float(sim[i]), 3)))
        out[gid] = {"theme": g["theme"], "seeds_in_corpus": len([p for p in seeds if p in meta]), "seeds": len(seeds),
                    "graph_total": len(graph), "graph": graph[:15], "neighbours": near[:25]}
        print(gid, g["theme"], "seeds", out[gid]["seeds_in_corpus"], "/", len(seeds), "graph", len(graph),
              "near_kw", sum(n["keyword_match"] for n in near[:25]))
    (G / "corpus_candidates.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
