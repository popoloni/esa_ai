## Feature Specification: Explain Routing

**Feature Branch**: 001-explain-treasury

**Created**: 2026-10-22

**Status**: Draft

**Input**: User description: "Project: /workspace/scratch/72d789d25fef/runtime_d8/native_sdd_01
SPECIFY_FEATURE_DIRECTORY=specs/001-explain-treasury
The native client attaches this complete source packet before your first response: @/workspace/scratch/72d789d25fef/runtime_d8/native_sdd_01/inputs/NATIVE_CONTEXT_BUNDLE.md
It contains all nine fixed JSONs including the authored reference contract, router, complete templates and unratified constitution. JSON whitespace alone changed. Use the attached full contents without rereading duplicates. Preserve every requirement/scenario ID, value, provenance and authority. SRC-POL-001/BR-001/v1 governs; ticket/wiki cannot change it. Routing never authorizes payment.
Execute the full native command now using actual tools: create the feature draft and truthful checklist, not just an announcement of future work. Write only .specify/feature.json, specs/001-explain-treasury/spec.md and specs/001-explain-treasury/checklists/requirements.md. Use permitted bash commands individually, without chaining. No extensions.yml exists; test exit1 means absent. Preset resolution returns a text path.
Keep all three source owner questions unanswered and benefit HYPOTHESIS_NOT_VALIDATED. Invent no owner answers, numeric benefit targets, ratification or approval. Present the actual unresolved questions and wait at that boundary; stop before planning/implementation. Leave failed readiness checks visibly incomplete. Report any blocking failure truthfully. This is a disclosed synthetic reference projection, not blind discovery or observed user benefit.

Read-scope guard: The complete source packet is already attached before inference. Model read access is limited to the three generated output paths; source, template and bundle rereads are denied. Use the supplied complete content directly. Read generated outputs only for a concrete necessary check, using a bounded line range; avoid duplicate full-file reads. No output files exist at the start. This guard supplies no draft text or owner answers and does not alter the full installed framework command."

**Requirements**:

1. **REQ-EXPL-001**: Explain the routing recommendation for a valid routing decision the explanation MUST present route, reason code and policy version without altering the routing decision.
   - **Source**: SRC-POL-001, SRC-OPS-004
   - **Owner**: Product Owner (synthetic scenario)

2. **REQ-EXPL-002**: Keep payment authorization separate
   - **Statement**: The explanation MUST explicitly say that a routing recommendation is not payment approval and that payment authorization remains a separate human process.
   - **Source**: SRC-POL-001, SRC-RISK-002
   - **Owner**: Treasury Policy Owner (synthetic scenario)

3. **REQ-EXPL-003**: Represent invalid requests safely
   - **Statement**: For invalid or non-positive amounts the explanation MUST report rejection and the INVALID_AMOUNT reason without creating an eligibility recommendation.
   - **Source**: SRC-POL-001
   - **Owner**: Product Owner (synthetic scenario)

4. **REQ-EXPL-004**: Carry verified policy provenance
   - **Statement**: The explanation MUST display the policy version from the routing decision and MUST NOT silently infer a newer policy version or threshold.
   - **Source**: SRC-POL-001
   - **Owner**: Treasury Policy Owner (synthetic scenario)

5. **REQ-EXPL-005**: Do not present unvalidated benefit as fact
   - **Statement**: The alpha MUST treat time savings and user benefit as hypotheses pending observation and MUST NOT report a measured ROI before a field study.
   - **Source**: SRC-OPS-004, SYN-TRIAGE-CSV
   - **Owner**: Product Owner (synthetic scenario)

**Scenarios**:

| Scenario ID | Requirement ID | Input Amount (EUR) | Expected Route | Expected Reason | Expected Policy Version | Payment Authorized |
|-------------|----------------|---------------------|----------------|------------------|--------------------------|-------------------|
| SC-EXPL-001 | REQ-EXPL-001 | 4999.99 | STANDARD_QUEUE | BELOW_LIMIT | BR-001/v1 | false |
| SC-EXPL-002 | REQ-EXPL-001 | 5000 | HUMAN_REVIEW | AT_OR_ABOVE_LIMIT | BR-001/v1 | false |
| SC-EXPL-003 | REQ-EXPL-001 | 5000.01 | HUMAN_REVIEW | AT_OR_ABOVE_LIMIT | BR-001/v1 | false |
| SC-EXPL-004 | REQ-EXPL-003 | 0 | REJECTED | INVALID_AMOUNT | BR-001/v1 | false |
| SC-EXPL-005 | REQ-EXPL-003 | -10 | REJECTED | INVALID_AMOUNT | BR-001/v1 | false |
| SC-EXPL-006 | REQ-EXPL-003 | nonsense | REJECTED | INVALID_AMOUNT | BR-001/v1 | false |
| SC-EXPL-007 | REQ-EXPL-003 | NaN | REJECTED | INVALID_AMOUNT | BR-001/v1 | false |
| SC-EXPL-008 | REQ-EXPL-004 | 1 | STANDARD_QUEUE | BELOW_LIMIT | BR-001/v1 | false |

**Unresolved Owner Questions**:
1. Which explanation vocabulary do real operators understand?
2. Does the interface accidentally induce payment approval?
3. How will actual user benefit be measured in a pilot?

**Benefit**: HYPOTHESIS_NOT_VALIDATED

**Constitution**: Unratified

**Payment-Authorization Boundary**: Separate human process

**Unratified Constitution**: Yes

**Unanswered Owner Questions**: 3

**Status**: The three unresolved owner questions remain unanswered and benefit HYPOTHESIS_NOT_VALIDATED. No owner answers, numeric benefit targets, ratification or approval are invented. The three artifacts are concise, aiming for at most 1,800 tokens of combined content without omitting fixed requirements or cases.