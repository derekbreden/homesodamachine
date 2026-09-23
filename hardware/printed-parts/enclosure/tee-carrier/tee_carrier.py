"""The tee carrier: one plate that carries Y-C, Y-D, Y-F and Y-G across the front column,
flank face to flank face. At each end it is a column, from the outer tee's trough edge out
through the flank, that stands from the opening's floor to its roof and reaches fore to a slip
short of the tee wall's aft face with every collet pressed home.

The four bare tees are tied into its troughs on the bench; the plate enters through the -X
flank `staged_dy` aft of its seat, where every branch nose passes the tee wall's aft face, and
slides fore until each branch stands in its journal.

Four return springs, two in each column, stand in blind bores in the column's fore face and bear
on the tee wall's aft face, one over the other either side of the tees' run axis.

Each column's end face is flush with its flank and is show face: all four of its edges roll over
on the enclosure's R6 shoulder, and the exporter strikes the enclosure's flute field on it.

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
SPRINGS = "tee-carrier-spring"

# The return springs: uxcell 304 stainless, 0.8 mm wire. Derek measured the delivered set at
# 6 mm OD, 27 mm free and about 7 mm solid (2026-09-20).
SPRING_OD = 6.0
SPRING_FREE = 27.0
SPRING_SOLID = 7.0
SPRING_WIRE = 0.8


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
    show_edge_r: float = 6.0
    backing: float = 3.0
    air: float = fits.running

    @classmethod
    def on(cls, plate, *, exterior_x, flank_x, tie_slot, strap_t, roof_z, show_edge_r):
        """The carrier on a collet plate's four tee stations, at its assembly state."""
        state = plate["carrier_states"][plate["assembly_state"]]
        return cls(
            tee_xs=tuple(sorted(x for x, _z in plate["holes"])),
            axis_y=plate["aft_y"] + tee.BRANCH_PRESSED_REACH + state["offset_y"],
            axis_z=plate["holes"][0][1],
            wall_aft_y=plate["wall_aft_y"],
            exterior_x=exterior_x, flank_x=flank_x,
            tie_slot=tuple(tie_slot), strap_t=strap_t, roof_z=roof_z, show_edge_r=show_edge_r)

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
    def spring_x(self):
        """The middle of the column's width that stays square at its fore face, inboard of the
        end face's shoulder."""
        return (self.column_x[0] + self.exterior_x - self.show_edge_r) / 2.0

    @property
    def spring_bore_r(self):
        return SPRING_OD / 2.0 + self.air

    @property
    def spring_zs(self):
        """Either side of the tees' run axis, as far apart as a backing's floor under the lower
        bore allows."""
        d = self.axis_z - self.column_z[0] - self.backing - self.spring_bore_r
        return self.axis_z - d, self.axis_z + d

    @property
    def spring_bore_y(self):
        """From the column's fore face to a backing short of the plate's back."""
        return self.column_y[0], self.plate_y[1] - self.backing

    def spring_length(self, offset_y=0.0):
        """Tee wall's aft face to the bore's floor, with the carrier `offset_y` aft of connected."""
        return self.spring_bore_y[1] + offset_y - self.wall_aft_y

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
    by0, by1 = c.spring_bore_y
    for side in (-1.0, 1.0):
        for z in c.spring_zs:
            body = body.cut(cq.Solid.makeCylinder(
                c.spring_bore_r, by1 - by0 + 1.0, cq.Vector(side * c.spring_x, by0 - 1.0, z),
                cq.Vector(0, 1, 0)))
    body = body.clean()
    return cq.Workplane(obj=body.fillet(c.show_edge_r, _shoulder_edges(c, body)).clean())


def _shoulder_edges(c: Carrier, body):
    """All four edges of each end face."""
    out = [edge for edge in body.Edges()
           if abs(abs(edge.startPoint().x) - c.exterior_x) < 1e-6
           and abs(abs(edge.endPoint().x) - c.exterior_x) < 1e-6]
    if len(out) != 8:
        raise ValueError(f"expected the two end faces' four edges each, found {len(out)}")
    return out


def _spring(length):
    """A spring `length` long on +Z from the origin: as many coils as its solid length holds of
    wire, both ends ground flat on their faces."""
    r = (SPRING_OD - SPRING_WIRE) / 2.0
    helix = cq.Wire.makeHelix(length / (SPRING_SOLID / SPRING_WIRE), length, r)
    profile = cq.Wire.makeCircle(SPRING_WIRE / 2.0, helix.startPoint(), helix.tangentAt(0))
    coil = cq.Solid.sweep(profile, [], helix, isFrenet=True)
    return coil.intersect(_box(-SPRING_OD, SPRING_OD, -SPRING_OD, SPRING_OD, 0.0, length))


