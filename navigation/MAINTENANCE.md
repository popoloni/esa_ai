# Maintenance and historical evidence

[Home](../README.md) · [Lab guide](LAB_GUIDE.md) · [Validation protocol](../validation/README.md)

## Documentation refactor

The root `README_*.md` guides now live in [guides/](../guides/README.md). Live navigation and protected-manifest paths follow the move. Historical observation snapshots retain their original paths and hashes; the coverage index records a separate current locator for the relocated Chapter 10 guide. Commands in chapter guides still run from the study-copy root, not from the guides folder.

The repository landing page is now a chapter index and quick start. Shared operating instructions moved to the [lab guide](LAB_GUIDE.md); chapter-specific procedures remain in the existing chapter guides. The [practice catalogue](../practice/README.md) and [solution index](SOLUTIONS.md) replace repeated inventories. Legacy text entry filenames remain as short pointers so printed references still resolve.

No chapter candidates, reference solutions, checkers, source pins or recorded experimental outcomes were changed. Finder metadata was removed from version control; it has no exercise content and remains recoverable from Git history.

The active [protected manifest](../reader_side/protected_sha256.json) is updated only for documentation changed in this maintenance pass. This is a maintainer documentation update, not a learner permission to refresh hashes after exercise edits. Historical manifests and receipts retain their original identities; old receipts must not be presented as observations of the new documentation.

## Pre-existing integrity findings

Before this refactor, the active manifest already disagreed with the root README and these three entries:

- `repo/.agents/skills/acceptance-review/SKILL.md`
- `repo/.agents/skills/acceptance-review/references/review-rubric.md`
- `repo/.agents/skills/context-audit/references/CASE_SOURCE_MAP.md`

All three protected paths above are missing. A separate check of the starter inventory also finds `repo/.agents/skills/context-audit/SKILL.md` missing, for a total of four required missing files. `doctor` reports `ACTION_REQUIRED`; `new` refuses preparation because the protected and starter checks fail.

The README digest is updated for the revised documentation. The missing-file entries are not rebaselined or repaired by this navigation change. Restore the original matching files from the complete source release, then rerun `doctor` and require empty protected and starter findings before preparing a study copy. The documentation checks do not certify runnable-lab readiness.

## Standalone repository versus author package

Run the repository's shared checks using the [lab guide](LAB_GUIDE.md). Earlier instructions for `scripts/validate_integrated_lab.py`, the chapter-specific author validators, `editorial/` archives and `revision_d8/` refer to the complete author package; those paths are not included here. They are not prerequisites a reader should try to execute in this checkout.

If a downloaded release supplies an external checksum inventory, verify it at that release's extraction root before modifying it. This Git checkout does not supply that archive inventory.

Historical checkpoint test counts describe those checkpoints, not today's cumulative test total. Consult the [runtime matrix](../RUNTIME_MATRIX.json) and [provenance notes](../reader_side/provenance/README.md) before interpreting a retained result.
