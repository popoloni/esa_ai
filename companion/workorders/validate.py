#!/usr/bin/env python3
"""Validate ESA EDOD/1 orders with the standard library.

This implements the keywords used by schema.json, not a general JSON Schema
engine. Structural validity does not approve the authority, budget or result.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
SCHEMA = json.loads((ROOT / "schema.json").read_text())


def validate(value, specification=None, path="$", errors=None):
    specification = SCHEMA if specification is None else specification
    errors = [] if errors is None else errors
    if "$ref" in specification:
        target = SCHEMA
        for component in specification["$ref"].removeprefix("#/").split("/"):
            target = target[component]
        return validate(value, target, path, errors)
    kind = specification.get("type")
    matches = {
        "object": type(value) is dict,
        "array": type(value) is list,
        "string": type(value) is str,
        "integer": type(value) is int,
        "boolean": type(value) is bool,
    }
    if kind and not matches[kind]:
        errors.append(f"{path}: expected {kind}")
        return errors
    if "const" in specification and value != specification["const"]:
        errors.append(f"{path}: incorrect constant")
    if "enum" in specification and value not in specification["enum"]:
        errors.append(f"{path}: value outside enum")
    if kind == "string":
        if len(value) < specification.get("minLength", 0):
            errors.append(f"{path}: empty or too short")
        if "pattern" in specification and not re.search(
                specification["pattern"], value):
            errors.append(f"{path}: pattern mismatch")
    elif kind == "integer":
        if value < specification.get("minimum", value):
            errors.append(f"{path}: below minimum")
        if value > specification.get("maximum", value):
            errors.append(f"{path}: above maximum")
    elif kind == "array":
        if len(value) < specification.get("minItems", 0):
            errors.append(f"{path}: too few items")
        if specification.get("uniqueItems"):
            encoded = [json.dumps(x, sort_keys=True) for x in value]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{path}: duplicate items")
        for index, item in enumerate(value):
            validate(item, specification["items"], f"{path}[{index}]", errors)
    elif kind == "object":
        properties = specification.get("properties", {})
        for key in specification.get("required", []):
            if key not in value:
                errors.append(f"{path}.{key}: required")
        if specification.get("additionalProperties") is False:
            for key in value.keys() - properties.keys():
                errors.append(f"{path}.{key}: unknown field")
        for key in value.keys() & properties.keys():
            validate(value[key], properties[key], f"{path}.{key}", errors)
    return errors


def validate_order(order):
    errors = validate(order)
    if errors:
        return errors
    delegate = order["delegate"]
    for writable in delegate["editable_paths"]:
        for protected in delegate["protected_paths"]:
            if writable.rstrip("/") == protected.rstrip("/") or (
                    protected.endswith("/") and writable.startswith(protected)) or (
                    writable.endswith("/") and protected.startswith(writable)):
                errors.append("$.delegate: editable and protected scopes overlap")
    for check in order["observe"]["checks"]:
        if check["method"] == "command" and not check["argv"]:
            errors.append(f"$.observe: {check['id']} has no command")
        if check["method"] == "review" and check["argv"]:
            errors.append(f"$.observe: {check['id']} confuses review and command")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true")
    group.add_argument("--file", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    paths = sorted((ROOT / "orders").glob("*.json")) if args.all else [args.file]
    rows = []
    for path in paths:
        data = path.read_bytes()
        errors = validate_order(json.loads(data))
        rows.append({"path": str(path), "sha256": hashlib.sha256(data).hexdigest(),
                     "status": "FAIL" if errors else "PASS", "errors": errors})
    report = {"schema": "esa-workorder-validation/v1",
              "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
              "status": "PASS" if rows and all(
                  r["status"] == "PASS" for r in rows) else "FAIL",
              "orders_checked": len(rows), "results": rows,
              "scope": "Structure and internal consistency; not execution or approval."}
    encoded = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x") as stream:
            stream.write(encoded)
    print(encoded, end="")
    return int(report["status"] != "PASS")


if __name__ == "__main__":
    sys.exit(main())
