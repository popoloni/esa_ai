# Run the pinned Harness² demonstration

[Home](../../README.md) · [Practice catalogue](../README.md) · [Chapter routes](../../navigation/CHAPTER_ROUTES.md)

This folder contains the **unmodified upstream deterministic demo** from
`google-research/harness2`, commit
`1cfe254e8d25b15f37048c3730134686abe60335`, package version `0.1.0`.
It complements the book's original Treasury experiment in
`../harness_engineering/`. The two implementations have separate receipts.

## Run it

Use **Python 3.12 or 3.13**, the upstream package's declared range. No model
credentials, API calls, benchmark download, installation or network connection
are needed for this included demo. From `companion/`:

```bash
python3 practice/harness2_upstream/run_demo.py --output ../oh_runs/upstream_01
```

Check that `python3 --version` reports 3.12 or 3.13 before this command. If it
selects another interpreter, use the path to an installed 3.12/3.13 interpreter
or skip this optional route; the core lab can still be studied. Use a separate
unchanged edition copy if your cumulative work has altered this practice's
files. The original Treasury harness has its own fresh-copy source-pin
requirement; see `../../navigation/CHAPTER_ROUTES.md` before switching exercises.

Choose a new output directory. The wrapper verifies the 43 pinned source files,
rejecting every unexpected file, including executable bytecode caches. It
runs the actual upstream `harness2.cli.demo` entry point in a separate Python
process, captures stdout/stderr and independently checks the selected ledger
answers. `--k 2 --mode both` is the default; `parallel` and `sequential` can be
run separately. The wrapper bounds `k` to 1–4 and applies a 60-second process
timeout. These convenience limits are the book's wrapper, not an upstream claim.

Read `REPORT.json`, then `run/demo.json`. The complete upstream run tree retains
base executions, candidate harnesses, probes, composition, selection, reflection
and the improvement library. Each later ledger task has access to the earlier
library entry within its mode. That is visible persistence; it does not measure
the incremental benefit of that entry.

The two included historical observations keep their original `REPORT.json`
locators and store the full raw tree in `RAW_EVIDENCE.zip`. This avoids copying
thousands of tiny trace files every time the cumulative lab creates a test copy.
`ARCHIVE_INDEX.json` binds every original file and the archive by SHA-256. To
inspect the retained V2 run, extract it into a new directory from `companion/`:

```bash
python3 -m zipfile -e \
  practice/harness2_upstream/observed/UPSTREAM_20261020_V2/RAW_EVIDENCE.zip \
  ../oh_runs/retained_upstream_v2
```

The extracted `REPORT.json` and `run/` tree preserve their original relative
layout. Fresh runs from the command above still produce unpacked evidence.

## What was actually observed

The included `observed/UPSTREAM_20261020_V2/REPORT.json` records a successful local
run on Python 3.12.14: two ledger tasks, both refinement modes, 28 real Python
executions and 32 **scripted editor calls**, with zero model calls. Across the
four task/mode results, the selected totals were correct. The initial totals
were 105.25 and 35.50; the signed totals were 85.15 and 20.25.

The source's `DemoProposer` removes the positive-only filter by a fixed string
replacement. Its selector calculates the signed total directly from the source
ledger. Those facts are essential to interpreting the result: this exercises
the upstream workflow with a known scripted repair. It does not test a model's
ability to invent the repair, demonstrate general self-improvement, or replicate
the paper's benchmark gains. Selection is not blind to arithmetic derived from
the source. Full trajectories and failed initial outputs remain inspectable.

The book wrapper and source hash record are not an OS security boundary. The
unmodified package also includes optional model-backed benchmark commands, but
they are not invoked by this wrapper. The upstream README and experiment guide
describe additional dependencies, credentials, costs and network controls for
those commands; do not infer their configuration from this local demo.

## Source, license and reproducibility

`UPSTREAM_SOURCE.json` names every retained file and SHA-256. `vendor/harness2/`
is the unchanged first-party Python package; `vendor/LICENSE` retains Apache
2.0 and the source files retain their copyright notices. The upstream README,
experiment guide and package metadata are retained alongside it. Benchmark
datasets and third-party executors are not included. Changes to the book's
wrapper do not change the vendored source.

- Paper: https://arxiv.org/abs/2610.14224v1
- Source: https://github.com/google-research/harness2/tree/1cfe254e8d25b15f37048c3730134686abe60335
- Experiment guide: https://github.com/google-research/harness2/blob/1cfe254e8d25b15f37048c3730134686abe60335/docs/EXPERIMENTS.md

The observed tree records absolute paths from the actual run. Use the paths
relative to `run/` in the wrapper report when browsing an extracted package;
create a fresh run to obtain evidence for your own environment.
