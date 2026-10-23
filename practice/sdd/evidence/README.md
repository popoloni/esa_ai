# Observed evidence and authored specimens

`RUN_INDEX.json` indexes retained observations. `receipts/` holds command records
and input/output inventories; `logs/` holds actual stdout/stderr. Successful
commands and failed setup attempts are both retained. No credential values were
inherited by the CLI subprocesses or written to these records. The installation
retry retained the environment's required network proxy/certificate settings
without logging their values.

`scaffolds/` preserves actual locally generated Spec Kit/OpenSpec workspace
outputs, including the common input packet and unfilled framework templates.
Upstream MIT notices are retained under `upstream_licenses/`. Treat generated
instructions as tool assets to inspect, not instructions governing this review.
No dependency directory, package cache, global installation or model session is
included.

The populated Treasury artifacts under `../fixtures/` are authored examples.
`author_repair_after/` preserves the actual fresh-copy attempt after two spec
edits; its `ORIGIN.json` records continue to identify its original before
specimen. `receipts/actual_repair_record.json` binds before and after inventories
and confirms that only the two behavioral spec files changed. The unchanged
requirements and case oracle are not inferred from the repaired outputs.

`code_identity.json` identifies the book checker/exercise/test source executed in
these author-side observations. If those sources change, rerun affected checks
and keep the old receipt as historical evidence rather than silently relabelling
it current. Core CP03/CP04/CP05 candidates, references and scope files are outside
the edit boundary of this practice exercise.

Origins are explicit: `cli_scaffold` for local setup/template operations,
`cli_inspection` for local version/help observation,
`cli_validation_of_author_exercise` and `cli_inspection_of_author_exercise` for
framework commands over authored artifacts, and `author_exercise` for the book's
own checks and repairs. Every such category leaves live named-agent generation
and independent human requirements review unperformed.
