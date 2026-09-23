from thesis_factory.integrations.crossref.client import _abstract_text


def test_crossref_abstract_jats_is_normalized() -> None:
    raw = (
        "<jats:title>Abstract</jats:title>"
        "<jats:p>"
        "We apply machine-learning techniques to "
        "consumer credit risk."
        "</jats:p>"
    )

    assert _abstract_text(raw) == (
        "Abstract "
        "We apply machine-learning techniques to "
        "consumer credit risk."
    )


def test_missing_crossref_abstract_stays_missing() -> None:
    assert _abstract_text(None) is None