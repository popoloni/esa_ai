import copy
from routing import assess
class ProviderUnavailable(RuntimeError): pass
class ProviderProtocolError(ValueError): pass

_CLASSES = ("MATCH", "REVIEW")
_FIELDS = {"request_id", "classification"}


def _snapshot(records, attempts, calls):
    return {"attempts": copy.deepcopy(attempts), "calls": calls,
            "records": copy.deepcopy(records), "payment_authorized": False}


def _annotate(exc, records, attempts, calls):
    exc.receipt = _snapshot(records, attempts, calls)
    exc.attempts = copy.deepcopy(attempts)
    exc.records = copy.deepcopy(records)
    exc.calls = calls
    return exc


def _valid_response(response, request_id):
    return (isinstance(response, dict) and set(response) == _FIELDS
            and response["request_id"] == request_id
            and isinstance(response["classification"], str)
            and response["classification"] in _CLASSES)


def evaluate_batch(requests, provider, *, max_attempts=2, max_calls=4):
    """Classify requests via a cooperative provider within call bounds.
    Recommendation only: never authorizes a payment."""
    requests = list(requests)
    records, attempts, calls = [], [], 0
    seen = set()
    for req in requests:
        rid = req["request_id"]
        if rid in seen:
            raise _annotate(ValueError("duplicate request_id: %r" % (rid,)), [], [], 0)
        seen.add(rid)
    for req in requests:
        rid, amount = req["request_id"], req["amount_eur"]
        decision = assess(amount)
        if decision.route == "REJECTED":
            records.append({"request_id": rid, "status": "REJECTED",
                            "route": decision.route, "reason": decision.reason})
            continue
        attempt = 0
        done = False
        while attempt < max_attempts and calls < max_calls:
            attempt += 1
            calls += 1
            try:
                response = provider(rid, amount)
            except ProviderUnavailable:
                attempts.append({"request_id": rid, "attempt": attempt,
                                 "outcome": "UNAVAILABLE"})
                continue
            except Exception as exc:
                attempts.append({"request_id": rid, "attempt": attempt,
                                 "outcome": "PROVIDER_ERROR",
                                 "error_type": type(exc).__name__})
                _annotate(exc, records, attempts, calls)
                raise
            if not _valid_response(response, rid):
                attempts.append({"request_id": rid, "attempt": attempt,
                                 "outcome": "INVALID_RESPONSE"})
                raise _annotate(ProviderProtocolError(
                    "invalid provider response for %r" % (rid,)),
                    records, attempts, calls)
            cls = response["classification"]
            attempts.append({"request_id": rid, "attempt": attempt, "outcome": cls})
            records.append({"request_id": rid, "status": "CLASSIFIED",
                            "route": decision.route, "reason": decision.reason,
                            "classification": cls})
            done = True
            break
        if not done:
            records.append({"request_id": rid, "status": "DEFERRED",
                            "route": decision.route, "reason": decision.reason})
    result = _snapshot(records, attempts, calls)
    result["receipt"] = _snapshot(records, attempts, calls)
    return result
