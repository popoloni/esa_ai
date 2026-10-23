# A native specification response, a failed save, and an explicit owner stop

This 22 October 2026 observation completes the original bounded R08 tutorial
journey: the installed Spec Kit command ran in OpenCode, the native model
generated substantive specification text, and an independent agent reviewed its
five requirements, eight cases and three unanswered owner questions. The native
session stopped before planning or implementation. The useful specification was
returned as an assistant response; it was **not saved into the native project’s
specification file**.

That distinction is part of the result. The first successful native write
contained a header and copied operator instructions, so the reviewer rejected
it. The later response supplied the substantive body but inaccurately referred
to three artifacts. The actual checklist and feature metadata do not exist.
Neither the response nor this packet supplies human requirements acceptance,
answers from an owner, an adopted constitution or implementation readiness.

## Read the three different artifacts

| Artifact | Origin | What to use it for |
| --- | --- | --- |
| [Exact final native response](raw/FINAL_NATIVE_RESPONSE.md) | The 5,530-byte completed assistant text from the actual native session; identical to the retained export and event stream. | Inspect the generated requirements, cases, unanswered questions, copied Input block and false three-artifacts claim. |
| [Actually written native file](raw/ACTUAL_NATIVE_SPEC_FILE.md) | The 2,230-byte first completed native write, also observed from the filesystem. | See the genuine rejected first candidate and the failure to persist the useful later response. |
| [Reader specification](editorial/reader_specification.md) | Separately attributed editorial extraction and relocation from the native response. | Read the useful specification without operational paths or the false completion sentence. This is not the native-persisted file. |

The [extraction record](editorial/EXTRACTION_RECORD.json) and
[exact diff](editorial/EXTRACTION.diff) disclose every editorial operation. The
operational Input block is removed; its exact source-authority sentences are
relocated under an editorial heading. The false final three-artifacts sentence
is removed. Native requirements, all eight scenario rows and the three actual
owner questions remain unchanged. No new requirement, scenario value, owner
answer or approval was supplied.

## What the native journey actually did

The framework was GitHub Spec Kit 1.2.2, the client OpenCode 1.19.3 and the local
model the pinned official Qwen3-4B Q4_K_M through llama.cpp b11799. The initial
attempt used a fresh session. The corrected attempt and both later guided
continuations used one other native session with its complete prior history.

| Invocation | Actual outcome | Retained evidence |
| --- | --- | --- |
| Attempt 01 | After the full source packet was already attached, the model read it again. The next prompt had 23,836 tokens in a 24,576-token context. The controller interrupted the exact client. No project file changed. | [Capture](recorded/attempt_01/RECEIPT.json), [intervention](recorded/INTERVENTION_01.json), [terminal collection](recorded/terminal_collection_01/COLLECTION_RECEIPT.json). |
| Attempt 02 | Corrected read permissions blocked repeated source reads; the model also encountered other retained permission refusals. It copied the upstream spec template, then stopped with exit 0. This was scaffold creation, with no generated specification body. | [Capture](recorded/attempt_02/RECEIPT.json), [terminal collection](recorded/terminal_collection_02/COLLECTION_RECEIPT.json). |
| Attempt 03 | A disclosed same-session request asked for real native writes. After about 1,500 seconds it ended with a provider error. The export retains an aborted write selection with empty input and no recoverable artifact content. All 50 files were unchanged. | [Exact guidance](recorded/continuation_preparation_01/PROMPT.txt), [capture](recorded/attempt_03/RECEIPT.json), [terminal collection](recorded/terminal_collection_03/COLLECTION_RECEIPT.json). |
| Attempt 04 | A second disclosed request asked for a compact specification write and reduced the configured response limit from 3,072 to 1,536 tokens. The first write copied header/Input text. The next native response supplied all five requirements, eight cases and three unanswered questions, then normally stopped. It did not save that body to the file. | [Exact guidance](recorded/continuation_preparation_02/PROMPT.txt), [first write](recorded/first_native_write_04/OBSERVATION.json), [capture](recorded/attempt_04/RECEIPT.json), [terminal collection](recorded/terminal_collection_04/COLLECTION_RECEIPT.json). |

These are a disclosed repair sequence, not independent blind trials. The
initial command and all first outputs remain in the exports. The appended
requests supplied execution guidance, not a specification draft or owner
answers. No fifth native invocation was made.

## The source and authority boundary

The client received all nine fixed JSON inputs, the unchanged router, the
complete active spec/checklist templates and the unratified constitution. The
JSON inputs include the authored reference contract with the five requirements
and eight expected cases. This is a framework-guided projection of disclosed
teaching inputs; it is not blind requirements elicitation or evidence of real
operator benefit. Earlier generated Markdown answers, the authored before/after
exercise answers and owner responses were excluded.

