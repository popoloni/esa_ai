def present(decision):
    return {"route": decision["route"], "reason_code": decision["reason_code"],
            "policy_version": decision["policy_version"],
            "payment_authorized": decision["route"] == "STANDARD_QUEUE"}
