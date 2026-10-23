# Optional adapter — GitHub Spec Kit Idea Assessment (checked 19 October 2026)

This is a **documentation-grounded** reader procedure, not a logged execution of Spec Kit or a live Copilot agent. Read the primary source before use:
- https://github.github.com/spec-kit/guides/assessment.html
- https://github.com/github/spec-kit/blob/main/docs/reference/agentic-assessment.md

The extension is **opt-in**. From an initialized Spec Kit project, documentation describes:

```bash
specify extension add assess
```

The next examples are **agent-chat skills, not shell commands**. In the GitHub Copilot default skills integration the documented spelling is:

```text
/speckit-assess-intake "Improve Treasury handoff delays without changing payment authority" slug=treasury-handoff
/speckit-assess-research slug=treasury-handoff
/speckit-assess-define slug=treasury-handoff
/speckit-assess-shape slug=treasury-handoff
/speckit-assess-decide slug=treasury-handoff
```

Other integrations may expose the `/speckit.assess.*` spelling. Inspect your installed version. Outcomes are under `.specify/assessments/treasury-handoff/`. Do not accept generated citations without source checks. The local CP03 deterministic discovery gate is **not** a test of the extension and is the publication baseline.

For this exercise the five stages should read the **synthetic source packet** only and produce a conditional plan, not modify production code. The exercise is valid with no vendor-specific tools by writing the candidate `assessment.json` manually.
