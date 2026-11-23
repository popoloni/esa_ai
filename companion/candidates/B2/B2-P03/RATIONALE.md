# Proposal B2-P03

Duplicate detection belongs before the first provider effect. This proposal examines the entire submitted batch before entering the existing bounded loop, so a late duplicate cannot invalidate work after calls have already occurred. It addresses identity within this batch only. A later process retry still needs the durable identity contract introduced in the history mission.
