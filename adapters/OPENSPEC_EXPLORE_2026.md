# Optional adapter — OpenSpec explore (checked 19 October 2026)

This is a **documentation-grounded** usage scenario, not a live tested OpenSpec installation.

Primary sources:
- https://github.com/Fission-AI/OpenSpec/blob/main/docs/explore.md
- https://github.com/Fission-AI/OpenSpec/blob/main/docs/commands.md

In a supported OpenSpec-enabled agent chat, begin with:

```text
/opsx:explore
Our Treasury routing sponsor requests automatic payment approval below EUR 5,000. Compare the request with BR-001/v1, the source packet and the measured triage baseline. Separate policy from testimony, expose contradictions, and offer bounded options. Do not edit the routing code.
```

According to current documentation, explore ordinarily reads and reasons about code without editing code. It can **write planning artefacts when the user explicitly asks for a capture**, and may transition to `/opsx:propose` when ready. It is not by itself a user-research validation or a policy approver. Transfer findings into CP03's portable `assessment.json` and run the reader-owned deterministic gate.
