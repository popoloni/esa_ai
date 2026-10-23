#!/usr/bin/env python3
"""Retain one actual command and before/after file inventories from a declared task.

Not a sandbox. Use a disposable source copy and synthetic inputs. A command may
have wider effects than the selected inventory can see. No human/model metrics
are inferred. Read the task JSON before running it; argv is executed literally.
"""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import json
import platform
import subprocess
import sys
import time


def inventory(root):
    result = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part in {".git", ".venv", "node_modules", "__pycache__"} for part in rel.parts) or path.suffix == ".pyc":
            continue
        if path.is_symlink():
            result[rel.as_posix()] = "SYMLINK:" + str(path.readlink())
        elif path.is_file():
            result[rel.as_posix()] = sha256(path.read_bytes()).hexdigest()
    return result


def run(spec_path, output):
    raw = spec_path.read_bytes(); spec = json.loads(raw)
    argv = spec["argv"]
    if not isinstance(argv, list) or not argv or not all(isinstance(v, str) and "\0" not in v for v in argv):
        raise ValueError("argv must be a nonempty array of literal strings")
    root = Path(spec["inventory_root"]).resolve(strict=True)
    cwd = Path(spec["cwd"]).resolve(strict=True)
    if not cwd.is_relative_to(root):
        raise ValueError("cwd must be inside inventory_root")
    allowed = set(spec.get("allowed_changed_files", []))
    for rel in allowed:
        parsed = PurePosixPath(rel)
        if parsed.is_absolute() or ".." in parsed.parts or str(parsed) != rel:
            raise ValueError("allowed changes must be canonical relative file paths")
    if output.exists() or output.is_symlink() or output.resolve().is_relative_to(root):
        raise ValueError("choose a NEW output directory outside the inventoried tree")
    output.mkdir(parents=True, exist_ok=False)
    (output / "TASK.json").write_bytes(raw)
    before = inventory(root)
    record = {"schema": "observed-command/v1", "origin": spec.get("origin", "local_cli"),
              "tool": spec.get("tool"), "tool_version": spec.get("tool_version"),
              "model": spec.get("model"), "human_review": "PENDING",
              "argv": argv, "cwd": str(cwd), "inventory_root": str(root),
              "python": platform.python_version(), "platform": platform.platform(),
              "started_at_utc": datetime.now(timezone.utc).isoformat(),
              "task_sha256": sha256(raw).hexdigest(), "before": before,
              "allowed_changed_files": sorted(allowed), "os_isolation": "NOT_ESTABLISHED",
              "human_effort_seconds": None, "billable_cost": None, "tokens": None}
    start = time.perf_counter()
    with (output / "stdout.txt").open("xb") as stdout, (output / "stderr.txt").open("xb") as stderr:
        try:
            result = subprocess.run(argv, cwd=cwd, stdout=stdout, stderr=stderr,
                                    timeout=spec.get("timeout_seconds", 120), check=False)
            record["exit_code"] = result.returncode
        except subprocess.TimeoutExpired:
            record.update(exit_code=124, execution_error="TIMEOUT")
        except OSError as exc:
            record.update(exit_code=127, execution_error=type(exc).__name__ + ": " + str(exc))
    record["duration_seconds"] = time.perf_counter() - start
    record["ended_at_utc"] = datetime.now(timezone.utc).isoformat()
    after = inventory(root); record["after"] = after
    changed = sorted(rel for rel in set(before) | set(after) if before.get(rel) != after.get(rel))
    record["changed_files"] = changed
    record["out_of_scope_changes"] = sorted(set(changed) - allowed)
    record["status"] = "OBSERVED_WITH_FINDINGS" if record["exit_code"] != 0 or record["out_of_scope_changes"] else "OBSERVED_COMMAND_SUCCESS"
    record["evidence_sha256"] = {p.name: sha256(p.read_bytes()).hexdigest() for p in output.iterdir() if p.is_file()}
    (output / "RECEIPT.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"status": record["status"], "exit_code": record["exit_code"], "changed_files": changed,
                      "out_of_scope_changes": record["out_of_scope_changes"], "receipt": str(output / "RECEIPT.json")}, indent=2))
    return 0 if record["status"] == "OBSERVED_COMMAND_SUCCESS" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        return run(args.spec, args.output)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    sys.exit(main())
