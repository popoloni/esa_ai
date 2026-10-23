# Corrected-context native server lifecycle

This is the closed lifecycle of the server used for the first corrected native
SDD recovery response on 22 October 2026. Fresh full-byte hashes of the same
pinned server executable and Qwen3-4B model match the installation identities.
The actual context was 24,576 tokens with q4_0 key and value caches; one slot,
eight CPU threads, bounded cache settings and the other server options remained
the same. This change concerns the KV-cache representation, not model weights.

PRE_START.json, START.json and HEALTH_AND_RESOURCES.json retain the actual
transition, command, launcher identity, context and startup health. A further
RESOURCE_SAMPLE_01.json records memory during prompt processing.
PRE_STOP_RESOURCES.json confirms no processing or deferred requests before the
owned launcher was stopped. FINISH.json records a clean server exit 0.

The client returned a short proposed name and a statement that it would proceed,
then ended without a tool call or changed file. A healthy server and client exit
0 do not establish specification, clarification or implementation completion.
Client-side inputs, first output and review belong to the separate native SDD
observation. The lifecycle totals include startup, checks and idle time, so they
are not active model effort or a complete task cost. Memory/OOM samples are
dated observations, not a minimum-hardware or performance claim.

To prepare the same server configuration in a fresh evidence directory, use
the portable launcher from the native-client directory:

```sh
python run_local_model.py --runtime-root /path/to/runtime \
  --evidence /path/to/new-server-evidence \
  --ctx-size 24576 --cache-type-k q4_0 --cache-type-v q4_0
```

The launcher's default remains the original 16,384/q8_0 configuration. The
SDD client must declare a matching context and retain its complete command,
inputs and own bounded task settings.

All original evidence files are copied byte-for-byte from
`revision_d7/evidence/native_reconstruction/llama_server_02/`. The packet manifest
binds their identities and this separate explanatory file. No model, executable
or client-state database is included.
