"""John Guest PP061208W: 3/8-inch stem to 1/4-inch push-connect reducer.

The exposed exterior follows the threaded ASSE assembly scan. The buried male
tip uses a nominal 18.29 mm stem-to-shoulder length; internal passages and the
stop are display geometry. Frame: stem tip X0, axis +X, socket mouth at +X.

Geometry is held in the frozen STEP and fine payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from __future__ import annotations
from pathlib import Path
import sys


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == 'hardware')
sys.path.insert(0, str(_hw/'scripts'))

STEP = _here.with_name('jg-pp061208w.step')
# Frozen component measurements keep layout imports independent of scan files.

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('jg_pp061208w')
globals().update({name: _reference_values[name] for name in ('PARAMETER_SNAPSHOT_SHA256', 'PARAMETERS', 'STEM_D', 'STEM_LENGTH', 'STEM_TIP_CHAMFER', 'TUBE_D', 'TUBE_BORE_D', 'THROUGH_BORE_D', 'TUBE_STOP_DEPTH', 'BODY_D', 'body_face_x', 'LENGTH', 'COLLET_PROUD', 'tube_stop_x', 'TUBE_INSERTION_DEPTH', 'stem_to_shoulder_x')})




def stem_tip():
    'Nominal hidden male tip and insertion direction; not a scanned stop.'
    return _reference_data('jg_pp061208w', 'stem_tip', (), {})


def stem_shoulder():
    'Fitted shoulder plane in the nominal full-part frame.'
    return _reference_data('jg_pp061208w', 'stem_shoulder', (), {})


def tube_port():
    'Captured representative release face and outward tube axis.'
    return _reference_data('jg_pp061208w', 'tube_port', (), {})


def captured_transform():
    'Part-to-captured-chain rigid transform; nominal buried tip remains explicit.'
    return _reference_data('jg_pp061208w', 'captured_transform', (), {})


_FROZEN_DIR = Path(__file__).resolve().parent
STEP_PATH = _FROZEN_DIR / 'jg-pp061208w.step'
PAYLOAD_PATH = _FROZEN_DIR / 'jg-pp061208w.step.mesh'
ASSET_MANIFEST_PATH = _FROZEN_DIR / "frozen-asset.json"


def main():
    print('jg-pp061208w frozen reference')
    print(f"  STEP: {STEP_PATH}")
    print(f"  Fine/display payload: {PAYLOAD_PATH}")


if __name__ == '__main__':
    main()
