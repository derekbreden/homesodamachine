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

A ⌀[6.35 mm](PRV_VENT_D) hole through the BARREL accepts a length of 1/4" OD
LLDPE tubing — the unpressurized vent line. The LLDPE runs down the
foam shell's PORT LANE and out its slot in the −X wall, one station
above the evaporator inlet copper that shares it, into the appliance
interior, where it terminates open.

The hole is radial and not in the cap because THE CAP HAS NOWHERE TO
SEND A TUBE. Installed, the shroud lies horizontally on the −Y port's
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
               │    PRV body, hex,    │  ← [19 mm](PRV_INNER_D) ID
               │    upper smooth cyl, │     [23 mm](PRV_OUTER_D) OD ([2 mm](PRV_WALL_T) wall)
               │    bonnet windows,   │
               │    pull-ring)        │
               │                      │
    Z = 0      └ open ────────────────┘  ← seats on elbow ⌀18.8 mm cyl

               ⌀[6.35 mm](PRV_VENT_D) vent bored radially through the −Y wall at
               Z = [37.88 mm](VENT_STATION); installed, −Y is the shell's −Z, so the
               tube leaves DOWNWARD onto the port lane.

The [44 mm](CAVITY_L) cavity length spans from the bottom of the elbow's smooth
cylinder to the tip of the PRV pull-ring with the valve hand-tight
in the elbow's lateral F outlet.

Coordinate convention: cylinder axis along Z, open end at Z=0, cap
top at Z=[46 mm](TOTAL_L). Installed orientation is horizontal — the shroud's Z
axis aligns with the lateral run of the TAISHER elbow off Port 4.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "scripts"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

from _cadq_export import export_step
from docgen import substitute_md, substitute_py_comments


# Physical dimensions

# [19 mm](PRV_INNER_D) — [0.1 mm](OVERCUT) radial slip-fit over the ⌀18.8 elbow seat cylinder.
inner_diameter = 19.0
# [2 mm](PRV_WALL_T) — radial wall around the PRV body.
wall_thickness = 2.0
# [2 mm](PRV_CAP_T) — closed (far) end carrying the vent hole.
cap_thickness = 2.0
# [44 mm](CAVITY_L) — elbow seat bottom to PRV pull-ring tip.
cavity_length = 44.0
# [6.35 mm](PRV_VENT_D) — 1/4" LLDPE tubing OD.
vent_hole_diameter = 6.35
# [37.88 mm](VENT_STATION) along the barrel from the open end — where the radial vent
# stands. The shroud seats on the PRV elbow's own lateral mouth and reaches along the
# vessel's −Y from there, so this distance is the mouth-to-lane gap: the mouth stands at
# y −39.62 (one catalog elbow leg off the −Y port) and the foam shell's port lane runs at
# y −77.5, so the hole lands on that lane's centreline and the tube falls it with no
# corner at all. It sits inside the cavity by more than its own radius, so the bore opens
# on the annulus around the valve. `cold-core-layout`'s `prv-vent-lands` is what holds
# this reading against the placed shroud's.
vent_station_z = 37.88

outer_diameter = inner_diameter + 2 * wall_thickness  # [23 mm](PRV_OUTER_D)
total_length = cavity_length + cap_thickness  # [46 mm](TOTAL_L)

overcut = 0.1


def build_prv_shroud():
    """One-piece cup on axis +Z: a full ⌀[23 mm](PRV_OUTER_D) cylinder spanning Z=0 to
    the cap top at Z=[46 mm](TOTAL_L), an open-end bore (⌀[19 mm](PRV_INNER_D), Z=0 inward) that the
    elbow seat enters and that stops at the cap inner face Z=[44 mm](CAVITY_L), and a
    ⌀[6.35 mm](PRV_VENT_D) vent hole bored RADIALLY through the −Y wall at
    Z=[37.88 mm](VENT_STATION)."""
    outer = (
        cq.Workplane("XY")
        .circle(outer_diameter / 2)
        .extrude(total_length)
    )
    cavity = (
        cq.Workplane("XY")
        .circle(inner_diameter / 2)
        .extrude(cavity_length + overcut)
    )
    vent_hole = (
        cq.Workplane("XZ")
        .workplane(offset=inner_diameter / 2 - overcut)
        .center(0.0, vent_station_z)
        .circle(vent_hole_diameter / 2)
        .extrude(wall_thickness + 2 * overcut)
    )
    return outer.cut(cavity).cut(vent_hole)


def main():
    out_dir = _here.parent
    shroud = build_prv_shroud()
    export_step(shroud, str(out_dir / "prv-shroud.step"))

    solids = shroud.solids().vals()
    assert len(solids) == 1, f"expected 1 solid, got {len(solids)}"
    solid = solids[0]
    bb = solid.BoundingBox()
    vol = solid.Volume()
    print(
        f"-> prv-shroud.step  "
        f"bbox X[{bb.xmin:6.2f}..{bb.xmax:6.2f}] "
        f"Y[{bb.ymin:6.2f}..{bb.ymax:6.2f}] "
        f"Z[{bb.zmin:6.2f}..{bb.zmax:6.2f}]  "
        f"vol {vol:.3f} mm^3"
    )

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
        "PRV_BBOX_X": f"{bb.xmin:.3f} to {bb.xmax:.3f} mm",
        "PRV_BBOX_Y": f"{bb.ymin:.3f} to {bb.ymax:.3f} mm",
        "PRV_BBOX_Z": f"{bb.zmin:.3f} to {bb.zmax:.3f} mm",
    }
    substitute_md(
        out_dir / "README.md",
        variables=variables,
        expected_counts={
            "PRV_INNER_D": 2,
            "PRV_WALL_T": 1,
            "PRV_CAP_T": 2,
            "CAVITY_L": 1,
            "PRV_VENT_D": 1,
            "VENT_STATION": 1,
            "PRV_OUTER_D": 1,
            "TOTAL_L": 1,
            "PRV_VOLUME": 1,
            "PRV_BBOX_X": 1,
            "PRV_BBOX_Y": 1,
            "PRV_BBOX_Z": 1,
        },
    )
    print("-> README.md")
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "PRV_INNER_D": 3,
            "OVERCUT": 1,
            "PRV_WALL_T": 2,
            "PRV_CAP_T": 2,
            "CAVITY_L": 4,
            "PRV_VENT_D": 4,
            "VENT_STATION": 4,
            "PRV_OUTER_D": 3,
            "TOTAL_L": 4,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
