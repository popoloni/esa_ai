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


---

# Selected prototype continuation: observed results

The AI recording operator selected the bounded prototype in `prompt_02.txt`. The original proposal above is retained unchanged as the Stage 1 record; its statements about stopping and not implementing describe that earlier stage. This continuation follows the requested scope decision and is not a correction of an observed implementation error. Independent acceptance and the final design selection remain with the operator.

## Implemented scope

Added only `design_probe.py`, with `render_decision`, `explain_direct`, and `explain_with`. Both wrappers call the same renderer. The direct wrapper calls the retained `routing.assess`; the other calls the one supplied callable. The renderer checks the route against the three contracted strings, copies the three decision fields, and adds the exact boolean and notice. It contains no amount parsing, threshold calculation, policy substitution, schema defaults, or provider registry.

The implementation write was recorded as AP-DESIGN/006, exit 0, with `changed=['design_probe.py']`. The continuation instruction read was AP-DESIGN/005, exit 0, with no changed files. The checks below were AP-DESIGN/007, exit 0, with no changed files. No protected routing or contract file was edited by these operations. No unknown non-route contract change was encountered; if one is encountered later, ask the operator before adapting it.

## Actual commands and outcomes

All continuation operations used the same recorder prefix. The implementation was written through a recorded `python3 -c` command. The behavioral check used the following actual command from the workspace; `-B` prevented imported modules from creating bytecode files.

```bash
python3 /workspace/scratch/c02668b5f4f9/ESA_v4_Agent_Process_20261116/book/tools/agent_capture.py AP-DESIGN -- python3 -B -c 'import json

import design_probe
import routing

notice = "Queue recommendation; payment approval is separate."
cases = [
    ("4000.00", "STANDARD_QUEUE", "BELOW_LIMIT"),
    ("5000.00", "HUMAN_REVIEW", "AT_OR_ABOVE_LIMIT"),
    ("-0.01", "REJECTED", "INVALID_AMOUNT"),
]
wrappers = [
    ("direct", design_probe.explain_direct),
    ("with_actual", lambda text: design_probe.explain_with(text, routing.assess)),
]
for name, explain in wrappers:
    for amount_text, route, reason in cases:
        expected = {
            "route": route,
            "reason": reason,
            "policy_version": "BR-001/v1",
            "payment_authorized": False,
            "notice": notice,
        }
        actual = explain(amount_text)
        assert actual == expected, (name, amount_text, actual, expected)
        assert actual["payment_authorized"] is False
        print(f"PASS {name} {amount_text}: {json.dumps(actual, sort_keys=True)}")

original_text = "+0001.00"
seen = []
fake_decision = routing.RoutingDecision(
    "HUMAN_REVIEW", "SUBSTITUTE_OBSERVATION", "OPS/preview:17+audit"
)

def fake(text):
    seen.append(text)
    return fake_decision

expected_fake = {
    "route": "HUMAN_REVIEW",
    "reason": "SUBSTITUTE_OBSERVATION",
    "policy_version": "OPS/preview:17+audit",
    "payment_authorized": False,
    "notice": notice,
}
injected = design_probe.explain_with(original_text, fake)
assert seen == [original_text], seen
assert injected == expected_fake, injected
assert injected["payment_authorized"] is False
print(f"PASS supplied fake input: {seen!r}; output: {json.dumps(injected, sort_keys=True)}")

rendered = design_probe.render_decision(fake_decision)
assert rendered == expected_fake, rendered
assert rendered["payment_authorized"] is False
print(f"PASS direct renderer: {json.dumps(rendered, sort_keys=True)}")

unsupported_seen = []
unsupported_decision = routing.RoutingDecision(
    "EXPRESS_QUEUE", "SUBSTITUTE_OBSERVATION", "OPS/preview:17+audit"
)

def unsupported_fake(text):
    unsupported_seen.append(text)
    return unsupported_decision

checks = [
    ("supplied fake", lambda: design_probe.explain_with(original_text, unsupported_fake)),
    ("direct renderer", lambda: design_probe.render_decision(unsupported_decision)),
]
for name, operation in checks:
    try:
        operation()
    except ValueError as error:
        print(f"PASS {name} EXPRESS_QUEUE: {type(error).__name__}: {error}")
    else:
        raise AssertionError(f"{name} accepted EXPRESS_QUEUE")
assert unsupported_seen == [original_text], unsupported_seen
print("Completed: 6 actual-provider cases, 2 unusual-policy results, 2 unsupported-route refusals.")
'
```

Observed command output:

