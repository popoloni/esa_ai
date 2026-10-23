# Select a workflow from the structure of the work

This original selector is a decision aid, not a benchmark or maturity ladder.
Start with the smallest arrangement that can produce the needed evidence.

| Question about the task | Initial pattern | Treasury example | Stop/change the pattern when |
|---|---|---|---|
| Is it one small, settled edit? | One attended writer with an independent check | CP01 invalid-input repair | Scope or intended behavior becomes uncertain |
| Is the missing item a known source or symbol? | Direct search/CLI lookup; retrieve the relevant source | Find BR-001/v1 or the first differing output field | The result has unresolved provenance or is incomplete |
| Does an external owner expose the needed capability? | Bounded tool integration, such as the read-only MCP lookup | Fetch the fixed policy record through an inspected local server | Credentials, exposure or returned authority differ from the task contract |
| Does the same procedure recur? | A narrow skill with explicit inputs and outputs | CP06 source audit | Source, client behavior or procedure becomes stale |
| Are there independent read-only questions? | Separate investigators plus one synthesizer | T07-01 specification and T07-02 architecture investigations | Shared uncertainty defeats independence; their conclusions conflict |
| Do several writes share a dependency or decision? | Sequential plan and one writer until boundaries are resolved | T07-04 remains blocked on architecture review | An actual owner decision revises the authorized plan |

Only after evidence justifies independent writable tasks should you add separate
worktrees and an explicit merge owner. A worktree separates working files; it is
not an OS sandbox or independent acceptance authority. An unattended retry loop
also needs bounded actions, observable failure handling and a real stop condition;
it is not the next obligatory step after using one agent.

## Fill the selection record

1. **Question/output:** What can the next worker actually deliver?
2. **Dependencies:** Which inputs or decisions are shared with other tasks?
3. **Write set:** Empty, one file, or a justified set of independent modules?
4. **Pattern:** Which row above fits, and why is the simpler row insufficient?
5. **Merge/synthesis owner:** Who resolves conflicting results?
6. **Budget and stop:** Which observation ends or escalates the task?

For the current CP07 state, choose read-only investigations and retain a blocked
writer. Do not mark T07-03 accepted to make a scheduling demonstration interesting.
Logical task rounds in the lab do not measure real-agent throughput or costs.

## A bounded prompt for each investigator

Specification investigator: “Read INT-001 and SPEC-004/v1. List the behavior
constraints and unresolved operator wording. Return source IDs and open questions.
No writes, no architecture decision, no payment or release approval.”

Architecture investigator: “Read the two prototypes and proposed ADR-005. Explain
what the eight selected cases establish, what shares a dependency, and which
decision still needs the technical owner. Return sources and uncertainties. No
writes and no fabricated execution.”

These are prompts for a future explicitly permitted delegation, not transcripts.
Record an actual host's child-task inputs, writable permissions and outputs if you
run them. Two model roles reading the same assumptions do not become independent
reviewers by acquiring different names.
