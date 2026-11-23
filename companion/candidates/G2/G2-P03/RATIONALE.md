# Proposal G2-P03

Migration is a compatibility operation with a clear rollback boundary. The conversion carries the approved representations into the current schema, preserving identifiers and public values, and leaves the source rows available for explanation. Ambiguous identities and invalid old commitments stop the conversion. Reinitialization and replay of an imported request are useful checks on whether that preservation is complete.
