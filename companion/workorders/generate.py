#!/usr/bin/env python3
"""Derive the 20 complete EDOD/1 orders and concise mission work orders."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

from validate import validate_order

ROOT = Path(__file__).resolve().parent
LABELS = {"bounded_repair": "Bounded repair",
          "new_capability": "New capability",
          "persistent_effect": "Persistent effect",
          "investigation": "Investigation"}


def quoted(values):
    return ", ".join(f"`{value}`" for value in values)


def printed(order):
    expect, delegate = order["expect"], order["delegate"]
    observe, decide = order["observe"], order["decide"]
    authority, budget = expect["authority"], delegate["budget"]
    # All named groups and fields are retained. The complete JSON has source
    # paths and executable argv; the printed references name the same checks.
    return "\n\n".join([
        f"**EDOD/1 work order {order['id']} — "
        f"{LABELS[order['evidence_profile']]}.**",
        "**Expect** — **outcome:** " + expect["outcome"]
        + " **authority:** " + authority["owner"] + ", "
        + authority["version"] + " (teaching contract). "
        + "**acceptance:** " + " ".join(expect["acceptance"]),
        "**Delegate** — **editable_paths:** "
        + quoted(delegate["editable_paths"]) + ". **protected_paths:** "
        + quoted(delegate["protected_paths"]) + ". **budget:** "
        + f"{budget['max_attempts']} attempts / "
        + f"{budget['implementation_minutes']} implementation minutes; "
        + f"{budget['check_timeout_seconds']} s per check process; "
        + f"{budget['max_external_calls']} external integration calls. "
        + "**stop_conditions:** " + " ".join(delegate["stop_conditions"]),
        "**Observe** — **checks:** "
        + quoted([check["id"] for check in observe["checks"]])
        + " (commands below). **receipt_fields:** "
        + quoted(observe["receipt_fields"]) + ".",
        "**Decide** — **owner:** " + decide["owner"]
        + " **object:** " + decide["object"]
        + " **allowed_decisions:** "
        + ", ".join(decide["allowed_decisions"]) + ".",
    ]) + "\n"


def main():
    registry = json.loads((ROOT / "registry.json").read_text())
    orders = registry["orders"]
    expected = {f"chapter_{n:02d}" for n in range(1, 13)} | {
        f"mission_{route}{n}" for route in "GB" for n in range(1, 5)}
    if {row["id"] for row in orders} != expected or len(orders) != 20:
        raise ValueError("Expected exactly 12 chapter and 8 mission orders")
    for row in orders:
        errors = validate_order(row)
        if errors:
            raise ValueError(row["id"] + ": " + "; ".join(errors))
    records = []
    for row in orders:
        target = ROOT / "orders" / (row["id"] + ".json")
        target.parent.mkdir(exist_ok=True)
        target.write_text(json.dumps(row, indent=2) + "\n")
        record = {"id": row["id"], "json": str(target.relative_to(ROOT)),
                  "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
        if row["id"].startswith("mission_"):
            target = ROOT / "printed" / (row["id"] + ".md")
            target.parent.mkdir(exist_ok=True)
            target.write_text(printed(row))
            record.update(printed=str(target.relative_to(ROOT)),
                          printed_sha256=hashlib.sha256(
                              target.read_bytes()).hexdigest())
        records.append(record)
    (ROOT / "PROVENANCE.json").write_text(json.dumps({
        "schema": "esa-edod-workorder-derivation/v1",
        "registry_sha256": hashlib.sha256(
            (ROOT / "registry.json").read_bytes()).hexdigest(),
        "schema_sha256": hashlib.sha256(
            (ROOT / "schema.json").read_bytes()).hexdigest(),
        "records": records,
        "claim": "Authored task specifications; no execution or approval is inferred."
    }, indent=2) + "\n")
    print(json.dumps({"status": "VALID_AND_DERIVED", "orders": len(records)}))


if __name__ == "__main__":
    sys.exit(main())
