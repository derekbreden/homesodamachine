"""Reference solid for the DIGITEN G1/4" Hall-effect water-flow sensor
(model FL-S402B / FL-S402BZJ, Amazon B07QRXLRTH) — the inline turbine flow
meter that sits between the rear-wall pass-through ports in the lite
edition (carbonated water spins the rotor; the Hall pulse train triggers
the flavor pumps). A purchased part, not a printed one — the model is a
keep-out envelope for placement and tube routing, not a manufacturing
drawing.

A round, coin-shaped housing with two quick-connect ports on OPPOSITE rims,
coaxial along one diameter: water enters one collet, spins the rotor in the
round chamber, and exits the collet straight across the body — an INLINE
(straight-through, 180°) flow path, not an L. Reduced to coaxial/cylindrical
keep-out:

- Body — the round white rotor housing (rotor + Hall sensor). A disk
  Ø[26 mm](FLOW_BODY_DIA) across the circular label / rotor-cover faces, the
  body running [22 mm](BODY_LEN) through its depth (the two molded halves,
  joined at a mid-plane seam with four screws). The flow axis is a diameter
  of the disk; the rotor spins about that body depth axis.
- Two quick-connect ports — coaxial on opposite rims, one opening +X, one
  opening -X, each a Ø[12 mm](FLOW_PORT_DIA) collet barrel whose outer collet
  face reaches [30 mm](PORT_FACE) from the body center along the flow axis
  ([60 mm] tip to tip). As sold these are 1/4" push-to-connect (push a 1/4"
  OD tube in past the blue collet ring), not exposed threads — "G1/4" is the
  size class, not a BSP thread.
- Wire-exit boss — the rim stub (Ø[8 mm](WIRE_BOSS_DIA), [3 mm](WIRE_BOSS_LEN)
  proud) where the 3-wire pigtail (red VCC / black GND / yellow signal) leaves
  the housing, off the rim perpendicular to the flow axis.

The label face (DIGITEN logo) and the opposite molded 5-spoke "wagon-wheel"
rotor cover with its flow-direction arrow are surface graphics, not enveloped.

Coordinate frame (the repo world frame)
---------------------------------------
- X = flow axis  : the two ports are coaxial along X, collet faces at
                   X = ±[30 mm](PORT_FACE), opening +X and -X.
- Y = body depth : normal to the round label / rotor-cover faces; the body
                   spans Y = ±[11 mm] (the [22 mm](BODY_LEN) depth). The
                   rotor spins about Y.
- Z = up         : the wire-exit boss leaves the rim toward +Z.

Origin is the body center. The two ports run out along ±X; the wire-exit boss
leaves +Z off the rim.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))
from _cadq_export import export_assembly
from docgen import substitute_md, substitute_py_comments


# --- Body: round rotor housing (rotor + Hall sensor) -------------------------
# Photo-estimated against the 1/4" PTC collet barrel and the published
# YF-S402B-family envelope (60 x 26 x 22 mm); no manufacturer dimension
# drawing is published for this part.
body_dia = 26.0       # round label / rotor-cover face diameter
body_len = 22.0       # body depth through the two molded halves (the flow axis
                      # is a diameter of the disk; the rotor spins about this axis)

# --- Ports: two coaxial quick-connect collets on opposite rims ---------------
port_dia = 12.0       # 1/4" PTC collet barrel OD (photo-estimated)
port_face = 30.0      # body center to outer collet face, along the flow axis
                      # (60 mm tip to tip)

# --- Wire-exit boss: pigtail root on the rim ---------------------------------
# Photo-estimated: a small stub off the housing rim where the 3-wire pigtail
# leaves, perpendicular to the flow axis. The pigtail itself (a flexible ~15 cm
# lead to a 3-pin JST connector) is not enveloped.
wire_boss_dia = 8.0      # boss diameter (photo-estimated)
wire_boss_len = 3.0      # boss stand-off proud of the rim (photo-estimated)


def inlet():
    """The -X collet face — a 1/4" push-to-connect mouth, taking the tube the
    water arrives on: (position, outward axis). The molded flow arrow runs -X
    to +X, so this is the end the rotor sees first."""
    return (-port_face, 0.0, 0.0), (-1.0, 0.0, 0.0)


def outlet():
    """The +X collet face — the same 1/4" PTC mouth, the water leaving straight
    across the body: (position, outward axis)."""
    return (port_face, 0.0, 0.0), (1.0, 0.0, 0.0)


def wire_exit():
    """The tip of the rim boss the 3-wire pigtail leaves from, perpendicular to
    the flow axis: (position, outward axis). Not a fluid port — it is where the
    JST lead must have room to stand off before it bends."""
    return (0.0, 0.0, body_dia / 2.0 + wire_boss_len), (0.0, 0.0, 1.0)


def build_body_disk():
    """Round rotor housing: Ø body_dia, the body_len depth along Y (the body
    axis the rotor spins about), centered on the origin."""
    return (
        cq.Workplane("XZ")            # sketch plane normal along Y
        .workplane(offset=-body_len / 2.0)
        .circle(body_dia / 2.0)
        .extrude(body_len)
    )


def build_port(sign):
    """Quick-connect collet barrel coaxial on the flow (X) axis, opening
    sign*X, from the body center out to the port_face collet face. Built
    through the body center so it fuses with the disk into one connected port."""
    return (
        cq.Workplane("YZ")            # sketch plane normal along X
        .circle(port_dia / 2.0)
        .extrude(sign * port_face)
    )


def build_wire_boss():
    """Rim stub where the pigtail leaves, projecting +Z off the rim,
    perpendicular to the flow axis."""
    return (
        cq.Workplane("XY")            # sketch plane normal along Z
        .workplane(offset=body_dia / 2.0)
        .circle(wire_boss_dia / 2.0)
        .extrude(wire_boss_len)
    )


_PARTS = [
    ("body", build_body_disk, cq.Color(0.92, 0.92, 0.94)),        # white housing
    ("port-a", lambda: build_port(+1), cq.Color(0.85, 0.87, 0.90)),
    ("port-b", lambda: build_port(-1), cq.Color(0.85, 0.87, 0.90)),
    ("wire-boss", build_wire_boss, cq.Color(0.20, 0.20, 0.22)),
]


def build_assembly():
    a = cq.Assembly(name="digiten-flow-sensor")
    for name, builder, color in _PARTS:
        a.add(builder(), name=name, color=color)
    return a


def build_scene():
    return cq.Compound.makeCompound([builder().val() for _, builder, _ in _PARTS])


def main():
    export_assembly(build_assembly(), str(_here.parent / "digiten-flow-sensor.step"))
    bb = build_scene().BoundingBox()
    print("-> digiten-flow-sensor.step")
    print("flow-sensor envelope  X[%.1f, %.1f]  Y[%.1f, %.1f]  Z[%.1f, %.1f]   (inline, ports ±X)"
          % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))

    md_vars = {
        "FLOW_BODY_DIA": f"{body_dia:.4g}",
        "BODY_LEN": f"{body_len:.4g}",
        "FLOW_PORT_DIA": f"{port_dia:.4g}",
        "PORT_FACE": f"{port_face:.4g}",
        "WIRE_BOSS_DIA": f"{wire_boss_dia:.4g}",
        "WIRE_BOSS_LEN": f"{wire_boss_len:.4g}",
    }
    substitute_md(
        _here.parent / "README.md",
        variables=md_vars,
        expected_counts={
            "FLOW_BODY_DIA": 2, "BODY_LEN": 2,
            "FLOW_PORT_DIA": 1, "PORT_FACE": 3,
            "WIRE_BOSS_DIA": 1, "WIRE_BOSS_LEN": 1,
        },
    )
    print("-> README.md")
    substitute_py_comments(
        Path(__file__),
        variables={k: f"{v} mm" for k, v in md_vars.items()},
        expected_counts={
            "FLOW_BODY_DIA": 1, "BODY_LEN": 2,
            "FLOW_PORT_DIA": 1, "PORT_FACE": 2,
            "WIRE_BOSS_DIA": 1, "WIRE_BOSS_LEN": 1,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
