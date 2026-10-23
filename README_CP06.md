> Integration update (20 October 2026): this chapter now runs inside the shared Chapters 1–10 companion. Test totals below describe its original checkpoint; `run_checks.py` runs the current combined suite. See `README.md` for current commands, chapter scopes and candidate-readiness reporting.

# Chapter 6 — Maintain Context, Knowledge and Agent Skills

The CP06 cumulative exercise extends CP05. Original chapter folders are unchanged.

1. Run `python reader_side/tools/run_checks.py` from the `companion/` directory.
2. Inspect the selected protected source references in `reader_side/knowledge/source_catalogue.json`.
3. Inspect the intentionally unsafe `repo/engineering/knowledge/context_packet.json` and
   `.agents/skills/context-audit/SKILL.md` candidates.
4. Run `python reader_side/tools/knowledge_gate.py` (expected FAIL).
5. Repair **only** the two candidate files and rerun the gate. Or use the two
   `reader_side/reference_solution/` examples to check the expected PASS.
6. Re-run the cumulative suite. It must pass before and after repairing the starter.
7. Review hypothetical dependency invalidation: ADR change affects `architecture_choice`;
   policy change affects `routing_threshold` and `payment_authority`; updating the
   excluded old wiki changes no accepted claim in this deliberately narrow graph.

The source catalogue hashes bytes and the gate compares selected synthetic facts. It cannot
certify semantic truth, architecture acceptance, correct tool execution, prompt-injection
resistance of a model, human permission or business value. Tool invocation is **offline only**.
