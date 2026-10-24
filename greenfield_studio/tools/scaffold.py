#!/usr/bin/env python3
"""Create a fresh attempt; --reference gives a separate controlled reference."""
import argparse
from pathlib import Path
import shutil

p=argparse.ArgumentParser()
p.add_argument('target', type=Path, help='new empty directory')
p.add_argument('--reference', action='store_true')
a=p.parse_args()
root=Path(__file__).resolve().parent.parent
if a.target.exists():
    raise SystemExit('Refusing to overwrite target; choose a new path.')
a.target.mkdir(parents=True)
shutil.copy2(root/('reference' if a.reference else 'starter')/'booking.py', a.target/'booking.py')
shutil.copytree(root/'docs', a.target/'docs')
shutil.copytree(root/'tests', a.target/'tests')
(a.target/'README.txt').write_text(
    'First read docs/contract.md and docs/decisions/0001-storage.md.\n'
    'Run: python3 -m unittest discover -s tests -v\n'
    'This is a local teaching slice, not an authenticated network service.\n')
print('Created', a.target)
print('Next: cd', a.target, '&& python3 -m unittest discover -s tests -v')
