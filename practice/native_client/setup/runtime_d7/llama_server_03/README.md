# Final guided SDD server lifecycle

This is the closed lifecycle of the last authorized native SDD continuation on
22 October 2026. It used the same pinned llama.cpp executable and Qwen3-4B
weights as the previous server, with a fresh process, 24,576-token context,
q4_0 key/value caches, one slot and eight CPU threads. PRE_START.json records
fresh full-byte identity checks; START.json records the actual command and
launcher identity. No earlier KV state was carried across the restart.

The native client completed one tool call that read the full input packet.
Its next request was still processing when the fixed 1,800-second client limit
ended the capture with TIMEOUT/124. No specification, checklist, clarification
or other changed file was produced. The client evidence and its separate
acceptance review remain in the native SDD observation; this server packet
alone does not establish completion of a framework phase.

HEALTH_AND_RESOURCES.json, two RESOURCE_SAMPLE files and
PRE_STOP_RESOURCES.json retain the actual health, context, memory and metrics.
The terminal sample showed one processing request and no deferred request.
The sampled cgroup OOM and OOM-kill counters remained zero. The metrics record
prefix reuse, but the incomplete second request has no completed native usage
record. These observations are not a minimum-hardware test or isolated
performance comparison. RESOURCE_SAMPLE_02.json also discloses an initial
collection failure caused by using the wrong log filename; its unsaved
measurements are not treated as evidence.

The server log recorded the client's cancellation. At 07:53:19 UTC the operator
sent SIGTERM to the exact owned launcher. The stated cleanup grace was at most
120 seconds; the actual force-stop intervention occurred 147.826 seconds after
that request. The owned child had still not exited and was then sent SIGKILL.
OPERATOR_STOP_REQUEST.json and OPERATOR_FORCE_STOP_REQUEST.json preserve both
actions and the exact process identities. FINISH.json records child exit -9;
the launcher returned 137. This is a forced operator cleanup, not a clean exit
or an observed out-of-memory termination. POST_STOP.json confirms both PIDs
were absent. No subsequent model request or restart was performed.

Service wall and CPU totals include startup, inspection, client processing,
waiting and cleanup. They are not an individual task's active effort or a
complete monetary cost. The original launcher pinned in START.json did not
bound its wait after SIGTERM; any later helper correction is separate from
this retained outcome.

To prepare the observed context/cache settings in a new evidence directory:

```sh
python run_local_model.py --runtime-root /path/to/runtime \
  --evidence /path/to/new-server-evidence \
  --ctx-size 24576 --cache-type-k q4_0 --cache-type-v q4_0
```

The [native guide](../../../README.md) and
[SDD route](../../../../sdd/NATIVE_ROUTE.md) explain the client configuration
and complete input requirements. Keep an explicit outer task bound and retain
the actual shutdown outcome. Do not infer safety or isolation from the
loopback binding or enabled client permissions.

All original evidence files are copied byte-for-byte from
`revision_d7/evidence/native_reconstruction/llama_server_03/`. This separate
explanatory file and the manifest add navigation without changing those
records. Model files, executables and the client-state database are excluded.
