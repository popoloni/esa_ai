# Proposal B1-P03

Users see monetary amounts with two decimal places. This input proposal makes the displayed amount the basis for routing by applying half-up rounding before the threshold comparison. The bounded validation repair remains a separate change, while the proposed normalization would give forms and routing one shared amount representation. Additional fractional digits would be resolved once at the input boundary.
