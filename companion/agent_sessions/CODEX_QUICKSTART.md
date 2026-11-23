# Run the companion with Codex CLI

Edition 5.3 checked the installed version and required local flags with Codex CLI 0.172.0-alpha.2. The archived 17 November attempt, using 0.167.0-alpha.4, stopped during startup. The project has recorded no completed native Codex mission.

The exercises in *Engineering Software with Agentic AI* support Codex CLI as
well as the Claude Code commands printed in the book. Use the same contract,
candidate, protected checks and operator decisions. Choose `--client codex`
when launching the worker. Use a fresh working copy to compare clients.

**Edition 5.2 verification:** the installed Codex CLI passes local syntax
inspection, and the adapter's transport controls pass. The retained native B1
attempt and a separate direct CLI control both stopped during client startup
with a read-only app-server error, before any model event or candidate change.
Codex mission execution therefore remains unverified in this edition. Read the
[Codex verification record](CODEX_STATUS_20261117.md) for the exact evidence.

Run these commands from the folder containing `START_HERE.html`. In the complete author archive, that folder is `book/`.
Python 3.10 or later and SQLite are required. G3 integration also needs Git.
Install and authenticate Codex using the
[official Codex documentation](https://developers.openai.com/codex/cli), then
inspect the client available on your machine:

```bash
python3 companion/start.py doctor
python3 companion/agent_session.py inspect-client --client codex \
  --output work/client-inspection-codex
codex login status
```

Inspection records the installed version and local help. It makes no model
call, does not log you in, and does not prove that your account can run a model.
`CLIENT_SYNTAX_AVAILABLE_LIVE_NOT_TESTED` establishes only the required syntax.
Keep its receipt with the subsequent run.

## First complete session: B1 v1

B1 has no software dependency on the Guild missions. Start with its deliberately
faulty router:

```bash
python3 companion/start.py new B1 --dest work/b1
python3 companion/start.py check B1 --candidate work/b1 --select core \
  --output work/evidence/b1-initial.json
python3 companion/agent_session.py prepare B1 --api v1 \
  --candidate work/b1 --output work/b1-agent-v1
```

The initial check is expected to fail on the supplied defect. Read
`work/b1/docs/BR-001.md`, `work/b1/docs/B1-API.md` and
`work/b1-agent-v1/task.txt`. Write your own acceptance examples and confirm the
allowed edits before launching:

```bash
python3 companion/agent_session.py run \
  --session work/b1-agent-v1 --client codex
```

This uses your client's configured model. To select a model available to your
account, append `--model MODEL_ID` with its exact identifier. A Claude model
identifier is not interchangeable with a Codex model identifier.
`--max-budget-usd` is a Claude Code option; for Codex, configure the account's
usage controls. The adapter enforces the work order's attempt allowance and
outer wall time, not a monetary limit or the model's internal tool count.

Read `work/b1-agent-v1/runs/01/RESULT.json`, `native_events.jsonl`, `stderr.txt`
and `agent_final.txt` when present. Compare the before/after files. A completed
turn remains a proposal to review. Run the protected checks yourself:

```bash
python3 companion/start.py check B1 --candidate work/b1 \
  --output work/evidence/b1-check.json
python3 companion/start.py continue B1 --candidate work/b1 \
  --output work/evidence/b1-context.json
```

Only after inspecting the receipts and patch, write a decision note naming the
observations, permitted scope, verdict and remaining limits. For an accepted
candidate, a human operator records their own decision as follows:

```bash
python3 companion/agent_session.py decide \
  --session work/b1-agent-v1 --operator "your name" --operator-kind human \
  --decision accept --note-file work/b1-acceptance.txt
```

Create that note yourself; the command does not generate or certify it. An AI
operator must use `--operator-kind AI`. If the evidence supports correction,
rejection or a question, record that disposition instead. A follow-up requires
an explicit `--task-file` and opens a fresh client conversation with the retained
candidate files. Preserve the earlier attempt; do not reset the budget by
silently creating another session for the same unfinished task.

The recorded decision binds the current candidate inventory, session
specification and latest run result. A later edit requires new checks and a new
decision. That binding makes the record reviewable; it does not establish the
operator's authority.

## Continue through the book

Keep the printed `new`, `clarify`, `advance`, `extend`, integration, `prepare`,
`check` and `continue` commands. In each printed `agent_session.py run`, replace
`--client claude` with `--client codex`. The expected session paths are:

| Mission | Session paths under `work/` |
|:--|:--|
| G1 | `g1-question`, then `g1-implementation` after clarification |
| G2 | `g2-agent` |
| G3 | `g3-agent`, then the separately prepared `g3-report-agent` and `g3-cli-agent` roles |
| G4 | `g4-agent` from the accepted integrated G3 candidate |
| B1 | `b1-agent-v1`, then `b1-agent-v2` in the separately extended candidate |
| B2 | `b2-agent` |
| B3 | `b3-agent` |
| B4 | `b4-agent` |

G1's first stage is question practice before the supplied owner response is
released. B1 v2 is a separately authorized interface change. G3 roles have fixed
contribution scopes and independent records. Changing the client does not skip
any of those transitions.

## Read the native record correctly

The adapter invokes `codex exec --json --sandbox workspace-write` in the
candidate directory. It preserves your installed configuration, authentication
and approval policy. `launch_profile` records the requested settings; it does
not claim that effective host permissions were verified. Review those
permissions before running. The adapter neither grants additional writable
directories nor bypasses approvals. Candidate snapshots cover the candidate
tree, excluding Git internals and Python/test caches; they do not monitor all
host files or enforce an operating-system boundary.

Codex emits thread, turn and item events. The recorder requires a valid stream,
an agent message, a completed turn, process exit zero and no covered change
outside the permitted paths. A wrong-client stream is rejected. Native transport
files are retained with hashes so later changes can be detected.

The [official noninteractive guide](https://developers.openai.com/codex/noninteractive)
documents the JSON event families and final-message option. Model identity is
read only from native metadata fields when emitted. A requested model name,
login identity or the worker's prose is not proof of a backend model. Missing
usage, model or cost fields mean unknown, not zero or success.

If startup fails before model events, retain the failed attempt and inspect
`stderr.txt`. A read-only client state database, authentication failure or
unavailable model is a setup observation. Keep existing permissions and
configuration while diagnosing it; use the supported client setup or ask the
environment administrator to resolve the cause. Preserve the candidate and
failed capture when continuing in a working environment.

## Collect Codex coverage separately

```bash
python3 companion/agent_sessions/collect_native.py \
  --workspace-root . --client codex \
  --output work/evidence/native-codex-coverage.json
```

Choose a fresh output filename each time. The report gives completed stages,
completed missions and separately identified client/model counts. It also
includes per-client coverage and every retained attempt. Only the latest Codex
attempt for a stage contributes to the Codex selection. Claude's successful
runs cannot fill a Codex gap. A completed run with no emitted model identity
keeps the identity requirement open.

The [native status record](../NATIVE_STATUS.json) describes the evidence shipped
with this edition. Local adapter controls and replaying retained captures make
no model call. Only a newly launched native client can supply evidence about a
new run, and its product still needs the independent checks and an operator's
decision.
