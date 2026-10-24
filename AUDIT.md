# Repository audit and history

[Home](README.md) · [Runtime matrix](RUNTIME_MATRIX.json)

This is the entry point for validation history, release identities and publication status. For installation and exercises use the [getting-started guide](navigation/GETTING_STARTED.md).

## Edition and maintenance history

The repository accompanies *Engineering Software with Agentic AI* d16
(24 October 2026). Its cumulative Treasury laboratory/starter remains the
`2026.10.22-d9` edition; d16 adds an independent, unnumbered Greenfield Studio
after Laboratory 14 rather than revising or adding to the Treasury sequence.
The original Treasury release baseline was Linux / Python 3.12.14 / Git 2.51.1.
These identify an observed release, not universal platform support.

Four missing hidden skill files were restored byte-for-byte from the original release. See [maintenance history](navigation/MAINTENANCE.md#pre-existing-integrity-findings). Always run the prerequisite doctor before creating a study copy.

## d16 Greenfield Studio — 24 October 2026

The d16 Greenfield Studio is a separate first-system exercise aligned with all
14 book chapters. It preserves the existing Treasury laboratories and their
`reader_start.py` workflow. The packaged reference passes ten local SQLite
contract and concurrency tests; that evidence does not establish production
readiness, operational authorization or real-world learning outcomes.

Run `python3 validation/check_greenfield_studio_d16.py` to verify the packaged
studio, its deliberately incomplete starter and the workbook mapping. See the
[d16 alignment guide](navigation/GREENFIELD_STUDIO_d16.md) for placement,
scope, responsibilities and claim limits.

Reader navigation was subsequently normalized across the Brownfield and
Greenfield routes without merging their implementations or evidence. The
[shared route chooser](navigation/STARTING_ROUTES.md) defines their common
workflow and makes their distinct entry commands, initial states, edit scopes
and reference boundaries explicit.

A fresh Apple Silicon rerun subsequently exercised both routes with the reused
Qwen3-4B Metal runtime. Brownfield passed 7/7 after guided model corrections;
Greenfield passed 10/10 after Metal attempts plus a bounded facilitator
correction. The [dual-route Metal report](validation/D16_DUAL_ROUTE_METAL_REPORT.md)
records the environment, complete deterministic regression results, failed
attempts and claim boundary.

## Observations — 23 October 2026

The [execution audit](validation/EXAMPLE_TEST_REPORT.md#current-summary--23-october-2026)
reports 518 core tests on macOS 26.5.1 ARM64 / Python 3.12.4 / Git 2.56.0,
with one explicit Linux real-clock skip, plus 11 extended tests. A **separate**
Linux ARM64 Docker run / Python 3.12.15 / Git 2.47.3 passed all 518 core tests
with zero skips and all 11 extended tests. This Linux core run is not the
emulated Linux x86-64 model-runtime experiment.

Native regression testing progressed from a historical 15-test stage to a later
17-test result after launcher/RSS fixes; do not add those counts. The later
guided Apple Silicon CSV repair passed its 7-case contract and 17-check review
(overlapping checks), not an autonomous or human-accepted trial. See the
[three separate CSV episodes](navigation/AUDIT.md).

The public companion is [popoloni/esa_ai](https://github.com/popoloni/esa_ai).
The d11 book reviewed commit `e58e0f3eeec5b4531d65d90fac7cb9948edad731`;
that review did not change the underlying d9 lab/starter edition. The later d16
addition is the independent Greenfield Studio described above. The
[d11 maintenance status](validation/repository_revision_20261023/README.md)
records which publication follow-ups are complete and which still require
the matching source/evidence package. Windows, Intel Mac, other Python versions,
independent reader acceptance and real learning outcomes remain unestablished.

## Audit records

- [Native CSV episode audit](navigation/AUDIT.md): separate budgets, interventions, outcomes and evidence availability.
- [Detailed execution audit](validation/EXAMPLE_TEST_REPORT.md): tests, fixes, unsuccessful attempts and remaining limits.
- [Publication follow-ups](validation/repository_revision_20261023/README.md): missing learning-guide package, verification-only payload and optional Mac evidence.
- [Learning-guide publication audit](practice/team_operations/AUDIT.md): edition identities and source availability.
- [d16 Greenfield Studio alignment](navigation/GREENFIELD_STUDIO_d16.md): workbook placement, 14-chapter crosswalk, executable check and claim limits.
- [d16 dual-route Metal rerun](validation/D16_DUAL_ROUTE_METAL_REPORT.md): reused environment, complete regression results and separately attributed route outcomes.
- [Folder audit](navigation/FOLDER_AUDIT.md) and [maintenance history](navigation/MAINTENANCE.md): consolidation and integrity decisions.

Historical receipts and manifests retain their original identities. Active documentation hashes are maintained separately; learners must not refresh them to bypass integrity checks.
