"""Reference solid for the DIGITEN G3/8" Hall-effect water-flow sensor
(model FL-308 / FL-308ZJ, Amazon B07QQW4C7R) — the inline turbine flow
meter that sits between the rear-panel pass-through ports in the lite
edition (carbonated water spins the rotor; the Hall pulse train triggers
the flavor pumps). A purchased part, not a printed one — the model is a
keep-out envelope for placement and tube routing, not a manufacturing
drawing.

Three pieces sharing one center, reduced to coaxial/cylindrical keep-out:

- Body — the round white turbine housing carrying the rotor and the
  Hall sensor. A disk Ø[36.42 mm](BODY_DIA) across the flow plane, the
  rotor axis through its thickness Z [28.35 mm](BODY_THICK).
- Two quick-connect ports — coaxial along the flow axis Y, one at each
  end, each a Ø[21.95 mm](PORT_DIA) collet barrel reaching out to the
  [60 mm](OVERALL_LEN) tip-to-tip overall length. As sold these are
  3/8" push-to-connect (push a 3/8" OD tube straight in), not exposed
  threads.
- Wire-exit boss — the rim stub (Ø[8 mm](WIRE_BOSS_DIA), [3 mm](WIRE_BOSS_LEN)
  proud) where the 3-wire pigtail (red VCC / black GND / yellow signal)
  leaves the housing.

Coordinate frame (the repo world frame)
---------------------------------------
- Y = flow axis : the through-flow runs along Y; the two ports open at
                  ±Y, their outer collet faces at Y = ±[30 mm](PORT_FACE_Y).
- Z = rotor axis : normal to the flow plane, through the disk thickness;
                   the rotor spins about Z.
- X = lateral   : completes the right-handed frame, in the flow plane.

Origin is the body center. The body disk is centered on it; the two ports
are mirror images along Y; the wire-exit boss leaves toward -X.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))
from _cadq_export import export_assembly
from docgen import substitute_md, substitute_py_comments


# --- Body: round turbine housing (rotor + Hall sensor) -----------------------
# Measured from the manufacturer dimension drawing (Amazon image 4).
body_dia = 36.42      # disk diameter across the flow plane (X-Y)
body_thick = 28.35    # disk thickness along the rotor axis (Z)

# --- Ports: coaxial quick-connect collets along the flow axis ----------------
overall_len = 60.0    # tip-to-tip along Y, collet face to collet face (measured)
port_dia = 21.95      # collet barrel OD (measured)
port_face_y = overall_len / 2.0  # outer collet face, ±Y

# --- Wire-exit boss: pigtail root on the rim ---------------------------------
# Photo-estimated: a small stub off the housing rim where the 3-wire
# pigtail leaves. Size and exact angle are read off product photos, not a
# drawing; the pigtail itself (a flexible 15 cm lead) is not enveloped.
wire_boss_dia = 8.0      # boss diameter (photo-estimated)
wire_boss_len = 3.0      # boss stand-off proud of the rim (photo-estimated)
wire_boss_z = -6.0       # boss center height along the rotor axis (photo-estimated)


def build_body_disk():
    """Round turbine housing: Ø body_dia disk, thickness body_thick centered
    on Z=0, rotor axis along Z."""
    return (
        cq.Workplane("XY")
        .workplane(offset=-body_thick / 2.0)
        .circle(body_dia / 2.0)
        .extrude(body_thick)
    )


def build_port(sign):
    """One quick-connect collet barrel along Y, from the body out to the
    ±port_face_y collet face."""
    return (
        cq.Workplane("XZ")  # sketch plane normal along Y
        .circle(port_dia / 2.0)
        .extrude(sign * port_face_y)
    )


def build_wire_boss():
    """Rim stub where the pigtail leaves, projecting toward -X."""
    return (
        cq.Workplane("YZ")  # sketch plane normal along X
        .workplane(offset=-(body_dia / 2.0))
        .center(0, wire_boss_z)
        .circle(wire_boss_dia / 2.0)
        .extrude(-wire_boss_len)
    )


_PARTS = [
    ("body", build_body_disk, cq.Color(0.92, 0.92, 0.94)),   # white housing
    ("port-plus", lambda: build_port(+1), cq.Color(0.85, 0.87, 0.90)),
    ("port-minus", lambda: build_port(-1), cq.Color(0.85, 0.87, 0.90)),
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
    print("flow-sensor envelope  X[%.1f, %.1f]  Y[%.1f, %.1f]  Z[%.1f, %.1f]   (flow along Y)"
          % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))

    md_vars = {
        "BODY_DIA": f"{body_dia:.4g}",
        "BODY_THICK": f"{body_thick:.4g}",
        "OVERALL_LEN": f"{overall_len:.4g}",
        "PORT_DIA": f"{port_dia:.4g}",
        "PORT_FACE_Y": f"{port_face_y:.4g}",
        "WIRE_BOSS_DIA": f"{wire_boss_dia:.4g}",
        "WIRE_BOSS_LEN": f"{wire_boss_len:.4g}",
    }
    substitute_md(
        _here.parent / "README.md",
        variables=md_vars,
        expected_counts={
            "BODY_DIA": 2, "BODY_THICK": 2, "OVERALL_LEN": 2,
            "PORT_DIA": 1, "PORT_FACE_Y": 1,
            "WIRE_BOSS_DIA": 1, "WIRE_BOSS_LEN": 1,
        },
    )
    print("-> README.md")
    substitute_py_comments(
        Path(__file__),
        variables={k: f"{v} mm" for k, v in md_vars.items()},
        expected_counts={
            "BODY_DIA": 1, "BODY_THICK": 1, "OVERALL_LEN": 1,
            "PORT_DIA": 1, "PORT_FACE_Y": 1,
            "WIRE_BOSS_DIA": 1, "WIRE_BOSS_LEN": 1,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
