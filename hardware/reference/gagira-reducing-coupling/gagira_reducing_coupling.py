"""GAGIRA 316L SS reducing coupling, 3/8" NPT F × 1/4" NPT F — the upstream
adapter that closes the gap between the appliance's 1/4" water run and the ASSE
1022's 3/8" male inlet ([`ledger/bom.md`](/hardware/ledger/bom.md) §3).

External envelope only — a hex barrel bored from each end at the major Ø of the
male thread that end takes, so a fitting threaded in occupies its socket rather
than the coupling's metal; the threads themselves are not cut. Hex 7/8" across
flats, the common size for a 3/8" body; length off the same fitting class.

The small (1/4" NPT F) end takes the John Guest PP010822E's male shank; the
large (3/8" NPT F) end threads onto the ASSE 1022's male inlet, so the coupling
sits between them on the flow axis.

Frame: +X = flow axis, the 1/4" (upstream) end at X = 0; centered on Y and Z.

Run:
    tools/cad-venv/bin/python hardware/reference/gagira-reducing-coupling/gagira_reducing_coupling.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

HEX_ACROSS_CORNERS = 25.67  # 7/8" hex (22.23 across flats)
LENGTH = 30.5               # along the flow axis (1.20")
SMALL_SOCKET_D = 13.72      # 1/4" NPT major Ø (0.540") — the shank it swallows
SMALL_SOCKET_DEPTH = 11.0   # how far the 1/4" NPT male shank threads in
LARGE_SOCKET_D = 17.15      # 3/8" NPT major Ø (0.675") — the ASSE inlet it swallows
LARGE_SOCKET_DEPTH = 13.0   # how far the 3/8" NPT male inlet threads in


def small_end():
    """The 1/4" NPT female end: (position, outward axis) — the PP010822E's shank
    threads in this far (SMALL_SOCKET_DEPTH)."""
    return (0.0, 0.0, 0.0), (-1.0, 0.0, 0.0)


def large_end():
    """The 3/8" NPT female end: (position, outward axis) — this is what goes onto
    the ASSE 1022's male inlet, LARGE_SOCKET_DEPTH deep."""
    return (LENGTH, 0.0, 0.0), (1.0, 0.0, 0.0)


def build():
    """A hex barrel along +X, bored from each end to the depth its male threads in."""
    barrel = (
        cq.Workplane("YZ")
        .polygon(6, HEX_ACROSS_CORNERS)
        .extrude(LENGTH)
        .val()
    )
    small = cq.Solid.makeCylinder(
        SMALL_SOCKET_D / 2.0, SMALL_SOCKET_DEPTH, cq.Vector(0, 0, 0), cq.Vector(1, 0, 0))
    large = cq.Solid.makeCylinder(
        LARGE_SOCKET_D / 2.0, LARGE_SOCKET_DEPTH,
        cq.Vector(LENGTH - LARGE_SOCKET_DEPTH, 0, 0), cq.Vector(1, 0, 0))
    return barrel.cut(small).cut(large)


def main():
    part = build()
    bb = part.BoundingBox()
    print("GAGIRA 316L SS reducing coupling, 3/8\" NPT F × 1/4\" NPT F")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Hex {HEX_ACROSS_CORNERS} across corners × {LENGTH:g} mm; "
          f"sockets {SMALL_SOCKET_DEPTH:g} (1/4\") / {LARGE_SOCKET_DEPTH:g} (3/8\") deep")
    out = _here.parent / "gagira-reducing-coupling.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
