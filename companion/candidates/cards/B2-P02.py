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
