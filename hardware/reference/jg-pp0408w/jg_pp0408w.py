"""Line-art reference solid of the John Guest PP0408W 1/4" inline union — the
push-to-connect fitting that joins two lengths of 1/4" OD tube end to end.

White acetal copolymer, rotationally symmetric about the flow axis. In profile
it is a barbell: two collet-ring bodies with a narrower centre barrel between
them, and a release sleeve standing proud of each end face. A tube pushes in
until it bottoms; a thumb on the sleeve lets it back out. Every figure below is
photo-measured off the part in hand —
`hardware/off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md`
is the measurement, and this is the solid struck from it.

One hangs under the hopper basin's spout, and the customer opens it every time
the basin goes to the dishwasher. What pushes into its upper collet is
`hardware/reference/hopper-drain-stub/`; `fluid-4` leaves the lower one.

Coordinate convention:
  Z = tube-flow axis, +Z toward the near port.
  Origin = the union's own mid-plane. The fitting is symmetric about it, so
      both ports stand at ±`OVERALL / 2` and neither end is the special one.

Run:
    tools/cad-venv/bin/python hardware/reference/jg-pp0408w/jg_pp0408w.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step, import_step

STEP = _here.parent / "jg-pp0408w.step"

# --- the measurement --------------------------------------------------------

RING_D = 15.10          # collet-ring body OD — the fitting's widest section, at both ends
RING_LEN = 12.08        # that body's length, per end
BARREL_D = 9.31         # centre barrel OD — the narrowest section
BARREL_LEN = 12.16      # its length
COLLET_D = 9.57         # release sleeve OD
COLLET_WALL = 1.44      # its wall — the annular face a release plate or a thumb bears on
PORT_D = 6.35           # 1/4" tube OD, the bore each end accepts
BODY_LEN = 36.32        # ring + barrel + ring, collets excluded
OVERALL = 41.80         # collets in their default EXTENDED position — the envelope to space to
OVERALL_PRESSED = 39.13  # the same with both sleeves pushed fully in
INSERTION = 16.0        # how far a tube runs into each end before it bottoms

COLLET_BORE = COLLET_D - 2.0 * COLLET_WALL      # 6.69 — the tube passes with 0.35 of slip
# What one sleeve stands proud of its own body end face, extended, and the travel a thumb
# takes out of that before the teeth let go.
COLLET_PROUD = (OVERALL - BODY_LEN) / 2.0
COLLET_TRAVEL = (OVERALL - OVERALL_PRESSED) / 2.0
# The through passage standing between the two tube ends, at the bore of the tube itself.
BORE_D = 4.32           # 1/4" LLDPE ID

# Seating planes along Z, from the mid-plane out. The far end mirrors these.
barrel_face_z = BARREL_LEN / 2.0
ring_face_z = barrel_face_z + RING_LEN
port_face_z = ring_face_z + COLLET_PROUD


def port(side: float) -> tuple:
    """One of the two 1/4" tube ports: `(position, outward axis)`, `side` picking the near
    (+Z) or far (−Z) end. The station is the RELEASE SLEEVE'S own outer face — the plane a
    tube crosses to enter, and runs `INSERTION` beyond."""
    s = 1.0 if side > 0 else -1.0
    return ((0.0, 0.0, s * port_face_z), (0.0, 0.0, s))


def envelope() -> tuple:
    """`(diameter, length)` the fitting takes, sleeves extended — what crowds a neighbour."""
    return (RING_D, OVERALL)


def reach() -> float:
    """Mid-plane to port face — half the envelope, and how far the fitting hangs below a
    body seated on its upper port."""
    return port_face_z


def stations_hold():
    """Hold the envelope and both ports to `jg-pp0408w.step` — the file the machine spaces
    the hopper's disconnect by, while it hangs the basin's stub in one end and starts a run
    at the other."""
    solid = import_step(str(STEP)).val()
    bb = solid.BoundingBox()
    for what, claimed, actual in (("ring width", RING_D, bb.xlen),
                                  ("ring height", RING_D, bb.ylen),
                                  ("near port", port_face_z, bb.zmax),
                                  ("far port", -port_face_z, bb.zmin)):
        if abs(claimed - actual) > 1e-6:
            raise ValueError(
                f"jg-pp0408w {what} is {claimed:g} and {STEP.name} carries {actual:.4f} — a "
                f"machine spaced to this figure is spaced to a fitting that is not there.")


# --- the solid --------------------------------------------------------------

def _cyl(d, z0, z1):
    return cq.Solid.makeCylinder(d / 2.0, abs(z1 - z0),
                                 cq.Vector(0, 0, min(z0, z1)), cq.Vector(0, 0, 1))


def _end(s: float):
    """One end of the barbell: the collet-ring body, then the release sleeve standing proud
    of its face, bored to `COLLET_BORE` so the sleeve reads as the ring it is."""
    body = _cyl(RING_D, s * barrel_face_z, s * ring_face_z)
    sleeve = (_cyl(COLLET_D, s * ring_face_z, s * port_face_z)
              .cut(_cyl(COLLET_BORE, s * ring_face_z, s * port_face_z)))
    return body.fuse(sleeve)


def build_jg_pp0408w():
    """The union as a single solid wrapped in a `cq.Workplane`: barrel, both ring bodies and
    both sleeves, bored the tube's socket at each end and the tube's own bore between them."""
    solid = _cyl(BARREL_D, -barrel_face_z, barrel_face_z).fuse(_end(1.0), _end(-1.0))
    sockets = (_cyl(PORT_D, port_face_z, port_face_z - INSERTION)
               .fuse(_cyl(PORT_D, -port_face_z, -port_face_z + INSERTION)))
    return cq.Workplane(obj=solid.cut(sockets).cut(_cyl(BORE_D, -port_face_z, port_face_z)))


def main():
    part = build_jg_pp0408w()
    bb = part.val().BoundingBox()
    print("John Guest PP0408W — 1/4\" push-to-connect inline union (simplified)")
    print(f"  Canonical-frame bounding box: "
          f"X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
          f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Ring Ø{RING_D} / barrel Ø{BARREL_D} / sleeve Ø{COLLET_D} / port Ø{PORT_D}")
    print(f"  Overall {OVERALL} extended, {OVERALL_PRESSED} pressed; "
          f"{INSERTION:g} mm of tube in each end")
    print(f"  Solid valid: {part.val().isValid()}")

    export_step(part, str(STEP))
    print(f"-> {STEP.name}")
    stations_hold()


if __name__ == "__main__":
    main()
