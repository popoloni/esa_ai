# Diagnose the local policy tool and the selected host

Start with `../practice/mcp_cli/README.md`. The table separates symptoms visible
in this example from conclusions that require a separate host or permissions
observation. Keep raw stderr apart from the stdio protocol stream.

| Symptom | Inspect next | Interpretation and next decision |
| --- | --- | --- |
| The CLI returns `UNKNOWN_POLICY` and exit 2 for a path-like identifier | The requested literal ID and `policy_lookup.py` | This is the expected domain refusal. It does not test general process filesystem access. |
| A schema-invalid list argument is rejected | The discovered schema and retained tool-call response | Compare the actual argument with the string parameter. Record host rendering separately from SDK behavior. |
| No response to the actual opening exchange, or a timeout | The exact executable and environment, process exit, stderr and both wire streams | Preserve the failed attempt. Check whether the process started and which side last produced a message before changing settings. |
| A tool is not listed | The actual negotiated session, registered server tool and host discovery output | Do not assume the model saw a tool because its Python definition exists. |
| CLI and MCP results appear different | Parse domain fields separately from each protocol/output envelope | Compare threshold, boundary, authority and source identity. Envelope size alone is not semantic disagreement. |
| The host displays a tool result but the answer omits required fields | Retained tool result and final response contract | Tool success and answer completeness are separate checks, as in the harness exercise. |
| A run works only after a permission change | Both settings, source identities, failed logs and successful logs | Record the changed boundary and source. A multi-change retry does not identify a single causal defect. |
| A receipt says a file or source is unchanged | Which exact bytes were hashed and at which stages | Identity evidence covers those inputs; it does not certify policy correctness, credential safety or network isolation. |

The retained first MCP attempt timed out and the later local attempt succeeded
after both environment and source changes. That history is useful evidence, but
does not prove a particular SDK defect. Reuse it as a diagnosis example, not as
a reason to broaden permissions automatically.

For the external coding-host trial, record the actual host/client version,
the observed protocol-era opening exchange, tool listing, valid call, domain refusal and malformed argument
in `records/MCP_HOST_AND_BOUNDARIES.json`. Audit filesystem, environment and
network exposure separately with disposable non-secret fixtures. The status of
an unobserved boundary remains `NOT_TESTED`; stdio alone is not a containment
mechanism.

## Inspect retained evidence before retrying

Run `python3 practice/mcp_cli/diagnose_trace.py <observed-directory>` from the
companion root. The standard-library diagnostic checks the identities of the
two wire streams and classifies the retained requests/results. It accepts the
failed attempt as evidence worth diagnosing; a diagnosis PASS does not turn
that attempt into a successful exchange. Use `inspect_trace.py` for the separate
frozen modern request-sequence check.

The diagnostic distinguishes discovery, schema-invalid arguments and a
well-formed domain refusal. An unanswered opening request leaves startup versus
transport unresolved. The process exit/stderr and actual host log are needed
to narrow that cause. A PATH-only preflight cannot supply them. Follow
[NATIVE_HOST_COLLECTION.md](NATIVE_HOST_COLLECTION.md) for a new named-host
packet, including actual model tool selection and a carefully scoped canary
observation.
