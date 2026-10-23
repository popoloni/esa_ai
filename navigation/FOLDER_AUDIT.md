# Folder audit and retention decisions

[Home](../README.md) · [Navigation](README.md) · [Maintenance](MAINTENANCE.md)

This audit classifies the top-level folders and the functional subfolders below. Nested fixture, snapshot, source and evidence directories inherit their containing exercise's **Keep** decision unless explicitly listed otherwise. The audit excludes Git's internal database. Decisions are based on tracked content, direct references, integrity manifests and byte comparisons—not file age or folder size.

## Top-level decisions

| Folder | Decision | Action and reason |
| --- | --- | --- |
| [adapters/](../adapters/README.md) | Keep | Optional tool notes referenced by chapters; indexed by purpose. |
| [exports/](../exports/README.md) | Consolidate | Removed four byte-identical committed outputs; link to protected originals and ignore new generated outputs. Keep the output location required by the exporter. |
| [guides/](../guides/README.md) | Keep | Canonical chapter procedures; already consolidated from root README files. |
| [navigation/](README.md) | Consolidate navigation | One entry index links setup, shared commands, route choices and solutions; retain distinct route cards and historical extracts. |
| [practice/](../practice/README.md) | Keep | Optional runnable extensions, pinned dependencies and original observations. Use its catalogue rather than duplicating instructions on the home page. |
| [reader_resources/](../reader_resources/README.md) | Keep unchanged | Reader workbooks are explicitly preserved. Text and JSON serve different uses. |
| [reader_side/](../reader_side/README.md) | Consolidate navigation | Add a role-based index; merge the standalone planning note into it. Keep independent checks and evidence separate from editable candidates. |
| [repo/](../repo/) | Keep | Actual learner workspace, intentional defective candidates and instructions. Restore missing hidden skill files from the original release. |
| [validation/](../validation/README.md) | Keep | Advanced collectors used by the optional native-client route, plus external observation templates. |

## Reader-side subfolders

