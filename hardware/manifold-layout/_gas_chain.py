"""External adapter envelopes and tube mouths on the warm CO2 chain.

The gray fittings represent acquired PI010822S adapters using the existing nominal
1/4-inch PTC reference dimensions. The purchased LTWFITTING B01ABDD8FY coupling
has no verified dimensional drawing: its 22 mm OD, 25.4 mm length and 11 mm thread
engagement below are provisional layout allowances, not supplier dimensions.
Measure the made-up fittings before accepting this layout for assembly.
"""

import sys
from pathlib import Path

import cadquery as cq

_hw = Path(__file__).resolve().parents[1]
for _folder in ("jg-pp010822e", "gasher-check-valve", "wr1110-regulator"):
    sys.path.insert(0, str(_hw / "reference" / _folder))
import jg_pp010822e as _ptc
import gasher_check_valve as _check
import wr1110_regulator as _reg

ADAPTER_REACH = _ptc.HEX_LENGTH + _ptc.COLLET_LENGTH
COUPLING_OD = 22.0
COUPLING_LENGTH = 25.4
COUPLING_ENGAGEMENT = 11.0

REG_IN_ADAPTER = "co2-adapter-regulator-in"
REG_OUT_ADAPTER = "co2-adapter-regulator-out"
CHECK_IN_ADAPTER = "co2-adapter-check-in"
CHECK_OUT_ADAPTER = "co2-adapter-check-out"
CHECK_COUPLING = "co2-check-coupling-nominal"
ADAPTER_NAMES = (REG_IN_ADAPTER, REG_OUT_ADAPTER, CHECK_IN_ADAPTER, CHECK_OUT_ADAPTER)
BODY_NAMES = ADAPTER_NAMES + (CHECK_COUPLING,)
PORT_ADAPTERS = {
    "wr1110.inlet": REG_IN_ADAPTER,
    "wr1110.outlet": REG_OUT_ADAPTER,
    "gasher-co2.inlet": CHECK_IN_ADAPTER,
    "gasher-co2.outlet": CHECK_OUT_ADAPTER,
}


def advance(port, reach):
    pos, axis = port
    return tuple(pos[i] + reach * axis[i] for i in range(3)), axis


def regulator_inlet():
    return advance(_reg.inlet(), ADAPTER_REACH)


def regulator_outlet():
    return advance(_reg.outlet(), ADAPTER_REACH)


def check_inlet():
    return advance(_check.inlet(), ADAPTER_REACH)


def coupling_outlet():
    return advance(_check.outlet(), COUPLING_LENGTH - COUPLING_ENGAGEMENT)


def check_outlet():
    return advance(coupling_outlet(), ADAPTER_REACH)


def check_socket():
    """The existing nominal round inlet boss, used for a local tied ceiling cradle."""
    mid = -_check.TOTAL_LENGTH / 2.0 + _check.SOCKET_LENGTH / 2.0
    return ((0.0, mid, 0.0), (0.0, 1.0, 0.0)), _check.SOCKET_D / 2.0, _check.SOCKET_LENGTH


def adapter(port):
    """Only the external hex and collet; the engaged NPT shank is inside its mate."""
    pos, axis = port
    plane = cq.Plane(origin=pos, normal=axis)
    hex_body = cq.Workplane(plane).polygon(6, _ptc.HEX_ACROSS_CORNERS).extrude(_ptc.HEX_LENGTH)
    collet_base = cq.Vector(*pos) + cq.Vector(*axis).multiply(_ptc.HEX_LENGTH)
    collet = cq.Solid.makeCylinder(_ptc.COLLET_D / 2, _ptc.COLLET_LENGTH,
                                  collet_base, cq.Vector(*axis))
    return hex_body.union(collet).val()


def coupling():
    """Provisional pipe-coupling envelope, with room for the check's engaged male stub."""
    pos, axis = advance(_check.outlet(), -COUPLING_ENGAGEMENT)
    base, direction = cq.Vector(*pos), cq.Vector(*axis)
    shell = cq.Solid.makeCylinder(COUPLING_OD / 2, COUPLING_LENGTH, base, direction)
    bore = cq.Solid.makeCylinder(_check.THREAD_D / 2, COUPLING_LENGTH, base, direction)
    return shell.cut(bore)


def bodies(regulator_carry, check_carry):
    return {
        REG_IN_ADAPTER: adapter(_reg.inlet()).moved(regulator_carry.where),
        REG_OUT_ADAPTER: adapter(_reg.outlet()).moved(regulator_carry.where),
        CHECK_IN_ADAPTER: adapter(_check.inlet()).moved(check_carry.where),
        CHECK_OUT_ADAPTER: adapter(coupling_outlet()).moved(check_carry.where),
        CHECK_COUPLING: coupling().moved(check_carry.where),
    }
