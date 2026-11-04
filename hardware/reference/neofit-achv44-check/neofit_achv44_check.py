"""neoFit ACHV44-E analytic layout reference from the vendor's product media.

The ACHV44-E listing gives nominal connections and product identity. Exterior
scale and socket engagement are inferred from neoFit ATEU44/ATRU444 published
1/4-inch socket dimensions. The vendor GLB supplies the check-specific form.
These are same-family layout estimates, not published ACHV44 dimensions.
See model-dimensions.json for the evidence scope.
Native Y runs with the inferred flow; the origin bisects the two mouth planes.

Geometry is in the frozen STEP and display payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('neofit_achv44_check')
globals().update({name: _reference_values[name] for name in ('NAME', 'TUBE_OD', 'LENGTH', 'FAMILY_SOCKET_COLLAR_OD', 'SOCKET_INSERTION', 'FLOW_BORE', 'MAX_BODY_RADIUS', 'VENDOR_SCALE_MM', 'FIXED_PROFILE', 'COLLET_MAJOR_RADIUS', 'COLLET_MINOR_RADIUS', 'COLLET_LIP_LENGTH', 'COLLET_STEM_RADIUS', 'COLLET_REACH')})

STEP_PATH = HERE / (NAME + '.step')
PAYLOAD_PATH = HERE / (NAME + '.step.mesh')
ASSET_MANIFEST_PATH = HERE / 'frozen-asset.json'
# Vendor node0 outlet socket collar has radius1.0. It corresponds to the
# sibling sheets' maximum female collar diameter, not the larger check barrel.

# (station from inlet mouth, radius), mm. The circular envelope retains the
# vendor body's distinct barrel, taper and socket bands. Sub-0.01 mm duplicate
# rings in its tessellation are represented by the adjacent analytic shoulder.


def inlet():
    'Inlet mouth and outward axis, in native mm; inferred flow enters here.'
    return _reference_data('neofit_achv44_check', 'inlet', (), {})


def outlet():
    'Outlet mouth and outward axis, in native mm.'
    return _reference_data('neofit_achv44_check', 'outlet', (), {})


def socket_depth(port=None):
    '16.891 mm sibling neoFit socket depth, inferred for this unmeasured check.'
    return _reference_data('neofit_achv44_check', 'socket_depth', (port,), {})


def ports():
    'One interface table shared by the water and gas installations.'
    return _reference_data('neofit_achv44_check', 'ports', (), {})


def bearing_band():
    'Fixed cylindrical barrel: (start, end, radius), measured from inlet.'
    return _reference_data('neofit_achv44_check', 'bearing_band', (), {})


def sections():
    'Conservative radial sections (label, radius, s0, s1) along flow.\n\n    Tapered fixed-body spans use their larger endpoint radius. The two\n    moving collets use their oval major radius. These are axial envelopes,\n    not a seal, release stroke, retention or load specification.\n    '
    return _reference_data('neofit_achv44_check', 'sections', (), {})


def specification():
    'Published identity and explicit scope of the estimated layout geometry.'
    return _reference_data('neofit_achv44_check', 'specification', (), {})


def main():
    print(NAME)
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
