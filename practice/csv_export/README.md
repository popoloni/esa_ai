# Transfer capstone: add CSV to an existing orders API

This develops the Chapter 5 export-design prompt into one small executable
change. An existing selector determines the actor's visible, filtered rows. The
feature adds a CSV presentation after that boundary and preserves JSON.

The starter spans selection, API presentation, a command-line demonstration and
synthetic data. `starter/CURRENT_CONTRACT.md` is the task authority; after copying,
read `CURRENT_CONTRACT.md` inside your new attempt folder. The archived note
describes an obsolete all-row prototype and is deliberately not current scope.
This lets you practise finding a dependency and resolving stale context before
changing a file. Authentication and deployment remain outside the local example.

## Try the change

From the companion root, copy `practice/csv_export/starter` into a **new** folder
outside the companion. Keep its first failing output. For example:

```bash
cp -R practice/csv_export/starter ../csv_attempt_01
cat ../csv_attempt_01/CURRENT_CONTRACT.md
python3 ../csv_attempt_01/demo.py --format json --actor alice --status open
python3 ../csv_attempt_01/demo.py --format csv --actor alice --status open
```

The JSON demonstration succeeds; the CSV command raises `NotImplementedError`.
Read the current contract, locate `selected_orders` and inspect its call site.
Only `api.py` and an optional new `presenter.py` are editable. Implement the
feature yourself or give that scope to your available coding agent. Retain its
first output, tool actions, any help and the final diff.

The fictional owner has resolved the consumer question for this exercise:
the CSV is for a machine importer and preserves values. Spreadsheet rendering
needs a separately approved consumer policy. Do not silently invent it here.

Run the independently authored checks against your copy:

```bash
python3 practice/csv_export/checks/check.py --candidate ../csv_attempt_01
```

The checks assert expected row membership directly. They parse CSV rather than
requiring the bytes or formatting style of the reference. They cover filtering,
empty results, quotes, commas, newlines, Unicode, formula-like text under the
declared machine-import contract, JSON compatibility and unchanged inputs.
They are selected local examples, not a complete authorization audit.

## Compare reasoning after your attempt

The `reference` directory is one direct-formatter solution. A separate presenter
is equally valid if it preserves the same interface and cases. Compare your
result with the contract before comparing its structure with the reference.

Use this short review rubric:

| Question | Defensible answer | Reopen the choice when |
|---|---|---|
| Where are rows selected? | The existing owner-controlled selector precedes either presentation. | Authentication, tenancy or filter semantics change. |
| How are cells encoded? | A CSV library preserves each field under the declared consumer contract. | A spreadsheet-specific consumer is introduced. |
| Why this design? | A direct formatter fits one small output, or a presenter isolates an actual changing seam. | A second exporter or source makes that seam useful. |
| What is still unknown? | HTTP integration, actual user usefulness, scale and any broader threat assessment. | The feature is proposed for deployment. |

At the end, write a five-line handoff: requested result, selected source and
constraint, changed files, checks actually run, and the next unresolved decision.
Do not describe the reference as the uniquely correct architecture.

`observed/starter_checks.json` and `reference_checks.json` retain the author's
executed starting failure and worked-solution result. Additional agent episodes,
when present, identify their own client scope and prior exposure separately.
