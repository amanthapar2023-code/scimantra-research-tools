"""Phase 118: production health and deployment readiness checks."""
from __future__ import annotations
from typing import Any


def check_environment(secrets: Any) -> dict[str, Any]:
    """Return safe deployment diagnostics without exposing secret values."""
    result = {"streamlit": True, "supabase_configured": False, "issues": []}
    try:
        from .cloud import configured
        result["supabase_configured"] = bool(configured(secrets))
    except Exception as exc:
        result["issues"].append(f"Cloud integration check failed: {type(exc).__name__}")
    return result


def check_bus(bus: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(bus, dict):
        return {"healthy": False, "issues": ["Research OS data bus is missing"]}
    try:
        from .research_os_data_bus import audit_bus
        audit = audit_bus(bus)
        issues = []
        if audit.get("duplicate_artifact_ids"): issues.append("Duplicate artifact IDs")
        if audit.get("broken_links"): issues.append("Broken artifact links")
        if audit.get("broken_provenance"): issues.append("Broken provenance references")
        return {"healthy": bool(audit.get("healthy")) and not issues, "issues": issues, "audit": audit}
    except Exception as exc:
        return {"healthy": False, "issues": [f"Bus audit failed: {type(exc).__name__}"]}


def readiness_report(secrets: Any, bus: dict[str, Any] | None = None) -> dict[str, Any]:
    environment = check_environment(secrets)
    bus_check = check_bus(bus)
    checks = [
        {"check": "Application runtime", "status": "PASS" if environment["streamlit"] else "FAIL"},
        {"check": "Research OS data bus", "status": "PASS" if bus_check["healthy"] else "WARN", "issues": bus_check["issues"]},
        {"check": "Supabase configuration", "status": "PASS" if environment["supabase_configured"] else "WARN", "issues": [] if environment["supabase_configured"] else ["Cloud persistence is not configured"]},
    ]
    failures = [x for x in checks if x["status"] == "FAIL"]
    warnings = [x for x in checks if x["status"] == "WARN"]
    return {"ready": not failures, "checks": checks, "failures": len(failures), "warnings": len(warnings), "environment": environment, "bus": bus_check}
