# Companion — operate an agent through eight missions

Begin at [Start here](../START_HERE.html) and the book's Part V practice guide.
The main route is a live coding agent working on a candidate you retain across
missions. Use the [agent practice guide](agent_sessions/README.md) to prepare a
session, observe its actions and record your next instruction. The same guide
provides recorded trace tours when a live client is unavailable.

The local tools require Python 3.10 or later with standard-library SQLite.
G3 integration also requires Git. Product Provider examples are deterministic
local fixtures; the coding agent is the participant that develops the product.
Proposal reviews and protected acceptance checks run without a model call.

## One entry point, two continuous routes

Run every command from the folder containing `START_HERE.html`. In the full archive this is `book/`. Create a fresh destination and use a fresh receipt filename for
every attempt. The CLI refuses to overwrite either. To repeat a printed check,
keep the earlier receipt and add `-02`, `-03` and so on to its name; the native
ledger reads these retries and takes the most recently recorded one as the gate. `work/` is your working
area; packaged contracts, checks and references remain under `companion/`.

When upgrading from 5.3 or 5.4, keep your learner directory and earlier
receipts. Point the new companion's `check` or `continue` command at that
directory and choose a fresh receipt name. For B1, `extend` creates a
separate v2 directory while preserving your v1 work. Each new check runs
the current protected suite against the retained implementation.

| Mission | Editable implementation | Current check scope | Continuation artifact |
|:---|:---|:---|:---|
| G1 | `booking.py` | Four public slice methods; two additional read-only methods at handoff | Normal write/read across two processes |
| G2 | `booking.py` | Seventeen behavior and migration methods | Migrated record, replay, payload conflict and adjacency |
| G3 | `booking.py` | Seven compatibility and cancellation methods | Historical record, current state and replacement reservation |
| G4 | `operations.py` | Thirteen diagnosis and accounting methods | Read-only incident diagnosis and illustrative cost report |
| B1 | `src/treasury/routing.py` | Seven core + five extended under v1; six additional grammar methods under v2 | Retained routing previews and explicit API extension |
| B2 | `intake.py` | Twelve bounded-provider methods | Actual local call sequence and classifications |
| B3 | `ledger.py` | Ten history and migration methods | Policy activation, old retry, new evaluation and restart |
| B4 | `incident.py` | Seven wrong-state and recovery methods | Diagnosis, local fixture restoration, preserved ledgers and costs |

```sh
python3 companion/start.py doctor
python3 companion/start.py new G1 --dest work/g1
```

G1 begins with an incomplete brief. Write your question in `work/g1/QUESTIONS.md`
before asking for the supplied owner response. The starter does not disclose the
missing lookup decision through its signature or error text. Then run:

```sh
python3 companion/start.py clarify G1 --candidate work/g1 --question-file work/g1/QUESTIONS.md
python3 companion/start.py check G1 --candidate work/g1 --select slice --output work/evidence/g1-initial.json
```

The starter fails because implementation is incomplete. Read the supplied decision
before implementing. `clarify` records the provided text and makes the dated
teaching decision available; it is not a live human approval or access-control
boundary. After implementation, use a new receipt filename and run the handoff.
The G1 mission in Part V provides the complete sequence and three proposal judgments.

For every later mission, choose one of two entry paths. `advance` checks a retained
learner predecessor and carries its source/dependencies into a fresh candidate,
keeping a source snapshot, entry and handoff under `prior/`. `new` supplies an
independent starter and its explicit dependencies. Do not run both into the same
destination. For example:

```sh
python3 companion/start.py advance G2 --from-candidate work/g1 --dest work/g2
```

The Reservation route continues G1 → G2 → G3 → report/CLI integration → G4.
Follow the [G3 integration guide](integration_assets/README.md) to combine the
two worktrees and check the extracted package before advancing the accepted
integrated workspace to G4. The Treasury route continues B1 → explicit B1 v2
extension → B2 → B3 → B4. `advance B2` requires the B1 v2 entry, because a v1
receipt does not identify the changed input contract.

Subsequent missions retain earlier work while adding a named module or API.
B3 introduces durable storage for the history that B2 held only in memory.

## Current and archived scopes

