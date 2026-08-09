"""Supco BPV31 Bullet piercing valve — the appliance's `bpv31`, the sealed loop's one
permanent service port.

A saddle clamp that bands round a copper line and drives a needle through its wall. It
goes on once, at `assembly/refrigerant-loop.md` step 2, and never comes off: it vents the
donor's factory R-600a, carries the argon purge through the whole loop-open period, takes
the vacuum manifold, takes the charge, and is then closed and capped. Every later service
of this machine reaches for this one fitting.

SO THE PART OWNS A CLEARANCE AS WELL AS AN ENVELOPE. Supco's own line is *requires only
2" clearance for installation and operation* — `SERVICE_CLEAR`, measured out of the tube
along the valve's own axis. A valve that fits is not a valve you can turn.

Coordinate frame
----------------
- X = THE TUBE'S OWN AXIS — the line the saddle bands round. The clamp is centred on it.
- Z = THE VALVE'S OWN AXIS, out of the tube: the direction the needle drives, the
  direction the body stands in, and the direction `SERVICE_CLEAR` is measured along.
  **Z = 0 is the tube's axis**, not the underside of anything, so the saddle hangs half
  its own depth below the origin and a placement seats this part on the line it pierces.
- Y carries the 1/4" male SAE flare port, which leaves the body sideways at `PORT_Z`.
  The valve is rolled about the tube to aim it — Supco's *non-positional mounting* — so
  whichever way this points is whichever way the machine turned the part.

Figures
-------
Catalogue envelope, not a manufacturing drawing. `STANDOFF` is the 1-3/4" both Grainger
and Global Industrial list for the valve's height; `CLAMP_L` and `CLAMP_W` are Global
Industrial's 1-1/8" x 7/8" for the saddle. `PORT_REACH` is a 1/4" male flare fitting's
own stand-off with its cap on, not a catalogue figure. The needle, the two clamp screws
and the gasket are inside the envelope and are not drawn.

Run:
    tools/cad-venv/bin/python hardware/reference/supco-bpv31/supco_bpv31.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step  # noqa: E402

# --- catalogue envelope (mm) ----------------------------------------------
STANDOFF = 44.45       # 1-3/4", the valve's whole height off the line it clamps
CLAMP_L = 28.58        # 1-1/8", the saddle along the tube
CLAMP_W = 22.23        # 7/8", the saddle across it
CLAMP_D = 22.23        # and round it — the block is square in section
BODY_D = 15.88         # 5/8", the valve column standing off the saddle
PORT_D = 12.70         # the 1/4" male flare's own hex, across flats
PORT_REACH = 25.40     # the flare port and its cap, off the valve's axis

# --- what the part is for -------------------------------------------------
# Supco: "Requires only 2" clearance for installation and operation." The body spends
# STANDOFF of it and the rest is the allen key and the flare nut.
SERVICE_CLEAR = 50.8
TUBE_ODS = (6.35, 7.94, 9.53)   # 1/4", 5/16", 3/8" — the sizes the adapter sleeves cover
MAX_PSI = 500

# --- what those give ------------------------------------------------------
CLAMP_TOP = CLAMP_D / 2.0              # the saddle's crown, where the column starts
PORT_Z = STANDOFF - PORT_D             # the flare port's axis, one hex down from the crown
# What the clearance leaves once the body has taken its share — the room a hand actually
# works in, above the valve.
WORKING_CLEAR = SERVICE_CLEAR - STANDOFF


def saddle():
    """Where the clamp bands the tube: `(position, the valve's own axis)` in this frame.

    The origin IS the tube's axis, so this is the station a placement seats on — put this
    point on the line the valve pierces and the part is where it belongs."""
    return ((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))


def flare():
    """The 1/4" male SAE flare port's mouth, as `(position, outward axis)`.

    The mouth the charging hose, the vacuum manifold and the argon rig all land on, one
    at a time, over the life of the appliance."""
    return ((0.0, PORT_REACH, PORT_Z), (0.0, 1.0, 0.0))


def stem():
    """The needle screw's crown, as `(position, outward axis)` — the top of the valve, and
    the point `SERVICE_CLEAR` is left above."""
    return ((0.0, 0.0, STANDOFF), (0.0, 0.0, 1.0))


def build():
    """Three solids on one origin: the saddle round the tube, the column standing off it,
    and the flare port off the column's side."""
    clamp = (cq.Workplane("XY")
             .box(CLAMP_L, CLAMP_W, CLAMP_D, centered=(True, True, True)))
    body = cq.Workplane(obj=cq.Solid.makeCylinder(
        BODY_D / 2.0, STANDOFF - CLAMP_TOP,
        cq.Vector(0.0, 0.0, CLAMP_TOP), cq.Vector(0, 0, 1)))
    port = cq.Workplane(obj=cq.Solid.makeCylinder(
        PORT_D / 2.0, PORT_REACH,
        cq.Vector(0.0, 0.0, PORT_Z), cq.Vector(0, 1, 0)))
    return clamp.union(body).union(port).val()


def envelope_hold():
    """Read the frame's three statements back off the solid: the valve stands `STANDOFF`
    off the tube, the saddle is centred ON the tube rather than sitting beside it, and the
    flare port reaches its whole stand-off."""
    bb = build().BoundingBox()
    for what, got, want in (("the valve's height off the tube", bb.zmax, STANDOFF),
                            ("the saddle under the tube", bb.zmin, -CLAMP_D / 2.0),
                            ("the flare port's reach", bb.ymax, PORT_REACH),
                            ("the saddle along the tube", bb.xmax - bb.xmin, CLAMP_L)):
        if abs(got - want) > 1e-6:
            raise ValueError(
                f"{what} reads {got:g} against the {want:g} this module declares — the "
                f"envelope has come off the figures it is built from.")
    if STANDOFF >= SERVICE_CLEAR:
        raise ValueError(
            f"the valve stands {STANDOFF:g} off the tube and Supco asks for "
            f"{SERVICE_CLEAR:g} of clearance — the body would fill the whole of its own "
            f"working room and no key could reach the needle.")


def main():
    envelope_hold()
    part = build()
    bb = part.BoundingBox()
    print("Supco BPV31 Bullet piercing valve — the loop's permanent service port")
    print(f"  X[{bb.xmin:.2f}, {bb.xmax:.2f}]  Y[{bb.ymin:.2f}, {bb.ymax:.2f}]"
          f"  Z[{bb.zmin:.2f}, {bb.zmax:.2f}]   (X = the tube, Z = the valve's own axis)")
    print(f"  saddle {CLAMP_L:g} x {CLAMP_W:g} x {CLAMP_D:g} round the tube; column "
          f"Ø{BODY_D:g} to {STANDOFF:g}")
    print(f"  1/4\" male flare at z {PORT_Z:g}, reaching {PORT_REACH:g} off the axis")
    print(f"  wants {SERVICE_CLEAR:g} along its own axis — {WORKING_CLEAR:g} of it left "
          f"over the valve's crown")
    print(f"  fits Ø" + ", Ø".join(f"{d:g}" for d in TUBE_ODS)
          + f" line, {MAX_PSI:g} PSI max")
    out = _here.parent / "supco-bpv31.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
