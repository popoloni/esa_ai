"""One fixed, synthetic catalog lookup shared by the CLI and MCP example."""
from pathlib import Path
from hashlib import sha256
import json

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "reader_side/evolution/policy_catalog.json"
ALLOWED = frozenset({"BR-001/v1", "BR-001/v2"})


def lookup(policy_id):
    if not isinstance(policy_id, str) or policy_id not in ALLOWED:
        return {"ok": False, "error": {"code": "UNKNOWN_POLICY", "message": "Choose BR-001/v1 or BR-001/v2. No file path is accepted."}}
    if any(p.is_symlink() for p in [CATALOG, CATALOG.parent, CATALOG.parent.parent, ROOT]):
        raise ValueError("catalog path contains a symlink")
    raw = CATALOG.read_bytes()
    catalog = json.loads(raw)
    return {"ok": True, "policy": catalog["policies"][policy_id],
            "boundary": catalog["boundary"], "authority": catalog["authority"],
            "source": {"path": CATALOG.relative_to(ROOT).as_posix(), "sha256": sha256(raw).hexdigest()}}
