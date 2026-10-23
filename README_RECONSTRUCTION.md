# Integration update — 20 October 2026

`companion/` is now the canonical cumulative Chapters 1–10 laboratory. Its
current guide is `README.md`. The earlier separate-branch reconstruction guide
is preserved in `editorial/pre_integration/` at the book-package root.

Use `python3 reader_side/tools/run_checks.py` from this directory for the one
shared suite. Use `integration_gate.py --reference` for the protected worked
example, and `integration_gate.py` for the current learner workflow. Read the
chapter-specific baseline procedure before editing a candidate.

The original CP01–CP09 snapshots are unchanged. Snapshot counts 229 / 200 / 191
are historical branch results; the current integrated report records a single
actual discovered test total. See `../editorial/verification/integration/`.

The Chapter 10 extension adds a dossier gate to this same codebase. Local Git
identifies and materializes the exact merge candidate; current and previous
artifact bytes support a bounded rollback rehearsal. Synthetic owner decisions
are kept separate from technical checks. Read `README_CP10.md` and the evidence
in `../editorial/verification/chapter10/`. The Chapters 1–9 parent package and
its protected baseline remain historical evidence, not the current test total.
