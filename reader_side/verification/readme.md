# Protected Chapter 9 verification fixtures

The independent oracle and reviewer controls live outside the candidate edit paths. `unsafe_candidate_fixture.py` and `unsafe_review_fixture.json` remain deliberately wrong after a learner repairs the editable files in `repo/engineering/verification/`. `circular_smoke.py` demonstrates why a reproducible answer can still be incorrect.

The migrated active fixtures are part of the unified companion. Original checkpoint bytes and old evidence remain in the separate historical CP09 snapshot. Current suite counts and integration results come from the unified runner.

`verification_core.check_known_candidate` retains `propose_explanation` as its default entry point. The cross-chapter bridge explicitly selects `build_explanation` to check the actual CP08 producer against this independent oracle, and adds presentation-label and evidence-receipt checks. Review results for the wrapper exercise must not be relabelled as bridge results.

These checks load known author-created modules. Their source precheck and hash manifest are educational controls, not an execution sandbox or a digital signature. Passing results retain the pending human-review and release boundaries.
