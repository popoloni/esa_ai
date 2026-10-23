# OpenSpec change adapter — documentation snapshot, 19 October 2026

Official: https://github.com/Fission-AI/OpenSpec/blob/main/docs/concepts.md , docs/commands.md and docs/examples.md

With OpenSpec installed and initialized, use the documented agent command (integration-dependent):

```text
/opsx:propose explanation-only-alpha
```

Review proposal.md, specs/<capability>/spec.md, design.md, tasks.md. Changes use `## ADDED Requirements`, `### Requirement:`, `#### Scenario:` and GIVEN/WHEN/THEN bullets. Do not run `/opsx:apply` before requirements owner review. For a complete change with no live implementation, `/opsx:archive` is not an acceptance shortcut.

The generated example in reader-side exports is author-created and has NOT been validated by OpenSpec CLI. No vendor execution claimed.
