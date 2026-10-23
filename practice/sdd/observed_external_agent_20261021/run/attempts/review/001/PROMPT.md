# Independent reviewer prompt and authority

## Actual task delegation

Actual independent fresh-context review worker. Read /workspace/scratch/efa0a59e0545/output/Engineering_Software_with_Agentic_AI_Competitive_Revision_20261021/companion/practice/sdd/observed_external_agent_20261021/run/attempts/review/001/DISPATCH.json, request, authorized supplied input_root and only generated artifacts reached through the request's dependency response. Verify hashes before reading generated artifacts. You may inspect practice/orchestration/external_worker.py or README only for submission schema. Do not read book, parent editorial notes or external reference answers. Follow request's independent semantic review, concrete case/requirement checks. Retain first review.json, RAW_RESPONSE.md, prompt, tool evidence and provenance in attempt output. Write submission.json atomically LAST as required by bridge. Need finish before 16:08:33 UTC (300-second controller deadline). Label actual ChatGPT collaboration, no native CLI or human acceptance. Do not alter generation outputs or spawn other agents. Report concrete findings and paths.

## Exact request JSON

```json
{
  "attempt": 1,
  "authority": "Read supplied inputs; write only this attempt's outputs. No acceptance or release authority.",
  "dependencies": {
    "generate": {
      "response_path": "/workspace/scratch/efa0a59e0545/output/Engineering_Software_with_Agentic_AI_Competitive_Revision_20261021/companion/practice/sdd/observed_external_agent_20261021/run/attempts/generate/001/result.json",
      "sha256": "3f51ec070fe727286f2c9565a15de9517af6e001defdbe2a7e515ea518d32a3a"
    }
  },
  "input_root": "/workspace/scratch/efa0a59e0545/output/Engineering_Software_with_Agentic_AI_Competitive_Revision_20261021/companion/practice/sdd/observed_external_agent_20261021/inputs",
  "schema": "treasury-worker-request/v1",
  "task": {
    "depends_on": [
      "generate"
    ],
    "id": "review",
    "idempotent": false,
    "kind": "worker",
    "max_attempts": 1,
    "parameters": {
      "instruction": "Independently review the generated specification, plan and tasks against\nthe supplied fixed requirements, case oracle, discovery evidence and policy\nsources. Read the generation result through the dependency response path and\nverify each referenced artifact hash before using it. Inspect exact equality,\ninvalid amounts, policy provenance, all five requirements and eight cases,\npayment authority, unknown benefit, dependencies and the pending human decision.\nDo not copy the author's review or inspect external reference answers. State\neach concrete defect, file location, evidence and proposed correction; a clean\nreview is permitted when justified. Write review.json and RAW_RESPONSE.md in\nthis attempt, preserve first outputs, and submit their hashes. A review is an\nagent assessment, not human acceptance. Do not modify the generation output.\n",
      "required_artifacts": [
        "review.json"
      ]
    },
    "response": "result.json",
    "timeout_seconds": 300
  }
}
```

## Supplied generation task context

# Generate a candidate explanation-only Treasury specification

Read the supplied inputs/specification.json, discovery_handoff.json,
case_oracle.json, assessment.json, policy sources and source/treasury/routing.py.
Use the retained Spec Kit 1.2.2 specification, plan and tasks templates and
relevant skill instructions. Apply them through the actual dispatch interface;
do not claim that native Codex slash commands ran unless that was observed.

Produce a coherent candidate spec.md, plan.md and tasks.md in the current
orchestrator attempt's artifacts/ directory. Preserve all five requirement IDs,
all eight scenario IDs and their values, the source and decision owners,
BR-001/v1 and the exact EUR 5000 boundary. Explain why the proposed solution
shows a recommendation without authorizing payment. Treat benefit as an
unvalidated hypothesis. Keep human requirements approval pending and dependent
implementation/release work blocked. Do not manufacture a passed human review.

Use only this input bundle and the current request. Do not inspect neighboring
book chapters, reference answers, authored before/after specimens, prior review
findings or other workspaces. This is an instruction boundary in a shared
filesystem, not a technical access barrier; report any actual prior exposure.
Do not change any input, request, plan, controller, policy or source file. Do not
install clients, call external services, use credentials, implement code, or
deploy. Write only within the current attempt. No planted flaw is requested.

Where an unanswered question prevents a decision, state the question and keep
that decision pending. Retain a complete final response in RAW_RESPONSE.md,
including sources read, assumptions, changes, unresolved questions and what
was actually checked. Submit the request-bound artifact hashes using the
external_worker.py submission contract. Report the actual interface and any
exposed model identity; leave unavailable version, usage or cost fields null.

The coordinator must retain the first output before requesting a correction.
An independent fresh-context reviewer will inspect it. A model review cannot
approve business requirements, payment, or production release.

