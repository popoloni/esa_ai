#!/usr/bin/env python3
"""Verify this companion's packaged bytes; user work remains outside the manifest."""
from pathlib import Path
import hashlib
import json
import sys

root = Path(__file__).resolve().parent
manifest = json.loads((root / 'MANIFEST.json').read_text(encoding='utf-8'))
failures = []
for row in manifest['files']:
    path = root / row['path']
    if not path.is_file() or path.is_symlink():
        failures.append({'path': row['path'], 'failure': 'MISSING_OR_SYMLINK'})
    elif hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
        failures.append({'path': row['path'], 'failure': 'SHA256_MISMATCH'})
print(json.dumps({'status': 'PASS' if not failures else 'FAIL',
                  'version': manifest['version'], 'checked_files': len(manifest['files']),
                  'native_model_calls': 0, 'failures': failures}, indent=2))
sys.exit(bool(failures))
