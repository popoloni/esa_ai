# CP08 — Implement and Debug Small Increments

The Chapter 8 implementation exercise now runs in the shared Chapters 1–10
companion. It uses the canonical specification, router and Chapter 5 design, while
retaining Chapter 6 knowledge and Chapter 7 planning artifacts. Start in a fresh
working copy of `companion/`.

The Chapter 7 plan and handoff are present. They still describe a planning-only
state with a blocked implementation task and pending human decisions. The local
teaching work order in `reader_side/implementation/WORK_ORDER_CP08.md` permits
this two-file classroom exercise; it does not claim that task T07-04 ran or that
its architecture/release decisions were accepted.

## Run the exercise

Run the shared harness first:

```bash
python reader_side/tools/run_checks.py
```

The harness checks protected references and negative controls. A passing harness
is compatible with an intentionally wrong learner candidate; it is not a verdict
that your candidate is ready.

Before making candidate edits, capture the repository state from the reader side:

```bash
python reader_side/tools/scope_guard.py --chapter CP08 --capture reader_side/evidence/CP08_EDIT_BASELINE.json
```

Then inspect the candidate with the same baseline:

```bash
python reader_side/tools/implementation_gate.py --scope-baseline reader_side/evidence/CP08_EDIT_BASELINE.json
```

The fresh faulty starter is expected to fail. Repair only these repository files:

- `repo/src/treasury/explanation_alpha.py`
- `repo/engineering/implementation/implementation_report.json`

The CP08 gate imports the local Treasury package itself; no manual `PYTHONPATH`
setting is required. Repeat the gate with the original before-edit baseline, then
rerun the shared harness. Preserve the original routing boundary, reason codes,
policy version, explicit no-payment-approval notice and unvalidated benefit
status. The report must stop at `READY_FOR_HUMAN_REVIEW_NOT_ACCEPTED`.

Do not recapture the baseline after editing: the actual diff check depends on the
reader retaining the before-edit snapshot. Without `--scope-baseline`, the gate
still checks protected-file integrity, selected outputs and report claims, but
explicitly reports that actual edit scope was not checked. These owner-run checks
are not an operating-system permission boundary.

## Reference and stable negative controls

The corrected teaching reference is in `reader_side/reference_solution/`. To
inspect it without overwriting your candidate:

```bash
python reader_side/tools/implementation_gate.py --candidate reader_side/reference_solution/explanation_alpha.py --report reader_side/reference_solution/implementation_report.json --scope-baseline reader_side/evidence/CP08_EDIT_BASELINE.json
```

This command evaluates the supplied reference; use the default candidate command
above to evaluate your own repair. The actual edit-scope check still applies to
the repository diff relative to the supplied baseline.

Protected faulty examples remain in
`reader_side/implementation/unsafe_explanation_fixture.py` and
`reader_side/implementation/unsafe_report_fixture.json`. They provide stable
negative controls after a reader repairs the mutable learner files.

No live coding-agent run, measured user benefit, human architecture acceptance,
production release, or complete security review is claimed by this exercise.
