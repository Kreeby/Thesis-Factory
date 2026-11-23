"""Quote matching used by the refutation gate (scripts/gap_*.py): a quote counts as verified only if it
occurs in the source after whitespace/typography normalisation, and a changed word must still fail."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from gap_apply_refutation import norm as apply_norm  # noqa: E402
from gap_verify_codex_quotes import found  # noqa: E402


def test_web_match_tolerates_pdf_typography_but_not_changed_words():
    page = "We can systematically evaluate the perfor-\n mance without having “ground truth” explanations"
    assert found("evaluate the performance without having \"ground truth\"", page)  # split word re-joined
    assert found("a well-known result", "a well-\nknown result")  # real hyphen kept
    assert not found("evaluate the performance with \"ground truth\"", page)


def test_apply_norm_collapses_whitespace_only():
    text = "only 21%   of these\nmethods have been user tested"
    assert apply_norm("only 21% of these methods") in apply_norm(text)
    assert apply_norm("only 25% of these methods") not in apply_norm(text)
