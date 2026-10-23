# Production-control practice

This directory adds a small, optional transfer exercise to Chapters 9–12. It does not change the protected CP01–CP14 candidates or any acceptance decision. It requires Python 3.10+ and the standard library; it uses no account, network, package installation, HTTP service, database migration or deployment.

## First useful result

From `companion/`, run:

```sh
python3 practice/production_controls/contract_drill.py --self-check
python3 practice/production_controls/contract_drill.py --fixture expanded
python3 practice/production_controls/contract_drill.py --fixture contracted
```

The first command checks the declared positive/negative fixture matrix. A successful self-check says `PASS_TEACHING_MATRIX_ONLY`, even though some individual consumer probes are expected to reject their inputs. The second command should report `PASS_SELECTED_CONSUMERS_ONLY` for two selected consumer readers. The third should exit 1 and report `FAIL_SELECTED_CONSUMERS`: moving `policy_version` into the nested `policy.version` field broke the legacy reader. That failure is the lesson, not an instruction to weaken the legacy contract.

Use `--consumer current` to see why checking only the new consumer misses the break. No default command writes a file. Retain the printed JSON with your own notes outside protected source if needed. Each report identifies the script, expectation and fixture bytes it used.

## Scope

The payloads concern one new EUR 5,000 request under BR-001/v1: human review, with payment authority false. The old reader consumes the top-level policy version; the new reader consumes the nested version. `expanded` carries both. These readers intentionally tolerate unrelated additional fields. A real strict decoder might not: inspect and test the real clients before applying this expansion pattern.

This is a local response compatibility probe, not an HTTP test, OpenAPI validator, Pact implementation, complete consumer inventory, security sandbox or release gate. The JSON files are educational inputs, not independently authenticated policy. A fixture pass does not prove every request, field, client version or state transition is compatible.

## Transfer

Read `CONTROL_SELECTION.md` and `ROLLOUT_AND_MIGRATION.md`. Then use `TRANSFER_EXERCISES.md` to explain what changes when the consumer is an authenticated API client or an asynchronous worker. Its worked feedback is for practice. It does not contain Chapter 13's reserved transfer solution and is not a validated learning assessment.
