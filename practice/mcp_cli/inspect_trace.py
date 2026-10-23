#!/usr/bin/env python3
"""Check the retained exercise's modern MCP wire exchange, without an SDK.

This is a trace-specific check, not a general protocol conformance validator.
It neither launches a coding host nor establishes a process sandbox.
"""
import argparse
import hashlib
import json
from pathlib import Path

PREFIX = "io.modelcontextprotocol/"


def inspect(directory):
    directory = Path(directory)
    paths = [directory / n for n in
             ("COMPARISON.json", "client_to_server.jsonl", "server_to_client.jsonl")]
    receipt = json.loads(paths[0].read_text())
    requests = [json.loads(line) for line in paths[1].read_text().splitlines() if line.strip()]
    responses = [json.loads(line) for line in paths[2].read_text().splitlines() if line.strip()]
    issues = []
    if receipt.get("protocol_version") != "2026-07-28":
        issues.append("RECEIPT_IS_NOT_THE_MODERN_EXERCISE")
    methods = [r.get("method") for r in requests]
    if methods != ["server/discover", "tools/list", *["tools/call"] * 4]:
        issues.append("UNEXPECTED_EXERCISE_REQUEST_SEQUENCE")
    versions, clients = [], []
    for request in requests:
        meta = request.get("params", {}).get("_meta", {})
        versions.append(meta.get(PREFIX + "protocolVersion"))
        clients.append(meta.get(PREFIX + "clientInfo"))
        if meta.get(PREFIX + "protocolVersion") != "2026-07-28":
            issues.append(f"VERSION_METADATA_MISSING_OR_CHANGED:{request.get('id')}")
        if not isinstance(meta.get(PREFIX + "clientCapabilities"), dict):
            issues.append(f"CAPABILITIES_METADATA_MISSING:{request.get('id')}")
    request_ids = [r.get("id") for r in requests]
    response_ids = [r.get("id") for r in responses]
    if (len(set(request_ids)) != len(request_ids)
            or sorted(request_ids, key=str) != sorted(response_ids, key=str)):
        issues.append("REQUEST_RESPONSE_IDS_DO_NOT_MATCH_ONCE_EACH")
    by_id = {r.get("id"): r for r in responses}
    discovery = by_id.get(request_ids[0], {}).get("result", {}) if request_ids else {}
    if "2026-07-28" not in discovery.get("supportedVersions", []):
        issues.append("DISCOVERY_DOES_NOT_ADVERTISE_SELECTED_VERSION")
    for response in responses:
        if response.get("result", {}).get("resultType") != "complete":
            issues.append(f"UNEXPECTED_RESULT_TYPE:{response.get('id')}")
    return {
        "schema": "mcp-exercise-trace-inspection/v1",
        "status": "PASS" if not issues else "FAIL", "issues": issues,
        "request_methods": methods, "request_count": len(requests),
        "response_count": len(responses), "per_request_versions": versions,
        "sdk_distribution_version": receipt.get("mcp_version"),
        "wire_client_info": clients[0] if clients else None,
        "discovery_supported_versions": discovery.get("supportedVersions"),
        "legacy_initialize_observed": "initialize" in methods,
        "files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        "scope": "Inspection of retained bytes; no new SDK or named-host run.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        result = inspect(args.directory)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        result = {"status": "FAIL", "issues": [str(exc)]}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
