# Install, start and work through the lab

[Home](../README.md) · [Lab guide](LAB_GUIDE.md) · [Chapter index](../README.md#find-your-chapter) · [Recovery](RECOVERY.md)

## 1. Know what you are building

This is a command-line teaching project, not a website to launch. You edit Python, JSON and Markdown files, run checks in a terminal, and inspect JSON result files. The cumulative Treasury lab spans Chapters 1–14. The book supplies the lesson; this repository supplies exercise inputs, checks and worked references. Basic terminal use, Python and JSON editing are assumed.

The earlier missing-file packaging problem has been repaired: four hidden skill files were restored from the original d9 reader pack with matching hashes. See [maintenance notes](MAINTENANCE.md#pre-existing-integrity-findings). If your copy still reports missing protected files, obtain the complete updated source; do not delete manifest entries or change hashes to bypass checks.

## 2. Install only the core tools first

| Software | Needed for | Installation |
| --- | --- | --- |
| Python 3.10 or newer | Entry command, exercises and checks | [Official Python setup guide](https://docs.python.org/3/using/index.html). Python 3.12 is the closest minor version to the recorded baseline; other versions are not certified by this lab. |
| Git with `merge-tree --write-tree` | Downloading the repository and local integration/release exercises | [Official Git installation options](https://git-scm.com/install/) |
| A text/code editor | Editing Python, JSON and Markdown | Use your existing editor; no particular editor or extension is required. |
| A terminal with a POSIX shell | Running the command examples | Linux terminal, macOS Terminal, or a Linux terminal inside WSL on Windows. |

No `pip install`, project package installation or virtual environment is required for the core lab. It uses Python's standard library, including SQLite; no database server, Docker, GPU, API key, paid account or coding agent is required. An editor alone does not install Python or Git.

### Linux

Use your distribution's Python and Git packages. On Debian/Ubuntu:

```bash
sudo apt update
sudo apt install python3 git
```

Check versions below; older distributions may provide versions that do not meet the requirements. Use your distribution's supported upgrade method if needed. The recorded lab baseline is Linux / Python 3.12.14 / Git 2.51.1, not every Linux distribution.

### macOS

Install Python using the [official macOS instructions](https://docs.python.org/3/using/mac.html), and Git using its official installation page above. Open a new Terminal window after installation. Native macOS is not covered by the recorded Linux baseline; a successful prerequisite check is not full platform validation.

### Windows

These examples use POSIX commands such as `cp` and shell line continuations. Use a Linux environment in WSL rather than pasting them unchanged into PowerShell. Follow [Microsoft's WSL installation guide](https://learn.microsoft.com/en-us/windows/wsl/install); the initial administrator PowerShell command is:

```powershell
wsl --install
```

After the requested restart and Linux account setup, open the Linux terminal and follow the Linux instructions. Install Python and Git **inside WSL** and keep both the checkout and study copy in its Linux filesystem. WSL is a suggested way to use these shell instructions, not a separately validated lab environment.

### Confirm the tools are visible

In the terminal you will use for the lab:

```bash
python3 --version
git --version
git merge-tree -h
```

Python must be at least 3.10. Git's help must list `--write-tree`; help may return a nonzero exit code simply because no merge inputs were supplied. The lab's `doctor` command checks that capability automatically. Use `python3` throughout; where an older chapter example says `python`, use the same Python 3 interpreter.

## 3. Obtain the lab and check it

If you already have this checkout, open a terminal in its top-level directory and skip cloning. Otherwise, from a parent directory of your choice:

```bash
git clone https://github.com/popoloni/esa_ai.git
cd esa_ai
```

Run from the directory containing [reader_start.py](../reader_start.py), not from the nested [repo/](../repo/) or [navigation/](README.md) directories. Older guides call this top-level directory `companion/`; in this checkout its name is `esa_ai/`.

```bash
python3 -B reader_start.py doctor
```

Before creating a copy, require **both** `status: PASS_PREREQUISITES_ONLY` and an empty `release_starter_findings` list. `protected_findings` must also be empty. A pass checks prerequisites, not all exercise behavior. Missing protected files are a source-packaging issue, not an intentional learner failure or a missing pip package.

## 4. Create one study copy

Once the source checks are clear, run these commands one at a time:

```bash
python3 -B reader_start.py show 1
python3 -B reader_start.py new 1 --destination ../my_treasury_lab
```

Only after you see `Prepared ...`, enter the new copy:

```bash
cd ../my_treasury_lab
python3 -B reader_start.py show 1
```

Open **my_treasury_lab** in your editor. Leave the original checkout unchanged. The new copy contains Chapter 1's deliberate routing defect and all later teaching candidates. The destination must not already exist; choose a different name for a genuinely new attempt. Do not also run the separate Chapter 1 preparation script for this same destination.

## 5. Complete your first exercise

From the study-copy root, read the [routing intent](../reader_side/intent/INT-001.md) and the `show 1` card. Links here display the starter files; edit the equivalent paths in **your study copy**.

Capture the allowed edit scope, then record the initial failing result:

```bash
python3 reader_side/tools/scope_guard.py --chapter CP01 --capture reader_side/evidence/CP01_EDIT_BASELINE_NEW.json
python3 reader_side/tools/run_acceptance.py --output reader_side/evidence/CH01_BASELINE_RESULT.json
```

The prepared exercise initially has seven cases: three passes, two failures and two errors. A nonzero exit from this acceptance command is expected. Missing protected inputs or an integrity failure is **not** that expected result.

Edit only `repo/src/treasury/routing.py` in your study copy. Then run:

```bash
python3 reader_side/tools/run_acceptance.py --output reader_side/evidence/CH01_ROUTING_RESULT.json
python3 reader_side/tools/scope_guard.py --chapter CP01 --baseline reader_side/evidence/CP01_EDIT_BASELINE_NEW.json
cp reader_side/templates/CH01_REVIEW_TEMPLATE.md reader_side/evidence/CH01_REVIEW.md
```

Inspect the result JSON: all seven selected routing cases should pass, and the scope check should find no out-of-scope edits. Fill in the copied review template to explain the repair and its limits. Preserve the original failing result. Then follow the [Chapter 1-to-2 transition](LAB_GUIDE.md#begin-the-chapter-1-exercise) to save your repaired router and adopt the exact reference router required by later chapter scopes.

## 6. Continue in chapter order

Stay in the same study copy. For example, start Chapter 2 with:

```bash
python3 -B reader_start.py show 2
```

Repeat this workflow for each chapter, replacing the number with 3, 4, and so on:

1. Read the matching book chapter and [chapter guide](../README.md#find-your-chapter).
2. Read the card's **Cumulative prerequisite**, **Editable paths** and **Supplied starter outcome**. `show` displays instructions; it does not execute checks or certify current files.
3. Run **Before editing** commands once to capture the baseline. Replace names such as `NEW_DIR` with an unused session path, and use that same path in the related commands. Keep the baseline from before your edits.
4. Edit only the named candidates, then run **Candidate checks**. Correct the candidate based on the result, not the protected checker or expected answer.
5. Review and save the result. Compare the **Worked-example route** only when you want a separate reference check; a reference pass does not repair or accept your work.
6. Read **Continue** and **Decisions still pending** before advancing. Use the next chapter's prerequisites to decide readiness, not a generic green result.

Do not run `new` for every chapter in cumulative mode. Chapters 3–9 build the discovery-to-verification chain; Chapters 10–14 add separately named release, policy, incident, transfer and measurement sessions. Follow their dedicated guides for session dependencies. Chapter 7's pending owner decisions remain pending even when later classroom exercises run. The ordinary synthetic Chapters 13–14 route does not require a 24-hour wait.

Run the [shared regression suite](LAB_GUIDE.md#start-with-the-shared-regression-suite) in the study copy as a cross-check. Intentionally incomplete candidates can fail while regression tests pass. When restarting tomorrow, open the same folder and use `show N`; when an input changes, follow [stale-receipt recovery](RECOVERY.md).

## 7. Add optional software only for a chosen extension

| If you choose… | Read before installing |
| --- | --- |
| A coding client and local model | [Native-client setup](../practice/native_client/README.md) — separate client, model and runtime requirements |
| Hypothesis and Bandit | [Verification tools](../practice/verification_tools/README.md) — extension-specific dependencies |
| MCP integration | [MCP/CLI exercise](../practice/mcp_cli/README.md) — SDK and host route |
| Upstream Harness² | [Upstream guide](../practice/harness2_upstream/README.md) — Python 3.12 or 3.13 |
| Other techniques | [Practice catalogue](../practice/README.md) — each guide owns its setup and evidence scope |

The core is useful without these extensions. There is no requirement to install all the tools mentioned in the book.

## Troubleshooting

| Symptom | What to do |
| --- | --- |
| `python3` or `git` not found | Install it in the environment running the terminal, reopen that terminal, and repeat the version checks. |
| `reader_start.py` cannot be opened | Change to the top-level checkout or study-copy directory. |
| `ACTION_REQUIRED` or nonempty protected findings | Read the listed paths. Restore original missing/changed protected files; do not treat this as a learner exercise failure. |
| `NOT_RELEASE_STARTER` | Use an unchanged complete starter for `new`; use `show` to continue an already edited study copy. |
| Destination or baseline already exists | Continue the original session, or choose a new name for a separate session; do not overwrite prior work. |
| Candidate gate fails | Compare with the card's expected starter outcome, inspect the result and fix only permitted candidate files. |
| Receipt is stale | Preserve it, rerun the affected checks using current inputs, and follow the recovery guide. |

### macOS checks and temporary paths

The folder audit exercised setup on macOS with Python 3.14.6 and Git 2.56.0; this does not replace the recorded Linux baseline. If checks reject a symlinked temporary-directory ancestor (`OWNED_PATH_SYMLINK`), use a canonical temporary location for the command, for example `TMPDIR=/private/tmp python3 -B reader_side/tools/run_checks.py`. Use a canonical, non-symlink path for study-copy destinations too.

The full regression suite includes a real-host-clock test for the optional human learning pilot. On macOS it raises `REAL_CLOCK_REQUIRES_SUPPORTED_LINUX_HOST_BOOT`; run that host-specific check on the required Linux environment. Do not weaken it or count an unsupported-host failure as a successful human-study validation. Keep source files unchanged while tests run: the Chapter 1 preparation test verifies that the original source tree is untouched.
