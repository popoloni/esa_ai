"""Retain an actual non-conflicting Git merge that violates an output contract.

These two contributions and the repair are authored teaching fixtures. This
runner executes them; it does not represent a live agent or a human review.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def now():
    return datetime.now(timezone.utc).isoformat()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path,
                        help="New output directory outside this supplied exercise")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if output.exists() or args.output.is_symlink():
        parser.error("--output already exists; preserve it and choose a new directory")
    if output.is_relative_to(HERE):
        parser.error("keep generated evidence outside the supplied exercise")
    output.mkdir(parents=True, exist_ok=False)
    repo = output / "repository"
    repo.mkdir()
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env.update(PYTHONDONTWRITEBYTECODE="1", GIT_CONFIG_NOSYSTEM="1",
               GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT="0",
               GIT_AUTHOR_NAME="Authored teaching scenario",
               GIT_AUTHOR_EMAIL="teaching@example.invalid",
               GIT_COMMITTER_NAME="Authored teaching scenario",
               GIT_COMMITTER_EMAIL="teaching@example.invalid",
               GIT_AUTHOR_DATE="2026-10-22T00:00:00+0000",
               GIT_COMMITTER_DATE="2026-10-22T00:00:00+0000")

    def command(arguments, allowed=(0,)):
        start = time.monotonic()
        process = subprocess.run(arguments, cwd=repo, env=env, capture_output=True,
                                 text=True, timeout=30)
        item = {"argv": arguments, "cwd": "repository", "ended_at_utc": now(),
                "elapsed_seconds": time.monotonic() - start,
                "exit_code": process.returncode, "stdout": process.stdout,
                "stderr": process.stderr}
        with (output / "commands.jsonl").open("a") as log:
            log.write(json.dumps(item) + "\n")
        if process.returncode not in allowed:
            raise RuntimeError("Unexpected command exit: " + json.dumps(item))
        return process.stdout.strip(), process.returncode

    def git(*args):
        return command(["git", "-c", "core.hooksPath=" + os.devnull,
                        "-c", "commit.gpgsign=false", "-c", "core.autocrlf=false",
                        *args])[0]

    def check(name, expected):
        body, code = command([sys.executable, "-B", str(HERE / "check_contract.py"),
                              "--source", str(repo)], allowed=(0, 1))
        result = json.loads(body)
        result["source_sha256"] = {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(repo.glob("*.py"))
        }
        (output / (name + ".json")).write_text(json.dumps(result, indent=2) + "\n")
        if result["status"] != expected or code != int(expected == "FAIL"):
            raise ValueError("Unexpected contract result at " + name)
        return result

    summary = {"schema": "semantic-integration-demo/v1", "status": "FAIL",
               "started_at_utc": now(), "authorship": "AUTHOR_CREATED_FIXTURES",
               "runtime": {"python": sys.version, "platform": platform.platform()},
               "human_review_observed": False, "live_agent_observed": False,
               "production_release_authorized": False,
               "checks": {}, "commits": {}, "findings": []}
    try:
        summary["runtime"]["git"] = command(["git", "--version"])[0]
        for file in (HERE / "fixtures/base").iterdir():
            shutil.copyfile(file, repo / file.name)
        git("init", "--quiet", "--object-format=sha1", "--initial-branch=base")
        git("add", ".")
        git("commit", "--quiet", "-m", "Baseline omits required notice")
        summary["commits"]["base"] = git("rev-parse", "HEAD")
        summary["checks"]["base"] = check("base", "FAIL")

        git("checkout", "--quiet", "-b", "head_a")
        shutil.copyfile(HERE / "fixtures/head_a/label.py", repo / "label.py")
        git("add", "label.py")
        git("commit", "--quiet", "-m", "A adds the notice in the label helper")
        summary["commits"]["head_a"] = git("rev-parse", "HEAD")
        summary["checks"]["head_a"] = check("head_a", "PASS")

        git("checkout", "--quiet", "-b", "head_b", "base")
        shutil.copyfile(HERE / "fixtures/head_b/view.py", repo / "view.py")
        git("add", "view.py")
        git("commit", "--quiet", "-m", "B adds the notice in the outer view")
        summary["commits"]["head_b"] = git("rev-parse", "HEAD")
        summary["checks"]["head_b"] = check("head_b", "PASS")

        changes = {name: git("diff", "--name-only", "base", name).splitlines()
                   for name in ("head_a", "head_b")}
        if set(changes["head_a"]) & set(changes["head_b"]):
            raise ValueError("Expected disjoint changed files")
        summary["changed_files"] = changes
        git("checkout", "--quiet", "-b", "combined", "head_b")
        git("merge", "--quiet", "--no-ff", "head_a", "-m", "Combine both fixes without a text conflict")
        summary["commits"]["combined"] = git("rev-parse", "HEAD")
        summary["combined_parents"] = git("show", "-s", "--format=%P", "HEAD").split()
        summary["combined_tree"] = git("rev-parse", "HEAD^{tree}")
        summary["recomputed_tree"] = git("merge-tree", "--write-tree", "head_b", "head_a").splitlines()[0]
        if summary["combined_tree"] != summary["recomputed_tree"]:
            raise ValueError("Merged tree identity mismatch")
        summary["checks"]["combined"] = check("combined", "FAIL")
        summary["textual_merge"] = "PASS_NO_CONFLICT"

        # Resolve the double responsibility in the declared outer presentation
        # layer, preserving the failing combined commit and its observation.
        git("checkout", "--quiet", "-b", "repaired", "combined")
        shutil.copyfile(HERE / "fixtures/base/label.py", repo / "label.py")
        git("add", "label.py")
        git("commit", "--quiet", "-m", "Repair: the outer view owns the single notice")
        summary["commits"]["repair"] = git("rev-parse", "HEAD")
        summary["checks"]["repair"] = check("repair", "PASS")
        summary["repair_changed_files"] = git("diff", "--name-only", "HEAD^", "HEAD").splitlines()
        if git("rev-parse", "combined") != summary["commits"]["combined"]:
            raise ValueError("The failed combined branch must remain inspectable")
        bundle = output / "history.bundle"
        git("bundle", "create", str(bundle), "--all")
        git("bundle", "verify", str(bundle))
        summary["history_bundle"] = {"file": "history.bundle",
                                     "sha256": hashlib.sha256(bundle.read_bytes()).hexdigest()}
        summary["status"] = "PASS_DEMONSTRATION"
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        summary["findings"].append(type(exc).__name__ + ":" + str(exc))
    finally:
        summary["ended_at_utc"] = now()
        summary["exercise_inputs_sha256"] = {
            p.relative_to(HERE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(HERE.rglob("*.py"))
        }
        (output / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"status": summary["status"],
                      "checks": {name: value["status"] for name, value in summary["checks"].items()},
                      "summary": str(output / "SUMMARY.json")}, indent=2))
    return int(summary["status"] != "PASS_DEMONSTRATION")


if __name__ == "__main__":
    raise SystemExit(main())
