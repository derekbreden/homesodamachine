"""PRV shroud — printed PETG cup that surrounds the Control Devices
SV-125 pressure-relief valve during the cold-core body foam pour.

The SV-125 is an open-port pop-off valve: gas exits through a single
radial discharge port on the smooth cylinder between the NPT threads
and the hex, and the spring chamber above the hex is open to
atmosphere through bonnet windows above. Both features need to see
air, not cured polyurethane foam, for the valve to function as a
relief device.

The shroud slips over the entire valve from the pull-ring end and
seats on the smooth ⌀18.8 mm cylindrical section of the TAISHER 316L
SS 90° street elbow (B0CZ38MYL1) that threads into Port 4. The
open shroud end-to-elbow joint is sealed with a bead of 100% RTV
silicone caulk, tooled to a fillet — foam-tight, not airtight.

A ⌀[6.8 mm](PRV_VENT_D) hole through the BARREL accepts a length of 1/4" OD
LLDPE tubing — the unpressurized vent line. The LLDPE runs down the
foam shell's WEST LANE and out its slot in the −X wall, one station
below the evaporator outlet copper that shares it, into the appliance
interior, where it terminates open.

The hole is radial and not in the cap because THE CAP HAS NOWHERE TO
SEND A TUBE. Installed, the shroud lies horizontally on the +Y port's
lateral axis and its cap face stands ~3 mm off the foam shell's own
inner wall — less than a tube's radius, so a line leaving axially has
no room to turn. Leaving radially through the barrel's underside, the
line is already pointing down the lane it has to fall, and needs no
corner at all. The hole's station along the barrel
([37.88 mm](VENT_STATION) from the open end) is what lands it on that
lane's centreline once the shroud is made up on the elbow.

Geometry
--------

    Z = [46 mm](TOTAL_L)  ┌──────────────────────┐  ← cap outside surface
               │ ░░░░ [2 mm](PRV_CAP_T) cap ░░░░░░ │  ← closed, no hole
    Z = [44 mm](CAVITY_L)  ├──────────────────────┤  ← cap inside surface
               │                      │
               │   (cavity around     │
               │    PRV body, hex,    │  ← [19.1 mm](PRV_INNER_D) ID
               │    upper smooth cyl, │     [23.1 mm](PRV_OUTER_D) OD ([2 mm](PRV_WALL_T) wall)
               │    bonnet windows,   │
               │    pull-ring)        │
               │                      │
    Z = 0      └ open ────────────────┘  ← seats on elbow ⌀18.8 mm cyl

               ⌀[6.8 mm](PRV_VENT_D) vent bored radially through the −Y wall at
               Z = [37.88 mm](VENT_STATION); the cup is rolled about its own axis at
               install so that wall faces the shell's −Z, and the tube leaves
               DOWNWARD onto the west lane (`cold_core_assembly._prv_roll`).

The [44 mm](CAVITY_L) cavity length spans from the bottom of the elbow's smooth
cylinder to the tip of the PRV pull-ring with the valve hand-tight
in the elbow's lateral F outlet.

Coordinate convention: cylinder axis along Z, open end at Z=0, cap
top at Z=[46 mm](TOTAL_L). Installed orientation is horizontal — the shroud's Z
axis aligns with the lateral run of the TAISHER elbow off Port 4.
"""

import argparse
import math
import sys
from pathlib import Path

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "scripts"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(0, str(_here.parents[1]))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

import fits
from docgen import substitute_md, substitute_py_comments


# Physical dimensions

# [19.1 mm](PRV_INNER_D) — 0.15 mm radial static clearance over the ⌀18.8 elbow seat cylinder.
inner_diameter = 18.8 + 2.0 * fits.slip
# [2 mm](PRV_WALL_T) — radial wall around the PRV body.
wall_thickness = 2.0
# [2 mm](PRV_CAP_T) — closed (far) end carrying the vent hole.
cap_thickness = 2.0
# [44 mm](CAVITY_L) — elbow seat bottom to PRV pull-ring tip.
cavity_length = 44.0
# [6.8 mm](PRV_VENT_D) — the vent tube's socket. Its sliding fit supports the
# installed tube; the shell crossings elsewhere provide loose passage clearance.
vent_hole_diameter = 6.5 + 2.0 * fits.slip  # tube socket; separate from loose shell passages
# [37.88 mm](VENT_STATION) along the barrel from the open end — where the radial vent
# stands. The shroud seats on the PRV elbow's own lateral mouth and reaches along the
# carbonator's port axis from there, so this distance is the mouth-to-lane gap: the mouth stands
# at y +39.62 (one catalog elbow leg off the +Y port) and the foam shell's west lane runs at
# y +77.5, so the hole lands on that lane's centreline and the tube falls it with no
# corner at all. It sits inside the cavity by more than its own radius, so the bore opens
# on the annulus around the valve.
vent_station_z = 37.88

outer_diameter = inner_diameter + 2 * wall_thickness  # [23.1 mm](PRV_OUTER_D)
total_length = cavity_length + cap_thickness  # [46 mm](TOTAL_L)

overcut = 0.1


