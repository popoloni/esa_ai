#!/usr/bin/env python3
"""Reproduce reference tests in an isolated temporary directory, without a user repo."""
from pathlib import Path
import subprocess
import sys
import tempfile
root=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='esa_gf_reference_') as tmp:
    p=Path(tmp)/'reference'
    subprocess.run([sys.executable,str(root/'scaffold.py'),str(p),'--reference'],check=True)
    r=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=p)
    sys.exit(r.returncode)
