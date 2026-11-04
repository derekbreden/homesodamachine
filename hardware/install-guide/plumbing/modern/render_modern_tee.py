"Render a modern-home, all-push-connect cold-water installation sequence.\n\nThe household line is 1/4-inch OD LLDPE already seated in an existing John\nGuest PP0408W-style push-to-connect union.  The installation shown here never\nopens a threaded or compression joint:\n\n1. turn the household quarter-turn shutoff from ON to OFF while the LLDPE and\n   its PTC union remain connected;\n2. press the union's release collet and withdraw the existing LLDPE;\n3. push the supplied stub/tee/appliance-tube assembly into that union;\n4. push the original household line into the tee's open run port.\n\nEvery visible fitting, tube, valve, and handle is literal CAD geometry.\nThe wide shutoff pair, release trio, and cumulative tee sequence each retain a\nregistered orthographic camera so motion is the only visual change within a\nstep. Motion arrows stay out of the renders: the guide page places one fixed\nflat glyph at each projected action anchor. The final PNGs have transparent\ncanvases so the guide page is their only background.\n\nRegenerate from the repository root with::\n\n    tools/cad-venv/bin/python       hardware/install-guide/plumbing/modern/render_modern_tee.py"
from __future__ import annotations
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[4]/"hardware/scripts"))
from _guides_compiled import compiled as _compiled, bind as _bind

from dataclasses import dataclass
@dataclass(frozen=True)
class View:
    camera: tuple[float, float, float]
    target: tuple[float, float, float]
    span: float

def _plumbing_data(*args, **kwargs):
    return _compiled('render_modern_tee',path=('_plumbing_data',),args=args,kwargs=kwargs)

def _canonicalize_png(*args, **kwargs):
    return _compiled('render_modern_tee',path=('_canonicalize_png',),args=args,kwargs=kwargs)

def _job(*args, **kwargs):
    return _compiled('render_modern_tee',path=('_job',),args=args,kwargs=kwargs)

def main(*args, **kwargs):
    return _compiled('render_modern_tee',path=('main',),args=args,kwargs=kwargs)

__all__ = ['annotations', 'sys', 'tempfile', 'shutil', 'dataclass', 'Path', 'HERE', 'HARDWARE', 'ROOT', 'ART', 'note_write', 'union_ref', 'View', 'SCENES', 'main']
_bind('render_modern_tee',globals())

if __name__ == '__main__':
    _compiled('render_modern_tee','main')