The native attachment contained every one of the 13 source bodies before
inference. JSON whitespace alone was compacted and wrapped to stay below the
pinned client’s line-reading limits. Subsequent model reads were restricted to
generated outputs, and the actual denial of a duplicate source read is retained.
The attachment preparation and the model’s later tool permissions use different
native paths; neither establishes OS containment. The logs retain background
plugin-registry activity, so a local inference endpoint is not an offline-host
claim.

The [argument-field qualification](review_notes/R08_FIRST_WRITE_INPUT_FIELD_QUALIFICATION.json)
explains one possible contributor to the failed first file. The unchanged
upstream template places the full command argument in its Input field, and the
command treats that argument as the feature description. Here the argument also
contained operational instructions. The first file copied it with one newline
changed to a space. This source-grounded observation does not establish why the
model omitted the body or identify a sole cause. The current tracked issue is
**D8-NATIVE-SPEC-PROMPT-ECHO**; the note’s earlier suggested identifier remains
as historical attribution. The response/file mismatch and false completion
claim are tracked as **D8-NATIVE-RESPONSE-PERSISTENCE-CLAIM**.

## What the independent review accepts

The [independent R08 review](../native_review_20261022_d8/INDEPENDENT_R08_REVIEW.json)
is a byte-identical copy of the formal author review. It verifies the actual
response against the unchanged inputs. In particular, exactly EUR 5,000 routes
to HUMAN_REVIEW with AT_OR_ABOVE_LIMIT; invalid and non-positive amounts remain
rejected; all cases retain BR-001/v1 and payment_authorized=false. The authority
of SRC-POL-001 is not transferred to the ticket or old wiki, and an explanation
does not authorize a payment.

The native response presents these questions and explicitly leaves them
unanswered:

1. Which explanation vocabulary do real operators understand?
2. Does the interface accidentally induce payment approval?
3. How will actual user benefit be measured in a pilot?

It retains HYPOTHESIS_NOT_VALIDATED and the unratified constitution, then reaches
a normal stop before planning. The review accepts that documented unanswered
question stop for the original bounded tutorial scope. There was **no separate
speckit.clarify invocation and no interactive owner dialogue**. No answer,
justified deferral by an owner or human acceptance was fabricated.

Original R08 requires linked native generation, retained first outputs,
clarification disposition and independent assessment. It does not require every
planned file to be successfully persisted or a second observed framework run.
The rejected first file, missing files and false completion claim remain real
defects. OpenSpec is still a clearly scoped unobserved native contrast; no
measured paired comparison or framework ranking follows.

## Reproduce and inspect

Use [the current native route](../NATIVE_ROUTE_D8.md). Its new configuration
helper was actually executed in a separate disposable project and isolated
client state after the model server stopped. The
[reproduction review](reproduction/actual_reproduction_01/REPRODUCTION_REVIEW.json)
records real version/configuration/agent diagnostics, all 13 unchanged source
bodies and both complete discovered framework commands. After explicit path
normalization, its configuration, environment, task prompt and complete native
argv match the corrected observed candidate. No model call or simulated
diagnostic was used for that check.

The [closed runtime packet](../../native_client/setup/runtime_d8/README.md)
records the separate server configuration and cleanup. The final server stopped
cleanly; its lifecycle is distinct from native client exit statuses.
Agent steps=12 is a last-step instruction in the pinned client, not a mechanical
tool-call bound. The capture timeout provides the outer subprocess bound.

[OBSERVATION_SUMMARY.json](OBSERVATION_SUMMARY.json) links outcomes and unique
completed native-step usage. Its timing sum covers only the four d8 client
invocations. Incomplete requests, setup, review and cleanup must not disappear
from a full effort account. Local client charge zero is not total cost or proof
of zero work. No time-saving or controlled performance claim is made.

[COPY_ORIGIN_MANIFEST.json](COPY_ORIGIN_MANIFEST.json) maps unchanged evidence
bytes to their original author paths. Absolute paths inside raw receipts are
historical execution locations, not instructions to overwrite a reader’s
workspace. [PORTABLE_MANIFEST.json](PORTABLE_MANIFEST.json) binds this complete
packet. The earlier [d7 native packet](../observed_native_20261022/README.md)
remains unchanged as the dated timeout/input-read observation.

The packet includes the Spec Kit distribution metadata and MIT license under
upstream/, and the pinned client-source license under
recorded/preparation/pinned_client_sources/. It contains no model weights or
installed dependency tree.
