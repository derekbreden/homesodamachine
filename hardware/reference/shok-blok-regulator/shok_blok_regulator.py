"""Hydronix Shok Blok SB-FPV-40, nominal 40 psi, 1/4-inch push-connect.

Provisional external envelope: 101.6 mm listing length, photo-scaled sections.
The inlet face is the origin; flow follows +X. Internal working parts are omitted.

Geometry is held in the frozen STEP and fine payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from __future__ import annotations
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
HW = next(p for p in HERE.parents if p.name == 'hardware')
sys.path.insert(0, str(HW / 'scripts'))


_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('shok_blok_regulator')
globals().update({name: _reference_values[name] for name in ('TUBE_D', 'LENGTH', 'SECTIONS')})



def sections():
    return _reference_data('shok_blok_regulator', 'sections', (), {})


def inlet():
    return _reference_data('shok_blok_regulator', 'inlet', (), {})


def outlet():
    return _reference_data('shok_blok_regulator', 'outlet', (), {})


def build():
    import cadquery as cq
    pieces = [cq.Solid.makeCylinder(r, b-a, cq.Vector(a, 0, 0), cq.Vector(1, 0, 0))
              for _label, r, a, b in sections()]
    return pieces[0].fuse(*pieces[1:]).clean()




_FROZEN_DIR = Path(__file__).resolve().parent
STEP_PATH = _FROZEN_DIR / 'shok-blok-regulator.step'
PAYLOAD_PATH = _FROZEN_DIR / 'shok-blok-regulator.step.mesh'
ASSET_MANIFEST_PATH = _FROZEN_DIR / "frozen-asset.json"


def __getattr__(name):
    if name in globals():
        return globals()[name]
    if name in ('cq',):
        import cadquery as cq
        value = locals()[name]
    elif name in ('export_assembly',):
        from _cadq_export import export_assembly
        value = locals()[name]
    elif name in ('M_JG_GREY_ACETAL', 'one_body'):
        from _materials import M_JG_GREY_ACETAL, one_body
        value = locals()[name]
    else:
        raise AttributeError(name)
    globals()[name] = value
    return value


def main():
    print('shok-blok-regulator frozen reference')
    print(f"  STEP: {STEP_PATH}")
    print(f"  Fine/display payload: {PAYLOAD_PATH}")


if __name__ == '__main__':
    main()
