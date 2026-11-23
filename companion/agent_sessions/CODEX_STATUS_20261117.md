# Codex verification — edition 5.2

Codex is an explicit supported launch option in the companion. A completed
Codex mission is still missing from the retained evidence. Claude Code's
completed matrix remains separate.

The installed client, `codex-cli 0.167.0-alpha.4`, accepted the required local
version/help inspection. A real B1 launch through the adapter then exited 1
during initialization. It emitted no native events and changed no candidate
files. Its stderr records:

> failed to initialize in-process app-server client: Read-only file system (os error 30)

The [B1 result](../../evidence/native_codex_20261117/work/b1-agent-v1/runs/01/RESULT.json),
[invocation](../../evidence/native_codex_20261117/work/b1-agent-v1/runs/01/INVOCATION.json)
and [stderr](../../evidence/native_codex_20261117/work/b1-agent-v1/runs/01/stderr.txt)
are retained with the unchanged before/after candidate.

A second, direct CLI diagnostic used an empty working directory, a read-only
sandbox and only a request to reply `READY`. It inherited the same environment
and configuration. It produced the identical initialization error, no events
and no files in that directory; see the
[direct result](../../evidence/native_codex_20261117/diagnostics/direct_cli_control_01/RESULT.json)
and [stderr](../../evidence/native_codex_20261117/diagnostics/direct_cli_control_01/stderr.txt).
This comparison locates the observed failure before the companion task can run.
Neither launch establishes model execution or product acceptance.

The adapter's 113 local capture controls use synthetic transport fixtures and
launch no client or model. They verify protocol separation, capture integrity,
scope reporting, decision binding and client-specific collection. Replaying
the retained Claude matrix preserves twelve completed Claude stages while
reporting zero completed Codex stages.

Use the [Codex quickstart](CODEX_QUICKSTART.md) in a working, authenticated Codex
installation. Retain new native events and independent protected checks before
updating the Codex coverage claim. Configuration or permission bypasses were
not used to turn the startup failure into a successful run.
