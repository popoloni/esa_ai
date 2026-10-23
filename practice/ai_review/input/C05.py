def present(decision):
    return {"route": decision["route"], "reason_code": decision["reason_code"],
            "policy_version": "BR-001/v1", "payment_authorized": False}
