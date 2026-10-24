#!/usr/bin/env python3
"""ESA d16 greenfield studio: executable alignment and contract checks.

Standard-library-only. Does not modify the existing Treasury curriculum.
"""
from pathlib import Path
import subprocess
import sys
import tempfile
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
STUDIO = ROOT / "greenfield_studio"
MANIFEST = ROOT / "validation/GREENFIELD_STUDIO_d16_ALIGNMENT.json"
assert STUDIO.is_dir(), "Missing studio directory"
metadata = json.loads(MANIFEST.read_text(encoding="utf-8"))
for relative, expected in metadata["patch_studio_sha256"].items():
    p = STUDIO / relative
    assert p.is_file(), f"Missing {p}"
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    assert digest == expected, f"Modified studio file (update manifest if intended): {p}"
readme = (ROOT / "README.md").read_text(encoding="utf-8")
crosswalk = (ROOT / "navigation/GREENFIELD_STUDIO_d16.md").read_text(encoding="utf-8")
assert "<!-- ESA-D16-GREENFIELD-START -->" in readme, "Missing homepage navigation"
assert "greenfield_studio/" in readme, "Missing live studio link"
assert all(f"| {n} |" in crosswalk for n in range(1, 15)), "Missing chapter mapping"
assert "RES-001/v1" in crosswalk, "Missing accepted contract"

with tempfile.TemporaryDirectory(prefix="esa_greenfield_check_") as temp:
    reference = Path(temp) / "reference"
    starter = Path(temp) / "starter"

    def run(command, cwd=None):
        return subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=90)

    for project, reference_flag in ((reference, True),(starter, False)):
        cmd=[sys.executable, '-S', str(STUDIO/"tools/scaffold.py"), str(project)]
        if reference_flag: cmd += ["--reference"]
        result=run(cmd)
        assert result.returncode == 0, f"Scaffold failed: {result.stdout} {result.stderr}"

    ref=run([sys.executable,'-S',"-m","unittest","discover","-s","tests","-v"],cwd=reference)
    assert ref.returncode == 0, f"Reference contract failed:\n{ref.stderr}"
    expected=int(metadata["expected_reference_tests"])
    assert f"Ran {expected} tests" in ref.stderr, f"Unexpected reference test count: {ref.stderr}"
    starter_result=run([sys.executable,'-S',"-m","unittest","discover","-s","tests","-v"],cwd=starter)
    assert starter_result.returncode != 0 and "NotImplementedError" in starter_result.stderr, "Starter must remain intentionally incomplete"

print("PASS: d16 workbook mapping covers 14 chapters")
print("PASS: studio content matches release manifest")
print(f"PASS: {expected} reference tests on an isolated SQLite database")
print("PASS: unimplemented learner starter produces expected initial failure")
print("NOT CLAIMED: GitHub publication, live operational authorization, performance or production security")
