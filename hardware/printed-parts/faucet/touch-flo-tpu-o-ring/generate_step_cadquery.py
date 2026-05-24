"""Touch-Flo TPU O-ring — printed-TPU sealing bushing for the 3/8" OD
LLDPE water tube where it descends into the harvested Westbrass valve
body's top water port.

Material: Bambu TPU 90A (same stock as the touch-flo-mounting-gasket,
foam-cap gasket, and reservoir face seals). 90A is the
gasket-industry-standard hardness — soft enough to compress and seal
under modest squeeze, firm enough to resist cold-flow over years.

Architecture: factory metal dispense tube was Ø 9.55 mm OD with two
toroidal rubber o-rings (Ø 10.15 mm uncompressed OD, sitting in grooves
on the tube) sealing into the body's Ø 10.0 mm port. We're replacing
the metal dispense tube with Ø 9.525 mm (3/8") LLDPE that descends from
the printed shell's gooseneck water channel into the same body port.
LLDPE can't have grooves cut into it, so the seal is a printed TPU
bushing that lives in the port and is compressed between the LLDPE OD
and the port wall.

Sizing (single continuous bushing; alternative "two-discrete-rings"
mimicking the factory layout was considered and rejected for v1 in
favor of simpler install):

- **Inner Ø 9.45 mm** vs LLDPE 9.525 mm — 0.0375 mm radial interference
  per side. Firm grip on the tube; resists pull-out, contributes to
  the seal at the tube-OD interface.
- **Outer Ø 10.2 mm** vs body port 10.0 mm — 0.1 mm radial compression
  per side. Firm seal at the port-wall interface, insertion force still
  manageable by hand.
- **Wall 0.375 mm** (= (10.2 − 9.45) / 2). Printable with Bambu Studio's
  Arachne thin-wall handling on a 0.4 mm nozzle.
- **Length 8 mm** axially — substantial sealing band, equivalent
  contact area to the two factory rubber o-rings combined.

Cross-section is plain rectangular (concentric cylinder shell). No
sealing ribs, no chamfers — if v1 insertion is too hard or sealing
performance is inadequate, add chamfers / ribs / longer length /
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
inner_diameter = 9.45    # ID — grips Ø 9.525 LLDPE with 0.0375 mm/side interference
outer_diameter = 10.2    # OD — compresses into Ø 10.0 body port with 0.1 mm/side squeeze
height = 8.0             # axial length of the sealing bushing


def build_o_ring() -> cq.Workplane:
    """Build the TPU bushing as a hollow cylinder centered on the
    origin, axis along +Z, base at Z=0."""
    outer = (
        cq.Workplane("XY")
        .circle(outer_diameter / 2.0)
        .extrude(height)
    )
    inner = (
        cq.Workplane("XY")
        .circle(inner_diameter / 2.0)
        .extrude(height)
    )
    return outer.cut(inner)


if __name__ == "__main__":
    o_ring = build_o_ring()

    out = Path(__file__).resolve().parent / "touch-flo-tpu-o-ring.step"
    export_step(o_ring, str(out))

    wall = (outer_diameter - inner_diameter) / 2.0
    print("Touch-Flo TPU O-ring")
    print(f"  Inner Ø:  {inner_diameter} mm  (grips Ø 9.525 LLDPE — 0.0375 mm/side interference)")
    print(f"  Outer Ø:  {outer_diameter} mm  (seats in Ø 10.0 body port — 0.1 mm/side compression)")
    print(f"  Wall:     {wall:.4f} mm")
    print(f"  Height:   {height} mm")
    print(f"-> {out.name}")
