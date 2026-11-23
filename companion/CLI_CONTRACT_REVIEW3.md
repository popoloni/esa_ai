# Printed command contract — Review 3

The commands and argument vectors in `ROUTES.json` govern the printed
Review 3 edition. Run them from the extracted package root. Runtime setup
and the version check are on `START_HERE.html`; `doctor` reports the local
interpreter and checks the pinned inputs.

The canonical proposal-review option is `--candidate-ids`, even when the
list contains one identifier. It produces one batch receipt with `results`
in the requested order. The compatibility option `--candidate-id` accepts
one identifier and produces the original individual receipt. The two
forms are mutually exclusive. Neither form edits a learner's working copy.
A review receipt is an observation; it leaves the human decision pending.

```bash
python3 companion/start.py review B1 --candidate-ids B1-P02 --output work/evidence/b1-batch.json
python3 companion/start.py review B1 --candidate-id B1-P02 --output work/evidence/b1-single.json
```

The single and batch receipt envelopes differ intentionally. The candidate
identity, primary answer, targeted failures and observed check result agree
for the same proposal. A fresh output path is required for each execution.
The Review 3 practice verifier exercises both interfaces on G1, B1 and the
later-mission dispatch path G2, as well as every printed three-card batch.

Existing public subcommands and flags remain supported for this edition.
Changing a printed command, receipt meaning, protected input or default
scope requires a new edition, explicit compatibility notes and a fresh
published-command replay. A change to a client product's setup belongs on
the companion start page and does not silently alter the printed contract.
