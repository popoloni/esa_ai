# Advanced learning guide: editions and safe entry

[Team operations](README.md) · [Chapter 13](../../guides/README_CP13.md) · [d11 maintenance status](../../validation/repository_revision_20261023/README.md)

## Participant exposure — read this first

The guide contains the changed transfer case and worked causal explanation.
An unseen-transfer participant must obtain the facilitator's packet **before**
reading the guide, Appendix A.13 or reference answers. Prior exposure must be
declared and treated as guided study, not an unseen response. Renaming a case
does not undo exposure. Ordinary synthetic lab work does not require a real
24-hour wait or establish actual learning.

## Which guide is available?

| Material | Status |
| --- | --- |
| [Bundled PDF](Advanced_Learning_Protocol.pdf) and [editable source instructions](advanced_learning_source/README.txt) | Historical pair retained unchanged. Source identifies edition 2026.10.21-d4; the d11 completion report describes the bundled older PDF as 29 pages. Do not relabel it d11. |
| d11 accepted 30-page PDF and canonical LaTeX/TikZ sources | Reported in the [d11 completion report](../../validation/repository_revision_20261023/COMPLETION_REPORT.pdf#page=5), but publication here awaits the matching package. The supplied d11 PDF hash differs from the report; matching canonical sources are missing. See the [identity details](../../validation/repository_revision_20261023/README.md#up03-artifact-mismatch-and-safe-next-step). |

There is currently no verified d11 PDF/source pair in this checkout. The
historical source tree remains useful for reproducing its own edition, not for
claiming a build of the accepted d11 supplement.

## Runtime boundary

The protected [learning protocol](../../reader_side/learning/PROTOCOL.md) governs
the real pilot. Its owner-clock check uses the Linux kernel boot ID and requires
the same host/boot. The macOS audit explicitly skipped that real Linux-clock
test; synthetic calibration and observed Mac execution cannot satisfy the real
participant, timing, independence or human-approval requirements.
