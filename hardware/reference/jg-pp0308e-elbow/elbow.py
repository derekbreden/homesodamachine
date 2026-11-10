"""The elbow reader supplies socket datums and optional native-CAD access to its published model.

The +Y socket is observed; the +Z collet is completed by symmetry. Internal
retention, sealing, insertion depth and operating travel are unmeasured.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEP = HERE / 'jg-pp0308e-elbow.step'

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('elbow')
globals().update({name: _reference_values[name] for name in ('TUBE_OD', 'COLLET_FACE', 'FIXED_FACE', 'INSERTION', 'RELEASE_TRAVEL')})



def port(leg):
    'Observed/resting release face, not an insertion stop or travel endpoint.'
    return _reference_data('elbow', 'port', (leg,), {})


def stations():
    return _reference_data('elbow', 'stations', (), {})


def build():
    """Read the named reference solids for optional native-CAD consumers."""
    import cadquery as cq
    shapes = cq.importers.importStep(str(STEP)).val().Solids()
    return [(name, cq.Workplane(obj=shape)) for name, shape in
            zip(('fixed_body', 'y_collet', 'z_collet'), shapes, strict=True)]


def build_elbow_connector():
    """Assembly-compatible compound; the three component solids stay separate."""
    import cadquery as cq
    return cq.Workplane(obj=cq.Compound.makeCompound([p.val() for _,p in build()]))
