# ESA d16 — Greenfield Studio: companion/workbook alignment

**Edition:** *Engineering Software with Agentic AI*, d16 (24 October 2026).
**Companion:** https://github.com/popoloni/esa_ai
**Workbook:** *ESA Laboratory Workbook d16*, 253 pages.
**Placement:** **Greenfield Studio** appears after the fourteen numbered Treasury laboratories.
It is an **independent, unnumbered studio**, not Laboratory 15 and not a prerequisite for any Treasury lab.

## Choose one of three valid starting routes

| Reader goal | Repository route | Workbook route |
|---|---|---|
| Build a first system (greenfield) | [`greenfield_studio/`](../greenfield_studio/README.md) | Unnumbered *Greenfield Studio*, after Laboratory 14 |
| Safely evolve an existing system (brownfield) | `reader_start.py doctor`, `show 1`, `new 1` | Laboratories 1–14, cumulative Treasury exercise |
| Try a tiny independent task | [`practice/`](../practice/) (CSV preview) | Optional warm-up, not a replacement for the numbered labs |

All three routes reinforce the same software engineering discipline: establish the
owner-approved behavior, constrain implementation scope, test from independent
expectations, retain evidence, and distinguish technical checks from release acceptance.

## Chapters and a coherent greenfield path

The main d16 book contains a greenfield thread across **all 14 chapters**.
The studio provides a single exercise that brings those ideas together.

| Chapter | Reader decision or evidence in the studio |
|---|---|
| 1 | Fix the model–harness–human decision boundary |
| 2 | Set up a local tool environment and inspect permissions |
| 3 | Separate owner assumptions, scope and accepted capability |
| 4 | Derive independent scenarios from RES-001/v1 |
| 5 | Evaluate and document first-slice storage architecture |
| 6 | Preserve a qualified contract and ADR as context |
| 7 | Sequence owner, implementer and independent verifier |
| 8 | Implement a vertical slice with constrained edits |
| 9 | Test half-open intervals, idempotency and concurrency |
| 10 | Tie build evidence to the candidate before release review |
| 11 | Turn a requested cancellation feature into v2 compatibility work |
| 12 | Identify missing telemetry, recovery and operational evidence |
| 13 | Record review ownership, handoffs and transferred knowledge |
| 14 | Define outcome measures, costs and keep/change/stop criteria |

## How to run, from the repository root

Prerequisites: Python **3.10+** with SQLite from the standard library. No
external model account, network access, external database server or third-party Python modules.

```shell
python3 greenfield_studio/tools/scaffold.py ../my_first_reservations
cd ../my_first_reservations
python3 -m unittest discover -s tests -v
```

The **starter is deliberately incomplete**. Its tests should fail until the student
implements `init_db` and `reserve` against the accepted contract. Do not
"fix" an expected initial red result by weakening or editing tests.

From the **repository root** (or another working directory using absolute paths),
test the **separate reference implementation**:

```shell
python3 greenfield_studio/tools/check_reference.py
```

Expected: **10 successful reference tests**. This proves only the local
synthetic implementation and its bounded test conditions, **not** a production
reservation service or an approved real-world booking deployment.

## Sources of authority and responsibilities

- **Product authority:** `greenfield_studio/docs/contract.md` (RES-001/v1)
  represents the fictional coordinator's accepted teaching decisions.
- **Architecture:** `greenfield_studio/docs/decisions/0001-storage.md`
  explains the bounded SQLite teaching choice and falsifying evidence.
- **Implementation:** `greenfield_studio/starter/booking.py` is deliberately
  incomplete; `reference/booking.py` is an isolated educational solution.
- **Independent checks:** `greenfield_studio/tests/test_booking.py`
  contains the scenarios; learners should preserve it.
- **Constraints:** trusted member identity is supplied by the caller, not
  authenticated or authorized by this package. No real API, payments, notifications,
  monitoring, backups, migrations, public deployment or performance SLA.

## Maintaining edition alignment

When changing the workbook, contract, tests or reference:

1. Update this crosswalk and mark the affected edition; **do not silently
   change the existing 14 Treasury laboratories**.
2. Keep RES-001/v1 invariant definitions and scenario semantics synchronized.
3. Run the studio reference and repo alignment checks.
4. Preserve a dated change note and label whether the change is to
   teaching material, a new accepted v2 behavior or a production concern.
5. If a release artifact changes, issue a new version; do not rewrite an
   existing d16 archive in place.

Do not infer that a passing automated test is approval to publish an actual
booking service. The final operational gate and accountable human decision
remain outside the synthetic lesson.
