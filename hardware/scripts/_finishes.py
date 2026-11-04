"""Material and tube-stock appearances merged by the Rust shared provider."""
from dataclasses import asdict
import _materials as _mat
import _routing
from _shared_data import call

SHARED = _mat._CATALOG['shared']


def _inputs():
    return {**_mat._finish_inputs(),'spools':{name:asdict(spool) for name,spool in _routing.SPOOLS.items()},'shared':SHARED}


def rows():
    return call('color.all_finishes',**_inputs())


def _place(name,spool,rgb,out,at):
    out[:] = call('color.place_finish',name=name,spool=asdict(spool),rgb=rgb,rows=out,shared=SHARED)
    at.clear()
    at.update({tuple(row['rgb']):row for row in out})


def find(rgb,tol=4e-4):
    return call('color.find_finish',rgb=rgb,tol=tol,**_inputs())
