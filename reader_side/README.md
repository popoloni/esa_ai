# Reader-side checks and references

[Home](../README.md) · [Lab guide](../navigation/LAB_GUIDE.md) · [Folder audit](../navigation/FOLDER_AUDIT.md)

This tree contains reader-controlled criteria, checkers and worked examples, not the ordinary editable chapter candidates. Work on the paths named by `reader_start.py show N` in your study copy. Run commands from the study-copy root.

## Where to go

| Need | Location |
| --- | --- |
| Understand the routing requirement | [Intent](intent/INT-001.md) and [acceptance cases](acceptance/test_routing.py) |
| Run current checks | [Shared runner](tools/run_checks.py), [regression tests](tests/) and [lab instructions](../navigation/LAB_GUIDE.md#start-with-the-shared-regression-suite) |
| Check edit scope | [Scope guard](tools/scope_guard.py) and the chapter's before-edit baseline |
| Follow a specific chapter | [Chapter guides](../guides/README.md); they link the matching work orders, contracts and tools |
| Compare a worked answer | [Solution navigation](../navigation/SOLUTIONS.md) and [reference solutions](reference_solution/) |
| Find Chapter 7 reference inputs | [Planning references](#planning-references) |
| Interpret old reports | [Historical evidence](evidence/) and [provenance notes](provenance/README.md) |
| Understand current record formats | [Schemas](schemas/REVIEW_SCHEMAS_V2.md) |
| Run the separate Chapter 10 extension suite | [Technical-completion tests](extended_tests/test_technical_completion.py) |

The [folder audit](../navigation/FOLDER_AUDIT.md#reader-side-subfolders) describes every direct subfolder. Old reports are retained as history; use newly generated receipts to assess the current source.

## Planning references

The candidate files in [repo/engineering/planning/](../repo/engineering/planning/) are deliberately defective. Repair only `delegation_plan.json` and `delegation_handoff.json` for Chapter 7. The [reference plan](reference_solution/delegation_plan.json) and [reference handoff](reference_solution/delegation_handoff.json) show a safe **planning** state, with human decisions unmade and no agent implementation run.

Source fingerprints refer to CP06 owner-side fixtures. Logical task levels are not timings. Running the Python tests is not a model benchmark, Git worktree security proof, production authorisation, release approval or real multi-agent experiment.

This section consolidates the former planning-only README; the protected reference data has not moved.
