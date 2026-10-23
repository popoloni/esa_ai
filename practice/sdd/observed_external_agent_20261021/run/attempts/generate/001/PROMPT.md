# Retained Task Prompt

This records the exact coordinator task message and supplied business instruction/request. It is not a transcript of private platform or system instructions.

## Coordinator task message

Actual bounded worker, fresh context. Read /workspace/scratch/efa0a59e0545/output/Engineering_Software_with_Agentic_AI_Competitive_Revision_20261021/companion/practice/sdd/observed_external_agent_20261021/run/attempts/generate/001/DISPATCH.json, its request, inputs/TASK.md, and needed files only within input_root. You may also read practice/orchestration/external_worker.py or its README for exact submission schema. Do not read parent book, reference solutions, prior authored outputs or independent checks elsewhere. Complete within 480 seconds from controller start 15:56:20 UTC. Generate the actual requested spec/plan/tasks from the provided new Spec Kit scaffold and business input. Retain first outputs, exact prompt, exposed model/interface identity (only what you know), uncertainties, tool actions and scope. Label ChatGPT collaboration, not commercial CLI or native framework slash invocation. Write all outputs in attempt_output_root, and atomically write submission.json LAST with request digest, artifact hashes and raw response path per adapter. No human approval claims. Finish with paths and actual status.

## Exact TASK.md

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

## Exact request.json

{
  "attempt": 1,
  "authority": "Read supplied inputs; write only this attempt's outputs. No acceptance or release authority.",
  "dependencies": {},
  "input_root": "/workspace/scratch/efa0a59e0545/output/Engineering_Software_with_Agentic_AI_Competitive_Revision_20261021/companion/practice/sdd/observed_external_agent_20261021/inputs",
  "schema": "treasury-worker-request/v1",
  "task": {
    "depends_on": [],
    "id": "generate",
    "idempotent": false,
    "kind": "worker",
    "max_attempts": 1,
    "parameters": {
      "instruction_file": "TASK.md",
      "required_artifacts": [
        "artifacts/spec.md",
        "artifacts/plan.md",
        "artifacts/tasks.md"
      ]
    },
    "response": "result.json",
    "timeout_seconds": 480
  }
}

## Exact DISPATCH.json

{
  "attempt_output_root": "/workspace/scratch/efa0a59e0545/output/Engineering_Software_with_Agentic_AI_Competitive_Revision_20261021/companion/practice/sdd/observed_external_agent_20261021/run/attempts/generate/001",
  "created_at_utc": "2026-10-21T15:56:20.886247+00:00",
  "input_root": "/workspace/scratch/efa0a59e0545/output/Engineering_Software_with_Agentic_AI_Competitive_Revision_20261021/companion/practice/sdd/observed_external_agent_20261021/inputs",
  "instruction": "Dispatch an actual worker with this request; retain its prompt, output, exposed identity and context limits. Write submission.json atomically after all referenced artifacts exist. Do not relabel a fixture as an agent run.",
  "request_path": "/workspace/scratch/efa0a59e0545/output/Engineering_Software_with_Agentic_AI_Competitive_Revision_20261021/companion/practice/sdd/observed_external_agent_20261021/run/attempts/generate/001/request.json",
  "request_sha256": "e4856cf0c5f84a315efd3d7004aa7b3388dece75b86e834bd5a7ccec64acfef3",
  "schema": "treasury-external-dispatch/v1",
  "submission_path": "/workspace/scratch/efa0a59e0545/output/Engineering_Software_with_Agentic_AI_Competitive_Revision_20261021/companion/practice/sdd/observed_external_agent_20261021/run/attempts/generate/001/submission.json",
  "submission_schema": "treasury-external-worker-submission/v1",
  "task_id": "generate"
}
