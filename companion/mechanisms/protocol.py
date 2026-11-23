"""The deliberately small MCP profile used by the ESA stdio demonstration."""
PROTOCOL = "2026-07-28"
PREFIX = "io.modelcontextprotocol/"
SERVER_INFO = {"name": "esa-policy-example", "version": "2.0.0"}
CLIENT_INFO = {"name": "esa-observation-client", "version": "2.0.0"}


def request_meta():
    return {PREFIX + "protocolVersion": PROTOCOL,
            PREFIX + "clientInfo": dict(CLIENT_INFO),
            PREFIX + "clientCapabilities": {}}


def completed_result(**fields):
    return {"resultType": "complete", **fields,
            "_meta": {PREFIX + "serverInfo": dict(SERVER_INFO)}}
