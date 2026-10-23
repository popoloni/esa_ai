# Two green changes, one failing integration

[Home](../../README.md) · [Practice catalogue](../README.md) · [Chapter routes](../../navigation/CHAPTER_ROUTES.md)

This optional Chapter 10 exercise shows a semantic interaction that Git can
merge without a text conflict. It is separate from the protected Treasury
release history. The code, two contributions and repair are authored teaching
fixtures; the runner performs actual local Git operations and Python checks.
No live agent, human approval, network service or production release is involved.

## Job and contract

A presentation shows one route label followed by exactly one routing-only
notice. The baseline forgot the notice. Contributor A repairs `label.py`;
contributor B independently repairs `view.py`. Each branch passes the same
four selected output-contract cases: standard queue, human review, rejection,
and refusal of an unknown route. The edits touch different files.

Before running, predict the combined sentence. Both layers now add the notice.
A conflict-free merge can therefore fail the behavior contract even though
both checked heads passed. The repair makes the outer view own the one notice
and preserves the combined failure as a separate Git commit and receipt.

## Run from any fresh companion extraction

Use Python 3.10 or later and a local Git supporting
`git merge-tree --write-tree`. The observed project baseline is Linux,
Python 3.12.14 and Git 2.51.1; other platforms are not established by this
receipt. This exercise does not require the earlier Treasury exercises.

From `companion/`, choose an unused sibling output directory:

```bash
python3 -B practice/semantic_integration/run_demo.py \
  --output ../semantic_merge_01
```

The command exits zero only if the whole expected sequence is observed.

| Saved check | Expected result | What it establishes |
| --- | --- | --- |
| `base.json` | `FAIL` | The original missing-notice defect is observable. |
| `head_a.json` | `PASS` | A's exact source passes all four selected cases. |
| `head_b.json` | `PASS` | B's exact source passes the same four cases. |
| `combined.json` | `FAIL` | Three valid routes have a doubled notice after the actual conflict-free merge; the unknown-route check still passes. |
| `repair.json` | `PASS` | One bounded source repair restores the declared output contract. |

Inspect `SUMMARY.json` for the exact commits, parents, recomputed merge tree,
disjoint changed files and source hashes. `commands.jsonl` retains the actual
commands, exit codes, output and timing. `repository/` retains all five commits;
the repaired tree is checked out. The verified `history.bundle` also retains
the complete local Git history for portable inspection. Evidence belongs
outside the supplied source.

To inspect the failed combined source without altering its history:

```bash
git -C ../semantic_merge_01/repository show combined:label.py
git -C ../semantic_merge_01/repository show combined:view.py
```

## Complete the learning task

Explain why the same contract could pass on each head and fail on their
combination. Identify the responsibility duplicated across the two layers and
justify the chosen owner of the notice. Then name one interaction in an
authorized project of your own, such as two layers both retrying a request or
both converting a unit, and propose a check on their actual combined behavior.

The supplied repair is one scoped design choice, not a general rule that all
formatting belongs at an outer layer. These four cases do not establish every
input, dependency or concurrency interaction. A real integration needs its
applicable contract, reviewed inputs and decision authority.
