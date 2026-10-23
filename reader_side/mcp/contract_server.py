"""CP02 miniature *read-only* MCP stdio server (protocol-level educational subset).

Supports initialize, notifications/initialized, tools/list, tools/call (get_record).
No network, no dynamic path arguments, no filesystem writes. Not host-certified.
The process does run under the OS permissions of its launcher; a trusted host
must still review the startup command and isolate the server as appropriate.
"""
import json
import sys
from pathlib import Path

DATA_ROOT = Path(__file__).resolve().parent
RECORDS = {"contract": "contract_snapshot.json", "archived_note": "archived_note.json"}
PROTOCOL_VERSION = "2025-11-25"

def response(req):
    if not isinstance(req, dict) or req.get("jsonrpc") != "2.0":
        return {"jsonrpc": "2.0", "id": req.get("id") if isinstance(req,dict) else None,
                "error": {"code": -32600, "message": "Invalid request"}}
    rid = req.get("id")
    method = req.get("method")
    if rid is None:  # notifications get no responses
        return None
    if method == "initialize":
        params = req.get("params", {})
        requested = params.get("protocolVersion") if isinstance(params, dict) else None
        # Stable pinned version for this sample; a full SDK handles negotiation.
        return {"jsonrpc":"2.0","id":rid,"result": {
            "protocolVersion":PROTOCOL_VERSION,
            "capabilities":{"tools": {}},
            "serverInfo":{"name":"treasury-contract-teaching-fixture","version":"0.1.0"}}}
    if method == "ping":
        return {"jsonrpc":"2.0","id":rid,"result":{}}
    if method == "tools/list":
        return {"jsonrpc":"2.0","id":rid,"result":{"tools":[{
          "name":"get_record",
          "description":"Return one synthetic, source-labeled routing record by allowlisted ID; no file paths or writes.",
          "inputSchema":{"type":"object","properties":{"record":{"type":"string","enum":["contract","archived_note"]}},"required":["record"],"additionalProperties":False}
          }]}}
    if method == "tools/call":
        params=req.get("params", {})
        if not isinstance(params, dict):
            return {"jsonrpc":"2.0","id":rid,"error":{"code":-32602,"message":"Tool parameters must be an object"}}
        args=params.get("arguments", {})
        if params.get("name")!="get_record" or not isinstance(args,dict):
            return {"jsonrpc":"2.0","id":rid,"error":{"code":-32602,"message":"Invalid tool name or arguments"}}
        if (set(args)!={"record"} or not isinstance(args["record"], str)
                or args["record"] not in RECORDS):
            # A known tool's input-schema failure is a tool result, not a
            # malformed CallToolRequest (MCP 2025-11-25, Tools/Error Handling).
            return {"jsonrpc":"2.0","id":rid,"result":{"content":[{
                "type":"text","text":"get_record requires only record: contract or archived_note."}],
                "isError":True}}
        data=json.loads((DATA_ROOT/RECORDS[args["record"]]).read_text(encoding="utf-8"))
        # Explicitly expose provenance/authority labels as data. No special privileges implied.
        return {"jsonrpc":"2.0","id":rid,"result":{"content":[{"type":"text","text":json.dumps(data,sort_keys=True)}],"isError":False}}
    return {"jsonrpc":"2.0","id":rid,"error":{"code":-32601,"message":"Method not found"}}

def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            msg=json.loads(line)
            out=response(msg)
        except (ValueError, TypeError) as exc:
            out={"jsonrpc":"2.0","id":None,"error":{"code":-32700,"message":"Invalid JSON"}}
        if out is not None:
            sys.stdout.write(json.dumps(out,separators=(",",":"))+"\n")
            sys.stdout.flush()

if __name__=="__main__":
    main()
