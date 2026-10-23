"""Explicit scenario arithmetic; measured process time is never human effort."""
from decimal import Decimal, ROUND_HALF_UP, localcontext
import re

ORIGIN = "SYNTHETIC_SCENARIO_ASSUMPTIONS"
CATEGORIES = ("initial", "review", "rework")


def nonnegative_decimal(value, field):
    if (not isinstance(value, str) or len(value) > 32
            or not re.fullmatch(r"(?:0|[1-9][0-9]*)(?:\.[0-9]{1,6})?", value)):
        raise ValueError("DECIMAL_STRING_REQUIRED:" + field)
    number = Decimal(value)
    if not number.is_finite() or number < 0 or number > Decimal("1000000000"):
        raise ValueError("DECIMAL_OUT_OF_BOUNDS:" + field)
    return number


def money(value):
    return format(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), ".2f")


def cost_per_accepted(total, accepted_count, currency):
    if not isinstance(total, Decimal) or not total.is_finite() or total < 0 or currency != "EUR":
        raise ValueError("TOTAL_OR_CURRENCY_INVALID")
    if type(accepted_count) is not int or accepted_count < 0:
        raise ValueError("ACCEPTED_COUNT_MUST_BE_NONNEGATIVE_INTEGER")
    return {"status": "DEFINED" if accepted_count else "UNDEFINED", "currency": currency,
            "amount": money(total / accepted_count) if accepted_count else None,
            "distinct_accepted_outcomes": accepted_count,
            "denominator_origin": "PROTECTED_SYNTHETIC_OWNER_ACCEPTANCE"}


def calculate_scenarios(fixture, attempt_ids, accepted_count):
    """All declared attempts enter every scenario; no missing value becomes zero."""
    if (not isinstance(fixture, dict) or fixture.get("schema") != "cp14-scenario-costs/v1"
            or fixture.get("origin") != ORIGIN or fixture.get("field_result") is not False
            or fixture.get("currency") != "EUR"
            or fixture.get("effort_categories") != "MUTUALLY_EXCLUSIVE_INITIAL_IMPLEMENTATION_REVIEW_AND_IMPLEMENTATION_REWORK"):
        raise ValueError("SCENARIO_SCHEMA_OR_CURRENCY")
    if (not isinstance(attempt_ids, list) or not attempt_ids or any(not isinstance(v, str) for v in attempt_ids)
            or len(set(attempt_ids)) != len(attempt_ids)):
        raise ValueError("ATTEMPT_IDENTITIES")
    if type(accepted_count) is not int or accepted_count < 0:
        raise ValueError("ACCEPTED_COUNT_MUST_BE_NONNEGATIVE_INTEGER")
    rates = fixture.get("rates_per_hour")
    if not isinstance(rates, dict) or set(rates) != set(CATEGORIES):
        raise ValueError("RATES_SCHEMA")
    rates = {name: nonnegative_decimal(value, "rate_" + name) for name, value in rates.items()}
    rows = fixture.get("attempt_costs")
    expected_fields = {"attempt_id", "initial_hours", "review_hours", "rework_hours", "vendor_cost", "compute_cost", "currency", "origin"}
    if not isinstance(rows, list) or len(rows) != len(attempt_ids):
        raise ValueError("ALL_ATTEMPT_COSTS_REQUIRED")
    observed_ids = []
    quantities = {name: Decimal(0) for name in CATEGORIES}
    charges = {name: Decimal(0) for name in ("vendor", "compute")}
    attempt_costs = []
    with localcontext() as context:
        context.prec = 50
        for row in rows:
            if (not isinstance(row, dict) or set(row) != expected_fields
                    or row["currency"] != fixture["currency"] or row["origin"] != ORIGIN):
                raise ValueError("ATTEMPT_COST_SCHEMA_OR_CURRENCY")
            observed_ids.append(row["attempt_id"])
            hours = {name: nonnegative_decimal(row[name + "_hours"], name + "_hours") for name in CATEGORIES}
            extras = {name: nonnegative_decimal(row[name + "_cost"], name + "_cost") for name in charges}
            amount = sum((hours[name] * rates[name] for name in CATEGORIES), Decimal(0)) + sum(extras.values(), Decimal(0))
            for name, value in hours.items():
                quantities[name] += value
            for name, value in extras.items():
                charges[name] += value
            attempt_costs.append({"attempt_id": row["attempt_id"], "currency": "EUR", "cost": money(amount),
                                  "origin": ORIGIN})
        if observed_ids != attempt_ids:
            raise ValueError("MISSING_DUPLICATED_OR_REORDERED_ATTEMPT_COST")
        labor = {name: quantities[name] * rates[name] for name in CATEGORIES}
        base = sum(labor.values(), Decimal(0)) + sum(charges.values(), Decimal(0))
        ceiling = nonnegative_decimal(fixture.get("pilot_ceiling_per_accepted_outcome"), "pilot_ceiling")
        scenarios = fixture.get("scenarios")
        if not isinstance(scenarios, list) or not scenarios:
            raise ValueError("SENSITIVITY_SCENARIOS_REQUIRED")
        ids, results = set(), []
        for scenario in scenarios:
            if (not isinstance(scenario, dict) or set(scenario) != {"id", "extra_rework_hours", "retain_final_acceptance"}
                    or not isinstance(scenario["id"], str) or not scenario["id"] or scenario["id"] in ids
                    or type(scenario["retain_final_acceptance"]) is not bool):
                raise ValueError("SENSITIVITY_SCHEMA")
            ids.add(scenario["id"])
            extra = nonnegative_decimal(scenario["extra_rework_hours"], "extra_rework_hours")
            total = base + extra * rates["rework"]
            denominator = accepted_count if scenario["retain_final_acceptance"] else 0
            cpa = cost_per_accepted(total, denominator, "EUR")
            decision = "STOP" if not denominator else ("GO" if total / denominator <= ceiling else "CHANGE")
            results.append({"scenario_id": scenario["id"], "origin": ORIGIN, "currency": "EUR",
                            "total_cost": money(total), "extra_rework_hours": str(extra),
                            "cost_per_accepted_outcome": cpa, "conditional_pilot_decision": decision,
                            "decision_authority": "NO_REAL_PILOT_PROCUREMENT_OR_RELEASE_AUTHORIZATION"})
        return {"schema": "cp14-scenario-calculation/v1", "origin": ORIGIN, "currency": "EUR",
                "rounding": "ROUND_HALF_UP_AT_CURRENCY_PRESENTATION; comparisons use unrounded Decimal totals",
                "attempt_costs": attempt_costs, "hours": {name: str(value) for name, value in quantities.items()},
                "labor_costs": {name: money(value) for name, value in labor.items()},
                "nonlabor_costs": {name: money(value) for name, value in charges.items()}, "total_cost": money(base),
                "cost_per_accepted_outcome": cost_per_accepted(base, accepted_count, "EUR"),
                "pilot_ceiling_per_accepted_outcome": money(ceiling), "scenarios": results,
                "measured_field_result": False}
