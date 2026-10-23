# Maintenance and historical evidence

[Home](../README.md) · [Lab guide](LAB_GUIDE.md) · [Validation protocol](../validation/README.md)

## Documentation refactor

The [23 October d11 reconciliation](../validation/repository_revision_20261023/README.md)
updates the landing/runtime summary and separates the historical 15-test native
stage from the later 17-test result. It adds an attributed three-episode CSV map.
The current learning-guide publication is blocked by a supplied-PDF hash mismatch
and missing canonical sources; the verification-only raw payload is also missing.
No historical learning source, native receipt or starter was relabeled. The root
README's active protected hash is refreshed only for this reviewed documentation
change; this is not permission to alter learner checkers or source pins.

The four committed Chapter 4 exports were byte-identical to the protected [reference projections](../reader_side/reference_solution/projections/). Only the duplicate copies and their active manifest entries were removed. The canonical copies remain protected; [exports/](../exports/README.md) is now reserved for ignored generated outputs. Historical receipts remain unchanged. Optional adapters, Appendix B templates and advanced validation collectors are retained with clearer entry guides.

The root `README_*.md` guides now live in [guides/](../guides/README.md). Live navigation and protected-manifest paths follow the move. Historical observation snapshots retain their original paths and hashes; the coverage index records a separate current locator for the relocated Chapter 10 guide. Commands in chapter guides still run from the study-copy root, not from the guides folder.

The repository landing page is now a chapter index and quick start. Shared operating instructions moved to the [lab guide](LAB_GUIDE.md); chapter-specific procedures remain in the existing chapter guides. The [practice catalogue](../practice/README.md) and [solution index](SOLUTIONS.md) replace repeated inventories. Legacy text entry filenames remain as short pointers so printed references still resolve.

No chapter candidates, reference solutions, checkers, source pins or recorded experimental outcomes were changed. Finder metadata was removed from version control; it has no exercise content and remains recoverable from Git history.

The active [protected manifest](../reader_side/protected_sha256.json) is updated only for documentation changed in this maintenance pass. This is a maintainer documentation update, not a learner permission to refresh hashes after exercise edits. Historical manifests and receipts retain their original identities; old receipts must not be presented as observations of the new documentation.

## Pre-existing integrity findings

Before this refactor, the active manifest already disagreed with the root README and these three entries:

- `repo/.agents/skills/acceptance-review/SKILL.md`
- `repo/.agents/skills/acceptance-review/references/review-rubric.md`
- `repo/.agents/skills/context-audit/references/CASE_SOURCE_MAP.md`

Those three protected files and the starter file `repo/.agents/skills/context-audit/SKILL.md` were restored during the folder audit. Their source was the original local `Engineering_Software_with_Agentic_AI_Reader_Pack_20261022_d9.zip`, under its `companion/` tree. Every restored file matched its pre-existing protected or starter SHA-256 hash exactly. No skill hash or starter criterion was weakened. The prerequisite check now reports `PASS_PREREQUISITES_ONLY` with empty protected and starter findings.

The [folder audit](FOLDER_AUDIT.md) records retention decisions. The planning-only README has been merged into the [reader-side index](../reader_side/README.md#planning-references), and its active protected-manifest entry follows that document. Historical manifests retain their original paths and hashes.

## Standalone repository versus author package

Run the repository's shared checks using the [lab guide](LAB_GUIDE.md). Earlier instructions for `scripts/validate_integrated_lab.py`, the chapter-specific author validators, `editorial/` archives and `revision_d8/` refer to the complete author package; those paths are not included here. They are not prerequisites a reader should try to execute in this checkout.

If a downloaded release supplies an external checksum inventory, verify it at that release's extraction root before modifying it. This Git checkout does not supply that archive inventory.

Historical checkpoint test counts describe those checkpoints, not today's cumulative test total. Consult the [runtime matrix](../RUNTIME_MATRIX.json) and [provenance notes](../reader_side/provenance/README.md) before interpreting a retained result.
