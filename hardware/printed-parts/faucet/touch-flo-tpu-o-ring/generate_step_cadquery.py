"""Touch-Flo TPU O-ring — printed-TPU sealing bushing for the 3/8" OD
LLDPE water tube where it descends into the harvested Westbrass valve
body's top water port.

Material: Bambu TPU 90A (same stock as the touch-flo-mounting-gasket,
foam-cap gasket, and reservoir face seals). 90A is the
gasket-industry-standard hardness — soft enough to compress and seal
under modest squeeze, firm enough to resist cold-flow over years.

Architecture: factory metal dispense tube was Ø 9.55 mm OD with two
toroidal rubber o-rings (Ø 10.15 mm uncompressed OD) sealing into the
body's Ø 10.0 mm port. We're replacing the metal dispense tube with
Ø 9.525 mm (3/8") LLDPE that descends from the printed shell's
gooseneck water channel into the same body port. LLDPE can't have
grooves cut into it, so the seal is a printed TPU **thimble** (open
top, closed bottom with a centered hole) that lives in the port:

- The cylindrical wall provides a radial seal — outer face squeezed
  against the port wall, inner face gripping the LLDPE OD.
- The bottom cap provides a *second* seal — face seal where the
  LLDPE's square-cut bottom end presses against the cap's top face.
  Pressure-energized: water below pushes the LLDPE end harder onto
  the cap.
- The cap's centered hole is sized between LLDPE ID and LLDPE OD —
  big enough for water to flow into the LLDPE bore unrestricted,
  small enough that the LLDPE bottoms out on the cap rather than
  passing through. This defines insertion depth: the LLDPE goes
  until it stops, no further.

Print orientation: **cap-down on the bed**. The first layer is then
a solid annular disk (the cap), not a thin ring, with maximum bed
adhesion. The thin cylindrical wall extrudes upward from a confident
base. This sidesteps the 0.4-nozzle TPU minimum-wall constraint that
the previous open-ended sleeve v1 hit (Bambu Studio rejected the
empty-thin-ring first layer).

Sizing:

- **Inner Ø (cylinder) 9.45 mm** vs LLDPE 9.525 mm — 0.0375 mm radial
  interference per side. Firm grip on the tube, resists pull-out,
  contributes to the seal at the tube-OD interface.
- **Outer Ø 10.20 mm** vs body port 10.0 mm — 0.1 mm radial
  compression per side. Firm seal at the port-wall interface,
  insertion force still manageable by hand.
- **Cap hole Ø 6.5 mm** — just above LLDPE ID (1/4" = 6.35 mm) so
  water flows into the LLDPE bore without restriction; well below
  LLDPE OD (9.525 mm) so the tube bottoms out on the cap.
- **Cap thickness 1.5 mm** — structural under face-seal load,
  prints cleanly as a solid first layer.
- **Cylinder length 13.5 mm** — sealing band, generous radial seal
  contact area. Combined with the 1.5 mm cap, total height is 15 mm
  vs ≥ 20 mm of available port depth.
- **Cylinder wall 0.375 mm** = (10.20 − 9.45) / 2. Below 0.4 nozzle's
  single-line minimum, but printable with Arachne thin-wall handling
  because layer 1 (the cap) is fully solid — the wall doesn't have
  to bootstrap from a thin ring on the bed.

Cross-section is plain rectangular (concentric cylinder shell + flat
disk cap). No sealing ribs, no chamfers — if v1 insertion is too
hard or sealing inadequate, add chamfers / ribs / longer length /
adjusted interference and re-print.

Regenerate: tools/cad-venv/bin/python generate_step_cadquery.py
"""

import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(
    0,
    str(next(p for p in Path(__file__).resolve().parents if p.name == "hardware")),
)
from _cadq_export import export_step


# Geometry inputs.
inner_diameter = 9.45      # cylinder ID — grips Ø 9.525 LLDPE (0.0375 mm/side interference)
outer_diameter = 10.20     # cylinder OD — compresses into Ø 10.0 body port (0.1 mm/side squeeze)
cap_hole_diameter = 6.50   # hole through the cap — > LLDPE ID (6.35), << LLDPE OD (9.525)
cap_thickness = 1.5        # axial thickness of the closed bottom
cylinder_length = 13.5     # axial length of the sleeve portion above the cap
total_height = cap_thickness + cylinder_length  # 15.0 mm


def build_o_ring() -> cq.Workplane:
    """Build the TPU thimble — closed bottom with a centered hole,
    open top, cylindrical wall.

    Z=0 is the bottom (cap-down on the bed). Cap spans Z = 0 to
    cap_thickness; sleeve spans Z = cap_thickness to total_height.
    """
    # Solid outer cylinder spanning the full part height.
    body = (
        cq.Workplane("XY")
        .circle(outer_diameter / 2.0)
        .extrude(total_height)
    )

    # Cut the cap's centered hole through the full height. (Through
    # the cap and also through the sleeve, but the sleeve's larger
    # bore — cut next — supersedes it above Z = cap_thickness.)
    cap_hole = (
        cq.Workplane("XY")
        .circle(cap_hole_diameter / 2.0)
        .extrude(total_height)
    )
    body = body.cut(cap_hole)

    # Cut the sleeve's larger inner bore from Z = cap_thickness to
    # the top of the part. Leaves the cap (Z = 0 to cap_thickness)
    # with only the smaller cap hole.
    sleeve_bore = (
        cq.Workplane("XY")
        .workplane(offset=cap_thickness)
        .circle(inner_diameter / 2.0)
        .extrude(cylinder_length)
    )
    body = body.cut(sleeve_bore)

    return body


if __name__ == "__main__":
    o_ring = build_o_ring()

    out = Path(__file__).resolve().parent / "touch-flo-tpu-o-ring.step"
    export_step(o_ring, str(out))

    wall = (outer_diameter - inner_diameter) / 2.0
    print("Touch-Flo TPU O-ring (thimble)")
    print(f"  Cylinder ID:    Ø{inner_diameter} mm  (grips Ø 9.525 LLDPE — 0.0375 mm/side interference)")
    print(f"  Outer Ø:        Ø{outer_diameter} mm  (seats in Ø 10.0 body port — 0.1 mm/side compression)")
    print(f"  Cylinder wall:  {wall:.4f} mm")
    print(f"  Cap hole:       Ø{cap_hole_diameter} mm  (> LLDPE ID 6.35, < LLDPE OD 9.525)")
    print(f"  Cap thickness:  {cap_thickness} mm")
    print(f"  Cylinder len:   {cylinder_length} mm")
    print(f"  Total height:   {total_height} mm  (port depth ≥ 20 mm — comfortable)")
    print(f"-> {out.name}")
