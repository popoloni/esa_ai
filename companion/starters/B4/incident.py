from operations import cost_summary
def inspect_ledger(path):
    raise NotImplementedError("Inspect existing state without initializing it")
def diagnose(selected_path, expected_path, *, expected_policy, anchor_key):
    raise NotImplementedError("Distinguish source code from selected ledger state")
def recovery_plan(diagnosis):
    raise NotImplementedError("Separate restoration from reconciliation")
