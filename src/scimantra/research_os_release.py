"""Phase 120: Research OS production release metadata and gate."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

VERSION = "1.0.0"
RELEASE_CHANNEL = "production"


def release_manifest(health: dict[str, Any], beta: dict[str, Any]) -> dict[str, Any]:
    return {
        "product": "SciMantra Research OS",
        "version": VERSION,
        "channel": RELEASE_CHANNEL,
        "released_at": datetime.now(timezone.utc).isoformat(),
        "health_ready": bool(health.get("ready")),
        "beta_ready": bool(beta.get("ready")),
        "release_ready": bool(health.get("ready")) and bool(beta.get("ready")),
        "scope": "Research workflow coordination, provenance, evidence linkage, decision support, and project persistence",
        "limitations": [
            "Does not certify scientific validity or novelty",
            "Does not guarantee publication acceptance",
            "AI outputs require researcher review",
        ],
    }
