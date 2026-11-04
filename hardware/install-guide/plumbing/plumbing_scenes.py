"Registered under-sink cold-water hookup scenes for the Install guide.\n\nThe four scenes use one literal coordinate frame and one camera.  They show the\ncommon older-home installation: a copper wall stub, quarter-turn angle stop,\nexisting braided 3/8-inch faucet supply, the John Guest Speedfit ASVPP1LF angle\nstop adapter valve interposed in that 3/8-inch run, and the appliance's white\n1/4-inch branch tube pushed into the adapter's collet.  Every instructional\nobject is CAD geometry; there are no labels, arrows, or raster additions.\n\nFrame:\n    +X = installer right\n    +Y = out from the wall and into the cabinet\n    +Z = up\n    Y=0 = finished wall face\n\nRun from the repository root:\n    tools/cad-venv/bin/python hardware/install-guide/plumbing/plumbing_scenes.py\n    tools/cad-venv/bin/python hardware/install-guide/plumbing/plumbing_scenes.py --render"
from __future__ import annotations
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[3]/"hardware/scripts"))
from _guides_compiled import compiled as _compiled, bind as _bind

def _plumbing_data(*args, **kwargs):
    return _compiled('plumbing_scenes',path=('_plumbing_data',),args=args,kwargs=kwargs)

def _render(*args, **kwargs):
    return _compiled('plumbing_scenes',path=('_render',),args=args,kwargs=kwargs)

def main(*args, **kwargs):
    return _compiled('plumbing_scenes',path=('main',),args=args,kwargs=kwargs)

__all__ = ['annotations', 'argparse', 'sys', 'Path', 'HERE', 'HARDWARE', 'ROOT', 'OUT', 'ART', 'SCENE_NAMES', 'main']
_bind('plumbing_scenes',globals())

if __name__ == '__main__':
    _compiled('plumbing_scenes','main')
