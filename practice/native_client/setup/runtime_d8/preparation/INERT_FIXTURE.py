#!/usr/bin/env python3
import signal,time
signal.signal(signal.SIGTERM, signal.SIG_IGN)
print("INERT_FIXTURE_READY_NO_MODEL_OR_NETWORK", flush=True)
while True: time.sleep(0.05)
