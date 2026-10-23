ADVANCED LEARNING PROTOCOL | Engineering Software with Agentic AI
Edition 2026.10.21-d4

This editable source reproduces the standalone companion guide. It includes
only its wrapper, layout configuration, preamble, bibliography and protocol.
The complete main book source is not needed.

Prerequisites: XeLaTeX, latexmk, Biber and the standard TeX Live packages used in
preamble.tex, including KOMA-Script, fontspec, TikZ and tcolorbox. The Latin
Modern Sans and Mono fonts are provided by a standard TeX Live installation.

From this directory, build with:

  latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error -outdir=.build advanced_learning.tex

The result is .build/advanced_learning.pdf. Keep the supplied guide unchanged
and use a new output filename for a local revision. The book's participant
exposure, timing, independence and human-approval boundaries remain applicable.

Chapter exercise commands in the guide run from the companion directory that
contains reader_start.py, not from this editable-source directory.
