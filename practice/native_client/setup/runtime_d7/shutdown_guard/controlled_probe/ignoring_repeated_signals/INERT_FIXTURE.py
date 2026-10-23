#!/usr/bin/env python3
"""Explicitly inert fixture: ignore SIGTERM and wait for exact-child cleanup."""
import json, os, signal, sys, time
signal.signal(signal.SIGTERM, signal.SIG_IGN)
print(json.dumps({'ready': True, 'fixture': 'ignoring', 'pid': os.getpid(), 'argv': sys.argv, 'model_loaded': False, 'network_opened': False}), flush=True)
while True:
    time.sleep(0.05)
