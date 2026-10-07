"""Read-time source bindings for native geometry and factory evidence."""
from pathlib import Path
import hashlib,json
from evidence_binding import content_sha256

STUDY=Path(__file__).resolve().parents[1]
ROOT=STUDY.parents[1]

def snapshot(*paths):
    sources={Path(__file__).resolve(),STUDY/'evidence_binding.py',STUDY/'audit.py'}
    sources.update(Path(p).resolve()for p in paths)
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(sources)}

def changed(bindings):
    return [p for p,h in bindings.items()
            if not (ROOT/p).is_file()or hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]

def scene_stock_current(manifest):
    """Admit recut parent stock against substantive read-time input digests."""
    projected=manifest.get('inputs_content_sha256')
    bindings=projected if projected is not None else manifest.get('inputs_sha256',{})
    for relative,digest in bindings.items():
        path=STUDY/relative
        if not path.is_file():return False
        raw=path.read_bytes()
        actual=content_sha256(json.loads(raw)) if projected is not None else hashlib.sha256(raw).hexdigest()
        if actual!=digest:return False
    return True