def spring_stations(c: Carrier) -> dict:
    """Each spring's axis where it meets the tee wall's aft face."""
    return {f"{SPRINGS}-{side}-{level}": (sx * c.spring_x, c.wall_aft_y, z)
            for side, sx in (("west", -1.0), ("east", 1.0))
            for level, z in zip(("lower", "upper"), c.spring_zs)}


def springs(c: Carrier) -> dict:
    """The four springs at connected, from the tee wall's aft face to their bores' floors."""
    spring = _spring(c.spring_length()).rotate((0, 0, 0), (1, 0, 0), -90.0)
    return {name: spring.translate(station) for name, station in spring_stations(c).items()}


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
        "SPRING_OD": SPRING_OD, "SPRING_FREE": SPRING_FREE, "SPRING_SOLID": SPRING_SOLID,
        "SPRING_WIRE": SPRING_WIRE, "SPRING_BORE_D": 2.0 * c.spring_bore_r,
        "SPRING_BORE_DEPTH": c.spring_bore_y[1] - c.spring_bore_y[0],
        "SPRING_SPREAD": c.spring_zs[1] - c.spring_zs[0],
        "SPRING_CONNECTED": c.spring_length(),
        "SPRING_RELEASE": c.spring_length(-release_travel()),
        "SPRING_CONNECTED_COMPRESSION": SPRING_FREE - c.spring_length(),
        "SPRING_RELEASE_COMPRESSION": SPRING_FREE - c.spring_length(-release_travel()),
        "SPRING_SIDE_WALL": c.spring_x - c.spring_bore_r - c.column_x[0],
        "FLANK_T": c.exterior_x - c.flank_x, "SHOW_EDGE_R": c.show_edge_r,
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
    if not SPRING_SOLID < c.spring_length(-release_travel()) < c.spring_length() < SPRING_FREE:
        errors.append("a spring is solid at release or slack at connected")
    if c.spring_x + c.spring_bore_r > c.exterior_x - c.show_edge_r - 1e-9:
        errors.append("a spring bore opens into the end face's fore shoulder")
    for name, spring in springs(c).items():
        if not spring.isValid():
            errors.append(f"{name} is not a valid solid")
    if c.column_y[0] - release_travel() < c.opening_y[0] + fits.slip - 1e-9:
        errors.append("the openings stop the columns short of pressing the collets home")
    for error in errors:
        print("FAIL", error)
    if not errors:
        print(f"ok tee carrier: {c.plate_t:g} mm plate, {c.plate_h:g} mm tall, "
              f"{c.staged_dy:.3f} mm slide from the staged pass to the seat")
    return int(bool(errors))


def _enclosure_box():
    sys.path.insert(0, str(_hw / "printed-parts" / "enclosure" / "enclosure"))
    import enclosure
    import _box_spec
    box, _bounds = _box_spec.read(enclosure.Box, enclosure.Bound,
                                  (enclosure.Pack, enclosure.PortField, enclosure.Nameplate))
    return enclosure, box


def _spec():
    """The carrier on the committed box, the way front-top cut its flanks."""
    enclosure, box = _enclosure_box()
    return enclosure.tee_carrier(box.pack)


def main():
    from _cadq_export import export_assembly
    from _materials import M_PETGF_BLACK, one_body
    from flute_payload import cut
    sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
                           / "tools"))
    from docgen import substitute_md

    import trimesh
    enclosure, box = _enclosure_box()
    c = enclosure.tee_carrier(box.pack)
    if selftest(c):
        return 1
    for name, part in parts(c).items():
        step, stl = _here.parent / f"{name}.step", _here.parent / f"{name}.stl"
        # THE END FACES ARE STRUCK ON THE ENCLOSURE'S OWN FIELD, at the connected pose the
        # plate is built at, so their grooves register with the flanks' round them.
        mesh = enclosure._flute_skin.flute(
            enclosure._piece_mesh(part.val()), enclosure.flute_rails(box)[:1],
            enclosure.flute_pitch(box.outer), enclosure.flute_depth, enclosure.flute_rise)
        mesh.export(str(stl))
        printed = trimesh.load_mesh(str(stl))
        if not printed.is_watertight or enclosure._flute_skin.non_manifold_edges(printed):
            raise ValueError(f"{name}'s fluted print is not a closed manifold mesh")
        export_assembly(one_body(part, name, M_PETGF_BLACK), str(step))
        cut(step, stl)
        print(f"-> {name}.step / .stl")
    substitute_md(_here.parent / "README.md",
                  {key: f"{value:.6g} mm" for key, value in figures(c).items()})
    return 0


if __name__ == "__main__":
    if sys.argv[1:] == ["selftest"]:
        sys.exit(selftest(_spec()))
    sys.exit(main())
