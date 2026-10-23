# Controlled shutdown correction review

The first probe failed before its intended test signals because the sandbox's
Popen PID values and mounted /proc view did not share a namespace. Its fixtures,
commands, output, failed report and inventory remain in this directory. The
separate environment note records the later host-view scan: no matching inert
child remained. No launcher change was made to satisfy that controller issue.

The fresh retry_02 run used the authorized host process view. It executed two
explicitly inert Python fixtures under fresh fake runtime paths. Neither loaded
a model, ran the real server, opened a network endpoint or invoked a coding
client. Fixture source, copied executable identities, actual command lines,
stdout/stderr, lifecycle receipts and results are retained.

REVIEW.json records 17 passing checks. The cooperative child exited with code 0
about 0.064 seconds after the signal. The SIGTERM-ignoring child received three
stop requests through its launcher; the single exact-child SIGKILL was sent
1.373 seconds after the first request with a configured 1.2-second grace. Later
signals did not reset that deadline. The launcher returned 137 and retained
child exit -9 and the forced-shutdown event. Both children were reaped.

These are process-control observations under one scheduler. They do not promise
a hard real-time bound or establish a new model result. The earlier server03
forced operator cleanup and native timeout are not rewritten by this check.
The original PROBE_MANIFEST.json inventories the files at the first attempt;
retry_02/PROBE_MANIFEST.json inventories the separate successful retry.
