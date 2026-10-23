"""Small, explicit contracts for the deterministic harness-engineering exercise."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
COMPANION = ROOT.parents[1]
REQUIRED_FIELDS = ("route", "reason", "policy_version", "payment_authorized")
STRATEGIES = ("cached_estimate", "router_tool", "memorized_development")


def validate_tasks(tasks: dict) -> None:
    """Case IDs become artifact filenames; validate before creating probe paths."""
    seen = set()
    for phase in ("development", "held_out", "later_tasks"):
        cases = tasks.get(phase)
        if not isinstance(cases, list) or not cases:
            raise ValueError("Every task phase must contain a nonempty case list")
        for case in cases:
            if not isinstance(case, dict) or set(case) != {"case_id", "amount_eur"}:
                raise ValueError("Each task must contain exactly case_id and amount_eur")
            case_id = case["case_id"]
            if not isinstance(case_id, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", case_id):
                raise ValueError("Case ID must be a filesystem-safe identifier")
            if case_id in seen:
                raise ValueError("Case IDs must be unique across all task phases")
            if not isinstance(case["amount_eur"], str) or len(case["amount_eur"]) > 80:
                raise ValueError("Task amounts must be bounded strings")
            seen.add(case_id)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def config_digest(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


def validate_config(config: dict) -> None:
    """Only data/configuration is editable. No commands, paths or policy edits."""
    if not isinstance(config, dict) or set(config) != {
        "schema", "routing_strategy", "response_fields", "development_memory"
    }:
        raise ValueError("Harness keys must be exactly the four allowed configuration fields")
    if config["schema"] != "treasury-harness/v1":
        raise ValueError("Unsupported harness schema")
    if config["routing_strategy"] not in STRATEGIES:
        raise ValueError("Unknown routing strategy")
    fields = config["response_fields"]
    if not isinstance(fields, list) or not fields or len(fields) != len(set(fields)):
        raise ValueError("response_fields must be a nonempty list without duplicates")
    if not all(isinstance(x, str) and x in REQUIRED_FIELDS for x in fields):
        raise ValueError("Unsupported response field")
    memory = config["development_memory"]
    if not isinstance(memory, dict) or len(memory) > 16:
        raise ValueError("development_memory must be a bounded object")
    for amount, result in memory.items():
        if not isinstance(amount, str) or len(amount) > 80 or not isinstance(result, dict):
            raise ValueError("Invalid memory entry")
        if set(result) != set(REQUIRED_FIELDS):
            raise ValueError("A memory entry must contain the exact response contract")
        if result["payment_authorized"] is not False:
            raise ValueError("A routing observation cannot authorize a payment")
        if not all(isinstance(result[k], str) for k in REQUIRED_FIELDS[:3]):
            raise ValueError("Routing result fields must be strings")
    if config["routing_strategy"] != "memorized_development" and memory:
        raise ValueError("Only the explicit memorization control may carry task answers")


def create_output_directory(value: str) -> Path:
    """Fail on reuse or symlinked path components; never delete/overwrite a run."""
    raw = Path(value).expanduser().absolute()
    cursor = Path(raw.anchor)
    for part in raw.parts[1:]:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError("Output path contains a symlink")
    path = Path(os.path.abspath(raw))
    if path.exists():
        raise ValueError("Output directory already exists; choose a new directory")
    protected_roots = (COMPANION / "repo", COMPANION / "reader_side", ROOT / "fixtures", ROOT / "tests")
    if any(path.is_relative_to(protected) for protected in protected_roots):
        raise ValueError("Output cannot be placed inside protected source, fixtures or tests")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.mkdir()
    return path


def require_source_pins() -> dict:
    pins = read_json(ROOT / "fixtures/SOURCE_PINS.json")
    for rel, expected in pins["companion_files"].items():
        path = COMPANION / rel
        if not path.is_file() or path.is_symlink() or digest(path) != expected:
            raise ValueError(f"Source differs from the published exercise: {rel}")
    return pins

