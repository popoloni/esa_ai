# An actual rejection at the journal boundary

An AI implementer developed the memory ledger in ChatGPT Work. An independent
AI reviewer found a product defect after its local controls had passed. The
reviewer changed only the input fixture: it removed the final newline from a
copy of a valid ledger. The reviewer did not plant the defect in the product.

## Read the observation before the correction

The [defective implementation](before/companion/memory/ledger.py) accepted the
unterminated stream as 23 events. A duplicate proposal was then refused, but
recording that refusal concatenated another JSON object onto the last line.
The next inspection failed with `BROKEN_EVENT_JSON`. The ordinary duplicate
refusal concealed a journal-integrity failure.

The [independent reproduction](../../memory_review_reject_20261116/reproduction_01/RESULT.json)
retains the three invocations, exit codes and before/after digests. Its sibling
command directories contain the exact stdout and stderr; the original valid
ledger and both changed copies are retained. The original source and source
ledger stayed unchanged.

## Follow the bounded decision

The AI operator's [exact REJECT](OPERATOR_REJECT.txt) required the candidate and
failed observation to be preserved, then bounded the correction: refuse an
unterminated tail before writing, without silently repairing it. The
[implementer's acknowledgement](IMPLEMENTER_RESPONSE.txt) retained that scope.

The invariant is specific: a nonempty journal must end with the delimiter
written by the application before another event can be appended. The
[narrow diff](ledger.diff) and [corrected snapshot](after/companion/memory/ledger.py)
show the check at the start of `load_events`. Both inspection and mutation now
refuse `UNTERMINATED_EVENT_TAIL`; the program does not append a newline, discard
an event or rewrite history.

The [independent correction recheck](../../memory_review_reject_20261116/correction_recheck_01/RESULT.json)
ran the same three operations against the corrected snapshot. Every operation
refused the incomplete tail and preserved its exact bytes. A separate valid,
terminated copy still accepted a normal refusal event and remained readable
with 24 events. Preserving the negative case and the valid control keeps a
blanket refusal from masquerading as a repair.

## Evidence boundary

This is an actual AI-operated development and review episode in ChatGPT Work.
It is separate from the deliberately false memory card in the scripted B1 lab.
The boundary input was constructed; no real crash or power failure was observed.
The reviewers and operator were AI assistants, not human participants. No native
Codex CLI mission was run. Client/model usage data for the development
conversation are not supplied by these local command receipts.

The packet preserves the immediate before/after tail-fix snapshots. The current
runtime may contain separately recorded maintenance corrections; those do not
rewrite this episode's candidate identities. `PUBLIC_SELECTION.json` binds the
selected files. Raw command paths identify the original execution workspace and
some inputs in the complete author archive; they are not commands to run in a
fresh extraction. Run the current self-contained
[memory lab](../../../companion/memory/README.md) for new local controls.
