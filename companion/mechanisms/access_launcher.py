#!/usr/bin/env python3
"""Trusted Linux setup process; drops privileges before exec of the worker."""
import ctypes
import os
from pathlib import Path
import sys


def prctl(option, arg2, arg3=0):
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(option, arg2, arg3, 0, 0) != 0:
        value = ctypes.get_errno()
        raise OSError(value, os.strerror(value))


def main():
    worker, root, uid, gid = sys.argv[1:]
    if os.geteuid() != 0 or int(uid) == 0:
        raise RuntimeError("A privileged launcher and a different worker identity are required")
    os.setgroups([])
    # Drop the bounding set while CAP_SETPCAP is still effective, then all IDs.
    last = int(Path("/proc/sys/kernel/cap_last_cap").read_text())
    for capability in range(last + 1):
        prctl(24, capability)  # PR_CAPBSET_DROP
    prctl(47, 4)              # PR_CAP_AMBIENT, PR_CAP_AMBIENT_CLEAR_ALL
    prctl(38, 1)              # PR_SET_NO_NEW_PRIVS
    os.setresgid(int(gid), int(gid), int(gid))
    os.setresuid(int(uid), int(uid), int(uid))
    os.execv(sys.executable, [sys.executable, "-I", "-B", worker, root])


if __name__ == "__main__":
    main()