| Folder | Decision | Role |
| --- | --- | --- |
| [acceptance/](../reader_side/acceptance/) | Keep | Independent routing cases. |
| [discovery/](../reader_side/discovery/) | Keep | Synthetic discovery sources and controls. |
| [evidence/](../reader_side/evidence/) | Keep | Historical checkpoint reports, not disposable build logs. |
| [evolution/](../reader_side/evolution/) | Keep | Policy-history contracts and controls. |
| [extended_tests/](../reader_side/extended_tests/) | Keep | Separately budgeted technical-completion suite; the small compatibility entry in tests dispatches here. |
| [implementation/](../reader_side/implementation/) | Keep | Chapter 8 work order and negative controls. |
| [intent/](../reader_side/intent/) | Keep | Independent routing intent. |
| [knowledge/](../reader_side/knowledge/) | Keep | Source catalogue and dependencies. |
| [learning/](../reader_side/learning/) | Keep | Transfer and optional human-study protocols; distinct from ordinary tests. |
| [mcp/](../reader_side/mcp/) | Keep | Read-only contract service and fixtures. |
| [measurement/](../reader_side/measurement/) | Keep | Measurement contracts and field templates. |
| [operations/](../reader_side/operations/) | Keep | Incident scenarios and controls. |
| Former reader_side/planning/ | Consolidate, remove empty folder | Its sole README is merged into [planning references](../reader_side/README.md#planning-references); actual reference JSON files already live in reference_solution. |
| [provenance/](../reader_side/provenance/) | Keep | Original checkpoint accounting and interpretation. |
| [reference_solution/](../reader_side/reference_solution/) | Keep | Protected worked examples, including canonical Chapter 4 projections and versioned references. |
| [release/](../reader_side/release/) | Keep | Fictional decisions, review threads and release controls. |
| [routing/](../reader_side/routing/) | Keep | Deliberately faulty router for preparation and negative controls. |
| [schemas/](../reader_side/schemas/) | Keep | Record schemas and migration guidance. |
| [specs/](../reader_side/specs/) | Keep | Independent specification oracle and handoff. |
| [templates/](../reader_side/templates/) | Keep | Reader review template. |
| [tests/](../reader_side/tests/) | Keep | Integrated regression suite; not interchangeable with acceptance or extended tests. |
| [tools/](../reader_side/tools/) | Keep | Entry points and shared implementations. Legacy runner aliases preserve printed commands. |
| [verification/](../reader_side/verification/) | Keep | Independent verification fixtures and negative controls. |

## Every optional practice folder

| Folder | Decision | Why it is distinct |
| --- | --- | --- |
| [agent_workflow/](../practice/agent_workflow/README.md) | Keep | Context/boundary practice and retained collaboration observations. |
| [ai_review/](../practice/ai_review/README.md) | Keep | Critic inputs and a separate small-case comparison. |
| [csv_export/](../practice/csv_export/README.md) | Keep | Independent executable CSV starter, references and checks. |
| [harness2_upstream/](../practice/harness2_upstream/README.md) | Keep | Pinned upstream demo; vendor bytes and licensing must remain intact. |
| [harness_engineering/](../practice/harness_engineering/README.md) | Keep | Treasury-specific harness experiment, source pins and evaluations. |
| [lifecycle/](../practice/lifecycle/README.md) | Keep | Separately approved fictional continuation; not the original pending chapter plan. |
| [mcp_cli/](../practice/mcp_cli/README.md) | Keep | CLI/MCP comparison and protocol behavior. |
| [native_client/](../practice/native_client/README.md) | Keep | Installed-client setup, failures, interventions and raw evidence. |
| [native_journey/](../practice/native_journey/README.md) | Keep | Separate specification-first CSV journey, not a duplicate of the original repair. |
| [orchestration/](../practice/orchestration/README.md) | Keep | Dependency, retry, timeout and interruption scenarios. |
| [production_controls/](../practice/production_controls/README.md) | Keep | Compatibility and transfer exercises. |
| [sdd/](../practice/sdd/README.md) | Keep | Format comparisons, scaffolds and distinct native/external attempts. |
| [semantic_integration/](../practice/semantic_integration/README.md) | Keep | Two-head integration counterexample. |
| [team_operations/](../practice/team_operations/README.md) | Keep | Team worksheets and advanced learning PDF plus its source. Reader-facing material is retained. |
| [verification_tools/](../practice/verification_tools/README.md) | Keep | Hypothesis/Bandit observations, separate from model critique. |
| [workflow_cost/](../practice/workflow_cost/README.md) | Keep | Prospective activity records, accounting and validation specimens. |

## Nested folders with important retention rules

- **repo/src/** and **repo/engineering/**: keep all chapter-specific sources and candidates. The engineering areas are architecture, context, discovery, evolution, implementation, knowledge, learning, measurement, operations, planning, release, specifications and verification. An intentionally stale context note is a teaching fixture, not obsolete guidance to delete.
- **repo/.agents/**: keep the restored acceptance-review and context-audit skills and their references. Their expected hashes belong to the protected or starter inventory.
- **navigation/observation_reference/**: keep readable extracts and exact source extracts. They serve different purposes and identify historical evidence.
- **practice/** nested **observed**, **observed_v2**, **observed_* dates**, **runs**, **recorded**, **evidence**, **snapshots**, **starting_files**, **source_snapshot**, **before**, **candidate**, **fixtures**, **setup** and **validation** trees: keep. Identical bytes often identify the same source at separate recorded steps. Deleting those copies would leave receipts or reproduction instructions incomplete.
- **practice/harness2_upstream/vendor/**: keep the pinned upstream implementation and its legal notices.
- **practice/team_operations/advanced_learning_source/**: keep source alongside the reader PDF, enabling reproduction.
- **validation/records/**: keep blank collection templates; their emptiness is intentional, not a failed cleanup.
- **reader_side/reference_solution/** nested chapter, projection and v2 directories: keep separate versioned or stage-specific references.

## Removed or consolidated

1. Four duplicate Chapter 4 exports removed; canonical protected examples retained.
2. The planning-only documentation folder merged into the reader-side index; its active manifest entry follows the consolidated document.
3. Finder metadata already removed from version control in the earlier pass; the ignore rule remains. Generated export outputs and regenerable Python bytecode caches are ignored. Historical evidence is not covered by a broad ignore/delete rule.
4. No reader workbook, learning PDF, chapter candidate, executable implementation, test, pinned dependency or recorded observation was removed.

Removed tracked files can be recovered from Git history. No further whole exercise folders were safe candidates for deletion.

## Restored lab prerequisites

The four missing hidden skill files were recovered from the local original `Engineering_Software_with_Agentic_AI_Reader_Pack_20261022_d9.zip`. Each restored byte sequence matched its pre-existing protected or starter SHA-256 value; no expected skill hash was changed to accept a substitute. See [maintenance notes](MAINTENANCE.md#pre-existing-integrity-findings) for provenance and [getting started](GETTING_STARTED.md) for the entry workflow.

## Verification outcome

- Prerequisite and source check: `PASS_PREREQUISITES_ONLY`, no protected or starter findings.
- Chapter 1: fresh study-copy preparation succeeded; the intentional starter produced 3 passes, 2 failures and 2 errors; the reference passed all 7 cases.
- Chapter 1 entry tests: all 4 passed on a focused rerun with source edits stopped.
- Chapter 4: fresh-copy export succeeded; all four generated projections matched the canonical protected bytes.
- Separate technical-completion extension: all 11 tests passed.
- Full cumulative run: 516 tests executed on macOS/Python 3.14.6. One source-inventory failure overlapped a maintenance edit and cleared in the focused rerun above. The real-clock test remains unsupported on macOS (`REAL_CLOCK_REQUIRES_SUPPORTED_LINUX_HOST_BOOT`). No Linux full-suite pass is claimed from this run; the clock guard remains unchanged.
- Reader workbook bytes are unchanged. Generated bytecode caches from verification were removed and are now ignored; Python can regenerate them.

The macOS run used a canonical temporary directory to avoid symlink-ancestor failures. See [platform troubleshooting](GETTING_STARTED.md#macos-checks-and-temporary-paths). Intentional learner-candidate failures are separate from regression results and remain part of the teaching starter.
