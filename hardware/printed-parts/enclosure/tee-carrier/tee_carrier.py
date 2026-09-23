"""The tee carrier: a plate that carries Y-C, Y-D, Y-F and Y-G across the front column, and the
grip that closes on its far end.

`enclosure-tee-carrier-plate` is the plate and its handle. The four bare tees are tied into its
troughs on the bench; the plate enters through the -X flank `staged_dy` aft of its seat, where
every branch nose passes the tee wall's aft face, and slides fore until each branch stands in
its journal. `enclosure-tee-carrier-grip` is a handle alone: it goes on over the plate's end
in the +X flank and fills the slide room behind it. Its socket is the plate's section, line to
line.

Both flanks carry one opening, the same box: the tee wall's aft face to the staged plate's
strapped back, and the plate's height with the grip's walls round it. Front-top and
front-bottom cut it straight across the column (`opening`).

+X across the enclosure, +Y aft, +Z up, in the assembly frame, at the tees' connected state.

Run:
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-carrier/tee_carrier.py
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-carrier/tee_carrier.py selftest
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts", _hw / "printed-parts" / "cadlib",
           _hw / "reference" / "tee-connector"):
    sys.path.insert(0, str(_p))
import fits                                                  # noqa: E402
import tee_connector as tee                                  # noqa: E402

PLATE = "enclosure-tee-carrier-plate"
GRIP = "enclosure-tee-carrier-grip"


def _box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


@dataclass(frozen=True)
class Carrier:
    tee_xs: tuple
    axis_y: float
    axis_z: float
    wall_aft_y: float
    exterior_x: float
    flank_x: float
    tie_slot: tuple
    strap_t: float
    backing: float = 3.0
    grip_wall: float = 3.0
    air: float = fits.running

    @classmethod
    def on(cls, plate, *, exterior_x, flank_x, tie_slot, strap_t):
        """The carrier on a collet plate's four tee stations, at its assembly state."""
        state = plate["carrier_states"][plate["assembly_state"]]
        return cls(
            tee_xs=tuple(sorted(x for x, _z in plate["holes"])),
            axis_y=plate["aft_y"] + tee.BRANCH_PRESSED_REACH + state["offset_y"],
            axis_z=plate["holes"][0][1],
            wall_aft_y=plate["wall_aft_y"],
            exterior_x=exterior_x, flank_x=flank_x,
            tie_slot=tuple(tie_slot), strap_t=strap_t)

    @property
    def trough_r(self):
        return tee.BARREL_R + self.air

    @property
    def plate_t(self):
        return self.trough_r + self.backing

    @property
    def plate_h(self):
        return tee.RUN_SPAN_PRESSED

    @property
    def plate_y(self):
        return self.axis_y, self.axis_y + self.plate_t

    @property
    def plate_z(self):
        return self.axis_z - self.plate_h / 2.0, self.axis_z + self.plate_h / 2.0

    @property
    def staged_dy(self):
        """How far aft of its seat the carrier crosses the column: each branch nose one running
        air behind the tee wall's aft face."""
        return self.wall_aft_y + tee.BRANCH_REACH + self.air - self.axis_y

    @property
    def opening_y(self):
        return self.wall_aft_y, self.plate_y[1] + self.staged_dy + self.strap_t + self.air

    @property
    def opening_z(self):
        reach = self.plate_h / 2.0 + self.grip_wall + self.air
        return self.axis_z - reach, self.axis_z + reach

    @property
    def tie_zs(self):
        """The two tie bands on each tee, round the run roots either side of the branch."""
        band = sum(tee.RUN_ROOT_BAND) / 2.0
        return self.axis_z - band, self.axis_z + band


def opening(c: Carrier):
    """The way in and the slide, straight through both flanks and everything between."""
    return _box(-c.exterior_x - 1.0, c.exterior_x + 1.0, *c.opening_y, *c.opening_z)


def _handle_section(c: Carrier):
    (y0, y1), (z0, z1) = c.opening_y, c.opening_z
    return y0 + c.air, y1 - c.air, z0 + c.air, z1 - c.air


def build_plate(c: Carrier):
    """The plate from flank face to flank face, a trough and four tie slots at each tee, and the
    handle filling the -X opening fore of the slide room."""
    (y0, y1), (z0, z1) = c.plate_y, c.plate_z
    body = _box(-c.exterior_x, c.exterior_x, y0, y1, z0, z1)
    sx, sz = c.tie_slot
    for x in c.tee_xs:
        body = body.cut(cq.Solid.makeCylinder(
            c.trough_r, z1 - z0 + 2.0, cq.Vector(x, c.axis_y, z0 - 1.0), cq.Vector(0, 0, 1)))
        for side in (-1.0, 1.0):
            cx = x + side * (c.trough_r + c.backing + sx / 2.0)
            for tz in c.tie_zs:
                body = body.cut(_box(cx - sx / 2.0, cx + sx / 2.0, y0 - 1.0, y1 + 1.0,
                                     tz - sz / 2.0, tz + sz / 2.0))
    hy0, _hy1, hz0, hz1 = _handle_section(c)
    body = body.fuse(_box(-c.exterior_x, -c.flank_x, hy0, y1, hz0, hz1))
    return cq.Workplane(obj=body.clean())


