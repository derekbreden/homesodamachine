"""The joint on each of the G Ganen pump's barbs ([`ledger/bom.md`](/hardware/ledger/bom.md)):

- a short piece of neoPure PVCR-0610 reinforced clear PVC, 3/8" ID × 0.594" OD, pushed over the
  barb to its casing-clear end plane;
- a John Guest PP061208W reducer, its 3/8" stem trimmed short, pushed into the tube's other end up
  to the stem's shoulder, its tip on the barb's tip;
- two YDS butterfly clamps, 10–16 mm with a 9 mm band, each centred on the length of fitting the
  tube covers: one on the barb, one on the stem.

The reducer's 1/4" collet carries the line on. The tube is drawn installed: its bore on the barb's
scanned profile and on the stem, its outside opened to keep its section. Each band is closed on the
tube's widest outside under it.

A joint can bend down: the reducer and the clamp on its stem turn about the lowest point of the
barb's tip, where the stem's tip bears on it, and the barb and its clamp stay as they are. The tube
runs straight on each and creases on the plane halfway between them.

Frame: +X = the port's outward axis, the barb's tip at X = 0, so the tube runs from its casing-clear
end at negative X out over the trimmed stem. Each clamp's housing stands on +Z, and its key lies flat in
the band's plane and runs along +Y or −Y. Down is −Z.

Numeric profiles and port frames describe the installed joint for Rust consumers.
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in ("scripts", "reference/g-ganen-pump", "reference/jg-pp061208w"):
    sys.path.insert(0, str(_hw / _p))
import g_ganen_pump as pump
import jg_pp061208w as reducer

STEP = _here.parent / "pump-barb-joint.step"

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('pump_barb_joint')
globals().update({name: _reference_values[name] for name in ('PORTS', 'TUBE_ID', 'TUBE_OD', 'TUBE_ROOT_SETBACK', 'TRIM', 'CUT_X', 'RANGE', 'BAND_W', 'BAND_T', 'HOUSING_L', 'HOUSING_W', 'HOUSING_H', 'NECK_D', 'NECK_L', 'KEY_L', 'KEY_NECK_W', 'KEY_W', 'KEY_T')})


# --- the tube: neoPure PVCR-0610 --------------------------------------------
# The separately fitted molded head extends 0.668/0.710 mm beyond the first
# scanned barb station inside the tube's occupied radius. This end setback
# retains at least 0.15 mm to that shoulder and the complete 9 mm clamp band.

# --- the reducer: the PP061208W, its stem cut short --------------------------
# The stem left ahead of the shoulder. SEEDED from Derek's photograph of the trimmed reducer,
# against its 17.3 mm mouth collar; NOT MEASURED.

# --- the clamp: YDS butterfly SS W2, 10–16 mm --------------------------------
# SEEDED from Derek's photograph against the 9 mm band, NOT RATIFIED — measure a clamp in hand
# before anything is spaced to these.


def barb(port):
    '`(x, radius)` along the scanned barb, root to tip.'
    return _reference_data('pump_barb_joint', 'barb', (port,), {})


def root(port):
    'The square-cut tube end, clear of the molded head/root: x, negative.'
    return _reference_data('pump_barb_joint', 'root', (port,), {})


def tube_length(port):
    return _reference_data('pump_barb_joint', 'tube_length', (port,), {})


def opened(r_bore):
    "The tube's outside radius with its bore opened to `r_bore`, keeping its section."
    return _reference_data('pump_barb_joint', 'opened', (r_bore,), {})


def bore(port):
    return _reference_data('pump_barb_joint', 'bore', (port,), {})


def band_d(port, xc):
    return _reference_data('pump_barb_joint', 'band_d', (port, xc), {})


def bands(port):
    '`{clamp: (centre x, band diameter)}`: each band centred on the fitting the tube covers.'
    return _reference_data('pump_barb_joint', 'bands', (port,), {})


def pivot(port):
    "Where the stem's tip bears on the barb's tip as the joint bends down: the tip's lowest point."
    return _reference_data('pump_barb_joint', 'pivot', (port,), {})


def mouth(port, bend=0.0):
    'The reducer\'s 1/4" collet mouth: (position, outward axis).'
    return _reference_data('pump_barb_joint', 'mouth', (port, bend), {})
