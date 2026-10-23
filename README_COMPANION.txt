ENGINEERING SOFTWARE WITH AGENTIC AI
Companion laboratory | Edition 2026.10.22-d8

START HERE
Extract the release into a new directory. Change into the directory containing
reader_start.py (companion/ in the complete author package). All commands below
run from that directory. Keep the delivered release unchanged and create a
separate study copy:

  python3 -B reader_start.py doctor
  python3 -B reader_start.py show 1
  python3 -B reader_start.py new 1 --destination ../my_treasury_lab

Read README.md and navigation/FIRST_WEEK.md. Continue Chapters 1-14 in the same
study copy. Do not run both reader_start.py new and prepare_chapter01.py for the
same destination. Either preparation route installs the deliberate Chapter 1
router defect in a new copy. Later candidates remain intentionally incomplete;
a passing regression suite is not acceptance of those starters.

PREREQUISITES
The observed baseline is Linux/Python 3.12.14/Git 2.51.1. The declared core
language floor is Python 3.10; other interpreter/OS combinations are unvalidated.
Git must support merge-tree --write-tree. Core exercises use synthetic data,
the standard library and local processes. The optional upstream Harness2 demo
requires Python 3.12 or 3.13. Other optional integrations state their own pins.
RUNTIME_MATRIX.json records the evidence and remaining external checks.

VERIFY BEFORE EDITING
Use the package's SHA-256 inventory before changing its contents. In a standalone
companion delivery this is COMPANION_SHA256SUMS.txt at the extraction root:

  sha256sum -c COMPANION_SHA256SUMS.txt

Run that command where the manifest is located, then enter the directory with
reader_start.py. Doctor checks prerequisites and protected source identity; it
does not repair candidates or grant human acceptance. The complete author
package also contains scripts/verify_hashes.py and scripts/validate_release.py.
Those author-package scripts are not required by the standalone companion.

A FIRST ROUTING REPAIR
Inside the prepared my_treasury_lab copy, run:

  python3 reader_side/tools/run_acceptance.py --output reader_side/evidence/CH01_BASELINE_RESULT.json

Exit 1 is expected for this prepared starter. Repair only
repo/src/treasury/routing.py according to the Chapter 1 contract, then run the
acceptance command again with a new result filename. Preserve both results.
README.md explains how to retain the reviewed repair and adopt the exact fixed
router required by later no-routing-change exercises.

For a separate reference check, without installing its source:

  python3 reader_side/tools/run_acceptance.py --candidate reader_side/reference_solution/routing.py --output reader_side/evidence/CH01_REFERENCE_NEW.json

That result assesses the named reference, not your current candidate.

CURRENT ROUTES
navigation/FIRST_WEEK.md supplies the minimum workflow and expansion triggers.
navigation/CHAPTER_ROUTES.md distinguishes the core, controller, harness,
fictional lifecycle and advanced human-study routes. navigation/RECOVERY.md explains stale
receipts and new study copies. The current v2 record migration is described in
reader_side/schemas/REVIEW_SCHEMAS_V2.md. Keep complete pending reviews and exact
source receipts; schema version 2 does not imply human approval.

practice/csv_export/ contains the ordinary feature exercise and an actual fresh
ChatGPT implementation with independent selected-contract checks.
practice/sdd/ preserves actual framework scaffolding and separate externally
dispatched ChatGPT generation/review. Its historical controller ended WAITING_HUMAN.
practice/sdd/NATIVE_ROUTE.md documents the separate installed-framework route and its actual
observation status. practice/native_client/ contains the OpenCode route, portable
setup receipts and retained native sessions. Read each observation summary before
inferring that an attempted phase passed.
practice/workflow_cost/ includes the real, prospectively recorded guide repair
through independent AGENT technical acceptance; complete money remains unknown.
practice/lifecycle/ connects a separately approved fictional operator feature
to release, policy history and incident recovery.
practice/verification_tools/ contains actual Hypothesis and Bandit observations.
practice/ai_review/ contains a small actual critic review and its comparison.

Read each practice README before running a command. The default orchestration
and harness demonstrations remain scripted local examples. Native interoperability
claims apply only to the exact observed client, configuration and retained requests.
Hosted CI, production approval, human comprehension and field economics remain
unobserved. Missing values remain unknown.

BOOK AND SOLUTIONS
The book has four Parts, fourteen chapters and two Appendices. Appendix A works
through the exercises as one continuing project. Appendix B, From AI Claims to
Engineering Decisions, connects research to local engineering decisions.
SOLUTION_NAVIGATION.txt maps the sections. EXERCISE_COVERAGE.json distinguishes
the 166 inherited prompt mappings from optional d4/d5/d7 practice routes. Current
source identities are verified separately; historical locators retain their scope.

The advanced learning guide is in practice/team_operations/. Participants in
its optional human study must leave the worked transfer solution and reference
artifacts unread until assessment is complete; record any prior exposure. The
ordinary synthetic Chapters 13-14 chain has no 24-hour waiting requirement.
