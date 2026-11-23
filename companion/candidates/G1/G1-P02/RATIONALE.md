# Proposal G1-P02

The three public operations share a path-keyed record registry. Initialization establishes the database location, and writes make the complete record immediately available to subsequent lookups. That arrangement keeps the first increment small and avoids introducing a larger persistence abstraction. The local scenarios exercise creation and retrieval through the public functions; the same interface remains available for the next increment.
