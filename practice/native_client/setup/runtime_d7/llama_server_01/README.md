# Original shared native server lifecycle

This is the closed lifecycle of the pinned loopback server used by the native
Chapter 1 episodes, the native MCP observation and the first native SDD attempt.
Its actual context was 16,384 tokens with q8_0 key and value caches. The retained
START and FINISH records cover the whole shared service interval, including
idle time; their CPU and wall totals are not costs attributable to one chapter
or one client request. Client prompts, tool calls, diffs and acceptance results
are retained in the separate observation packets.

The server stopped cleanly with exit code 0 after the authorized context
transition. The first default-sandbox signal call failed with ProcessLookupError;
its request and failure are retained separately. An authorized escalated call
rechecked the exact process identities and successfully stopped the owned
launcher, which recorded its signal and waited for its child. A clean server
exit does not establish successful completion of a client task.

All original evidence files are copied byte-for-byte from
`revision_d7/evidence/native_reconstruction/llama_server_01/`. The packet manifest
binds their identities and this separate explanatory file. No model, executable
or client-state database is included.
