def present(decision):
    result = {key: decision[key] for key in
              ("route", "reason_code", "policy_version")}
    result["payment_authorized"] = False
    return result
