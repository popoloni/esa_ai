# Choose a control for a consequence

These are suggested design choices. The named roles are responsibilities, not mandatory job titles. Select the smallest set that addresses the current change, then add controls when its consequence warrants them. Record what is omitted and why. A test list alone is not a production policy.

| Failure or changed boundary | Selected check and evidence | Responsible role and decision |
|---|---|---|
| Wrong routing or authority label | Requirement-derived boundary/negative cases; exact candidate and expected fields | Domain reviewer rejects behavior outside the authorized contract |
| Consumer cannot read a new response | Exercise supported consumer versions against produced examples; preserve failing pair | API owner defers removal until consumer migration is evidenced |
| Slower query, extra calls or memory growth | Repeat a declared workload/environment; compare traces/plans and a chosen budget | Service owner investigates a budget breach before expanding traffic |
| UI text, accessibility or locale regression | User task, keyboard/accessibility checks and locale cases; human findings | Product/accessibility owner settles interpretation and remaining manual checks |
| Architectural coupling or forbidden access | Dependency/interface rule plus affected integration checks | Technical owner reviews a new dependency or boundary violation |
| Known vulnerable dependency | Locked versions, dated advisory result and documented disposition | Dependency/security owner triages applicability; absence of an advisory is not proof of safety |
| Secret included in a change | Configured secret scan and exposure response, retaining safe finding identifiers | Security owner arranges revocation/rotation and history treatment; deletion alone is insufficient |
| Substituted or untrusted artifact | Artifact digest, authenticated provenance and configured verification policy | Release owner checks producer/source/parameters before artifact use |
| Incompatible persisted data or repeated effect | Mixed-version and retry/restart cases; preserved migration inputs and state | Data/consumer owner authorizes a phased change or blocks ambiguous history |
| Harm during rollout or wrong effective state | Bounded exposure, per-version signals, state identity and a rehearsed stop/recovery action | Operator pauses according to declared criteria; reconciliation remains a separate owner decision |

The current cumulative lab directly exercises selected routing, evidence freshness, local artifact identity, policy history and incident-state obligations. The added `contract_drill.py` directly exercises two small readers and response fixtures. Scanners, accessibility tooling, realistic load testing, signed production provenance, traffic rollout and live telemetry are documented extensions here, not newly executed capabilities.

## Three scale choices

- **Reversible label-only change:** intended wording, preserved routing assertions, the exact diff and one appropriately scoped review may be sufficient for a local practice. It does not gain payment authority.
- **Shared API representation:** add consumer-version evidence and a compatibility/removal plan. Passing the new consumer alone is insufficient.
- **Persistent history or external effects:** add identity, retry and failed-write behavior, migration/rollback limits, retained evidence and the relevant data/operation owner. A low-risk label workflow is no longer enough.

For every chosen control write: consequence, selected scope, expected refusal, evidence location, owner, blocking versus advisory rule, and next decision. For an advisory result record an explicit triage path; for a blocker ensure the actual repository or release system enforces it. An agent can draft this record but cannot grant approval by filling it in.

Primary documentation: Pact introduction (https://docs.pact.io/), Google SRE Canarying Releases (https://sre.google/workbook/canarying-releases/), and AWS Ensuring rollback safety during deployments (https://aws.amazon.com/builders-library/ensuring-rollback-safety-during-deployments/). Existing chapter references cover scanning, access control and provenance. These sources ground particular mechanisms, not every illustrative decision in this original map.
