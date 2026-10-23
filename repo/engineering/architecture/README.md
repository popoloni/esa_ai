# Chapter 5 — Explore architecture and prototype alternatives

Two deliberately small, executable Python designs implement the Chapter 4
explanation-only behavioral contract without changing the routing authority.

Editable, learner-owned material:
- `src/treasury/architecture/direct.py` and `ports.py` — prototype code
- `engineering/architecture/architecture_decision.json` — intentionally wrong starter
- `engineering/architecture/ADR-005.md` — intentionally wrong starter

The protected reference solutions and the independent case oracle live in
`../reader_side/` and must not be modified by the delegated implementer.
Use `python reader_side/tools/architecture_gate.py` from `companion/`.
Both candidates are design *proposals*; neither authorizes a release.
