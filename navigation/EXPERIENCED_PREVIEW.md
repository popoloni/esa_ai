# Start with a small feature in a different repository

This preview uses the existing orders CSV exercise. You can run it before the
Treasury chapters: it needs no completed Treasury candidate, Git history, model
account or optional SDK. The commands below use a POSIX shell and Python 3.10 or
later. The recorded environment is Linux with Python 3.12.14; the language floor
does not establish observations on every platform. Run commands from the
companion root. Choose an unused destination and keep all results.

If you prefer a cumulative case, start with [the first-week route](FIRST_WEEK.md)
and Chapter 1. Both routes mean the same thing by **candidate** (the change you
propose), **evidence** (the observations retained about it), and **acceptance**
(the applicable review and owner decision, separate from a green test run).

## 1. Find the current behavior and predict one failure

Copy the small starter into a new sibling directory:

```bash
cp -R practice/csv_export/starter ../csv_preview_01
cat ../csv_preview_01/CURRENT_CONTRACT.md
python3 ../csv_preview_01/demo.py --format json --actor alice --status open
python3 ../csv_preview_01/demo.py --format csv --actor alice --status open
```

The JSON command returns Alice's visible open orders. The CSV command raises
`NotImplementedError`. Keep that initial failure. Before editing, locate
`selected_orders` and its call in `api.py`. Predict the error a formatter would
introduce if it selected all stored rows itself. Which actor or filter case
would expose that error?

The [current contract](../practice/csv_export/starter/CURRENT_CONTRACT.md)
is the task source. Its fictional owner has chosen a machine-import consumer:
CSV preserves values, including formula-like text. A spreadsheet-specific policy
would be another decision. The archived note describes an obsolete prototype;
it does not override the current selector or contract.

## 2. Make one bounded change and observe its result

Edit only `api.py` and, if useful, a new `presenter.py` in your preview copy.
Keep selection, synthetic data, the JSON interface and the independent checks
unchanged. Implement it yourself or give that scope to your chosen coding
client. If a client helps, retain its prompt, first output, tool actions and
any corrective help; a displayed completion message is only a claim.

```bash
python3 practice/csv_export/checks/check.py --candidate ../csv_preview_01
python3 ../csv_preview_01/demo.py --format csv --actor alice --status open
```

The independent checker evaluates selected rows, filtering, empty results,
CSV parsing of quotes/commas/newlines/Unicode, the declared formula-cell policy,
unchanged JSON behavior and protected inputs. It permits different correct
implementations. Compare the actual CSV with your prediction; inspect the
changed files and the checker details before calling the task complete.

## 3. Hand off the candidate and one remaining limit

Write five lines: requested result; current source and preserved constraint;
changed files; checks actually observed; next unresolved decision. State one
plausible limitation, such as untested HTTP integration or an additional
consumer. There is no need for a PRD, task graph or release rehearsal for this
local presentation exercise. Do not claim deployed access control, user benefit
or production readiness from its selected checks.

The [full exercise](../practice/csv_export/README.md) includes a review rubric
and alternative-design discussion. Consult its reference only after your own
attempt. The historical ChatGPT observation is not evidence of a human reader's
transfer. Independent reader use remains an observation to collect.

## Apply the same five questions to your own authorized task

Choose a small repository change whose purpose and edit scope you are allowed
to assess. For example, preserve an existing filtered JSON response while adding
one export format. Identify the current request or owner statement, find the
selection boundary, predict one concrete failure, write or retain an expectation
outside the implementation edit, and inspect a real before/after result.

Your handoff should use the repository's own terms. It need not copy Treasury
identifiers or status strings. If the purpose is disputed, return the question
to its owner. If data persists or another service acts on it, use the additional
controls in [the lifecycle map](LIFECYCLE_MAP.md). For selected examples involving
API compatibility, repeated messages and the wrong tenant, use the existing
[short transfer exercises](../practice/production_controls/TRANSFER_EXERCISES.md).
Record your prediction before reading their worked feedback, then explain what
the actual observation changed in your reasoning.
