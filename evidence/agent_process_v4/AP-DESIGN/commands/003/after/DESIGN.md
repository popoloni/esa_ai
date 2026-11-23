# Treasury explanation design investigation

## Stage and evidence

Stage 1: design only. This document proposes an investigation for the AI recording operator to select. No prototype is implemented and no runtime verification has been performed.

Observed sources: `AGENTS.md`, `DESIGN_CONTRACT.md`, and the retained, protected `routing.py` in this workspace. Static inspection shows one provider, `routing.assess(amount_eur)`, returning an immutable `RoutingDecision` with `route`, `reason`, and `policy_version`. The provider currently uses policy identifier `BR-001/v1` and a EUR 5000.00 threshold. Parsing, validity checks, threshold comparison, and reasons belong to that provider; the presentation layer must not repeat them. The contract supplies no second production provider, throughput target, or measured maintenance gain.

## Shared behavior and boundary

Both alternatives use the same `render_decision(decision)` behavior. It exposes exactly these five fields:

| Output field | Source or required value |
| --- | --- |
| `route` | The supplied decision route, unchanged, after the route allowlist check |
| `reason` | The supplied decision reason, unchanged |
| `policy_version` | The supplied decision policy identifier, unchanged |
| `payment_authorized` | Boolean `false` |
| `notice` | `Queue recommendation; payment approval is separate.` |

The only supported routes are `STANDARD_QUEUE`, `HUMAN_REVIEW`, and `REJECTED`; any other route raises `ValueError`. Rendering does not parse amounts, compare thresholds, infer a reason, normalize policy identifiers, or convert a recommendation into payment approval. A policy identifier that differs from the retained constant is a legitimate supplied value under the existing contract and must be preserved.

A newly encountered non-route contract change, such as a missing or renamed field, altered field shape, or changed authorization semantics, requires a question to the operator before adapting the design. Do not silently invent defaults, translate a new schema, or broaden the interface. Both alternatives initially consume the retained `RoutingDecision` shape. No registry, provider framework, network, database, deployment, or financial effect is included.

## Two low-complexity alternatives

| Consideration | A. Direct module dependency | B. One explicitly supplied callable |
| --- | --- | --- |
| Structure | `explain_direct(amount_text)` obtains a decision from `routing.assess` and passes it to the shared renderer. | `explain_with(amount_text, decide)` calls the supplied callable once with the unchanged amount text and passes its decision to the same renderer. |
| Paying scenario today | One retained provider and an inspectable presentation boundary. The dependency is visible in a small wrapper and callers only supply the amount text. | The stated investigation needs a focused substitute at the wrapper boundary to exercise an unusual policy identifier and an unsupported route without editing the retained provider. |
| Implementation cost | One provider import and a wrapper in addition to the common renderer. The common rendering checks are still necessary. | One callable parameter and a wrapper in addition to the same renderer. The caller supplies the provider; no class hierarchy, registration, or default-provider machinery is needed. |
| Use and review cost | Callers have no provider choice to manage. Reviewing the complete wrapper requires reading its fixed dependency. | Call sites must identify and supply the callable. Review must confirm that the selected callable accepts the amount text and returns the agreed decision shape. |
| Negative consequences | A focused substitute for the complete wrapper would require a patching technique or a code change; the fixed provider cannot naturally emit the proposed unusual identifier or unsupported route. The shared renderer remains independently exercisable with constructed decisions. | The extra argument creates another configuration choice and permits an unsuitable callable to be passed. The seam may be unnecessary when only renderer behavior needs investigation. It does not itself validate or adapt an unknown provider contract. |
| Observation that could reverse a choice | Prefer B if an actual bounded wrapper-level substitution exercise is required repeatedly and needs provider replacement without patching or changing the wrapper. Merely testing the renderer is insufficient evidence for that choice. | Prefer A if the needed observations are obtained by invoking the shared renderer directly, or if the complete wrapper adds no useful observation beyond its fixed provider delegation. Reconsider B if concrete callable contract ambiguity makes the boundary harder to inspect. |

## Provisional choice and limits

A is the provisional choice for the stated product situation: one provider with a small, inspectable presentation boundary. B is a deliberately small experimental alternative for the stated substitution question. Neither choice changes routing policy. The shared renderer can already demonstrate preservation and route refusal with constructed decisions, so those two observations alone cannot establish that callable injection is necessary in production.

This is a design judgment based on the supplied scenario and static source inspection. There are no measured performance results, maintenance savings, throughput comparisons, or claims that either option scales better. A future second provider is not assumed. The prototype should reveal observable delegation and rendering behavior, not be presented as proof of long-term architectural benefit.

## Proposed bounded prototype for operator selection

Proposed scope: after explicit operator selection, add one local `design_probe.py` containing only the three specified entry points: `explain_direct(amount_text)`, `explain_with(amount_text, decide)`, and `render_decision(decision)`. Both wrappers use the identical renderer. Leave the retained provider, contracts, acceptance material, and unrelated files unchanged. Keep verification local and bounded; do not add a provider framework or additional production integration.

The discriminating question is whether supplying one callable produces a useful, inspectable wrapper-level observation beyond the observations already available from the common renderer.

Planned observations, not results:

1. Pass the retained `routing.assess` to the callable wrapper and compare both wrappers on `4999.99`, `5000.00`, and `0`. Require equal output, the exact five-field shape, and preservation of the retained decisions. These examples exercise the existing routing paths without recreating their threshold logic in presentation.
2. Supply one focused local callable that records its input and returns a retained-shape `RoutingDecision` with route `HUMAN_REVIEW`, reason `SUBSTITUTE_OBSERVATION`, and policy identifier `OPS/preview:17+audit`. Use amount text `1.00`. Observe that the wrapper calls the substitute exactly once with unchanged text and preserves the supplied route, reason, and unusual identifier. This intentionally differs from what the retained provider would recommend for that amount and can expose presentation that recalculates routing.
3. Use the same focused substitution mechanism to return route `EXPRESS_QUEUE`. Require `ValueError`, with no recommendation output. Invoke the shared renderer directly with equivalent allowed and unsupported decisions to establish which observations are available without callable injection.
4. For every successful result, check the exact field set, literal boolean `false`, and exact notice. Record only actual observations and any unresolved contract question; do not infer speed or maintenance gains from passing checks.

The narrow decision after that investigation is whether a caller-supplied dependency contributes an observation that is needed at the complete wrapper boundary. If renderer-only checks cover the stated need, keep the direct option. If complete-wrapper substitution is a concrete requirement and is achieved with the single explicit parameter, retain B as the smallest demonstrated seam for that requirement.

## Stop for selection

The AI recording operator must select the bounded prototype scope before implementation. This stage edits `DESIGN.md` only. No `design_probe.py`, implementation, acceptance changes, or prototype tests have been created or run.
