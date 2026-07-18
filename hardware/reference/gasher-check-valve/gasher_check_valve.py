"""GASHER 1/4" NPT inline check valve — brass hex-barrel body with a male NPT
threaded stub each end. Two sit in the enclosure pack: the water-pump outlet
check (gasher-water, on the SeaFlo discharge) and the CO2 inlet check
(gasher-co2, on the DERPIPE → WR1110 chain).

External envelope only — the internal spring + poppet is not modeled. The
silhouette is a hex barrel with two threaded stubs, read off the
manufacturer's dimensioned drawing (~Ø17 across the hex corners × 40 mm along
the flow axis). The hex inscribes the old Ø17 placeholder cylinder, so the
real shape is strictly smaller than the box it replaces. 1/4" NPT is a plain
cylinder at the nominal major Ø — the repo's no-thread-helix convention
(cf. jg-bulkhead-union's 51055K3-no-threads, co2-coupling-body).

Frame: +Y = flow axis (matches the enclosure placement, which laid the
placeholder as _cyl(..., (0, 1, 0))); centered on X/Z. +Z up.

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

HEX_ACROSS_CORNERS = 17.0   # inscribes the old Ø17 placeholder cylinder
TOTAL_LENGTH = 40.0         # along the flow axis
THREAD_D = 13.7             # 1/4" NPT major Ø (simplified, no helix)
STUB_LENGTH = 11.0          # male NPT engagement each end
HEX_LENGTH = TOTAL_LENGTH - 2 * STUB_LENGTH   # 18 mm hex barrel


def build():
    """Hex barrel + a threaded stub each end, flow axis along +Y."""
    # Build along +Z, then reorient the flow axis +Z -> +Y.
    hexb = cq.Workplane("XY").polygon(6, HEX_ACROSS_CORNERS).extrude(HEX_LENGTH)
    lower = cq.Workplane("XY").circle(THREAD_D / 2.0).extrude(-STUB_LENGTH)
    upper = (
        cq.Workplane("XY")
        .workplane(offset=HEX_LENGTH)
        .circle(THREAD_D / 2.0)
        .extrude(STUB_LENGTH)
    )
    part = hexb.union(lower).union(upper)
    return part.rotate((0, 0, 0), (1, 0, 0), -90.0)


def main():
    part = build()
    bb = part.val().BoundingBox()
    print("GASHER 1/4\" NPT inline check valve")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Hex: {HEX_ACROSS_CORNERS} across corners × {HEX_LENGTH:g} mm; "
          f"stubs Ø{THREAD_D} × {STUB_LENGTH:g} mm; total {TOTAL_LENGTH:g} mm")
    out = _here.parent / "gasher-check-valve.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
