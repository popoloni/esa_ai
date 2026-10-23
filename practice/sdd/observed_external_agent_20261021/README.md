# Actual generated SDD documents and independent agent review

This episode uses a newly installed Spec Kit 1.2.2 scaffold and its real helper
commands. Two actual ChatGPT collaboration agents supplied generation and review
through the controller's external-worker bridge. It is not a run of a native
Codex, Claude Code, Copilot, Gemini or OpenCode CLI, and does not establish a
paired framework comparison.

Read `OBSERVATION_SUMMARY.json`, then `run/state.json`. Generation completes
before review; the controller stops at `WAITING_HUMAN` with exit code 3 and no
human-task attempt. `inputs/` is the snapshotted framework and source packet.
Each attempt retains its dispatch request, prompt, tool journal, first output,
input/output identities, submission and result. These are historical records;
their absolute scratch paths describe the original execution location. Do not
rewrite those receipts or resume the archived run after relocation. To create
another observation, use a new output directory and the external-worker contract
in `practice/orchestration/README.md`.

The reviewer checked all five requirements and eight cases without the author's
reference answers. It found one minor inconsistency: T019 omitted T021 from its
inline dependencies, although the human alpha prerequisite remained explicit in
the task prose and overall graph. `reviewed_revision_02/` contains the separately
corrected documents and change manifest. Original generation and review outputs
remain unchanged; the correction was made by the primary authoring agent after
review and was not retroactively attributed to the first generator.

All tasks remain unchecked. Application behavior, operator understanding,
requirements acceptance and release authority were not established by this run.
Exact provider model release, tokens and billing were not exposed.
