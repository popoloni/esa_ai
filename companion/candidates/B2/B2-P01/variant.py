"""Bounded local classification with evidence retained on
failure.
"""
from routing import assess


class ProviderUnavailable(RuntimeError):
    pass


class ProviderProtocolError(ValueError):
    pass


def _receipt(records, attempts):
    return {
        "records": [dict(item) for item in records],
        "attempts": [dict(item) for item in attempts],
        "calls": len(attempts),
        "payment_authorized": False,
        "external_network_used": False,
    }


def evaluate_batch(
    requests, provider, *, max_attempts=2, max_calls=4
):
    """Bound invocations; a cooperative adapter must supply
    time limits.

    Errors retain their original type and expose a snapshot
    as ``receipt`` plus ``attempts``, ``records`` and ``calls``.
    No failed call disappears.
    """
    records, attempts = [], []
    try:
        if type(max_attempts) is not int or max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        if type(max_calls) is not int or max_calls < 0:
            raise ValueError("max_calls must be nonnegative")
        requests = list(requests)
        seen = set()
        for request in requests:
            key = request["request_id"]
            if key in seen:
                raise ValueError("duplicate request_id in this batch")
            seen.add(key)
        for request in requests:
            key = request["request_id"]
            decision = assess(request["amount_eur"])
            if decision.route == "REJECTED":
                records.append({
                    "request_id": key, "status": "REJECTED",
                    "route": decision.route})
                continue
            response = None
            for attempt in range(1, max_attempts + 1):
                if len(attempts) > max_calls:
                    break
                event = {"request_id": key, "attempt": attempt}
                attempts.append(event)
                try:
                    response = provider(key, request["amount_eur"])
                except ProviderUnavailable:
                    event["outcome"] = "UNAVAILABLE"
                    continue
                except Exception as error:
                    event["outcome"] = "PROVIDER_ERROR"
                    event["error_type"] = type(error).__name__
                    raise
                if (
                    not isinstance(response, dict)
                    or set(response) != {
                        "request_id", "classification"}
                    or response["request_id"] != key
                    or not isinstance(
                        response["classification"], str)
                    or response["classification"] not in (
                        "MATCH", "REVIEW")
                ):
                    event["outcome"] = "INVALID_RESPONSE"
                    raise ProviderProtocolError(
                        "response identity or schema does not match"
                    )
                event["outcome"] = response["classification"]
                break
            if response is None:
                records.append({
                    "request_id": key, "status": "DEFERRED",
                    "route": decision.route})
            else:
                records.append({
                    "request_id": key, "status": "CLASSIFIED",
                    "route": decision.route,
                    "provider_classification":
                        response["classification"]})
    except Exception as error:
        error.receipt = _receipt(records, attempts)
        error.attempts = error.receipt["attempts"]
        error.records = error.receipt["records"]
        error.calls = error.receipt["calls"]
        raise
    return _receipt(records, attempts)
