# d11 repository follow-ups — 23 October 2026

[Home](../../README.md) · [Runtime matrix](../../RUNTIME_MATRIX.json) · [Execution audit](../EXAMPLE_TEST_REPORT.md)

This page reconciles UP01–UP05 from page 7 of the supplied
[d11 completion report](COMPLETION_REPORT.pdf#page=7). It is repository maintenance,
not the book's R01–R11 acceptance gate, a new release, or a claim of remote publication.
The report inspected public commit `e58e0f3eeec5b4531d65d90fac7cb9948edad731`.
Its original bytes are retained here, SHA-256
`cb2c8674129616630570672edaa4b36d82697e03cd0410384cc70bb5ecedf38f`.

## Action status

| Follow-up | Repository disposition | Evidence / remaining requirement |
| --- | --- | --- |
| UP01 — landing/runtime summary | COMPLETE locally | Landing page now separates dated Mac and Linux ARM64 core observations; runtime matrix adds a report-backed current summary and public locator while retaining the d9 release records. No wider platform certification. |
| UP02 — 15 versus 17 native tests | COMPLETE locally | Execution audit labels the initial 15-test stage as historical and links the later 17-test result. These are successive native regression suites; neither is the CSV reviewer count. |
| UP03 — current learning PDF and canonical sources | BLOCKED on accepted package/identity | Supplied PDF is 30 pages and labels itself d11, but has a different hash from the report's accepted artifact. Canonical d11 LaTeX/TikZ sources were not supplied/found. Existing historical PDF/source pair remains unchanged. |
| UP04 — verification-only continuation | Navigation COMPLETE; payload publication BLOCKED | [Episode map](../../navigation/NATIVE_CSV_EPISODES.md) links the supplied report and names its preserved-package locators. The 86-file payload is not available locally, so no repository link or independent acceptance is fabricated. |
| UP05 — optional portable Mac subset | DEFERRED, not required for UP01/UP02 | Complete raw packets remain outside Git. A report or summary-only copy would not satisfy the requested evidence subset. No new raw-publication claim is made. |

## UP03: artifact mismatch and safe next step

The report's accepted `Advanced_Learning_Protocol_20261023_d11.pdf` hash is:

`3836f076c2456be6fd437d3721c45885a2d4a1d694ebd393c4b5d4ecb7418392`

The file supplied in Downloads has this actual hash:

`849be21a97d3e38f16d1902aa087d82b68f938933fa360b0efa90e2a4c3ff73e`

Both the observed page count (30) and title-page edition are consistent with d11,
but those facts do not establish byte identity. The cause of the mismatch has not
been established. Do not regenerate the missing source from the PDF or change the
old source's edition label and call it canonical. Supply the accepted d11 archive
or a separately approved corrected artifact and matching source manifest first.

Required source inputs include the supplement wrapper/protocol, config/preamble,
bibliography, refactored TikZ figures and build instructions/dependencies. Once
available, verify the accepted hashes, publish PDF and matching sources together,
and explicitly archive or supersede the existing d4 source/d9-delivered PDF pair.
Do not imply a new d11 build/delivery acceptance from this documentation change.

See [learning-guide editions and participant warning](../../practice/team_operations/LEARNING_GUIDE.md)
before opening any guide or answers for an unseen-transfer exercise.

## UP04: source payload required

The report names `publication_evidence/native_csv_completion_20261023/INDEX.md`
and `review/NATIVE_CONTINUATION_ACCEPTANCE.json` inside the d11 package. Supply
that directory with its wrapper/source map and acceptance records. Import the
86 historical files byte-for-byte and verify their original identities before
replacing the report-only pointer with local evidence links. Keep the original
four-call status and its 2,700-second budget unchanged; the verification-only
episode has its own three-call/1,800-second ceiling.

## UP05: conditions for an optional portable subset

The retained Mac packets are at sibling directories
`esa_ai_native_runtime_darwin_01/validation_evidence_retry/` and
`esa_ai_native_runtime_darwin_01/validation_evidence_guided_fresh/` on the audit
workstation. These names identify local evidence, not public URLs.

If publication is selected, inspect for credentials/private data and preserve:
candidate hashes and snapshots; exact prompts and effective preparation configs;
failed stages and their outcomes; session exports and per-invocation streams;
independent checker/reviewer receipts; interventions; runtime identities; chronology
and cleanup. Include a portable path map and hash inventory. Any redacted record
must be labeled a derivative with its source identity, not silently substituted
for the original. Do not publish model weights, binaries, venvs or client databases.
Link the resulting subset from both the execution audit and reproduction guide.

## Boundaries and maintenance integrity

R17/CR10 remains **OPEN_EXTERNAL**. No independent intended-reader observations,
real learning/delayed transfer, team field economics or production outcomes were
collected. The Linux real pilot still requires kernel boot identity and the same
host/boot; no macOS runtime observation makes that clock portable.

Only the active protected-manifest hash for the deliberately edited root README
is refreshed as a maintainer action. Historical manifests, receipts, source pins,
starter candidates and the existing learning-guide source inventory are preserved.
Learners must not use this maintenance step to bypass their integrity checks.

Validation of this documentation update: source doctor returned
`PASS_PREREQUISITES_ONLY` with empty protected/starter findings; all 17 current
native validation tests passed on macOS/Python 3.12.4 in 2.913 seconds; 184 local
links across the changed Markdown resolved; the runtime JSON parsed and
`git diff --check` passed. No model calls, full 518-test rerun, Linux rerun,
new learning experiment, commit or push was performed during that validation pass.
