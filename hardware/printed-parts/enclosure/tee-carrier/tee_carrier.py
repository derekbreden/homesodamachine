"""The tee carrier: one plate that carries Y-C, Y-D, Y-F and Y-G across the front column,
flank face to flank face. At each end it is a column, from the outer tee's trough edge out
through the flank, that stands from the opening's floor to its roof and reaches fore to a slip
short of the tee wall's aft face with every collet pressed home.

The four bare tees are tied into its troughs on the bench; the plate enters through the -X
flank `staged_dy` aft of its seat, where every branch nose passes the tee wall's aft face, and
slides fore until each branch stands in its journal.

The opening is one cutter: the tees' sweep across the column at their height, the +X column's
crossing at the staged plate, and a window through each flank from the tees' floor to the root
of the fore valve tray's corbel. Front-top and front-bottom cut it (`opening`).

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
    roof_z: float
    backing: float = 3.0
    air: float = fits.running

    @classmethod
    def on(cls, plate, *, exterior_x, flank_x, tie_slot, strap_t, roof_z):
        """The carrier on a collet plate's four tee stations, at its assembly state."""
        state = plate["carrier_states"][plate["assembly_state"]]
        return cls(
            tee_xs=tuple(sorted(x for x, _z in plate["holes"])),
            axis_y=plate["aft_y"] + tee.BRANCH_PRESSED_REACH + state["offset_y"],
            axis_z=plate["holes"][0][1],
            wall_aft_y=plate["wall_aft_y"],
            exterior_x=exterior_x, flank_x=flank_x,
            tie_slot=tuple(tie_slot), strap_t=strap_t, roof_z=roof_z)

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
    def floor_z(self):
        """The opening's floor: the tees' extended run span, running air under it."""
        return self.axis_z - tee.RUN_HALF - self.air

    @property
    def tee_top_z(self):
        return self.axis_z + tee.RUN_HALF + self.air

    @property
    def column_x(self):
        """From the outer tee's trough edge out to the flank face."""
        return max(abs(x) for x in self.tee_xs) + self.trough_r, self.exterior_x

    @property
    def column_y(self):
        """Fore to a slip short of the tee wall's aft face at release, back to the plate's back."""
        return self.wall_aft_y + fits.slip + release_travel(), self.plate_y[1]

    @property
    def column_z(self):
        """Running air over the floor; under the roof, which front-top prints facing down over
        support, a supported face's allowance more."""
        return self.floor_z + self.air, self.roof_z - self.air - fits.supported_surface

    @property
    def tie_zs(self):
        """The two tie bands on each tee, round the run roots either side of the branch."""
        band = sum(tee.RUN_ROOT_BAND) / 2.0
        return self.axis_z - band, self.axis_z + band


def opening(c: Carrier):
    """The way in and the slide: the tees' sweep across the column, the +X column's crossing at
    the staged plate, and each flank's window."""
    x0, x1 = -c.exterior_x - 1.0, c.exterior_x + 1.0
    crossing = (c.column_y[0] + c.staged_dy - c.air, c.plate_y[1] + c.staged_dy + c.air)
    cutter = _box(x0, x1, *c.opening_y, c.floor_z, c.tee_top_z).fuse(
        _box(x0, x1, *crossing, c.floor_z, c.roof_z))
    for side in (-1.0, 1.0):
        wx0, wx1 = sorted((side * c.flank_x, side * (c.exterior_x + 1.0)))
        cutter = cutter.fuse(_box(wx0, wx1, *c.opening_y, c.floor_z, c.roof_z))
    return cutter.clean()


def build_plate(c: Carrier):
    """The plate from flank face to flank face, with a trough at each tee, a tie slot at each of
    its edges for each tie band, and a column at each end."""
    (y0, y1), (z0, z1) = c.plate_y, c.plate_z
    body = _box(-c.exterior_x, c.exterior_x, y0, y1, z0, z1)
    sx, sz = c.tie_slot
    for x in c.tee_xs:
        body = body.cut(cq.Solid.makeCylinder(
            c.trough_r, z1 - z0 + 2.0, cq.Vector(x, c.axis_y, z0 - 1.0), cq.Vector(0, 0, 1)))
        for side in (-1.0, 1.0):
            cx = x + side * (c.trough_r - sx / 2.0)
            for tz in c.tie_zs:
                body = body.cut(_box(cx - sx / 2.0, cx + sx / 2.0, y0 - 1.0, y1 + 1.0,
                                     tz - sz / 2.0, tz + sz / 2.0))
    for side in (-1.0, 1.0):
        x0, x1 = sorted(side * x for x in c.column_x)
        body = body.fuse(_box(x0, x1, *c.column_y, *c.column_z))
    return cq.Workplane(obj=body.clean())


def parts(c: Carrier) -> dict:
    return {PLATE: build_plate(c)}


def release_travel():
    """How far fore of connected the plate goes to press every branch collet home: the nose's
    air to the tee wall's release face, and the sleeve's stroke."""
    return tee.CARRIER_AFT_COLLET_GAP + tee.BRANCH_COLLET_TRAVEL


def figures(c: Carrier) -> dict:
    return {
        "PLATE_T": c.plate_t, "PLATE_H": c.plate_h, "BACKING": c.backing,
        "TROUGH_D": 2.0 * c.trough_r, "BARREL_D": 2.0 * tee.BARREL_R,
        "RUN_SPAN_PRESSED": tee.RUN_SPAN_PRESSED, "STAGED_DY": c.staged_dy,
        "COLUMN_H": c.column_z[1] - c.column_z[0],
        "COLUMN_X": c.column_x[1] - c.column_x[0],
        "COLUMN_Y": c.column_y[1] - c.column_y[0],
        "COLUMN_FORE": c.axis_y - c.column_y[0], "SLIP": fits.slip,
        "ROOF_AIR": c.roof_z - c.column_z[1], "SUPPORTED": fits.supported_surface,
        "OPENING_Y": c.opening_y[1] - c.opening_y[0],
        "OPENING_Z": c.roof_z - c.floor_z, "TEE_SWEEP_Z": c.tee_top_z - c.floor_z,
        "AIR": c.air, "STRAP_T": c.strap_t,
        "TIE_SLOT_X": c.tie_slot[0], "TIE_SLOT_Z": c.tie_slot[1],
        "TIE_BAND": sum(tee.RUN_ROOT_BAND) / 2.0,
        "NOSE_GAP": tee.CARRIER_AFT_COLLET_GAP, "COLLET_STROKE": tee.BRANCH_COLLET_TRAVEL,
        "RELEASE_TRAVEL": release_travel(),
        "FORE_ROOM": c.column_y[0] - c.opening_y[0],
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
    if c.tee_top_z > c.roof_z:
        errors.append("the flank pockets' floor stands under the tees' run span")
    if abs(c.plate_y[1] + c.staged_dy - (c.opening_y[1] - c.strap_t - c.air)) > 1e-9:
        errors.append("the staged plate's strapped back does not close the opening")
    if c.column_y[0] - release_travel() < c.opening_y[0] + fits.slip - 1e-9:
        errors.append("the openings stop the columns short of pressing the collets home")
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
    return enclosure.tee_carrier(box.pack)


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
