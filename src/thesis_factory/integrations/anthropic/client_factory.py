import os

from anthropic import Anthropic


def create_anthropic_client() -> Anthropic:
    workspace_id = os.environ.get(
        "ANTHROPIC_WORKSPACE_ID"
    )

    if workspace_id is None:
        return Anthropic()

    normalized_workspace_id = (
        workspace_id.strip()
    )

    if not normalized_workspace_id:
        return Anthropic()

    return Anthropic(
        default_headers={
            "anthropic-workspace-id": (
                normalized_workspace_id
            ),
        }
    )
