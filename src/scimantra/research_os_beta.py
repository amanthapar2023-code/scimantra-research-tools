"""Phase 119: beta release gate helpers."""
from __future__ import annotations
from typing import Any

REQUIRED_CHECKS = [
    "Core workflow tested",
    "Cloud persistence tested",
    "Authentication/project isolation tested",
    "Export/import tested",
    "Research OS health page reviewed",
    "Sample project completed end-to-end",
    "Privacy/secret configuration reviewed",
    "User feedback channel prepared",
]


def gate(health: dict[str, Any], checks: dict[str, bool]) -> dict[str, Any]:
    missing = [name for name in REQUIRED_CHECKS if not checks.get(name, False)]
    failures = int(health.get("failures", 0))
    return {"ready": failures == 0 and not missing, "missing_checks": missing, "health_failures": failures, "completed": len(REQUIRED_CHECKS) - len(missing), "total": len(REQUIRED_CHECKS)}
