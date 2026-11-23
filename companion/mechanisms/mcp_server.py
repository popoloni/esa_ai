#!/usr/bin/env python3
"""Bounded MCP 2026-07-28 stdio example: fixed-source, read-only tool calls."""
import json
import sys

from policy_tool import INPUT_SCHEMA, SOURCE_IDS, read_policy
from protocol import PREFIX, PROTOCOL, completed_result

TOOL = {
    "name": "read_policy",
    "description": "Read an approved rule or an unapproved proposal with provenance.",
    "inputSchema": INPUT_SCHEMA,
    "annotations": {"readOnlyHint": True},
}


def reply(request_id, result=None, error=None):
    message = {"jsonrpc": "2.0"}
    if request_id is not None:
        message["id"] = request_id
    message["error" if error is not None else "result"] = error if error is not None else result
    print(json.dumps(message, ensure_ascii=False, separators=(",", ":")), flush=True)


def tool_error(text):
    return completed_result(content=[{"type": "text", "text": text}], isError=True)


def handle(request):
    if (not isinstance(request, dict) or request.get("jsonrpc") != "2.0"
            or not isinstance(request.get("method"), str)):
        reply(None, error={"code": -32600, "message": "Invalid Request"})
        return
    if "id" not in request:
        # This bounded synchronous server has no outstanding work to cancel.
        return
    request_id = request["id"]
    if not isinstance(request_id, (str, int)) or isinstance(request_id, bool):
        reply(None, error={"code": -32600, "message": "Invalid Request"})
        return
    params = request.get("params")
    meta = params.get("_meta") if isinstance(params, dict) else None
    if (not isinstance(meta, dict)
            or not isinstance(meta.get(PREFIX + "protocolVersion"), str)
            or not isinstance(meta.get(PREFIX + "clientCapabilities"), dict)):
        reply(request_id, error={"code": -32602,
              "message": "Required request metadata missing; supported MCP: " + PROTOCOL})
        return
    version = meta[PREFIX + "protocolVersion"]
    if version != PROTOCOL:
        reply(request_id, error={"code": -32022, "message": "Unsupported protocol version",
              "data": {"supported": [PROTOCOL], "requested": version}})
        return
    info = meta.get(PREFIX + "clientInfo")
    if info is not None and (not isinstance(info, dict) or
            not all(isinstance(info.get(k), str) for k in ("name", "version"))):
        reply(request_id, error={"code": -32602, "message": "Invalid clientInfo"})
        return
    method = request["method"]
    print("mcp: " + method, file=sys.stderr, flush=True)
    if method == "server/discover":
        reply(request_id, completed_result(
            supportedVersions=[PROTOCOL], capabilities={"tools": {"listChanged": False}},
            ttlMs=300000, cacheScope="public"))
    elif method == "tools/list":
        if params.get("cursor") is not None:
            reply(request_id, error={"code": -32602, "message": "No pagination cursor is issued"})
        else:
            reply(request_id, completed_result(tools=[TOOL], ttlMs=300000, cacheScope="public"))
    elif method == "tools/call":
        if not isinstance(params.get("name"), str):
            reply(request_id, error={"code": -32602, "message": "Tool name must be a string"})
            return
        if params["name"] != "read_policy":
            reply(request_id, error={"code": -32602, "message": "Unknown tool: " + params["name"]})
            return
        arguments = params.get("arguments", {})
        if not isinstance(arguments, dict):
            reply(request_id, error={"code": -32602, "message": "Tool arguments must be an object"})
            return
        if set(arguments) != {"source_id"} or not isinstance(arguments["source_id"], str):
            reply(request_id, tool_error("Use exactly one string argument named source_id."))
            return
        source_id = arguments["source_id"]
        if source_id not in SOURCE_IDS:
            reply(request_id, tool_error("Unknown source_id. Allowed: BR-001/v1, legacy-note-001."))
            return
        try:
            result = completed_result(**read_policy(source_id))
        except (OSError, UnicodeError, ValueError) as error:
            result = tool_error("Source unavailable: " + type(error).__name__)
        reply(request_id, result)
    else:
        reply(request_id, error={"code": -32601,
              "message": "Method not found; supported MCP: " + PROTOCOL})


def main():
    for line in sys.stdin:
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            reply(None, error={"code": -32700, "message": "Parse error"})
        else:
            handle(request)


if __name__ == "__main__":
    main()
