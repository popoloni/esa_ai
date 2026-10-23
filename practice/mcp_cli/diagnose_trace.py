#!/usr/bin/env python3
"""Classify this exercise's retained MCP trace without launching an SDK or host.

Use inspect_trace.py for the frozen modern request-sequence check. This reader
instead explains what the available evidence does and does not diagnose.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys


def load_lines(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def diagnose(directory):
    directory = Path(directory)
    receipt = json.loads((directory / "COMPARISON.json").read_text())
    requests = load_lines(directory / "client_to_server.jsonl")
    responses = load_lines(directory / "server_to_client.jsonl")
    issues = []
    for name in ["client_to_server.jsonl", "server_to_client.jsonl"]:
        identity = receipt.get("evidence_files", {}).get(name, {})
        path = directory / name
        if identity.get("sha256") != sha256(path.read_bytes()).hexdigest():
            issues.append("TRACE_IDENTITY_MISMATCH:" + name)
    response_by_id = {item.get("id"): item for item in responses}
    request_ids = [item.get("id") for item in requests if "id" in item]
    response_ids = [item.get("id") for item in responses]
    if len(response_ids) != len(set(response_ids)):
        issues.append("DUPLICATE_RESPONSE_ID")
    if any(value not in request_ids for value in response_ids):
        issues.append("UNSOLICITED_RESPONSE_ID")
    opening = [item for item in requests if item.get("method") in {"initialize", "server/discover"}]
    answered = [item for item in opening if item.get("id") in response_by_id]
    if not opening:
        opening_status = "OPENING_REQUEST_NOT_RETAINED"
    elif not answered:
        opening_status = "NO_OPENING_RESPONSE_STARTUP_OR_TRANSPORT_UNRESOLVED"
    elif any("error" in response_by_id[item["id"]] for item in answered):
        opening_status = "OPENING_PROTOCOL_ERROR"
    else:
        opening_status = "OPENING_RESPONSE_OBSERVED"
    listed = []
    for item in requests:
        if item.get("method") == "tools/list":
            result = response_by_id.get(item.get("id"), {}).get("result", {})
            listed += [tool.get("name") for tool in result.get("tools", [])]
    calls = []
    for request in requests:
        if request.get("method") != "tools/call":
            continue
        response = response_by_id.get(request.get("id"))
        params = request.get("params", {})
        arguments = params.get("arguments") if isinstance(params, dict) else None
        if response is None:
            classification = "CALL_RESPONSE_NOT_RETAINED"
        elif "error" in response:
            classification = "PROTOCOL_ERROR"
        else:
            result = response.get("result", {})
            structured = result.get("structuredContent", {})
            policy_id = arguments.get("policy_id") if isinstance(arguments, dict) else None
            invalid_input = not isinstance(policy_id, str)
            if result.get("isError") is True:
                classification = ("SCHEMA_INVALID_ARGUMENT_REJECTED" if invalid_input
                                  else "TOOL_EXECUTION_ERROR_REQUIRES_DIAGNOSIS")
            elif isinstance(structured, dict) and structured.get("ok") is False:
                classification = "DOMAIN_REFUSAL"
            elif isinstance(structured, dict) and structured.get("ok") is True:
                classification = "DOMAIN_SUCCESS"
            else:
                classification = "UNCLASSIFIED_RESULT_INSPECT_RAW_CONTENT"
        calls.append({"request_id": request.get("id"), "arguments": arguments,
                      "classification": classification})
    return {
        "schema": "mcp-teaching-trace-diagnosis/v1",
        "status": "PASS_RETAINED_TRACE_DIAGNOSIS" if not issues else "FAIL_TRACE_IDENTITY",
        "issues": issues,
        "opening": {"methods": [item.get("method") for item in opening],
                    "classification": opening_status},
        "loaded_tools_in_sdk_trace": listed,
        "tool_discovery": "EXPECTED_TOOL_DISCOVERED" if "lookup_policy" in listed else "EXPECTED_TOOL_NOT_OBSERVED",
        "calls": calls,
        "process_startup": "NOT_PROVEN_BY_AN_UNANSWERED_REQUEST" if not responses else "RESPONSES_OBSERVED",
        "named_host_run": "NOT_RUN_BY_THIS_INSPECTION",
        "model_tool_selection": "NOT_ESTABLISHED",
        "process_boundaries": "NOT_ESTABLISHED_BY_TRACE_OR_READ_ONLY_SCHEMA",
        "scope": "Classification of retained exercise messages; no new connection, token measurement or native-host certification.",
        "input_sha256": {name: sha256((directory / name).read_bytes()).hexdigest()
                         for name in ["COMPARISON.json", "client_to_server.jsonl", "server_to_client.jsonl"]},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        result = diagnose(args.directory)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        result = {"status": "FAIL_INPUT", "issues": [str(exc)]}
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS_RETAINED_TRACE_DIAGNOSIS" else 1


if __name__ == "__main__":
    sys.exit(main())
