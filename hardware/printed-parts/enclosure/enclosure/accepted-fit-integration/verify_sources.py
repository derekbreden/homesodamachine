"""Reject geometry evidence when its recorded source or artifact bytes change."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools').is_dir())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


if __name__ == '__main__':
    generation = json.loads((HERE / 'generation.json').read_text())
    rows = []
    for path, digest in generation['source_sha256'].items():
        assert sha(ROOT / path) == digest, f'Changed geometry source: {path}'
        rows.append({'path': path, 'sha256': digest})
    for part, artifacts in generation['outputs'].items():
        for name, digest in artifacts.items():
            assert sha(HERE.parent / name) == digest, f'Changed artifact: {name}'
    (HERE / 'source-bindings.json').write_text(json.dumps(
        {'pass': True, 'generation_sources_current': True, 'sources': rows}, indent=2) + '\n')
    print(f'{len(rows)} geometry sources and all generated upper-shell artifacts match.')
