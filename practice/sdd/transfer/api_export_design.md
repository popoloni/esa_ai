# Design transfer: add CSV export to an existing orders API

This is a bounded reasoning exercise, not another production implementation or
a measured architecture comparison. Use a disposable reader repository or the
scenario below; do not expose private production data.

The API already returns the authorized user's filtered order rows. The proposed
change adds CSV output for exactly those rows. It must preserve authorization,
filters and the existing JSON response. Empty results and fields containing a
comma, a quote or a line break need explicit examples. Spreadsheet formula
interpretation is an additional consumer/security question to resolve with the
owner before choosing escaping or formatting policy.

## Two small alternatives

1. A direct formatter called after the existing authorization/filtering step.
2. An export presenter that accepts an already filtered row provider through a
   small interface.

Keep the same authorized-row examples for both. Write a short ADR proposing one
alternative, a negative consequence and a condition that would reopen it. Use
the existing test framework if you implement a tiny prototype. Do not infer
throughput or memory superiority from the number of files or from successful
formatting examples.

## Reasoning criteria

- Does the comparison preserve the same user-visible contract and permission
  boundary, or does one design quietly export a different row set?
- Which seam changes independently: selection/authorization, serialization or
  transport? Is that independence needed now or merely possible?
- Which observations distinguish correctness from convenience of substitution?
- What workload and environment would be needed before a performance conclusion?
- Can the proposal be reversed without changing the source of authorized rows?

## Worked feedback

For one exporter and a stable row-selection function, a direct formatter is a
reasonable candidate because it adds fewer collaborating components. That is a
conditional design judgment, not a universal result. A second row source or
repeated difficulty isolating serialization tests could justify the interface.
Both designs can still share the same authorization bug, so agreement between
them is not independent evidence of access correctness. Test expected row
membership separately from CSV shape. Keep unresolved spreadsheet-consumer
behavior explicit; a formatter that produces valid CSV has not automatically
settled how a spreadsheet will interpret its cells.

This mirrors Chapter 5's distinction: eight shared Treasury cases constrain
behavior; the routing seam informs a design choice. Neither settles production
load, user comprehension or a broad security review.
