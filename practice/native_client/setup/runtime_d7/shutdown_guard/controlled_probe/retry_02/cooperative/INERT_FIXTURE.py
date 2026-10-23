#!/usr/bin/env python3
"""Explicitly inert fixture: print identity, wait, and exit on SIGTERM."""
import json, os, signal, sys, time
def stop(signum, frame):
    print(json.dumps({'fixture': 'cooperative', 'received_signal': signum}), flush=True)
    sys.exit(0)
signal.signal(signal.SIGTERM, stop)
print(json.dumps({'ready': True, 'fixture': 'cooperative', 'pid': os.getpid(), 'argv': sys.argv, 'model_loaded': False, 'network_opened': False}), flush=True)
while True:
    time.sleep(0.05)
