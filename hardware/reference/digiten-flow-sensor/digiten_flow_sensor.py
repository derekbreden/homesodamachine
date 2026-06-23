"""Reference solid for the DIGITEN G1/4" Hall-effect water-flow sensor
(model FL-S402B / FL-S402BZJ, Amazon B07QRXLRTH) — the inline turbine flow
meter that sits between the rear-panel pass-through ports in the lite
edition (carbonated water spins the rotor; the Hall pulse train triggers
the flavor pumps). A purchased part, not a printed one — the model is a
keep-out envelope for placement and tube routing, not a manufacturing
drawing.

A round rotor-chamber body with two quick-connect ports cast onto its rim
at 90° to each other — water enters one port, spins the rotor in the round
chamber, and exits the perpendicular port (an L-shaped flow path, not a
straight through-bore). Reduced to coaxial/cylindrical keep-out:

- Body — the round white rotor housing carrying the rotor and the Hall
  sensor. A disk Ø[34 mm](BODY_DIA) across the chamber plane (X-Y), the
  rotor axis through its thickness Z [13 mm](BODY_THICK).
- Two quick-connect ports — at 90° in the chamber plane, one opening +Y
  (inlet) and one opening +X (outlet), each a Ø[12 mm](PORT_DIA) collet
  barrel whose outer collet face reaches [27 mm](PORT_FACE) from the body
  center along its own axis. As sold these are 1/4" push-to-connect (push a
  1/4" OD tube in past the blue collet ring), not exposed threads — "G1/4"
  is the size class, not a BSP thread.
- Wire-exit boss — the rim stub (Ø[8 mm](WIRE_BOSS_DIA), [3 mm](WIRE_BOSS_LEN)
  proud) where the 3-wire pigtail (red VCC / black GND / yellow signal,
  JST-XH 2.54 3-pin) leaves the housing.

Coordinate frame (the repo world frame)
---------------------------------------
- Z = rotor axis : normal to the chamber plane, through the disk thickness;
                   the rotor spins about Z.
- Y = inlet axis  : the inlet port opens toward +Y, its collet face at
                    Y = +[27 mm](PORT_FACE).
- X = outlet axis : the outlet port opens toward +X at 90° to the inlet,
                    its collet face at X = +[27 mm](PORT_FACE).

Origin is the body center. The disk is centered on it; the two ports run out
along +Y and +X; the wire-exit boss leaves toward -X-and-up off the rim.
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
# Photo-estimated against the 1/4" PTC collet barrel; no manufacturer
# dimension drawing is published for this part.
body_dia = 34.0       # rotor-chamber disk diameter across the chamber plane (X-Y)
body_thick = 13.0     # disk thickness along the rotor axis (Z)

# --- Ports: two quick-connect collets at 90° in the chamber plane ------------
port_dia = 12.0       # 1/4" PTC collet barrel OD (photo-estimated)
port_face = 27.0      # body center to outer collet face, along each port axis

# --- Wire-exit boss: pigtail root on the rim ---------------------------------
# Photo-estimated: a small stub off the housing rim where the 3-wire pigtail
# leaves. Size and exact angle are read off product photos, not a drawing;
# the pigtail itself (a flexible 15 cm lead) is not enveloped.
wire_boss_dia = 8.0      # boss diameter (photo-estimated)
wire_boss_len = 3.0      # boss stand-off proud of the rim (photo-estimated)
wire_boss_z = 0.0        # boss center height along the rotor axis (photo-estimated)


def build_body_disk():
    """Round rotor housing: Ø body_dia disk, thickness body_thick centered on
    Z=0, rotor axis along Z."""
    return (
        cq.Workplane("XY")
        .workplane(offset=-body_thick / 2.0)
        .circle(body_dia / 2.0)
        .extrude(body_thick)
    )


def build_inlet_port():
    """Quick-connect collet barrel opening +Y, from the body out to the
    port_face collet face."""
    return (
        cq.Workplane("XZ")  # sketch plane normal along Y
        .circle(port_dia / 2.0)
        .extrude(port_face)
    )


def build_outlet_port():
    """Quick-connect collet barrel opening +X (90° from the inlet), from the
    body out to the port_face collet face."""
    return (
        cq.Workplane("YZ")  # sketch plane normal along X
        .circle(port_dia / 2.0)
        .extrude(port_face)
    )


def build_wire_boss():
    """Rim stub where the pigtail leaves, projecting toward -X off the rim."""
    return (
        cq.Workplane("YZ")  # sketch plane normal along X
        .workplane(offset=-(body_dia / 2.0))
        .center(0, wire_boss_z)
        .circle(wire_boss_dia / 2.0)
        .extrude(-wire_boss_len)
    )


_PARTS = [
    ("body", build_body_disk, cq.Color(0.92, 0.92, 0.94)),   # white housing
    ("port-inlet", build_inlet_port, cq.Color(0.85, 0.87, 0.90)),
    ("port-outlet", build_outlet_port, cq.Color(0.85, 0.87, 0.90)),
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
    print("flow-sensor envelope  X[%.1f, %.1f]  Y[%.1f, %.1f]  Z[%.1f, %.1f]   (inlet +Y, outlet +X)"
          % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))

    md_vars = {
        "BODY_DIA": f"{body_dia:.4g}",
        "BODY_THICK": f"{body_thick:.4g}",
        "PORT_DIA": f"{port_dia:.4g}",
        "PORT_FACE": f"{port_face:.4g}",
        "WIRE_BOSS_DIA": f"{wire_boss_dia:.4g}",
        "WIRE_BOSS_LEN": f"{wire_boss_len:.4g}",
    }
    substitute_md(
        _here.parent / "README.md",
        variables=md_vars,
        expected_counts={
            "BODY_DIA": 2, "BODY_THICK": 2,
            "PORT_DIA": 1, "PORT_FACE": 3,
            "WIRE_BOSS_DIA": 1, "WIRE_BOSS_LEN": 1,
        },
    )
    print("-> README.md")
    substitute_py_comments(
        Path(__file__),
        variables={k: f"{v} mm" for k, v in md_vars.items()},
        expected_counts={
            "BODY_DIA": 1, "BODY_THICK": 1,
            "PORT_DIA": 1, "PORT_FACE": 3,
            "WIRE_BOSS_DIA": 1, "WIRE_BOSS_LEN": 1,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
