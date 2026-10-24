# Repository audit and history

[Home](README.md) · [Runtime matrix](RUNTIME_MATRIX.json)

This is the entry point for validation history, release identities and publication status. For installation and exercises use the [getting-started guide](navigation/GETTING_STARTED.md).

## Edition and maintenance history

The bundled laboratory/starter edition is `2026.10.22-d9`. Its original release baseline was Linux / Python 3.12.14 / Git 2.51.1. These identify an observed release, not universal platform support.

Four missing hidden skill files were restored byte-for-byte from the original release. See [maintenance history](navigation/MAINTENANCE.md#pre-existing-integrity-findings). Always run the prerequisite doctor before creating a study copy.

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
this does not change the underlying d9 lab/starter edition. The
[d11 maintenance status](validation/repository_revision_20261023/README.md)
records which publication follow-ups are complete and which still require
the matching source/evidence package. Windows, Intel Mac, other Python versions,
independent reader acceptance and real learning outcomes remain unestablished.

## Audit records

- [Native CSV episode audit](navigation/AUDIT.md): separate budgets, interventions, outcomes and evidence availability.
- [Detailed execution audit](validation/EXAMPLE_TEST_REPORT.md): tests, fixes, unsuccessful attempts and remaining limits.
- [Publication follow-ups](validation/repository_revision_20261023/README.md): missing learning-guide package, verification-only payload and optional Mac evidence.
- [Learning-guide publication audit](practice/team_operations/AUDIT.md): edition identities and source availability.
- [Folder audit](navigation/FOLDER_AUDIT.md) and [maintenance history](navigation/MAINTENANCE.md): consolidation and integrity decisions.

Historical receipts and manifests retain their original identities. Active documentation hashes are maintained separately; learners must not refresh them to bypass integrity checks.

=== ESA-D16-GREENFIELD-AUDIT-BEGIN ===

ESA d16, 2026-10-24 — independent Greenfield Studio (unnumbered).
Source: ESA d16 release greenfield_studio, after Laboratory 14 in the workbook.
Existing 14 Treasury laboratories and their reader_start.py workflow preserved.
Reference: ten local SQLite contract/concurrency tests, no production claims.
Run: python3 validation/check_greenfield_studio_d16.py
Check: navigation/GREENFIELD_STUDIO_d16.md
=== ESA-D16-GREENFIELD-AUDIT-END ===
