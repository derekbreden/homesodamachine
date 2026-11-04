"The installation pictures' producer surfaces and illustration props.\n\nProducer meshes keep their normals, face ranges and material colours. Only the\ntwo faucet detail crops pass through the solid kernel, to close their cut ends.\nThese scene payloads serve pictures; they are not measurement models."
from __future__ import annotations
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[2]/"hardware/scripts"))
from _guides_compiled import compiled as _compiled, bind as _bind

def _read(*args, **kwargs):
    return _compiled('_install_art_mesh',path=('_read',),args=args,kwargs=kwargs)

def payloads(*args, **kwargs):
    'Stage the requested named scenes beside the existing render job paths.'
    return _compiled('_install_art_mesh',path=('payloads',),args=args,kwargs=kwargs)

__all__ = ['annotations', 'json', 'Path', 'struct', 'np', 'linear', 'payloads']
_bind('_install_art_mesh',globals())

if __name__ == '__main__':
    _compiled('_install_art_mesh','main')
