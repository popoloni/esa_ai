# Bounded shutdown guard and controlled probe

The actual final SDD server used the old launcher preserved here as
OBSERVED_LAUNCHER_BEFORE_FIX.py. That launcher sent SIGTERM and then waited
without a deadline. The [closed server03 packet](../llama_server_03/README.md)
retains the real result: native client TIMEOUT/124, a still-processing backend,
SIGTERM, and later operator SIGKILL. The actual escalation delay was 147.826
seconds against a planned 120-second manual target. Those historical records
are unchanged by this correction.

The corrected launcher snapshot adds --shutdown-grace-seconds with a default
of 30 seconds. The first stop request starts a monotonic deadline; repeated stop
signals do not restart it. After the grace, the launcher checks and kills only
its own still-running direct child, recording the actual signal and exit. The
poll interval and scheduler can add delay; this is not a hard real-time promise.
The current executable recipe remains the parent run_local_model.py file;
CORRECTED_LAUNCHER_SNAPSHOT.py preserves the exact bytes reviewed here.

These verification runs used explicitly inert Python subprocesses under fresh
fake runtime directories. No actual llama.cpp executable, model weights,
coding-client inference or network endpoint was used. The fixtures only print
readiness, wait, and either cooperate with SIGTERM or ignore it. File names
matching the server's expected installation path do not turn these fixtures
into a native model run.

controlled_probe/ preserves the first controller attempt, which failed before
its intended test signals because sandbox Popen PID values and the mounted
/proc view differed. The retained environment note records a later host-view
scan that found no matching leftover inert children. This was a controller
setup failure, not a demonstrated launcher defect. The original first-attempt
manifest remains its dated inventory; it is not silently refreshed for the
later retry or annotations.

controlled_probe/retry_02/ is the separate successful run in a consistent,
authorized process view. It retains source fixtures/controllers, runtime-copy
identities, actual arguments, stdout/stderr, lifecycle receipts and outcomes.
The independent REVIEW.json records 17 passing checks: the cooperative child
exited 0 in about 0.064 seconds without force; the ignoring child received three
launcher stop signals and one exact-child SIGKILL 1.373 seconds after the first
request, with a 1.2-second configured grace. Repeated signals did not reset that
deadline. The forced child exited -9 and its launcher returned 137. Both children
were reaped. A fast cooperative exit records its stop event in FINISH.json;
SHUTDOWN.json is retained when the polling loop observed the pending shutdown.

IDENTITIES.json connects the old source, corrected source and independent
review. PORTABLE_MANIFEST.json covers every file in this packet except itself.
Copied records remain byte-for-byte identical to their author-side originals;
this README and identity note are separate annotations. Historical absolute
paths describe the observation environment. No runtime tree, executable binary
or model weight is included. These tests establish the controlled shutdown
behavior; they do not replace the historical SDD result or supply human review.
