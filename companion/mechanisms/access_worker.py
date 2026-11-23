#!/usr/bin/env python3
"""An intentionally adversarial worker for a disposable protected fixture."""
import errno
import hashlib
import json
import os
from pathlib import Path
import stat
import sys


def metadata(path):
    value = path.stat()
    return {"path": str(path), "uid": value.st_uid, "gid": value.st_gid,
            "mode": oct(stat.S_IMODE(value.st_mode)), "inode": value.st_ino}


def credentials():
    status = Path("/proc/self/status").read_text()
    return {"uid": os.getuid(), "euid": os.geteuid(), "gid": os.getgid(),
            "egid": os.getegid(), "groups": os.getgroups(),
            "capabilities": {line.split(":", 1)[0]: line.split(":", 1)[1].strip()
              for line in status.splitlines() if line.startswith(("Cap", "NoNewPrivs:"))}}


def main():
    root = Path(sys.argv[1])
    protected = root / "tests" / "test_policy.py"
    scratch = root / "scratch"
    paths = [protected, protected.parent, root, *root.parents]
    before_metadata = [metadata(p) for p in paths]
    before = protected.read_bytes()  # Reaches the actual file before any mutation.
    positive = scratch / "positive_control.txt"
    positive.write_text("ordinary write reached the writable fixture\n")
    positive_ok = positive.read_text() == "ordinary write reached the writable fixture\n"
    replacement = scratch / "replacement.py"
    replacement.write_text("THRESHOLD = 10000\n")
    events = []
    operations = [
        ("write", protected, lambda: protected.write_text("THRESHOLD = 10000\n")),
        ("replace", protected, lambda: os.replace(replacement, protected)),
        ("chmod_file", protected, lambda: protected.chmod(0o644)),
        ("chmod_directory", protected.parent, lambda: protected.parent.chmod(0o755)),
        ("chmod_parent", root, lambda: root.chmod(0o777)),
        ("rename_directory", protected.parent, lambda: protected.parent.rename(root / "moved_tests")),
    ]
    for operation, path, call in operations:
        event = {"operation": operation, "target": str(path), "target_reached": path.exists()}
        try:
            call()
        except OSError as error:
            expected = {errno.EPERM} if operation.startswith("chmod") else {errno.EACCES, errno.EPERM}
            event.update(exception=type(error).__name__, errno=error.errno,
                         expected_errno=sorted(expected), denied=error.errno in expected)
        else:
            event.update(denied=False, errno=None, exception=None)
        events.append(event)
    after = protected.read_bytes()
    print(json.dumps({**credentials(), "positive_control_writable": positive_ok,
        "positive_control": {"path": str(positive), "sha256": hashlib.sha256(positive.read_bytes()).hexdigest()},
        "protected_read_succeeded": True, "metadata_before": before_metadata,
        "metadata_after": [metadata(p) for p in paths], "events": events,
        "unchanged": before == after,
        "sha256_before": hashlib.sha256(before).hexdigest(),
        "sha256_after": hashlib.sha256(after).hexdigest()}))


if __name__ == "__main__":
    main()