def build_grip(c: Carrier):
    """The +X handle: the whole opening less its air, with the plate's section through it."""
    hy0, hy1, hz0, hz1 = _handle_section(c)
    (y0, y1), (z0, z1) = c.plate_y, c.plate_z
    body = _box(c.flank_x, c.exterior_x, hy0, hy1, hz0, hz1).cut(
        _box(c.flank_x - 1.0, c.exterior_x + 1.0, y0, y1, z0, z1))
    return cq.Workplane(obj=body.clean())


def parts(c: Carrier) -> dict:
    return {PLATE: build_plate(c), GRIP: build_grip(c)}


def figures(c: Carrier) -> dict:
    hy0, hy1, hz0, hz1 = _handle_section(c)
    return {
        "PLATE_T": c.plate_t, "PLATE_H": c.plate_h, "BACKING": c.backing,
        "TROUGH_D": 2.0 * c.trough_r, "BARREL_D": 2.0 * tee.BARREL_R,
        "RUN_SPAN_PRESSED": tee.RUN_SPAN_PRESSED, "STAGED_DY": c.staged_dy,
        "OPENING_Y": c.opening_y[1] - c.opening_y[0],
        "OPENING_Z": c.opening_z[1] - c.opening_z[0],
        "GRIP_WALL": c.grip_wall, "AIR": c.air, "STRAP_T": c.strap_t,
        "TIE_SLOT_X": c.tie_slot[0], "TIE_SLOT_Z": c.tie_slot[1],
        "TIE_BAND": sum(tee.RUN_ROOT_BAND) / 2.0,
        "HANDLE_FORE": c.axis_y - hy0,
        "SLIDE_ROOM": hy1 - c.plate_y[1],
        "FLANK_T": c.exterior_x - c.flank_x,
        "LENGTH": 2.0 * c.exterior_x,
    }


def selftest(c: Carrier) -> int:
    errors = []
    for name, part in parts(c).items():
        solid = part.val()
        if not solid.isValid() or len(solid.Solids()) != 1:
            errors.append(f"{name} is not one valid solid")
        bb = solid.BoundingBox()
        if max(-bb.xmin, bb.xmax) > c.exterior_x + 1e-6:
            errors.append(f"{name} stands past the enclosure's X extremity")
    if c.axis_z + tee.RUN_HALF + c.air > c.opening_z[1] + 1e-9:
        errors.append("an extended run collet does not pass the opening")
    if abs(c.plate_y[1] + c.staged_dy - (c.opening_y[1] - c.strap_t - c.air)) > 1e-9:
        errors.append("the staged plate's strapped back does not close the opening")
    hy0, hy1, _hz0, _hz1 = _handle_section(c)
    if min(c.axis_y - hy0, hy1 - c.plate_y[1], c.grip_wall) < 3.0 - 1e-9:
        errors.append("a grip wall is under 3 mm")
    for error in errors:
        print("FAIL", error)
    if not errors:
        print(f"ok tee carrier: {c.plate_t:g} mm plate, {c.plate_h:g} mm tall, "
              f"{c.staged_dy:.3f} mm slide from the staged pass to the seat")
    return int(bool(errors))


def _spec():
    """The carrier on the committed box, the way front-top cut its flanks."""
    sys.path.insert(0, str(_hw / "printed-parts" / "enclosure" / "enclosure"))
    import enclosure
    import _box_spec
    box, _bounds = _box_spec.read(enclosure.Box, enclosure.Bound,
                                  (enclosure.Pack, enclosure.PortField, enclosure.Nameplate))
    return enclosure.tee_carrier(box.pack.collet_plate)


def main():
    from _cadq_export import export_assembly
    from _materials import M_PETGF_BLACK, one_body
    from flute_payload import cut
    sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
                           / "tools"))
    from docgen import substitute_md

    c = _spec()
    if selftest(c):
        return 1
    for name, part in parts(c).items():
        step = _here.parent / f"{name}.step"
        export_assembly(one_body(part, name, M_PETGF_BLACK), str(step))
        part.val().copy(mesh=False).exportStl(str(step.with_suffix(".stl")),
                                              tolerance=0.005, angularTolerance=0.05,
                                              relative=False)
        cut(step, step.with_suffix(".stl"))
        print(f"-> {name}.step / .stl")
    substitute_md(_here.parent / "README.md",
                  {key: f"{value:.6g} mm" for key, value in figures(c).items()})
    return 0


if __name__ == "__main__":
    if sys.argv[1:] == ["selftest"]:
        sys.exit(selftest(_spec()))
    sys.exit(main())
