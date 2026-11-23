# Proposal G1-P01

The persistence boundary is the public record, so I kept storage layout behind that interface. A row identifier locates a JSON representation of the five request fields; each read reconstructs a new mapping with the identifier added. This makes an alternative physical layout possible while keeping callers unchanged. Please judge the returned fields and the process-boundary observation together.
