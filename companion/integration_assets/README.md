# G3 paired-worktree integration

This increment continues a retained G3 candidate. One coding-agent role implements a read-only report through the public booking API; the other implements a CLI against that report interface. The separate component checks deliberately leave a composition question for the integration reviewer.

## Prepare and operate the two roles

Run from the extracted ESA package root:

```bash
python3 companion/integration.py prepare \
  --candidate work/g3 \
  --dest work/g3-integration
```

The helper first checks the retained G3 handoff, then creates a local Git repository at `work/g3-integration/workspace` and two actual worktrees:

| Role | Workspace | Allowed edits | Component selection |
|:--|:--|:--|:--|
| report | `work/g3-integration/worktrees/report` | `reservation_report.py`, `CONTRIBUTION_A.md` | `test_integration_a.py` |
| cli | `work/g3-integration/worktrees/cli` | `reservation_cli.py`, `CONTRIBUTION_B.md` | `test_integration_b.py` |

Each role receives the same `docs/INTEGRATION-G3.md`, protected tests and retained `booking.py`. Its `INTEGRATION_ROLE.json` records its scope and shared-contract hash. Operate a real coding client in each worktree and retain the actual interaction separately. The helper does not invoke or simulate a model. The report component uses the real booking API; the CLI component uses an explicitly identified fake report provider. Those selections do not establish the combined behavior.

The workers should leave their changes uncommitted. The integration helper checks complete file inventories against the prepared baselines, stages only the declared source and note files, and records their commits as the AI recording operator. Git is used locally; no push occurs.

## Combine and check the transported package

```bash
python3 companion/integration.py combine \
  --workspace work/g3-integration/workspace \
  --output work/g3-integration/REPORT.json
```

The helper retains each actual command and result under `operator/`, combines the contributions with local cherry-picks, repeats the component selections and G3 handoff, packages the combined candidate, and extracts that ZIP into a separate directory. It checks the components and G3 contract again there, then executes the actual CLI with the actual report provider.

The independent CLI observations cover import behavior; a confirmed record; the same historical record after cancellation; an absent identifier; missing storage; invalid identifiers `0`, `-1` and `abc`; and a missing required argument. Expected JSON is type-sensitive and comes from the shared contract. Every read observation checks the fixture's file hashes before and after. The package's complete extracted inventory must equal its combined-source inventory.

A failure remains in its command receipt and the requested report. A failed cherry-pick is not reset or replaced with a reference. Preserve that state, inspect the failure and define the next correction before another attempt. Receipt paths are never reused. Git commits are provenance records; the helper makes no claim that a commit alone proves correctness.

On success, `READER_ENTRY.json` receives an integration record bound to the exact `booking.py`, `reservation_report.py` and `reservation_cli.py`, an immutable acceptance receipt and the tested archive. The ZIP represents the combined candidate **before** this acceptance metadata is added; `REPORT.json` separately binds the updated entry and the final Git commit. Human acceptance remains pending, and no production authorization or performance improvement is inferred.

## Continue the same candidate into G4

```bash
python3 companion/start.py advance G4 \
  --from-candidate work/g3-integration/workspace \
  --dest work/g4
```

When the retained G3 stores its current reservations in a layout that OPS-G4/v3
does not name, `advance` also writes the owner mapping `docs/G4-OD-01.md` and
`docs/G4-SCHEMA-MAP.json` for this lineage and prints `owner_mapping` in its
output. Read the decision before delegating. If no mapping follows from the
column names, `advance` refuses and shows how to supply one with `--schema-map`.

G4 verifies the acceptance receipt and all three source hashes, copies the report and CLI alongside booking, retains their source snapshots and a local receipt copy, and includes the forwarded modules in dependency checks. Changing an integrated source blocks the check before the mission tests run. The standalone `new G4` and `solution G4` routes still serve their separate fixture/reference purpose; `advance G4` requires the integrated learner lineage.

## Reuse an existing recorded layout

`INTEGRATION.json` explicitly records `main_workspace`, each role's `workspace` and `baseline`, baseline inventories and the shared baseline commit. Paths are relative to that manifest and may identify retained sibling workspaces. Pass `--manifest PATH` to `combine` when the manifest is not next to the main workspace. Adapting this metadata does not move or rewrite a raw recording.

The edition's actual observation is retained at `evidence/agent_process_v4/AP-INTEGRATION/REPORT.json`, with the original sibling worktrees and worker command records preserved.

## Exercise the helper using a retained actual bundle

```bash
python3 -B companion/integration_assets/verify_helper.py \
  --candidate evidence/agent_process_v4/AP-G3/workspace \
  --recorded-report evidence/agent_process_v4/AP-INTEGRATION/REPORT.json \
  --workdir work/integration-helper-replay \
  --output work/integration-helper-test.json
```

It needs `evidence/agent_process_v4/AP-INTEGRATION/packages/integration-001.zip`, which this public
companion does not include; here the command stops with `FileNotFoundError`.
This system test extracts the recorded bundle, copies only its actual contribution bytes into freshly prepared role worktrees, combines them again, performs the transport checks and verifies G4 forwarding. It also retains a deliberate changed-source refusal and an unintegrated-G4 refusal. These are labelled source replay and controlled integrity tests; they are not new agent observations or G4 completion.
