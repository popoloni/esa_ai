"""Read two fixed teaching sources; never interpret an argument as a path."""
import hashlib
import json
from pathlib import Path

CONTEXT = Path(__file__).resolve().parents[1] / "context"
SOURCE_IDS = ("BR-001/v1", "legacy-note-001")
INPUT_SCHEMA = {
    "type": "object",
    "properties": {"source_id": {"type": "string", "enum": list(SOURCE_IDS)}},
    "required": ["source_id"],
    "additionalProperties": False,
}


def read_policy(source_id):
    if source_id == "BR-001/v1":
        metadata = json.loads((CONTEXT / "policy.json").read_text("utf-8"))
        path = CONTEXT / "BR-001.md"
        date = metadata["effective_date"]
    elif source_id == "legacy-note-001":
        path = CONTEXT / "legacy_note.json"
        metadata = json.loads(path.read_text("utf-8"))
        date = metadata["written_at"]
    else:
        raise ValueError("unknown source_id")
    if metadata["source_id"] != source_id:
        raise ValueError("source metadata does not match requested source_id")
    raw = path.read_bytes()
    return {
        "content": [{"type": "text", "text": raw.decode("utf-8")}],
        "structuredContent": {
            "source_id": source_id,
            "status": metadata["status"],
            "owner": metadata["owner"],
            "date": date,
            "sha256": hashlib.sha256(raw).hexdigest(),
        },
        "isError": False,
    }
