# G3 integration increment: read-only reservation report and CLI

Authored teaching contract INTEGRATION-G3/v1, 16 November 2026. Authorization:
author's ESA implementation instruction, exercised by AI recording operator.
Continue the actual accepted G3 implementation; booking.py stays protected.
No new booking rule, payment, refund, deletion, network or deployment is authorized.

Contribution A owns reservation_report.py and CONTRIBUTION_A.md.
build_report(path, reservation_id) calls the public booking get_reservation and
reservation_status operations. Existing record: return exactly
{"found": true, "reservation": six-field historical record, "current": {"state": ..., "version": ...}}.
Absent identifier in initialized storage: return exactly
{"found": false, "reservation": null, "current": null}.
Never initialize or mutate storage. Unexpected errors must propagate to the caller.
The historical record and current state have different meanings. Do not change the
original reservation confirmation or revive a cancellation. These separate public
reads are not claimed to be one concurrent snapshot.

Contribution B owns reservation_cli.py and CONTRIBUTION_B.md.
main(argv=None) supports: inspect --database PATH --reservation-id POSITIVE_INTEGER.
Call reservation_report.build_report; print one JSON object on stdout and no extra
status text. Exit0 for found, exit3 for absent. Invalid/missing arguments exit2.
A storage error produces a concise error on stderr and exit2; stdout stays empty.
Importing the CLI must not run it. A __main__ entry exits with main's status.
Do not read SQL tables, initialize storage, implement report semantics or embed data.

Both contributions depend on this exact interface and the retained booking.py.
Each workspace contains the other contribution as an unimplemented stub.
Component tests use the real booking API for A and an explicit fake report provider
for B. Passing those tests alone cannot establish combined import or behavior.
The operator integrates both contributions and checks the real CLI in an extracted
package on a confirmed record, after cancellation, an absent ID and missing storage.
