"""INTAKE/v1: bounded intake and cooperative-provider classification.

Never authorizes a payment. Snapshots on exceptions are local evidence, not a
durable ledger; this is not durable idempotency (B3).
"""
import copy
from routing import assess

class ProviderUnavailable(RuntimeError): pass
class ProviderProtocolError(ValueError): pass

_CLASSES = ("MATCH", "REVIEW")
_FIELDS = {"request_id", "classification"}


def _snapshot(attempts, records, calls):
    return {"attempts": copy.deepcopy(attempts), "records": copy.deepcopy(records),
            "calls": calls, "payment_authorized": False}


def _attach(exc, attempts, records, calls):
    exc.receipt = _snapshot(attempts, records, calls)
    exc.attempts = copy.deepcopy(attempts)
    exc.records = copy.deepcopy(records)
    exc.calls = calls
    return exc


def _valid(response, request_id):
    return (isinstance(response, dict) and set(response) == _FIELDS
            and response["request_id"] == request_id
            and isinstance(response["classification"], str)
            and response["classification"] in _CLASSES)


def evaluate_batch(requests, provider, *, max_attempts=2, max_calls=4):
    attempts, records, calls = [], [], 0
    try:
        requests = list(requests)
        # Whole-batch duplicate validation before any provider call.
        seen = set()
        for req in requests:
            rid = req["request_id"]
            if rid in seen:
                raise ValueError("duplicate request_id: %r" % (rid,))
            seen.add(rid)

        for req in requests:
            rid, amount = req["request_id"], req["amount_eur"]
            decision = assess(amount)
            if decision.route == "REJECTED":
                records.append({"request_id": rid, "status": "REJECTED",
                                "route": decision.route, "reason": decision.reason})
                continue
            n, done = 0, False
            while n < max_attempts and calls < max_calls:
                n += 1
                calls += 1
                try:
                    response = provider(rid, amount)
                except ProviderUnavailable:
                    attempts.append({"request_id": rid, "attempt": n,
                                     "outcome": "UNAVAILABLE"})
                    continue
                except Exception as exc:
                    attempts.append({"request_id": rid, "attempt": n,
                                     "outcome": "PROVIDER_ERROR",
                                     "error_type": type(exc).__name__})
                    raise
                if not _valid(response, rid):
                    attempts.append({"request_id": rid, "attempt": n,
                                     "outcome": "INVALID_RESPONSE"})
                    raise ProviderProtocolError(
                        "invalid provider response for request %r" % (rid,))
                cls = response["classification"]
                attempts.append({"request_id": rid, "attempt": n, "outcome": cls})
                records.append({"request_id": rid, "status": "CLASSIFIED",
                                "route": decision.route, "reason": decision.reason,
                                "classification": cls})
                done = True
                break
            if not done:
                records.append({"request_id": rid, "status": "DEFERRED",
                                "route": decision.route, "reason": decision.reason})
    except Exception as exc:
        raise _attach(exc, attempts, records, calls)
    return _snapshot(attempts, records, calls)
