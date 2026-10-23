# Engineering Software with Agentic AI

Companion laboratory for *Engineering Software with Agentic AI*. Work through one cumulative Treasury project across fourteen chapters, or try an independent CSV exercise first.

[Install and start](navigation/GETTING_STARTED.md) · [CSV preview](navigation/EXPERIENCED_PREVIEW.md) · [Lab guide](navigation/LAB_GUIDE.md) · [Optional practice](practice/README.md) · [Worked solutions](navigation/SOLUTIONS.md)

## Start here

New to the lab? Follow the [installation and step-by-step walkthrough](navigation/GETTING_STARTED.md): required software, Linux/macOS/Windows setup, first repair, expected results and chapter progression. This is a command-line lab, not a web application. No model account or core pip installation is needed.

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

The core uses synthetic data, Python's standard library and local processes. Use Python 3.10 or newer and Git with `merge-tree --write-tree`; run the doctor to check prerequisites. Optional integrations have their own dependencies. See the [audit and supported-environment evidence](AUDIT.md) for validation scope and limitations.

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
- **Inspect recorded observations:** [audit and history](AUDIT.md) and [external validation protocol](validation/README.md).

## Repository map

| Location | What belongs here |
| --- | --- |
| [guides/](guides/README.md) | Chapter-specific instructions |
| [navigation/](navigation/README.md) | Reading routes, shared lab instructions, recovery and solution navigation |
| [repo/](repo/) | Treasury source and chapter candidates; use the chapter's permitted edit scope |
| [reader_side/](reader_side/README.md) | Independent checks, contracts, templates and protected references |
| [practice/](practice/README.md) | Optional exercises and integration guides |
| [adapters/](adapters/README.md) | Optional tool integrations; not core installation requirements |
| [exports/](exports/README.md) | Generated exercise outputs and links to canonical reference projections |
| [reader_resources/](reader_resources/README.md) | Optional Appendix B decision workbooks in text and JSON |
| [validation/](validation/README.md) | Advanced/maintainer observation protocols and collectors used by the optional native-client route |

Validation history, release identities and maintenance decisions are collected in the [repository audit](AUDIT.md). The repository includes the [Apache 2.0 license](LICENSE).
