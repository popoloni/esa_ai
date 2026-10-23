# Engineering Software with Agentic AI

Companion laboratory for *Engineering Software with Agentic AI*, edition `2026.10.22-d9`. Work through one cumulative Treasury project across fourteen chapters, or try an independent CSV exercise first.

[Install and start](navigation/GETTING_STARTED.md) · [CSV preview](navigation/EXPERIENCED_PREVIEW.md) · [Lab guide](navigation/LAB_GUIDE.md) · [Optional practice](practice/README.md) · [Worked solutions](navigation/SOLUTIONS.md)

## Start here

New to the lab? Follow the [installation and step-by-step walkthrough](navigation/GETTING_STARTED.md): required software, Linux/macOS/Windows setup, first repair, expected results and chapter progression. This is a command-line lab, not a web application. No model account or core pip installation is needed.

The four previously missing hidden skill files have been restored from the original release with their expected hashes unchanged. Always run the source checks below before creating a study copy. See [maintenance notes](navigation/MAINTENANCE.md#pre-existing-integrity-findings).

Run these commands from this repository's root. Keep this checkout as your starter and make exercise changes in a separate study copy:

```bash
python3 -B reader_start.py doctor
```

Continue only when the status is `PASS_PREREQUISITES_ONLY` and `release_starter_findings` is empty:

```bash
python3 -B reader_start.py show 1
python3 -B reader_start.py new 1 --destination ../my_treasury_lab
```

After `new` reports `Prepared ...`:

```bash
cd ../my_treasury_lab
```

Then follow the [Chapter 1 repair and continuation](navigation/LAB_GUIDE.md#begin-the-chapter-1-exercise). For cumulative work, continue in that same copy; `show N` displays each chapter's prerequisites, editable files and check commands. A fresh `new N` copy does not complete earlier exercises for you.

The core uses synthetic data, Python's standard library and local processes; no model account is required. The declared language floor is Python 3.10, and Git must support `merge-tree --write-tree`. The original d9 release baseline is Linux / Python 3.12.14 / Git 2.51.1. Later observations are dated below; neither a language floor nor one observed machine certifies other environments. See the [runtime evidence](RUNTIME_MATRIX.json); optional integrations document their own dependencies.

## Current repository observations — 23 October 2026

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
[three separate CSV episodes](navigation/NATIVE_CSV_EPISODES.md).

The public companion is [popoloni/esa_ai](https://github.com/popoloni/esa_ai).
The d11 book reviewed commit `e58e0f3eeec5b4531d65d90fac7cb9948edad731`;
this does not change the underlying d9 lab/starter edition. The
[d11 maintenance status](validation/repository_revision_20261023/README.md)
records which publication follow-ups are complete and which still require
the matching source/evidence package. Windows, Intel Mac, other Python versions,
independent reader acceptance and real learning outcomes remain unestablished.

## Find your chapter

| Part | Chapter | Guide |
| --- | --- | --- |
| I — Foundations | 1. Repair routing | [Repair, verify and preserve your result](navigation/LAB_GUIDE.md#begin-the-chapter-1-exercise) |
| | 2. Prepare the workspace | [First-week route](navigation/FIRST_WEEK.md) · [Interface chooser](navigation/INTERFACE_CHOOSER.md); use `show 2` for the entry card |
| | 3. Discover the problem | [Discovery and value](guides/README_CP03.md) |
| | 4. Specify behavior | [Specifications](guides/README_CP04.md) · [Lifecycle map](navigation/LIFECYCLE_MAP.md) |
| II — Design and coordination | 5. Compare designs | [Architecture](guides/README_CP05.md) |
| | 6. Maintain context | [Knowledge and context](guides/README_CP06.md) |
| | 7. Plan and delegate | [Planning](guides/README_CP07.md) · [Optional execution routes](navigation/CHAPTER_ROUTES.md#chapter-7) |
| III — Implementation and delivery | 8. Implement a bounded change | [Implementation](guides/README_CP08.md) |
| | 9. Check independently | [Verification](guides/README_CP09.md) |
| | 10. Review and rehearse release | [Technical completion, release and rollback](guides/README_CP10.md) |
| IV — Evolution and outcomes | 11. Evolve policy and state | [Policy history](guides/README_CP11.md) |
| | 12. Investigate an incident | [Recovery](guides/README_CP12.md) |
| | 13. Develop team practice | [Learning and transfer](guides/README_CP13.md) |
| | 14. Measure outcomes | [Measurement and tool decisions](guides/README_CP14.md) |

The [lab guide](navigation/LAB_GUIDE.md) covers shared checks, edit baselines and cross-chapter receipts. Teaching candidates are intentionally incomplete: a passing regression suite does **not** mean the candidate workflow is accepted. Technical checks and fictional owner decisions are separate.

## Choose another route

- **Try a small task first:** [independent CSV preview](navigation/EXPERIENCED_PREVIEW.md), with no Treasury prerequisite.
- **Explore a specific technique:** [practice catalogue](practice/README.md), grouped by purpose and chapter.
- **Resume or recover:** [route chooser](navigation/CHAPTER_ROUTES.md), [lifecycle map](navigation/LIFECYCLE_MAP.md) and [stale-receipt recovery](navigation/RECOVERY.md).
- **Compare your work:** [solutions and Appendix B workbooks](navigation/SOLUTIONS.md). Try the exercise before opening its reference.
- **Inspect recorded observations:** [observation archive guide](navigation/observation_reference/README.md), [runtime matrix](RUNTIME_MATRIX.json) and [external validation protocol](validation/README.md).

## Repository map

| Location | What belongs here |
| --- | --- |
| [guides/](guides/README.md) | Chapter-specific instructions and the historical reconstruction note |
| [navigation/](navigation/README.md) | Reading routes, shared lab instructions, recovery and solution navigation |
| [repo/](repo/) | Treasury source and chapter candidates; use the chapter's permitted edit scope |
| [reader_side/](reader_side/README.md) | Independent checks, contracts, templates and protected references |
| [practice/](practice/README.md) | Optional exercises and their dated observations |
| [adapters/](adapters/README.md) | Optional, dated tool-integration notes; not core installation requirements |
| [exports/](exports/README.md) | Generated exercise outputs and links to canonical reference projections |
| [reader_resources/](reader_resources/README.md) | Optional Appendix B decision workbooks in text and JSON |
| [validation/](validation/README.md) | Advanced/maintainer observation protocols and collectors used by the optional native-client route |

[Folder audit](navigation/FOLDER_AUDIT.md) records keep/consolidate/remove decisions for every functional folder. [Maintenance notes](navigation/MAINTENANCE.md) explain the refactor and historical evidence. The repository includes the [Apache 2.0 license](LICENSE).
