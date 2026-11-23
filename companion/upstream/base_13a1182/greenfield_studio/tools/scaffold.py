#!/usr/bin/env python3
"""Create a fresh attempt; --reference gives a separate controlled reference."""
import argparse
import json
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
(a.target/'README.md').write_text(
    '# Greenfield Reservation Studio — learner copy\n\n'
    '1. Read `docs/contract.md`, `docs/decisions/0001-storage.md`, and `tests/test_booking.py`.\n'
    '2. Run `python3 -m unittest discover -s tests -v` and preserve the expected initial failure.\n'
    '3. Edit only `booking.py`; preserve the approved contract, decision, and tests.\n'
    '4. Rerun the tests, review the evidence boundary, and preserve the result.\n\n'
    'This is a local teaching slice, not an authenticated or production-ready network service.\n',
    encoding='utf-8')
(a.target/'READER_ENTRY.json').write_text(json.dumps({
    'schema': 'reader-entry/v1',
    'route': 'GREENFIELD_RESERVATION_STUDIO',
    'release': '2026.10.24-d16',
    'mode': 'REFERENCE' if a.reference else 'INCOMPLETE_STARTER',
    'source_studio': str(root),
    'candidate_readiness': 'REFERENCE_ONLY' if a.reference else 'NOT_ESTABLISHED',
    'human_acceptance': 'PENDING',
    'meaning': ('An isolated teaching reference; its pass does not repair or accept a learner candidate.'
                if a.reference else
                'A new learner copy with an intentional NotImplementedError initial state.'),
}, indent=2) + '\n', encoding='utf-8')
print('Prepared', a.target)
print('Next: cd', a.target, '&& python3 -m unittest discover -s tests -v')
