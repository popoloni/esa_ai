# Three separate native CSV episodes

[Home](../README.md) · [Original journey](../practice/native_journey/README.md) · [Execution audit](../validation/EXAMPLE_TEST_REPORT.md)

These observations use a selected CSV contract but do not have the same candidate,
budget or assistance. A later check cannot rewrite an earlier invocation's outcome.

| Episode | What happened | Evidence available here |
| --- | --- | --- |
| Original four-call implementation | Four invocations used 1,274.40 of 2,700 allowed client seconds. Attempt 3 checked its candidate; attempt 4 cleaned it without another native check. Original status remains `OPEN_PARTIAL_BUDGET_EXHAUSTED`. Independent final review passed 17 selected checks. | [Original evidence index](../practice/native_journey/observed/INDEX.md), with unchanged receipts/candidate |
| Separate verification-only continuation | The d11 report records one additional call (fifth across these two episodes), using 202.64792135199968 seconds of its separate three-call/1,800-second allowance. The author supplied the exact checker command; candidate edits were forbidden. Seven native cases and the separate 17-check review passed; all eight candidate files stayed unchanged. One client invocation made three backend requests. | [Supplied d11 report, page 3](../validation/repository_revision_20261023/COMPLETION_REPORT.pdf#page=3); **raw continuation not present in this checkout** |
| Later fresh guided Mac repair | Two successful-route invocations took 24.856 and 27.330 seconds, each within a 900-second bound. First passed behavior but lacked docs (15/17); second added docs without changing the API hash. Final 7/7 and 17/17, both demos exit 0. Earlier failed Mac attempts remain distinct. | [Published narrative](../validation/EXAMPLE_TEST_REPORT.md#successful-fresh-guided-csv-retry) and [reproduction guide](../practice/native_client/REPRODUCE_GUIDED_CSV.md); raw Mac packets remain outside Git |

The report says the verification-only payload is preserved in the d11 author
package at `publication_evidence/native_csv_completion_20261023/INDEX.md`, with
acceptance in `review/NATIVE_CONTINUATION_ACCEPTANCE.json`: 86 historical files,
307,019 bytes. These are **author-package locators, not working repository links**.
The supplied report is linked so readers can inspect the claim now; importing
and verifying that payload requires the matching d11 package. This page does not
pretend the payload is present or independently reverify its reported results.

The original journey's “no fifth call” statement describes its frozen four-call
episode. It is not a denial of the separate continuation reported later. Do not
edit its outcome, budget or raw event files when adding later navigation.

The seven-case checker is included in the 17-check reviewer. Do not sum them.
The Mac pass used guidance to read API/selection/contract, preserve API/JSON,
and use `csv.writer`/`io.StringIO`; it was not blind or autonomous. Its plan still
contains a stale finding. None of these episodes establishes human acceptance,
production readiness, or an accurate final written handoff for every candidate.

[Publication status and missing inputs](../validation/repository_revision_20261023/README.md)
distinguishes report-backed claims from portable, independently inspectable evidence.
