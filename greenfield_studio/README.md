# ESA Greenfield Studio — from an empty repository to first reliable slice

Self-contained **offline Python 3.10+ / SQLite standard library** teaching project. It complements the 14-chapter book with an independent first-system journey; it leaves the Treasury companion exercises unchanged and is intended to live alongside them in the official companion repository.

**Before generating code:** read `docs/contract.md`, then derive the independent expectations in `tests/test_booking.py`. There is no existing application, no legacy behavior and no existing regression suite to inherit.

Start from a blank learner copy:

```bash
python3 tools/scaffold.py /tmp/my_first_reservations
cd /tmp/my_first_reservations
python3 -m unittest discover -s tests -v
```

The tests initially fail with `NotImplementedError`: that is the intended initial state. Implement `booking.py` without changing the approved contract or tests. Review failures and the resulting candidate before consulting the solution.

Validate the separately provided reference in isolation:

```bash
python3 tools/check_reference.py
```

No third-party packages, model endpoint, payment credential or real-world booking account are needed. The test suite checks selected functional and concurrency behavior on a **single local database file**. It does **not** validate public deployment, real authentication/authorization, reliability under production load, security hardening, backups or compliance. A live rollout would require the missing boundaries plus independent review and acceptance.

Further use: classify any proposed waiting-list or cancellation feature as a new product decision, then write a compatible second-version contract before changing code. A completed first system becomes a brownfield system for the next change.
