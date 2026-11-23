# Proposal B2-P01

The batch loop tries to finish an item already in progress after a transient provider interruption. It preserves the request identifier and records every invocation so the caller can see the effort spent before the batch returns. The completion path is designed to avoid abandoning useful work at the edge of an allowance. Review that path against both the item-level and batch-level budgets.
