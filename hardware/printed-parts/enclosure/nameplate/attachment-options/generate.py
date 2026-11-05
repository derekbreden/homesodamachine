"""Export the body-connected attachment proposals with the installed Rust kernel.

Run manually through tools/run.py. This writes review GLBs, not production parts
or printer packages.
"""
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools').is_dir())
sys.path.insert(0, str(ROOT / 'hardware/scripts'))
import _rust_part

_rust_part.start()
numbers = json.loads((HERE / 'review.numbers.json').read_text())
numbers['source_sha256'] = hashlib.sha256((ROOT / numbers['plate_model']).read_bytes()).hexdigest()
result = _rust_part.cut('enclosure-components', 'nameplate-attachment-options',
    numbers, ROOT / 'hardware/assembly/scenes/glb')
print(json.dumps(result, indent=2))
