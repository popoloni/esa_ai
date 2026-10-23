---
name: acceptance-review
description: Review a proposed Treasury-routing change against INT-001 and the separately controlled acceptance suite. Use before declaring the lab repair ready for human review.
---
# Inspect an accountable candidate

1. Read the current approved intent at `../reader_side/intent/INT-001.md`.
2. Inspect only the relevant code and the candidate diff; report scope changes explicitly.
3. Request that the reader run `python reader_side/tools/run_checks.py` from the companion root.
4. State the observed test status and which checks were run; never infer a result from your own proposed test.
5. Record open questions and an evidence-backed *ready for human review* assessment.
6. Do not rewrite intent, acceptance files, policy hashes or tool permission settings.

This skill gives process instructions, **not** permission to execute commands or edit protected files.
See `references/review-rubric.md` for the review checklist.
