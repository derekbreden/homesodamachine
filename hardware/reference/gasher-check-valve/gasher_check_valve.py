"""GASHER 1/4" NPT inline check valve — a hex-barrel body with a female NPT
socket on the inlet end and a male NPT stub on the outlet end. Two sit in the
enclosure pack: the water-pump outlet check (gasher-water, on the SeaFlo
discharge) and the CO2 inlet check (gasher-co2, on the DERPIPE → WR1110 chain).

The casting's flow arrow runs from the female socket toward the male stub, so
the female end is what a male NPT upstream threads INTO and the male stub is
what threads into the female downstream. Nickel-plated copper body, soft seat,
150 psi.

External envelope only — the internal spring + poppet is not modeled. A hex
barrel (Ø17 across the corners) with a socket boss one end and a male stub the
other, the NPT a plain cylinder at the nominal major Ø.

Frame: +Y = flow axis (matches the enclosure placement), the female inlet at
−Y and the male outlet at +Y; centered on X/Z, +Z up.

Run:
    tools/cad-venv/bin/python hardware/reference/gasher-check-valve/gasher_check_valve.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

HEX_ACROSS_CORNERS = 17.0   # hex circumdiameter (across corners)
TOTAL_LENGTH = 40.0         # along the flow axis
THREAD_D = 13.7             # 1/4" NPT major Ø (simplified, no helix)
STUB_LENGTH = 11.0          # male NPT engagement, the outlet end
SOCKET_D = 15.5             # female socket boss OD, the inlet end
SOCKET_LENGTH = 11.0        # the depth a male NPT threads in
HEX_LENGTH = TOTAL_LENGTH - STUB_LENGTH - SOCKET_LENGTH   # 18 mm hex barrel


def inlet():
    """The mouth of the female NPT socket — where the upstream male threads in:
    (position, outward axis)."""
    return (0.0, -TOTAL_LENGTH / 2.0, 0.0), (0.0, -1.0, 0.0)


def outlet():
    """The far end of the male NPT stub — it threads SOCKET-deep into whatever
    female it meets: (position, outward axis)."""
    return (0.0, TOTAL_LENGTH / 2.0, 0.0), (0.0, 1.0, 0.0)


def build():
    """Female socket boss (−Y, inlet) → hex barrel → male stub (+Y, outlet).
    Built along +Z low-to-high = upstream-to-downstream, then reoriented
    +Z -> +Y and centred on the flow axis."""
    socket = cq.Workplane("XY").circle(SOCKET_D / 2.0).extrude(SOCKET_LENGTH)
    hexb = (
        cq.Workplane("XY")
        .workplane(offset=SOCKET_LENGTH)
        .polygon(6, HEX_ACROSS_CORNERS)
        .extrude(HEX_LENGTH)
    )
    stub = (
        cq.Workplane("XY")
        .workplane(offset=SOCKET_LENGTH + HEX_LENGTH)
        .circle(THREAD_D / 2.0)
        .extrude(STUB_LENGTH)
    )
    part = socket.union(hexb).union(stub).translate((0, 0, -TOTAL_LENGTH / 2.0))
    return part.rotate((0, 0, 0), (1, 0, 0), -90.0)


def main():
    part = build()
    bb = part.val().BoundingBox()
    print("GASHER 1/4\" NPT inline check valve")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Hex: {HEX_ACROSS_CORNERS} across corners × {HEX_LENGTH:g} mm; "
          f"female socket Ø{SOCKET_D} × {SOCKET_LENGTH:g} mm; "
          f"male stub Ø{THREAD_D} × {STUB_LENGTH:g} mm; total {TOTAL_LENGTH:g} mm")
    for label, (pos, axis) in (("inlet  (F)", inlet()), ("outlet (M)", outlet())):
        print(f"  {label}: ({pos[0]:7.2f}, {pos[1]:6.2f}, {pos[2]:7.2f})  out {axis}")
    out = _here.parent / "gasher-check-valve.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
