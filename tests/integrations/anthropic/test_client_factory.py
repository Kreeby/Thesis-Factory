from unittest.mock import patch

from thesis_factory.integrations.anthropic.client_factory import (
    create_anthropic_client,
)


def test_client_factory_uses_workspace_header(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "ANTHROPIC_WORKSPACE_ID",
        "wrkspc_test",
    )

    with patch(
        "thesis_factory.integrations.anthropic."
        "client_factory.Anthropic"
    ) as anthropic:
        create_anthropic_client()

    anthropic.assert_called_once_with(
        default_headers={
            "anthropic-workspace-id": (
                "wrkspc_test"
            ),
        }
    )


def test_client_factory_omits_workspace_header(
    monkeypatch,
) -> None:
    monkeypatch.delenv(
        "ANTHROPIC_WORKSPACE_ID",
        raising=False,
    )

    with patch(
        "thesis_factory.integrations.anthropic."
        "client_factory.Anthropic"
    ) as anthropic:
        create_anthropic_client()

    anthropic.assert_called_once_with()
