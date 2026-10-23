"""Run the seven reader-owned Chapter 1 cases against known local teaching code.

Each candidate runs as treasury.routing in a fresh Python process. The paths
are the exercise router and its two protected fixtures. This runner does not
isolate arbitrary untrusted code or grant payment, merge or release authority.
"""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import platform
import subprocess
import sys

from scope_guard import check_candidate_path, check_integrity


ROOT = Path(__file__).resolve().parents[2]
ROUTER = ROOT / "repo/src/treasury/routing.py"
INTENT = ROOT / "reader_side/intent/INT-001.md"
ACCEPTANCE = ROOT / "reader_side/acceptance/test_routing.py"
KNOWN_CANDIDATES = {
    ROUTER,
    ROOT / "reader_side/routing/unsafe_routing_fixture.py",
    ROOT / "reader_side/reference_solution/routing.py",
}
WORKER_SOURCE = r'''
from pathlib import Path
import contextlib
import importlib.util
import io
import json
import sys
import traceback
import unittest

root, candidate = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(root / "repo/src"))
captured, log = io.StringIO(), io.StringIO()
record = {"tests_total": 0, "passed": 0, "failures": 0, "errors": 0,
          "skipped": 0, "expected_failures": 0, "unexpected_successes": 0}
exit_code = 1
try:
    with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(log):
        import treasury
        spec = importlib.util.spec_from_file_location("treasury.routing", candidate)
        module = importlib.util.module_from_spec(spec)
        sys.modules["treasury.routing"] = module
        treasury.routing = module
        exec(compile(candidate.read_bytes(), str(candidate), "exec"), module.__dict__)
        acceptance = root / "reader_side/acceptance/test_routing.py"
        test_spec = importlib.util.spec_from_file_location("chapter01_owner_acceptance", acceptance)
        test_module = importlib.util.module_from_spec(test_spec)
        sys.modules[test_spec.name] = test_module
        exec(compile(acceptance.read_bytes(), str(acceptance), "exec"), test_module.__dict__)
        suite = unittest.defaultTestLoader.loadTestsFromModule(test_module)
        class CountingResult(unittest.TextTestResult):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.successes = 0
            def addSuccess(self, test):
                self.successes += 1
                super().addSuccess(test)
        result = unittest.TextTestRunner(stream=log, verbosity=2,
                                         resultclass=CountingResult).run(suite)
        record.update({"tests_total": result.testsRun, "passed": result.successes,
                       "failures": len(result.failures), "errors": len(result.errors),
                       "skipped": len(result.skipped),
                       "expected_failures": len(result.expectedFailures),
                       "unexpected_successes": len(result.unexpectedSuccesses)})
        exit_code = 0 if result.wasSuccessful() and result.testsRun == 7 and result.successes == 7 else 1
except BaseException as exc:
    record["execution_error"] = type(exc).__name__ + ":" + str(exc)
    log.write(traceback.format_exc())
record.update({"exit_code": exit_code, "stdout": captured.getvalue(), "test_log": log.getvalue()})
print(json.dumps(record))
raise SystemExit(exit_code)
'''


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=ROUTER,
                        help="The working router or the protected unsafe/reference routing fixture")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "reader_side/evidence/CH01_ROUTING_RESULT.json")
    args = parser.parse_args(argv)
    candidate = args.candidate.resolve()
    if candidate not in KNOWN_CANDIDATES:
        parser.error("--candidate must be the working router or a protected Chapter 1 routing fixture")
    output = args.output.resolve()
    evidence_root = ROOT / "reader_side/evidence"
    if output.is_relative_to(ROOT) and not output.is_relative_to(evidence_root):
        parser.error("--output must not replace a candidate, checker or protected source")
    findings = []
    before = check_integrity()
    counts = {"tests_total": 0, "passed": 0, "failures": 0, "errors": 0,
              "skipped": 0, "expected_failures": 0, "unexpected_successes": 0}
    report = {
        "schema": "chapter01-routing-result/v1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version.split()[0], "platform": platform.platform(),
        "status": "FAIL", "candidate": candidate.relative_to(ROOT).as_posix(),
        "candidate_sha256": None, "intent_sha256": None, "acceptance_sha256": None,
        "integrity_before": before, "integrity_after": [],
        "exit_code": None, "stdout": "", "test_log": "", "stderr": "",
        "meaning": "Seven owner-side cases for known local teaching code; not a security sandbox, payment approval or release approval.",
    }
    try:
        if candidate == ROUTER:
            check_candidate_path("src/treasury/routing.py", chapter="CP01")
        report.update(candidate_sha256=digest(candidate), intent_sha256=digest(INTENT),
                      acceptance_sha256=digest(ACCEPTANCE))
        if before:
            findings.extend("protected_integrity:" + item for item in before)
        else:
            environment = dict(os.environ)
            environment.pop("PYTHONPATH", None)
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            command = [sys.executable, "-I", "-B", "-c", WORKER_SOURCE,
                       str(ROOT), str(candidate)]
            process = subprocess.run(command, cwd=ROOT, env=environment,
                                     capture_output=True, text=True, timeout=180)
            report["exit_code"] = process.returncode
            report["stderr"] = process.stderr
            child = json.loads(process.stdout)
            if not isinstance(child, dict):
                raise ValueError("acceptance worker returned a non-object report")
            for name in counts:
                value = child.get(name)
                if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                    raise ValueError("acceptance worker count missing or invalid: " + name)
                counts[name] = value
            report["stdout"] = child.get("stdout", "")
            report["test_log"] = child.get("test_log", "")
            if child.get("execution_error"):
                findings.append("EXECUTION_ERROR:" + child["execution_error"])
            if process.returncode != 0:
                findings.append("ACCEPTANCE_REJECTED")
            if counts["tests_total"] != 7:
                findings.append("EXPECTED_SEVEN_OWNER_CASES")
        report["candidate_sha256_after"] = digest(candidate)
        if report["candidate_sha256_after"] != report["candidate_sha256"]:
            findings.append("CANDIDATE_CHANGED_DURING_RUN")
    except subprocess.TimeoutExpired:
        report["exit_code"] = 124
        findings.append("ACCEPTANCE_TIMEOUT:180_seconds")
    except (OSError, ValueError, TypeError, PermissionError) as exc:
        findings.append("RUN_ERROR:" + type(exc).__name__ + ":" + str(exc))
    after = check_integrity()
    report["integrity_after"] = after
    findings.extend("protected_integrity_after:" + item for item in after)
    report.update(counts)
    report["findings"] = findings
    successful = (not findings and report["exit_code"] == 0 and counts["tests_total"] == 7
                  and counts["passed"] == 7 and all(counts[key] == 0 for key in
                      ("failures", "errors", "skipped", "expected_failures", "unexpected_successes")))
    report["status"] = "PASS" if successful else "FAIL"
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        report["status"] = "FAIL"
        report["findings"].append("REPORT_WRITE_ERROR:" + type(exc).__name__ + ":" + str(exc))
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(run())
