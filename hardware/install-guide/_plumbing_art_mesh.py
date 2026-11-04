'The under-sink instruction scenes as Rust-kernel illustration geometry.'
from __future__ import annotations
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[2]/"hardware/scripts"))
from _guides_compiled import compiled as _compiled, bind as _bind

def note_read(*args, **kwargs):
    'Record an input supplied to the Rust geometry program.'
    return _compiled('_plumbing_art_mesh',path=('note_read',),args=args,kwargs=kwargs)

def note_write(*args, **kwargs):
    'Record an output emitted by a child geometry or rendering program.'
    return _compiled('_plumbing_art_mesh',path=('note_write',),args=args,kwargs=kwargs)

def _plain(*args, **kwargs):
    return _compiled('_plumbing_art_mesh',path=('_plain',),args=args,kwargs=kwargs)

def export(*args, **kwargs):
    'Export registered named states from the Rust-authored instruction recipe.'
    return _compiled('_plumbing_art_mesh',path=('export',),args=args,kwargs=kwargs)

__all__ = ['annotations', 'json', 'Path', 'tempfile', 'note_read', 'note_write', 'export']
_bind('_plumbing_art_mesh',globals())

if __name__ == '__main__':
    _compiled('_plumbing_art_mesh','main')
