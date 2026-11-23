# Proposal B3-P02

The retry response is aligned with the currently active policy while retaining the stored operation identifier. The persisted historical row is left intact, giving the caller an up-to-date classification without another write. This keeps the query side responsive to a policy change. Review the meaning of that response against the promise attached to a reused request identity.
