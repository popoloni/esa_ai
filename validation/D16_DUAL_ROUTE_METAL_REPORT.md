# d16 dual-route Metal rerun — 24 October 2026

[Audit index](../AUDIT.md) · [Starting routes](../navigation/STARTING_ROUTES.md) · [Runtime matrix](../RUNTIME_MATRIX.json)

This record covers a fresh rerun of both d16 starting routes on Apple Silicon.
It reports observed engineering evidence only; it is not human acceptance,
production authorization or evidence of learning outcomes.

## Reused environment

- Python: existing `esa_ai_test_env`, Python 3.12.4.
- Model server: existing native `llama-server` build `b11799`.
- Client: existing native OpenCode installation.
- Model: `Qwen3-4B-Q4_K_M.gguf`.
- Accelerator evidence: llama.cpp reported Apple M2 Max Metal initialization
  and 37 of 37 model layers offloaded to the GPU.

After the tests, the bounded launcher sent its configured stop signal and
recorded `EXIT_AFTER_STOP_REQUEST`; the llama.cpp child reported exit code
`-6`. This happened during teardown, after all inference and route checks, and
is retained as a lifecycle observation rather than described as a clean server
exit.

The aligned disposable repository identified itself as `2026.10.24-d16`.
The prerequisite doctor passed. The complete deterministic repository run
passed 518 tests with the one documented macOS real-clock skip; the extended,
orchestration, SDD, workflow-cost, harness-engineering, MCP CLI and validation
suites also passed (11, 31, 14, 28, 16, 4 and 17 tests respectively). The d16
Greenfield alignment checker passed its ten reference tests and observed the
expected failure of the deliberately incomplete starter.

The first core run used a temporary directory exposed through a macOS symlink
and correctly failed three owned-path checks. Repeating the unchanged tests
with the physical `/private/tmp` path passed. No virtual-environment repair or
package installation was required.

## Brownfield route

A fresh Chapter 1 copy began at the specified three passes, two failures and
two errors. The Metal model's first edit reached six of seven cases. Two short
failure-guided correction turns were required to place the finite-value guard
before the comparison. The final independent run passed all seven cases and
the scope/integrity check passed.

Result: **PASS (7/7)**. This was a guided model run, not an autonomous-success
claim.

## Greenfield route

A fresh scaffold began with all ten tests raising the intended
`NotImplementedError`. The Metal model implemented the database schema and
part of the reservation path over two attempts. It then produced a duration
type error and malformed SQL; a compact correction turn fixed the duration
comparison but became trapped retrying the malformed edit. A facilitator made
the bounded correction in the disposable learner implementation: strict
timestamp handling, transaction ordering, idempotency, overlap detection and
resource cleanup. The independent suite then passed.

Result: **PASS (10/10), with facilitator correction**. This establishes that
the scaffold, contract and tests operate in the reused environment. It does
not establish that this 4B model completes the exercise without assistance.

## Conclusion

Both d16 routes remain executable and preserve their separate learning
purposes. The shared reader framing is valid, while the observed intervention
profiles are intentionally reported separately: guided Metal completion for
Brownfield and Metal-assisted plus facilitator completion for Greenfield.
