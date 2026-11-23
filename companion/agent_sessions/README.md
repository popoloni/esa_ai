# Operate an agent, then check its work

The primary practice route is a live coding agent working on your retained
candidate. You supply the contract and allowed scope, observe its operations,
decide what it should do next, and run the protected acceptance check yourself.
The agent may run development checks. Its completion message is a claim to review.

The reviewer of companion 5.3 reported three live Claude Code launches on its Opus 5.5 default: G1 question, G1 implementation and B1 v1. G1 passed its slice and handed off, and B1 returned a context handoff. The client reported USD 0.98 across these launches.

For companion 5.5, the reviewer extended an accepted 5.3 B1 candidate and reported one live Claude Code launch on the resulting v2. Using claude-opus-5-5, the candidate passed 18 of 18 checks and was accepted with a handoff. The reviewer reported USD 0.53 for that launch. Edition 5.6 was checked offline.

**Native-client evidence carried into edition 5.6.** An AI operator completed
all eight missions and all twelve required stages with Claude Code 2.1.330 on
22 November 2026 using companion 5.2. G4 passed 13/13 and its handoff on the
original G3 lineage after `advance G4` supplied the owner mapping G4-OD-01.
The native evidence and earlier attempts remain in
`evidence/native_claude_20261122/`. See the [22 November run](NATIVE_RUN_20261122.md)
and the [earlier 16 November run](NATIVE_RUN_20261116.md). Human proficiency
and native Codex mission completion remain unverified. Edition 5.3 checked local syntax on Codex CLI 0.172.0-alpha.2. The 17 November attempt on 0.167.0-alpha.4 stopped during startup.
The recorded AP tours below come from ChatGPT Work coding workers.
Choose a trace tour if you want an immediately inspectable recorded case.
For live work, first inspect your installed client, then retain its actual
events and independent checks as described below.

The standard-library `agent_session.py` adapter prepares the task and captures
the native Codex CLI or Claude Code events, stderr, final response and
before/after files emitted during your session. The packaged AP tours use separate ChatGPT Work
coding-worker recordings; each tour points to the available command records
and their capture limits.

Run every command below from the folder containing `START_HERE.html`: `book/`
in the full archive.

The book uses **Claude Code** in its printed `run` commands. To perform the same
missions with **Codex CLI**, use `--client codex` and remove the Claude-only
`--max-budget-usd` option. Preparation, candidate scope,
protected checks and operator decisions stay the same. The
[Codex quickstart](CODEX_QUICKSTART.md) gives the complete first B1 session and
the client-specific coverage command. Keep separate working copies when
comparing clients so one client's implementation cannot substitute for the
other's work.

## Before a live run

The local mission tools require Python 3.10 or later with its standard SQLite
module. G3 integration also requires Git for local contribution worktrees; it
does not require a remote repository or push.