```text
RECORDED AP-DESIGN/007 exit=0 changed=[]
PASS direct 4000.00: {"notice": "Queue recommendation; payment approval is separate.", "payment_authorized": false, "policy_version": "BR-001/v1", "reason": "BELOW_LIMIT", "route": "STANDARD_QUEUE"}
PASS direct 5000.00: {"notice": "Queue recommendation; payment approval is separate.", "payment_authorized": false, "policy_version": "BR-001/v1", "reason": "AT_OR_ABOVE_LIMIT", "route": "HUMAN_REVIEW"}
PASS direct -0.01: {"notice": "Queue recommendation; payment approval is separate.", "payment_authorized": false, "policy_version": "BR-001/v1", "reason": "INVALID_AMOUNT", "route": "REJECTED"}
PASS with_actual 4000.00: {"notice": "Queue recommendation; payment approval is separate.", "payment_authorized": false, "policy_version": "BR-001/v1", "reason": "BELOW_LIMIT", "route": "STANDARD_QUEUE"}
PASS with_actual 5000.00: {"notice": "Queue recommendation; payment approval is separate.", "payment_authorized": false, "policy_version": "BR-001/v1", "reason": "AT_OR_ABOVE_LIMIT", "route": "HUMAN_REVIEW"}
PASS with_actual -0.01: {"notice": "Queue recommendation; payment approval is separate.", "payment_authorized": false, "policy_version": "BR-001/v1", "reason": "INVALID_AMOUNT", "route": "REJECTED"}
PASS supplied fake input: ['+0001.00']; output: {"notice": "Queue recommendation; payment approval is separate.", "payment_authorized": false, "policy_version": "OPS/preview:17+audit", "reason": "SUBSTITUTE_OBSERVATION", "route": "HUMAN_REVIEW"}
PASS direct renderer: {"notice": "Queue recommendation; payment approval is separate.", "payment_authorized": false, "policy_version": "OPS/preview:17+audit", "reason": "SUBSTITUTE_OBSERVATION", "route": "HUMAN_REVIEW"}
PASS supplied fake EXPRESS_QUEUE: ValueError: Unsupported route: 'EXPRESS_QUEUE'
PASS direct renderer EXPRESS_QUEUE: ValueError: Unsupported route: 'EXPRESS_QUEUE'
Completed: 6 actual-provider cases, 2 unusual-policy results, 2 unsupported-route refusals.
```

The expected routing values were literal values supplied by the continuation contract, not values obtained from `routing.assess` to construct the assertions. Both actual-provider entry points matched all three independent expectations:

| Amount text | Expected and observed route | Expected and observed reason | Expected and observed policy |
| --- | --- | --- | --- |
| `4000.00` | `STANDARD_QUEUE` | `BELOW_LIMIT` | `BR-001/v1` |
| `5000.00` | `HUMAN_REVIEW` | `AT_OR_ABOVE_LIMIT` | `BR-001/v1` |
| `-0.01` | `REJECTED` | `INVALID_AMOUNT` | `BR-001/v1` |

Every successful result matched the exact five-field dictionary and exact notice; a separate identity assertion checked that `payment_authorized` was the boolean `False`.

The supplied fake was called once with `+0001.00`, preserving the plus sign, leading zeros, and decimal text. Its `HUMAN_REVIEW` route, `SUBSTITUTE_OBSERVATION` reason, and `OPS/preview:17+audit` policy identifier all survived unchanged. Calling the shared renderer directly on that same decision produced the same required output. An `EXPRESS_QUEUE` decision raised `ValueError` through the supplied-callable wrapper and through the renderer directly. The unsupported fake was also called once with the unchanged original text.

## Differences from the proposal and limits of the observations

There was no observed behavioral discrepancy from the proposal in this bounded exercise. The operator selected `4000.00`, `5000.00`, and `-0.01` instead of the originally suggested `4999.99`, `5000.00`, and `0`. The substitute used `+0001.00` instead of `1.00` so that unchanged text delegation was observable through its preserved spelling.

The shared renderer alone demonstrated preservation of the unusual policy identifier and refusal of the unsupported route. Therefore, those outcomes do not distinguish the need for injection. The callable wrapper added an observation about the complete wrapper boundary: a supplied substitute was invoked once with unchanged input and its returned decision reached that same renderer without editing or patching the retained provider.

These checks establish the recorded behavior for these cases. They do not establish a second production-provider requirement, exhaustive input coverage, schema compatibility with an unknown provider, reduced maintenance effort, performance improvement, or a throughput result. No timing benchmark or maintenance study was performed, and no external provider was exercised. Passing the checks does not make the operator's independent acceptance or final design decision automatic.

## Scoped recommendation and revisit condition

Keep the direct module dependency as the provisional product recommendation for the stated one-provider situation. Retain the callable variant in this bounded investigation as the demonstrated, small way to substitute a provider for a complete-wrapper check. The observed preservation and route-refusal results are already available through the renderer, so they do not by themselves justify adding a provider choice to every product call site.

Revisit that recommendation when a concrete requirement calls for repeating complete-wrapper checks with supplied decisions while avoiding provider patching or wrapper changes. That requirement would make the single callable parameter useful for an observed task. If renderer-only checks continue to cover the real need, the direct option remains sufficient for that scope. An actual future provider contract change requires a question and renewed review rather than a silent adapter or default.

This stage is complete at the selected local prototype boundary. It awaits the AI recording operator's independent acceptance and final design selection; no deployment or financial action was performed.
