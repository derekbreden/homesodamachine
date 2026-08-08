"""John Guest PP010822E male connector, 1/4" OD push-to-connect × 1/4" NPT M,
black polypropylene — the appliance's NPT-to-PTC transition. Six per build
([`ledger/bom.md`](/hardware/ledger/bom.md) §3): three on the water path, two on
the CO2 path, one on the carbonated-water outlet.

External envelope only — a PTC collet body, a wrench hex, and a plain-cylinder
NPT shank at its nominal major, no helix. Same modeling class as the DERPIPE
inlet next door, one tube size down.

On the ASSE 1022 chain this is the last piece before the metal: the 1/4" LLDPE
from the rear-wall bulkhead pushes into the collet, and the shank threads into
the GAGIRA coupling's small end.

Frame: +X = flow axis, the PTC collet at X = 0 (upstream, where the tube pushes
in), the NPT shank at +X. Centered on Y and Z.

Run:
    tools/cad-venv/bin/python hardware/reference/jg-pp010822e/jg_pp010822e.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

COLLET_D = 14.0             # 1/4" PTC collet body OD
COLLET_LENGTH = 13.5        # push-in cartridge + release collar
HEX_ACROSS_CORNERS = 16.5   # 9/16" hex (14.29 across flats)
HEX_LENGTH = 5.0            # wrench flat thickness
SHANK_D = 13.7              # 1/4" NPT major Ø (simplified, no helix)
SHANK_LENGTH = 11.0         # NPT engagement
TUBE_D = 6.35               # the 1/4" OD LLDPE it accepts
LENGTH = COLLET_LENGTH + HEX_LENGTH + SHANK_LENGTH


def tube_port():
    """The PTC mouth the 1/4" LLDPE pushes into: (position, outward axis)."""
    return (0.0, 0.0, 0.0), (-1.0, 0.0, 0.0)


def shank_end():
    """The far end of the NPT male shank: (position, outward axis) — it threads
    SHANK_LENGTH into whatever female it meets."""
    return (LENGTH, 0.0, 0.0), (1.0, 0.0, 0.0)


def build():
    """PTC collet (X = 0, upstream) → hex → NPT shank (+X). Built along +Z
    low-to-high = upstream-to-downstream, then reoriented +Z -> +X."""
    collet = cq.Workplane("XY").circle(COLLET_D / 2.0).extrude(COLLET_LENGTH)
    hex_sec = (
        cq.Workplane("XY")
        .workplane(offset=COLLET_LENGTH)
        .polygon(6, HEX_ACROSS_CORNERS)
        .extrude(HEX_LENGTH)
    )
    shank = (
        cq.Workplane("XY")
        .workplane(offset=COLLET_LENGTH + HEX_LENGTH)
        .circle(SHANK_D / 2.0)
        .extrude(SHANK_LENGTH)
    )
    part = collet.union(hex_sec).union(shank)
    return part.val().rotate((0, 0, 0), (0, 1, 0), 90.0)


def main():
    part = build()
    bb = part.BoundingBox()
    print("John Guest PP010822E 1/4\" PTC × 1/4\" NPT M male connector")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Collet Ø{COLLET_D} × {COLLET_LENGTH:g}; hex {HEX_ACROSS_CORNERS} corners × "
          f"{HEX_LENGTH:g}; NPT Ø{SHANK_D} × {SHANK_LENGTH:g}; total {LENGTH:g} mm")
    out = _here.parent / "jg-pp010822e.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