G1 `slice` (alias `first`) runs four public-interface methods after G1-OD-01 is
available. `all` remains four slice plus ten final-contract API diagnostics.
The minimal slice passes four; its final-contract group has three passes and
seven assertion failures, identifying work for G2. `readonly` runs two extra
public checks; G1 handoff runs slice + readonly and then a separately reported
two-process persistence observation. A missing storage path must not be created.

G1 `archived` runs the original ten schema-dependent methods; `historical` remains
a compatibility alias. G1's current checks use the public interface and accept
the ordinary and JSON representations. G2's migration decisions authorize those
two representations and the exact six-column `reservations` signature in
[G2-OD-02](contracts/G2_OD_02.md). Unsupported mappings require an owner decision.
[G4's contract](contracts/G4.md) recognizes three specific schema-3
representations: the reference `reservations` table and the recorded and native
`reservations_v2` tables. When your own G3 keeps its current reservations in
another layout, `advance G4` records the owner mapping G4-OD-01 for that lineage
(`docs/G4-OD-01.md` and `docs/G4-SCHEMA-MAP.json`) if every column uses a name the
named layouts already use for the same role. Otherwise it refuses and explains
how to supply a mapping with `--schema-map`, acting for the owner; the companion
checks it against the columns your `init_db` creates. These later mappings do not
narrow G1's public acceptance contract.

B1 `core` runs seven unchanged numeric methods; `extended` runs five additional
public finite/type methods. Under B1-API/v1, `all` runs both groups. A separate
B1-API/v2 working copy adds six grammar methods, making eighteen in total. B1's
`historical` selection remains an alias for core. Two public precision probes are
separate proposal-review observations under v1; their inputs are outside the v2
grammar and must not silently be reused as v2 defect claims.

## Proposal review and separate solutions

Each mission has three proposals. Read the printed cards or `variant.py` and
`RATIONALE.md`, record an ACCEPT, REJECT or ASK judgment with its reason, then
reveal the batch receipt. Open `TRUTH.json` only after recording your judgment;
it contains the solution.

```sh
python3 companion/start.py review G2 --candidate-ids G2-P01 G2-P02 G2-P03 --output work/evidence/g2-review.json
python3 companion/start.py review B1 --candidate-id B1-H01 --output work/evidence/b1-recorded.json
```

The mission proposals are constructed teaching variants, not model transcripts.
B1-H01 contains code and an edit event retained from a native agent session on
22 October 2026; no final agent rationale was captured. Its historical numeric
result is distinct from the current API's additional obligation.

`review` leaves learner source unchanged. Exit 0 means the review receipt was
saved, even when the candidate fails. Inspect the observed check status and
expected decision after making your own judgment. `check` and `continue` return
0 for their scoped success, 1 for observed failure, and 2 for a refused request.
Timeouts and input-integrity checks are diagnostic controls, not an operating
system sandbox for arbitrary Python.

```sh
python3 companion/start.py solution B3 --dest work/solution-b3
python3 companion/start.py check B3 --candidate work/solution-b3 --reference --output work/evidence/b3-reference.json
```

Reference exports require a separate directory and `--reference` for checks.
They cannot become learner handoffs. A reference receipt belongs to its own bytes.
Your dossier records acceptance reasoning; a CLI result establishes only the
behavior observed by its selected checks.

## Further practice and case limits

The [mechanisms lab](mechanisms/README.md) lets you inspect recorded instruction
delivery, operating-system file denials and a local MCP exchange. Follow its
setup requirements and interpret each observation within its stated scope.

G4/B4 monetary and time inputs are explicitly illustrative scenarios. B4 executes
restoration only of its local JSON state-binding fixture and verifies new policy
on a disposable ledger copy. The preserved originals remain unchanged;
reconciliation stays pending. No production recovery or financial authority is
implied by a passing demonstration.

## License and recorded cases

The companion retains its [Apache 2.0 license](LICENSE) and [notice of changes](NOTICE.md).
The [agent practice guide](agent_sessions/README.md) maps recorded cases to
their commands, source files and decisions. The [historical native episode](../evidence/historical_episode/README.md)
has its own capture and contract limits. Use Part V of the book for the mission
sequence and return to a source record when you need to inspect a specific claim.
