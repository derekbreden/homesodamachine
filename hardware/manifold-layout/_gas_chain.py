"""External adapter envelopes and tube mouths on the warm CO2 chain.

WR1110 and the downstream GASHER check each run female 1/4-inch NPT in and male 1/4-inch NPT
out, and gray acetal John Guest fittings take every end onto 1/4-inch tube: a PI010822S male
connector threads into each female socket, and a PI450822S female adapter onto each male stub.
The PI010822S uses the existing nominal 1/4-inch PTC reference dimensions. The PI450822S is the
PP450822E's form in gray acetal and takes the nominal sections the SeaFlo discharge chain draws
for that adapter. Measure the made-up fittings before accepting this layout for assembly.
"""

import sys
from pathlib import Path

import cadquery as cq

_hw = Path(__file__).resolve().parents[1]
for _folder in ("jg-pp010822e", "gasher-check-valve", "wr1110-regulator",
                "seaflo-discharge-chain"):
    sys.path.insert(0, str(_hw / "reference" / _folder))
import jg_pp010822e as _ptc
import gasher_check_valve as _check
import wr1110_regulator as _reg
import seaflo_discharge_chain as _female   # the PP450822E's sections, the PI450822S's form

# Past the mate's face: the male connector's hex and collet, and the female adapter's socket,
# hex and collet less the stub it swallows.
MALE_REACH = _ptc.HEX_LENGTH + _ptc.COLLET_LENGTH
FEMALE_REACH = (_female.JG_SOCKET_L + _female.JG_HEX_L + _female.JG_COLLET_L
                - _female.NPT_ENGAGE)
# The scanned WR1110 stub bounds how far this nominal adapter can advance.
# Shoulder seating is a layout assumption until the actual fitting is made up.
REGULATOR_ENGAGEMENT = min(_female.NPT_ENGAGE, _reg.STUB_LENGTH)
REGULATOR_FEMALE_REACH = (_female.JG_SOCKET_L + _female.JG_HEX_L
                         + _female.JG_COLLET_L - REGULATOR_ENGAGEMENT)

REG_IN_ADAPTER = "co2-adapter-regulator-in"
REG_OUT_ADAPTER = "co2-adapter-regulator-out"
CHECK_IN_ADAPTER = "co2-adapter-check-in"
CHECK_OUT_ADAPTER = "co2-adapter-check-out"
ADAPTER_NAMES = (REG_IN_ADAPTER, REG_OUT_ADAPTER, CHECK_IN_ADAPTER, CHECK_OUT_ADAPTER)
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
    return advance(_reg.inlet(), MALE_REACH)


def regulator_outlet():
    return advance(_reg.outlet(), REGULATOR_FEMALE_REACH)


def check_inlet():
    return advance(_check.inlet(), MALE_REACH)


def check_outlet():
    return advance(_check.outlet(), FEMALE_REACH)


def check_socket():
    """The existing nominal round inlet boss, used for a local tied ceiling cradle."""
    mid = -_check.TOTAL_LENGTH / 2.0 + _check.SOCKET_LENGTH / 2.0
    return ((0.0, mid, 0.0), (0.0, 1.0, 0.0)), _check.SOCKET_D / 2.0, _check.SOCKET_LENGTH


def male_connector(port):
    """A PI010822S in a female socket: only the external hex and collet; the engaged NPT
    shank is inside its mate."""
    pos, axis = port
    plane = cq.Plane(origin=pos, normal=axis)
    hex_body = cq.Workplane(plane).polygon(6, _ptc.HEX_ACROSS_CORNERS).extrude(_ptc.HEX_LENGTH)
    collet_base = cq.Vector(*pos) + cq.Vector(*axis).multiply(_ptc.HEX_LENGTH)
    collet = cq.Solid.makeCylinder(_ptc.COLLET_D / 2, _ptc.COLLET_LENGTH,
                                  collet_base, cq.Vector(*axis))
    return hex_body.union(collet).val()


def female_adapter(port, stub_d, engagement=_female.NPT_ENGAGE):
    """A PI450822S made up on a male stub whose far end is `port`: socket, hex and collet,
    the socket face standing the engagement back from the stub's end and bored to the stub
    for that depth, so the stub stands inside it."""
    pos, axis = advance(port, -engagement)
    base, direction = cq.Vector(*pos), cq.Vector(*axis)
    socket = cq.Solid.makeCylinder(_female.JG_SOCKET_D / 2, _female.JG_SOCKET_L,
                                   base, direction)
    hex_origin = base + direction.multiply(_female.JG_SOCKET_L)
    hex_body = (cq.Workplane(cq.Plane(origin=hex_origin.toTuple(), normal=axis))
                .polygon(6, _female.JG_HEX).extrude(_female.JG_HEX_L).val())
    collet = cq.Solid.makeCylinder(
        _female.JG_COLLET_D / 2, _female.JG_COLLET_L,
        base + direction.multiply(_female.JG_SOCKET_L + _female.JG_HEX_L), direction)
    bore = cq.Solid.makeCylinder(stub_d / 2, engagement, base, direction)
    return socket.fuse(hex_body, collet).clean().cut(bore)


def bodies(regulator_carry, check_carry):
    return {
        REG_IN_ADAPTER: male_connector(_reg.inlet()).moved(regulator_carry.where),
        REG_OUT_ADAPTER: female_adapter(_reg.outlet(), _reg.STUB_D,
                                       REGULATOR_ENGAGEMENT).moved(regulator_carry.where),
        CHECK_IN_ADAPTER: male_connector(_check.inlet()).moved(check_carry.where),
        CHECK_OUT_ADAPTER: female_adapter(_check.outlet(), _check.THREAD_D)
        .moved(check_carry.where),
    }