def build_prv_shroud():
    """One-piece cup on axis +Z: a full ⌀[23.1 mm](PRV_OUTER_D) cylinder spanning Z=0 to
    the cap top at Z=[46 mm](TOTAL_L), an open-end bore (⌀[19.1 mm](PRV_INNER_D), Z=0 inward) that the
    elbow seat enters and that stops at the cap inner face Z=[44 mm](CAVITY_L), and a
    ⌀[6.8 mm](PRV_VENT_D) vent hole bored RADIALLY through the −Y wall at
    Z=[37.88 mm](VENT_STATION)."""
    import cadquery as cq
    outer = (
        cq.Workplane("XY")
        .circle(outer_diameter / 2)
        .extrude(total_length)
    )
    # The overcut clears the open end; the cavity stops at the cap's inside face.
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=-overcut)
        .circle(inner_diameter / 2)
        .extrude(cavity_length + overcut)
    )
    # The bore starts on the cup's axis, inside the cavity, so it opens through the curved
    # inner wall across its whole width.
    vent_hole = (
        cq.Workplane("XZ")
        .center(0.0, vent_station_z)
        .circle(vent_hole_diameter / 2)
        .extrude(outer_diameter / 2 + overcut)
    )
    # Print cap-down (-Z), with the open elbow seat upward. Only the radial
    # vent has a bridge crown: extend that side toward print-up, keeping the
    # tube station and opposite edge fixed.
    vent_hole = vent_hole.union(vent_hole.translate((0, 0, -fits.supported_surface)))
    return outer.cut(cavity).cut(vent_hole)


def numbers():
    """The cup and its supported radial vent, in the native +Z frame."""
    from _materials import C_SHROUD, linear
    return {"inner_radius": inner_diameter / 2.0,
            "outer_radius": outer_diameter / 2.0,
            "cavity_length": cavity_length, "total_length": total_length,
            "vent_radius": vent_hole_diameter / 2.0,
            "vent_station_z": vent_station_z, "overcut": overcut,
            "supported_surface": fits.supported_surface,
            "color": list(linear(C_SHROUD))}


def volume():
    """The cup less the union of the vent's two supported circular bores.

    At x = r*sin(theta), the radial depth through the two cup cylinders is
    sqrt(Ro²-x²) - sqrt(Ri²-x²). The union's height is 2*r*cos(theta) +
    allowance while its two circles overlap, and 4*r*cos(theta) outside
    that band. Splitting there makes both integrands smooth at their ends.
    """
    outer, inner, radius = outer_diameter / 2.0, inner_diameter / 2.0, vent_hole_diameter / 2.0
    allowance = fits.supported_surface
    split = math.acos(allowance / (2.0 * radius))

    def strip(theta, overlapping):
        x = radius * math.sin(theta)
        half = radius * math.cos(theta)
        depth = math.sqrt(outer * outer - x * x) - math.sqrt(inner * inner - x * x)
        height = 2.0 * half + allowance if overlapping else 4.0 * half
        return depth * height * half

    def integral(start, stop, overlapping):
        count = 128
        step = (stop - start) / count
        total = strip(start, overlapping) + strip(stop, overlapping)
        total += sum((4 if i % 2 else 2) * strip(start + i * step, overlapping)
                     for i in range(1, count))
        return total * step / 3.0

    removed = 2.0 * (integral(0.0, split, True) + integral(split, math.pi / 2.0, False))
    return math.pi * (outer * outer * total_length - inner * inner * cavity_length) - removed


def main(output=None, native=False):
    out_dir = Path(output) if output is not None else _here.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    if native:
        from _cadq_export import export_assembly
        from _materials import C_SHROUD, one_body
        shroud = build_prv_shroud()
        export_assembly(one_body(shroud, "prv-shroud", C_SHROUD),
                        str(out_dir / "prv-shroud.step"))
        solids = shroud.solids().vals()
        assert len(solids) == 1, f"expected 1 solid, got {len(solids)}"
        vol = solids[0].Volume()
    else:
        import _rust_part
        _rust_part.cut("cold-core", "prv-shroud", numbers(), out_dir)
        vol = volume()
    radius = outer_diameter / 2.0
    print(
        f"-> prv-shroud.step  "
        f"bbox X[{-radius:6.2f}..{radius:6.2f}] "
        f"Y[{-radius:6.2f}..{radius:6.2f}] "
        f"Z[{0.0:6.2f}..{total_length:6.2f}]  "
        f"vol {vol:.3f} mm^3"
    )

    document(vol)


def document(vol):
    out_dir = _here.parent
    radius = outer_diameter / 2.0
    variables = {
        "PRV_INNER_D": f"{inner_diameter:.4g} mm",
        "PRV_WALL_T": f"{wall_thickness:.4g} mm",
        "PRV_CAP_T": f"{cap_thickness:.4g} mm",
        "CAVITY_L": f"{cavity_length:.4g} mm",
        "PRV_VENT_D": f"{vent_hole_diameter:.4g} mm",
        "VENT_STATION": f"{vent_station_z:.4g} mm",
        "PRV_OUTER_D": f"{outer_diameter:.4g} mm",
        "TOTAL_L": f"{total_length:.4g} mm",
        "OVERCUT": f"{overcut:.4g} mm",
        "PRV_VOLUME": f"{vol:.3f} mm³",
        "PRV_BBOX_X": f"{-radius:.3f} to {radius:.3f} mm",
        "PRV_BBOX_Y": f"{-radius:.3f} to {radius:.3f} mm",
        "PRV_BBOX_Z": f"{0.0:.3f} to {total_length:.3f} mm",
    }
    substitute_md(
        out_dir / "README.md",
        variables=variables,
    )
    print("-> README.md")
    substitute_py_comments(
        Path(__file__),
        variables=variables,
    )
    print(f"-> {Path(__file__).name} (self)")


def import_part(path):
    """The emitted shroud for the caller's native or f64 mesh API."""
    import cadquery as cq
    from _cadq_export import import_step
    path = Path(path)
    if not getattr(cq, 'MESH', False):
        with path.open('rb') as stream:
            triangles = b'meshcad tessellated' in stream.read(200)
        if triangles and path.stem == 'prv-shroud':
            return build_prv_shroud().val()
    return import_step(str(path)).val()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', action='store_true', help='Run the retained native builder')
    parser.add_argument('--output', type=Path, default=_here.parent)
    args = parser.parse_args()
    main(args.output, native=args.native)