Use an installed, authenticated Codex CLI in a disposable working copy. Review
your account's model, usage and spending settings before starting. In print mode Claude Code stops when its estimated spend reaches the per-launch budget. A call can cross that amount, and the estimate can differ from the bill. [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference) For Codex, use the spending controls available to your account. The adapter does not impose a Codex dollar limit. Follow the
[official noninteractive-mode documentation](https://developers.openai.com/codex/noninteractive)
for current client setup and event semantics. Record the installed version:

```bash
python3 companion/start.py doctor
python3 companion/agent_session.py inspect-client --client codex \
  --output work/client-inspection-codex
codex login status
```

`inspect-client` records the local version and supported command options. It
makes no model call; `CLIENT_SYNTAX_AVAILABLE_LIVE_NOT_TESTED` means only that
the required syntax is present. Authentication and a completed mission are
separate observations. Keep the existing client permissions and configuration
while diagnosing a setup failure.

The launch uses `codex exec --json --sandbox workspace-write` with an explicit
candidate directory. It inherits the installed client's configuration and
approval policy; the adapter does not change authentication, request extra
writable directories or bypass approvals. Review effective permissions in your client and host.
Neither the task text nor the file-hash comparison creates an OS sandbox.
Do not put credentials or unrelated source in the teaching workspace. The task
does not require network access or dependency installation.

If the client exits before emitting model events, inspect `stderr.txt` and its
runtime configuration before retrying. A read-only client state directory is a
setup failure; it does not establish anything about the candidate's behavior.
Preserve the failed run and candidate snapshots while correcting the setup.

### Claude Code as the native client

Edition 5.1 adds Claude Code as a second client. Every printed `run` command
accepts `--client claude` in place of `--client codex`; preparation, snapshots,
scope checks, decisions and the coverage collector are unchanged.

```bash
python3 companion/agent_session.py inspect-client --client claude \
  --output work/client-inspection-claude
python3 companion/agent_session.py run \
  --session work/b1-agent-v1 --client claude \
  --model claude-sonnet-5-5 --max-budget-usd 5
```

The book's printed `run` commands omit `--model`. Without it the client uses its
own default model, and the session records the model it observes. In the 22 November record, eleven stages requested `claude-sonnet-5-5` and the G1 question stage used the client default. Select an available model when repeating a comparison.

The launch uses `claude --print --output-format stream-json --verbose` from the
candidate directory with this profile:

| Setting | Value | Effect |
|:--|:--|:--|
| `--tools` | `Read,Edit,Write,Glob,Grep,Bash` | No web, subagent, notebook or other built-in tools |
| `--allowedTools` | `Bash(python3:*)`, `Bash(ls:*)`, read-only `git`, and similar prefixes | Other shell commands are denied and reported in the final event, with the exception in the next row |
| `--permission-mode` | `acceptEdits` | File edits inside the working directory are accepted without a prompt. The client also auto-approves some file-system commands there: in the 16 November run, `rm -rf __pycache__` ran in the G3 CLI worktree without appearing as a denial |
| `--strict-mcp-config` with an empty `--mcp-config`, `--no-chrome` | no servers | The worker cannot reach your connectors, memory or browser |
| `--disable-slash-commands`, `--setting-sources project` | no skills, no user settings | Your personal configuration does not enter the task |
| `--no-session-persistence` | on | The client keeps no resumable conversation |
| `--max-budget-usd` | 5 by default | Client-enforced spend ceiling for that launch |

These are client settings, not an operating-system sandbox: an allowed
`python3` command can still reach any path your account can. The post-run
snapshot comparison remains the scope check. Claude Code's built-in plugins
are still loaded; one of them can deliver `AGENTS.md` automatically, so check
in the events which instruction file the worker actually read.

A Claude Code attempt counts as a completed turn only when its final `result`
event has `subtype: success` and `is_error: false`, at least one assistant text
message exists, the process exits 0 and no file outside the declared scope
changed. The model identity is read from the `model` field of the `init` event
and from each assistant `message.model`; `total_cost_usd` and
`permission_denials` from the final event are copied into `RESULT.json`.
`agent_final.txt` holds the final `result` text.

The recorder binds events to the selected client: Claude's `result` cannot
complete a Codex launch, and Codex's `turn.completed` cannot complete a Claude
launch. `NATIVE_CLIENT_PROTOCOL_MISMATCH` preserves the mixed or unexpected
stream for review. New captures also retain hashes of the native stream,
stderr and final response when present; the collector checks those bindings.

## Prepare, inspect, run, decide

For B1 v1, after the mission creates `work/b1`:

```bash
python3 companion/agent_session.py prepare B1 --api v1 \
  --candidate work/b1 --output work/agent-b1-v1
```

Read `work/agent-b1-v1/task.txt`. Check the candidate path, authority, permitted
edit and stop conditions against your own acceptance example. Then launch:

```bash
python3 companion/agent_session.py run \
  --session work/agent-b1-v1 --client codex
```

Inspect `runs/01/native_events.jsonl`, `stderr.txt`, `agent_final.txt` if emitted,
and `RESULT.json`. Before/after snapshots preserve a candidate even if the
client times out. Absence of events or usage means unavailable evidence, not
a zero-cost successful run. A nonzero exit can leave useful code that still
needs checking. Do not restart blindly and lose that state.

You may append `--model MODEL_ID`, replacing `MODEL_ID` with the exact identifier
available in your installed client and account. The invocation records that
requested identifier. The result records a model identity only when a native
metadata field supplies it; the agent's own prose is insufficient. When the
client exposes no model metadata, retain the value as unknown and keep any
separately captured client/provider identity evidence with the session.

`NATIVE_TURN_COMPLETED_REVIEW_REQUIRED` requires a valid native stream with an
agent message, a completed turn, a successful process exit and no changed file
outside the declared edit scope. An empty stream, a lone thread identifier,
malformed JSON or an error event cannot produce that result. It establishes a
completed client turn; the operator still checks the product and records the
acceptance decision independently.

Write a decision note naming the observation, scope, next instruction and limit.
Keep the run decision (continue, correct or stop) separate from the candidate
verdict (accept, reject or ask). You can retain it with:

```bash
python3 companion/agent_session.py decide \
  --session work/agent-b1-v1 --operator "your name" \
  --operator-kind human --decision continue \
  --note-file work/next-decision.txt
```

An AI facilitator must identify `--operator-kind AI`. This command records the
statement and binds it to the current candidate files, session specification
and latest retained result; it does not establish its truth or the person's
authority. Changing files after that decision requires new checks and a new
decision. A bounded
correction can be sent using `run --session ... --task-file ...`. Each launch
opens a fresh native session with retained candidate files and the explicit
next task; this adapter does not claim to resume a hidden conversation. Include
the applicable context and earlier observation in that next task. Native events
identify the actual client thread where available.

Implementation allows at most three launches within the work order's declared
implementation minutes, counted from the first launch across follow-ups.
Each launch has a default 900-second wall limit clipped to that remaining
allowance. B1 v2 uses its separate 20-minute implementation allowance. G1's
pre-owner question stage permits one launch within ten minutes; its later
implementation stage has the normal 25-minute allowance. Record manual work
before launch and later review separately. The mission's total session time is
a planning target, not an observed completion time. The requested 40-command
allowance is an instruction; the adapter does not enforce the client's internal
tool count. After a limit, preserve state and assess scope. Protected-file
changes require review even if the client exits successfully.

Run the mission's printed `start.py check` and `start.py continue` commands on
the exact candidate. Retain both receipts and the agent record. If a printed
receipt name is already taken, for example by a check run before the agent,
keep that file and add `-02`, `-03` and so on; the ledger takes the most
recently recorded attempt as the gate and lists the others as superseded. Advance from
that candidate to the next mission; never substitute a reference unnoticed.

### Count the client you actually ran

From your working copy, collect Codex's twelve required stages with:

```bash
python3 companion/agent_sessions/collect_native.py \
  --workspace-root . --client codex \
  --output work/evidence/native-codex-coverage.json
```

Use `--client claude` for Claude Code. Omitting `--client` retains an aggregate
inventory that may contain both clients. Every report includes separate
`client_coverage` counts. A successful Claude capture never counts as Codex
coverage. The filter selects the most recent attempt by that client for each
stage while retaining the other attempts for inspection.

Completion and identity remain separate: a native turn can complete even when
the JSON stream omits a model identifier. Such a run keeps
`observed_model_ids: []`; a requested `--model` is not substituted for observed
metadata. The coverage report then keeps the identity requirement open.
`publication_ready` remains false: the collector verifies local capture
consistency, while the protected checks, operator authority and publication
decision have separate evidence.

## The two special transitions

**G1:** write your own acceptance example and questions before seeing the owner
response. Prepare `G1 --stage question`; the agent can write `AGENT_QUESTIONS.md`
and `AGENT_PLAN.md`, preserving your original. The preparation snapshots your
original questions. Only after you record your question and run `start.py clarify`
may you prepare a separate `G1 --stage implement` session. The supplied response
is part of the fictional case, not a live owner's approval. Preparing question
practice after exposing that answer is refused.

**B1:** preserve the accepted v1 directory. `start.py extend B1` creates a new v2
candidate with the owner's grammar decision. Prepare `B1 --api v2` for that
candidate; the adapter refuses a version mismatch. The old receipt remains true
about the old scope and bytes. It does not certify the expanded interface.

G2–G4 and B2–B4 use `prepare MISSION --candidate ... --output ...` after the
printed `advance` command. Their module and lineage come from `READER_ENTRY.json`.
Read the current supplied decisions, including any explicit migration mapping.

**G3 integration roles:** first use `companion/integration.py prepare` as described
in `companion/integration_assets/README.md`. Prepare each resulting role explicitly:

```bash
python3 companion/agent_session.py prepare G3 --role report \
  --candidate work/g3-integration/worktrees/report \
  --output work/agent-g3-report

python3 companion/agent_session.py prepare G3 --role cli \
  --candidate work/g3-integration/worktrees/cli \
  --output work/agent-g3-cli
```

Preparation checks each role against its fixed source/note scope, prepared
worktree, baseline and shared contract. Omitting the role, requesting the other
role, widening its metadata or changing the shared contract is refused before
a task is prepared. Each role has its own session record and allowance; this
adapter does not aggregate elapsed time or spend across multiple role sessions.
Keep the combined mission ledger separately. After combination, advance the
accepted integrated workspace to G4. Preparation verifies a carried integration
receipt and its source identities when one is present.

## Rehearse from a retained trace

Without a live client, study a recording in stages:

```bash
python3 companion/agent_session.py trace --task AP-G1 \
  --output work/trace-g1
```

The tool displays an observation and asks for your next action. Write your
reason before revealing what happened:

```bash
python3 companion/agent_session.py trace --session work/trace-g1 \
  --decision-file work/my-next-action.txt
```

Repeat for each stop. The record retains your decisions before each reveal.
This is an exposure-order teaching aid; the full archive remains inspectable.
Completion records your decisions about a saved run. The adapter does not assess
their correctness or establish that you operated a live agent. Manual
implementation likewise exercises engineering and checks; record that route
honestly.

Each trace session binds one exact tour version. Its state contains the tour
identity and progress, without copying future outcomes. A short or missing
decision cannot advance a reveal. If the tour changes, preserve the old session
and start a fresh one; earlier decisions are not silently attached to new text.
Observation locators are shown with the question. Outcome locators are shown
only after the corresponding decision is retained. `TOUR_PROVENANCE.json`
records the catalogue and source-file hashes.

### Primary mission tours

| Task identifier | Mission | Main disposition to practise |
|:--|:--|:--|
| `AP-G1` | G1 | Ask about an unspecified outcome before implementing it |
| `AP-G2` | G2 | Resolve operator scope and mapping gaps; distinguish a checker defect |
| `AP-G3` | G3 | Preserve historical meaning while adding authorized cancellation |
| `AP-G4` | G4 | Distinguish a verification-fixture error from a product defect |
| `AP-B1-V1` | B1 v1 | Bound the repair and request independent acceptance |
| `AP-B1-V2` | B1 v2 | Retain the old scope and select the complete current gate |
| `AP-B2` | B2 | Distinguish the coding agent from the scripted product Provider |
| `AP-B3` | B3 | Separate replay, recomputation and a new policy decision |
| `AP-B4` | B4 | Clarify a consumer interface without inventing restoration authority |

Three focused tours examine integration, design and security decisions:

| Task identifier | Focus |
|:--|:--|
| `AP-INTEGRATION` | Review the real report/CLI composition and extracted artifact before G4 |
| `AP-DESIGN` | Select and interpret a discriminating prototype before adding a dependency seam |
| `AP-SECURITY` | Separate agent abstention, application-tool denials and host isolation |

Use the same `trace --task IDENTIFIER --output NEW_DIRECTORY` command for any
row. Distinguish the source of a failure before choosing a correction: G2
includes an operator task correction and a checker correction; B4 includes a
missing consumer contract; G4 includes an agent-authored verification-fixture
correction, with the product source unchanged.

## Evidence map

The `evidence/agent_process_v4/AP-*/` recordings retain named task messages,
submitted commands with outputs and snapshots, worker reports and separate
operator decisions/checks. Worker `SESSION.json` files name the operator,
authority and capture limits; the integration group has its own setup,
manifest and numbered operator receipts. Follow the exact source locators
given by each tour.

## Check the adapter without launching a client

Run `python3 -B companion/agent_sessions/verify_adapter.py --output work/adapter-controls`
with a new output directory. It uses disposable candidates and the retained
G3/G4 fixtures to check preparation, role boundaries, carried source identities
and every trace's decision/reveal sequence. These local controls use automated
fixture decisions and do not launch a model.
