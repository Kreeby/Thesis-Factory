"""Fetch each Codex evidence source and check its quote verbatim (whitespace/quote-mark normalised).

Downloads go to a separate directory and are only converted to text (pdftotext / tag strip).
Result per item: VERIFIED, NOT_FOUND (page read, quote absent), UNREADABLE (fetch blocked/failed).
Usage: ./scripts/uv run python scripts/gap_verify_codex_quotes.py codex_review_A.json <download_dir>"""
import hashlib, html, json, re, subprocess, sys
from pathlib import Path

import httpx

G = Path(".thesis-corpus/gaps")


def norm(s, join_hyphens=False):
    s = html.unescape(s).replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("‐", "-").replace("‑", "-").replace("–", "-").replace("—", "-").replace("­", "")
    # PDF line-break hyphenation: "perfor-\nmance" is a split word, "well-\nknown" a real hyphen; callers try both
    s = re.sub(r"-\s+", "" if join_hyphens else "-", s)
    return " ".join(s.split()).lower()


def found(quote, text):
    return any(norm(quote) in norm(text, join_hyphens=j) for j in (False, True))


def page_text(url, dl, client):
    url = url.replace("arxiv.org/abs/", "arxiv.org/pdf/")  # abstract pages lack the full text
    if url.startswith("10."):
        url = "https://doi.org/" + url
    r = client.get(url)
    if r.status_code != 200 or not r.content:
        return None, f"HTTP {r.status_code}"
    f = dl / hashlib.sha256(url.encode()).hexdigest()[:16]
    if r.content[:5] == b"%PDF-":
        f.with_suffix(".pdf").write_bytes(r.content)
        out = subprocess.run(["pdftotext", str(f.with_suffix(".pdf")), "-"], capture_output=True)
        return out.stdout.decode("utf-8", "replace"), "pdf"
    t = r.text
    f.with_suffix(".html").write_text(t, encoding="utf-8")
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    # shortcut: <3000 visible chars treated as a bot-challenge page (MDPI/AAAI/Springer gave ~1.4k); upgrade with a browser fetch
    if len(" ".join(t.split())) < 3000:
        return None, "bot/challenge page"
    return t, "html"


def main():
    src, dl = G / sys.argv[1], Path(sys.argv[2])
    dl.mkdir(parents=True, exist_ok=True)
    data = json.loads(src.read_text(encoding="utf-8"))
    cache, counts = {}, {}
    with httpx.Client(follow_redirects=True, timeout=40, headers={"User-Agent": "Mozilla/5.0"}) as client:
        for gid, g in data["gaps"].items():
            for e in g.get("evidence", []):
                url = e.get("doi_or_url") or ""
                if url not in cache:
                    try:
                        cache[url] = page_text(url, dl, client)
                    except Exception as ex:  # one bad source must not stop the rest
                        cache[url] = (None, type(ex).__name__)
                text, how = cache[url]
                if text is None:
                    e["check"] = f"UNREADABLE ({how})"
                elif found(e.get("quote", ""), text):
                    e["check"] = "VERIFIED"
                else:
                    e["check"] = f"NOT_FOUND ({how})"
                k = e["check"].split()[0]
                counts[k] = counts.get(k, 0) + 1
                print(gid, e["check"], url[:80])
    src.with_name(src.stem + ".checked.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(counts)


if __name__ == "__main__":
    main()
