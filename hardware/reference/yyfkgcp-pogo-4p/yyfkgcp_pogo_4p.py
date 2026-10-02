"""YYFKGCP 4-pin magnetic pogo connector with ears — the pump cartridge's contact pair
(Amazon B0GCBNTBT8, `ledger/purchases.md` §9). The FEMALE half, four flush gold pads between
two magnets, rides the cartridge in the top clamp's flat back; the MALE half, four spring pins
between two magnets, stands in the bay bulkhead facing it. Sliding the cartridge home mates the
pair, so the pumps connect without a cord.

External envelope only, read off the listing's two drawings. Either half is one moulded body
4.00 deep: a 17.54 x 4.00 stadium NOSE from the mating face to the ear plate, the EAR PLATE
1.00 thick under it, and the stadium again behind the plate. The plate runs past both ends of
the nose as two ears, each a semicircle on the body's own width, holed Ø1.50 on a 20.44
pitch; its front face stands 2.00 under the mating face. Four Ø0.70 solder tails stand 1.50
off the back on the contacts' 2.54 pitch. The magnets lie flush in the nose face on a 13.54
pitch, N at -X as drawn face-on, and are that face's own material here, not drawn apart from
it. The male's pins stand 1.00 above the nose at rest (5.00 ± 0.15 overall) and travel 1.10.

The ears' overall reach is not dimensioned; `EAR_L` is read off the drawing's scale, with the
ear ends' arcs concentric a little inboard of the holes.

    Rating, per contact   12 V, 2 A; 30 mΩ max at working height
    Spring                45 ± 10 gf at the 1.0 mm working height; 10,000 cycles
    Materials             UL94 V-0 housing; C3604 brass plunger and barrel, gold over nickel

Frame: the MATING FACE is the XY plane at Z = 0, facing +Z, and the body hangs -Z. The long
axis is X, contacts and ears on it. Origin at the face's centre — the station either half is
seated on, as `jhyossthi_pogo_dock` seats its pill.

Run:
    tools/cad-venv/bin/python hardware/reference/yyfkgcp-pogo-4p/yyfkgcp_pogo_4p.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_assembly  # noqa: E402
from _materials import C_DOCK, one_body  # noqa: E402

# The nose and the body behind the ear plate: one stadium, the body's whole depth.
BODY_L, BODY_W, BODY_T = 17.54, 4.00, 4.00
# The ear plate: its front face under the mating face, its thickness, and the two holes.
EAR_FACE, EAR_T = 2.00, 1.00
EAR_PITCH, EAR_HOLE_D = 20.44, 1.50
# The plate's overall reach, end to end — read off the drawing, not dimensioned on it.
EAR_L = 23.4
# The four contacts and their solder tails off the back.
PINS, PIN_PITCH = 4, 2.54
TAIL_D, TAIL_L = 0.70, 1.50
# The male's plunger tip, how far it stands proud of the nose at rest, and its whole travel.
PIN_D, PIN_PROUD, STROKE = 0.90, 1.00, 1.10
# The female's flush pad, and the magnets' pitch.
PAD_D = 1.50
MAGNET_PITCH = 13.54


def contact_xs():
    """The four contacts' X stations, -X first."""
    return tuple((i - (PINS - 1) / 2.0) * PIN_PITCH for i in range(PINS))


def ear_xs():
    """The two ear holes' X stations."""
    return (-EAR_PITCH / 2.0, EAR_PITCH / 2.0)


def ear_back():
    """Mating face to the ear plate's back — the face the plate bears on when seated."""
    return EAR_FACE + EAR_T


def reach_back():
    """Mating face to the tails' tips."""
    return BODY_T + TAIL_L


def stadium(length, width, z0, z1):
    """A stadium `length` x `width` overall in the XY plane, standing from `z0` to `z1`."""
    return (cq.Workplane("XY", origin=(0.0, 0.0, z0))
            .slot2D(length, width).extrude(z1 - z0))


def _half():
    body = stadium(BODY_L, BODY_W, -BODY_T, 0.0)
    plate = stadium(EAR_L, BODY_W, -ear_back(), -EAR_FACE)
    for x in ear_xs():
        plate = plate.cut(cq.Workplane("XY", origin=(x, 0.0, -ear_back() - 0.1))
                          .circle(EAR_HOLE_D / 2.0).extrude(EAR_T + 0.2))
    body = body.union(plate)
    for x in contact_xs():
        body = body.union(cq.Workplane("XY", origin=(x, 0.0, -reach_back()))
                          .circle(TAIL_D / 2.0).extrude(TAIL_L))
    return body


def build_female():
    """The pad half: the body, its four pads flush in the nose face."""
    return _half()


def build_male(pin_reach=PIN_PROUD):
    """The pin half: the body with its four plungers standing `pin_reach` above the nose face,
    each a Ø`PIN_D` post under a hemispherical tip. A caller mating the pair across a gap it
    knows asks for that reach instead of the rest position.

    The tip's apex is the reach. Pressed nearer the face than the tip's own radius, the dome's
    centre sinks under the face and the body takes the rest of it."""
    body = _half()
    r = PIN_D / 2.0
    centre = pin_reach - r
    for x in contact_xs():
        if centre > 1e-6:
            body = body.union(cq.Workplane("XY", origin=(x, 0.0, 0.0)).circle(r).extrude(centre))
        body = body.union(cq.Workplane("XY").sphere(r).translate((x, 0.0, centre)))
    return body


def main():
    print("YYFKGCP 4-pin magnetic pogo connector")
    for name, part in (("pogo-4p-female", build_female()), ("pogo-4p-male", build_male())):
        bb = part.val().BoundingBox()
        print(f"  {name}: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
              f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
        out = _here.parent / f"{name}.step"
        export_assembly(one_body(part, name, C_DOCK), str(out))
        print(f"-> {out.name}")
    print(f"  body {BODY_L:g} x {BODY_W:g} x {BODY_T:g}; ears {EAR_L:g} overall, holes "
          f"Ø{EAR_HOLE_D:g} on {EAR_PITCH:g}, plate {EAR_FACE:g}..{ear_back():g} under the face; "
          f"contacts on {PIN_PITCH:g}, pins {PIN_PROUD:g} proud with {STROKE:g} travel")


if __name__ == "__main__":
    main()
