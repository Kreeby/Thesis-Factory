"""Compare first-review refutation verdicts with Codex part A (blind) and part B (comparison)."""
import json
from pathlib import Path

G = Path(".thesis-corpus/gaps")


def load(name):
    p = G / name
    if not p.exists():
        return {}
    text = p.read_text(encoding="utf-8").strip()
    if text.startswith("```"):  # tolerate a fenced reply
        text = text.strip("`").removeprefix("json").strip()
    return json.loads(text).get("gaps", {})


def main():
    review = json.loads((G / "review.json").read_text(encoding="utf-8"))["clusters"]
    a, b = load("codex_review_A.json"), load("codex_review_B.json")
    rows, agree_a = [], 0
    for gid, c in review.items():
        if c.get("verdict") != "SPECIFIC_GAP":
            continue
        ca, cb = a.get(gid, {}), b.get(gid, {})
        same = ca.get("refutation") == c["refutation"]
        agree_a += same
        rows.append({"gap": gid, "mine": c["refutation"], "mine_crowded": c["crowded"],
                     "codex_A": ca.get("refutation"), "codex_A_crowded": ca.get("crowded"),
                     "codex_B": cb.get("refutation"), "codex_B_agree": cb.get("agree"),
                     "codex_A_evidence": len(ca.get("evidence", [])),
                     "note_A": ca.get("note"), "note_B": cb.get("note")})
    (G / "review_comparison.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"part A same verdict: {agree_a}/{len(rows)}; missing in A: {[r['gap'] for r in rows if not r['codex_A']]}")
    for r in rows:
        flag = "" if r["codex_A"] == r["mine"] else "  <-- A differs"
        print(f"{r['gap']} mine={r['mine']:<9} A={str(r['codex_A']):<9} B={str(r['codex_B']):<9} B_agree={r['codex_B_agree']}{flag}")


if __name__ == "__main__":
    main()
