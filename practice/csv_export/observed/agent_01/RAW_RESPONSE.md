Implemented CSV-001/v1 in `work/api.py` using Python's standard `csv.DictWriter`. CSV uses the existing selected and public rows, preserves their order, includes the required five-column header even for empty results, and returns `text/csv; charset=utf-8`. JSON behavior remains unchanged.

The initial JSON demonstration succeeded. The initial CSV demonstration exited 1 with `NotImplementedError: CSV presentation requested but not implemented`; that actual failure is preserved. After the change, both demonstrations exit 0.

All six self-authored focused tests pass. They cover the original JSON baseline; Alice, Bob, status filters and missing actors; empty headers; commas, quotes, embedded LF and CRLF, Unicode and literal formula-like values; no mutation of source rows; unsupported-format errors; and SHA-256 equality for every protected input. These checks were authored for this attempt and are not independent external acceptance evidence.

Only `work/api.py` changed within the supplied work tree. The active authority is `CURRENT_CONTRACT.md`; the archived note was recognized as superseded. No author reference solution or external acceptance check was read. No deployment or human approval is claimed.

Artifacts are in:
`/workspace/scratch/efa0a59e0545/output/Engineering_Software_with_Agentic_AI_Competitive_Revision_20261021/companion/practice/csv_export/observed/agent_01`

- `INITIAL_UNDERSTANDING.md`: constraints and dependency understanding recorded before editing.
- `INITIAL_JSON.output.txt` and `INITIAL_CSV.output.txt`: original demonstrations, including the failure.
- `COMMAND_JOURNAL.json`: exact task-bearing commands, tool edits, outputs and exit codes.
- `FOCUSED_CHECKS.py` and `FINAL_CHECKS.output.txt`: the six checks and their actual result.
- `FINAL_OUTPUTS.json`: final JSON and CSV demonstration outputs, with exact newline escapes.
- `INITIAL_API.py.txt`, `FINAL_API.py.txt` and `FINAL.diff`: initial code, final code and diff.
- `SESSION.json`: actual interface/model disclosure, source visibility, timing and limitations.
- `HANDOFF.md`: fresh-session continuation notes.
- `RAW_RESPONSE.md`: this user-facing response.

The current machine-importer contract is complete. Spreadsheet viewing would require a separate consumer decision and checks; the implementation intentionally preserves formula-like values literally.
