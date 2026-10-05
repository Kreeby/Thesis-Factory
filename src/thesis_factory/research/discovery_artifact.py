import json
from pathlib import Path

from pydantic import TypeAdapter

from thesis_factory.domain.web_research import (
    ResearchLeadSet,
)
from thesis_factory.research.proposal_verification_planning import (
    DiscoveryArtifact,
    DiscoveryObjective,
)


class DiscoveryArtifactError(ValueError):
    pass


_LEAD_SET_ADAPTER = TypeAdapter(
    tuple[ResearchLeadSet, ...]
)


def load_discovery_artifact(path: Path) -> DiscoveryArtifact:
    payload = json.loads(
        path.read_text(encoding="utf-8")
    )

    if not isinstance(payload, dict):
        raise DiscoveryArtifactError(
            "discovery artifact must be a JSON object"
        )

    topic = payload.get("topic")
    if not isinstance(topic, str) or not topic.strip():
        raise DiscoveryArtifactError(
            "discovery artifact has no topic"
        )

    raw_packets = payload.get("packets")
    raw_lead_sets = payload.get("lead_sets")

    if not isinstance(raw_packets, list):
        raise DiscoveryArtifactError(
            "discovery artifact has no packets"
        )
    if not isinstance(raw_lead_sets, list):
        raise DiscoveryArtifactError(
            "discovery artifact has no lead_sets"
        )
    if len(raw_packets) != len(raw_lead_sets):
        raise DiscoveryArtifactError(
            "packets and lead_sets must have the same length"
        )

    lead_sets = _LEAD_SET_ADAPTER.validate_python(
        tuple(raw_lead_sets)
    )

    objectives: list[DiscoveryObjective] = []
    all_lead_ids: list[str] = []

    for index, (packet, lead_set) in enumerate(
        zip(raw_packets, lead_sets, strict=True),
        start=1,
    ):
        if not isinstance(packet, dict):
            raise DiscoveryArtifactError(
                f"packet {index} must be an object"
            )

        packet_objective = packet.get("objective")
        if (
            not isinstance(packet_objective, str)
            or not packet_objective.strip()
        ):
            raise DiscoveryArtifactError(
                f"packet {index} has no objective"
            )

        raw_citations = packet.get("citations")
        if not isinstance(raw_citations, list):
            raise DiscoveryArtifactError(
                f"packet {index} has no citations"
            )

        citation_ids = {
            citation.get("citation_id")
            for citation in raw_citations
            if isinstance(citation, dict)
        }

        for lead in lead_set.leads:
            missing = (
                set(lead.source_citation_ids)
                - citation_ids
            )
            if missing:
                raise DiscoveryArtifactError(
                    f"lead {lead.lead_id} references missing "
                    f"citation ids: {sorted(missing)}"
                )
            all_lead_ids.append(lead.lead_id)

        objectives.append(
            DiscoveryObjective(
                objective=packet_objective.strip(),
                leads=lead_set.leads,
            )
        )

    if len(all_lead_ids) != len(set(all_lead_ids)):
        raise DiscoveryArtifactError(
            "discovery lead ids must be globally unique"
        )

    return DiscoveryArtifact(
        topic=topic.strip(),
        objectives=tuple(objectives),
    )
