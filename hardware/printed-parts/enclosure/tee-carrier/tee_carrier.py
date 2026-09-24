"""The tee carrier: one plate that carries Y-C, Y-D, Y-F and Y-G across the front column,
flank face to flank face. At each end it is a column, from the outer tee's trough edge out
through the flank, that stands from the opening's floor to its roof and reaches fore to a slip
short of the tee wall's aft face with every collet pressed home.

The four bare tees are tied into its troughs on the bench; the plate enters through the -X
flank `staged_dy` aft of its seat, where every branch nose passes the tee wall's aft face, and
slides fore until each branch stands in its journal.

Four return springs, two in each column, one over the other either side of the tees' run axis.
Each runs from a blind bore in the column's fore face across the gap into a pocket in the tee
wall's aft face (`spring_pockets`, cut by front-top).

Each column's end face is flush with its flank and is show face. All four of its edges and the
column's four edges running inboard to it roll over on the enclosure's R6 shoulder, so each corner
closes as one blend the way the enclosure's front corners do. The end face is smooth.

The opening is one cutter: the tees' sweep across the column at their height, the +X column's
crossing at the staged plate, and a window through each flank from the tees' floor to the root
of the fore valve tray's corbel. Front-top and front-bottom cut it (`opening`).

A window cover closes each window aft of the seated carrier from inside. Front-top carries a post
on each flank's inner face at the window's aft face (`posts`), slotted against the flank over
its top half; the cover's tongue drops into the slot and its slab wraps the post fore and aft.

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
COVER = "enclosure-window-cover"
COVERS = {f"{COVER}-west": -1.0, f"{COVER}-east": 1.0}

# The return springs: uxcell 304 stainless, 0.8 mm wire. Derek measured the delivered set at
# 6 mm OD, 27 mm free and about 7 mm solid (2026-09-20).
SPRING_OD = 6.0
SPRING_FREE = 27.0
SPRING_SOLID = 7.0
SPRING_WIRE = 0.8

# The window covers, in Derek's figures (2026-09-23): a post 6 mm across and 12 mm aft up the
# edge of the window's aft face, slotted 3 mm against the flank over its top half; a 6 mm slab
# reaching 12 mm aft of the post, so the two stand 24 mm aft of the window.
POST_W = 6.0
POST_D = 12.0
SLOT_W = 3.0
COVER_T = 6.0
COVER_AFT = 12.0


def _box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def _xz_prism(y0, y1, pts):
    """The `(x, z)` polygon at `y0`, run aft to `y1`."""
    pts = [cq.Vector(x, y0, z) for x, z in pts]
    face = cq.Face.makeFromWires(cq.Wire.makePolygon(pts + pts[:1]))
    return cq.Solid.extrudeLinear(face, cq.Vector(0, y1 - y0, 0))


def _sided(solid, side):
    """A +X solid, or its mirror on the -X flank."""
    return solid if side > 0 else solid.mirror("YZ")


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
    flank_root_z: float
    show_edge_r: float = 6.0
    spring_connected_length: float = 20.2
    backing: float = 3.0
    air: float = fits.running

    @classmethod
    def on(cls, plate, *, exterior_x, flank_x, tie_slot, strap_t, roof_z, flank_root_z,
           show_edge_r):
        """The carrier on a collet plate's four tee stations, at its assembly state."""
        state = plate["carrier_states"][plate["assembly_state"]]
        return cls(
            tee_xs=tuple(sorted(x for x, _z in plate["holes"])),
            axis_y=plate["aft_y"] + tee.BRANCH_PRESSED_REACH + state["offset_y"],
            axis_z=plate["holes"][0][1],
            wall_aft_y=plate["wall_aft_y"],
            exterior_x=exterior_x, flank_x=flank_x,
            tie_slot=tuple(tie_slot), strap_t=strap_t, roof_z=roof_z, flank_root_z=flank_root_z,
            show_edge_r=show_edge_r)

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
        """A backing of column inboard of the bore; outboard, the round thickens the wall past
        the flat land the fore face keeps before its shoulder."""
        return self.column_x[0] + self.backing + self.spring_bore_r

    @property
    def spring_land(self):
        """The flat fore face between a bore's mouth and the end face's shoulder."""
        return self.exterior_x - self.show_edge_r - self.spring_x - self.spring_bore_r

    @property
    def spring_bore_r(self):
        return SPRING_OD / 2.0 + self.air

    @property
    def spring_zs(self):
        """Either side of the tees' run axis, as far apart as keeps the lower bore's mouth the
        same land clear of the column's rounded bottom edge."""
        d = (self.axis_z - self.column_z[0] - self.show_edge_r - self.spring_land
             - self.spring_bore_r)
        return self.axis_z - d, self.axis_z + d

    @property
    def spring_bore_y(self):
        """From the column's fore face, as deep as keeps a free spring's tip no further fore of the
        staged column than the branch noses: one running air behind the tee wall's aft face."""
        staged_room = self.column_y[0] + self.staged_dy - (self.wall_aft_y + self.air)
        return self.column_y[0], self.column_y[0] + SPRING_FREE - staged_room

    @property
    def spring_pocket_y(self):
        """Into the tee wall's aft face, as deep as leaves the spring its connected length."""
        return self.spring_bore_y[1] - self.spring_connected_length, self.wall_aft_y

    def spring_length(self, offset_y=0.0):
        """Pocket floor to bore floor, with the carrier `offset_y` aft of connected."""
        return self.spring_bore_y[1] + offset_y - self.spring_pocket_y[0]

    @property
    def post_y(self):
        """Aft from the window's aft face."""
        return self.opening_y[1], self.opening_y[1] + POST_D

    @property
    def post_z(self):
        """Up the flank's inner face from where front-top's grown flank face begins to the
        window's roof."""
        return self.flank_root_z, self.roof_z

    @property
    def slot_z(self):
        """The post's top half."""
        return sum(self.post_z) / 2.0, self.post_z[1]

    @property
    def cover_y(self):
        """A slip aft of the seated carrier's back, to past the post's aft face."""
        return self.plate_y[1] + fits.slip, self.post_y[1] + COVER_AFT

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


def _column(c: Carrier, side):
    """One end's column on its own, every edge but its inboard face's rolled over on the R6
    shoulder, so each corner of its end closes as one blend."""
    x0, x1 = sorted(side * x for x in c.column_x)
    column = _box(x0, x1, *c.column_y, *c.column_z)
    inboard = side * c.column_x[0]
    edges = [e for e in column.Edges()
             if not (abs(e.startPoint().x - inboard) < 1e-6 and abs(e.endPoint().x - inboard) < 1e-6)]
    return column.fillet(c.show_edge_r, edges)


def _plate_body(c: Carrier):
    """The plate between the columns, with a trough at each tee and a tie slot at each of its
    edges for each tie band, and a column at each end."""
    (y0, y1), (z0, z1) = c.plate_y, c.plate_z
    body = _box(-c.column_x[0], c.column_x[0], y0, y1, z0, z1)
    sx, sz = c.tie_slot
    for x in c.tee_xs:
        body = body.cut(cq.Solid.makeCylinder(
            c.trough_r, z1 - z0 + 2.0, cq.Vector(x, c.axis_y, z0 - 1.0), cq.Vector(0, 0, 1)))
        for side in (-1.0, 1.0):
            cx = x + side * (c.trough_r - sx / 2.0)
            for tz in c.tie_zs:
                body = body.cut(_box(cx - sx / 2.0, cx + sx / 2.0, y0 - 1.0, y1 + 1.0,
                                     tz - sz / 2.0, tz + sz / 2.0))
    body = body.fuse(_column(c, -1.0), _column(c, 1.0))
    by0, by1 = c.spring_bore_y
    for side in (-1.0, 1.0):
        for z in c.spring_zs:
            body = body.cut(cq.Solid.makeCylinder(
                c.spring_bore_r, by1 - by0 + 1.0, cq.Vector(side * c.spring_x, by0 - 1.0, z),
                cq.Vector(0, 1, 0)))
    return body.clean()


def build_plate(c: Carrier):
    return cq.Workplane(obj=_plate_body(c))


def _post(c: Carrier):
    """The +X post, rooted a millimetre into the flank, its underside a 45° corbel off the flank's
    inner face, less the slot between its top half and the flank."""
    (y0, y1), (z0, z1) = c.post_y, c.post_z
    x_in = c.flank_x - POST_W
    post = _xz_prism(y0, y1, [(c.flank_x + 1.0, z0), (c.flank_x, z0), (x_in, z0 + POST_W),
                              (x_in, z1), (c.flank_x + 1.0, z1)])
    return post.cut(_box(c.flank_x - SLOT_W, c.flank_x, y0 - 1.0, y1 + 1.0,
                         c.slot_z[0], z1 + 1.0))


def posts(c: Carrier) -> tuple:
    """The post on each flank that front-top fuses."""
    post = _post(c)
    return tuple(_sided(post, side) for side in (-1.0, 1.0))


def _cover(c: Carrier):
    """The +X cover: the slab against the flank's inner face, fore of the post from the window's
    floor to its roof and aft of it the post's height, joined over the post's top half by the
    tongue in its slot. It stands on the window's floor, and its face lies on the flank; a slip
    stands between it and the post everywhere else, and across the slot's floor the tongue
    takes the floor's rounded turn too."""
    x0, x1 = c.flank_x - COVER_T, c.flank_x
    (y0, y1), (p0, p1) = c.cover_y, c.post_y
    fore = _box(x0, x1, y0, p0 - fits.slip, c.floor_z, c.roof_z)
    aft = _box(x0, x1, p1 + fits.slip, y1, *c.post_z)
    tongue = _box(c.flank_x - SLOT_W + fits.slip, x1, p0 - fits.slip, p1 + fits.slip,
                  c.slot_z[0] + fits.clearance(at_floor=True), c.slot_z[1])
    return fore.fuse(tongue, aft).clean()


def covers(c: Carrier) -> dict:
    cover = _cover(c)
    return {name: cq.Workplane(obj=_sided(cover, side)) for name, side in COVERS.items()}


def _spring(length):
    """A spring `length` long on +Z from the origin: as many coils as its solid length holds of
    wire, both ends ground flat on their faces."""
    r = (SPRING_OD - SPRING_WIRE) / 2.0
    helix = cq.Wire.makeHelix(length / (SPRING_SOLID / SPRING_WIRE), length, r)
    profile = cq.Wire.makeCircle(SPRING_WIRE / 2.0, helix.startPoint(), helix.tangentAt(0))
    coil = cq.Solid.sweep(profile, [], helix, isFrenet=True)
    return coil.intersect(_box(-SPRING_OD, SPRING_OD, -SPRING_OD, SPRING_OD, 0.0, length))


def spring_stations(c: Carrier) -> dict:
    """Each spring's axis on its pocket's floor."""
    return {f"{SPRINGS}-{side}-{level}": (sx * c.spring_x, c.spring_pocket_y[0], z)
            for side, sx in (("west", -1.0), ("east", 1.0))
            for level, z in zip(("lower", "upper"), c.spring_zs)}


def spring_pockets(c: Carrier) -> tuple:
    """`(x, z, y0, y1, r)` for each pocket front-top cuts: the bore's radius, from the pocket's
    floor out past the tee wall's aft face."""
    y0, y1 = c.spring_pocket_y
    return tuple((x, z, y0, y1 + 1.0, c.spring_bore_r)
                 for x, _y, z in spring_stations(c).values())


def springs(c: Carrier) -> dict:
    """The four springs at connected, from the tee wall's aft face to their bores' floors."""
    spring = _spring(c.spring_length()).rotate((0, 0, 0), (1, 0, 0), -90.0)
    return {name: spring.translate(station) for name, station in spring_stations(c).items()}


def parts(c: Carrier) -> dict:
    return {PLATE: build_plate(c), **covers(c)}


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
        "SPRING_POCKET_DEPTH": c.spring_pocket_y[1] - c.spring_pocket_y[0],
        "SPRING_GAP": c.column_y[0] - c.wall_aft_y,
        "SPRING_STAGED_REACH": SPRING_FREE - (c.spring_bore_y[1] - c.spring_bore_y[0]),
        "SPRING_SPREAD": c.spring_zs[1] - c.spring_zs[0],
        "SPRING_CONNECTED": c.spring_length(),
        "SPRING_RELEASE": c.spring_length(-release_travel()),
        "SPRING_CONNECTED_COMPRESSION": SPRING_FREE - c.spring_length(),
        "SPRING_RELEASE_COMPRESSION": SPRING_FREE - c.spring_length(-release_travel()),
        "SPRING_SIDE_WALL": c.spring_x - c.spring_bore_r - c.column_x[0],
        "SPRING_LAND": c.spring_land,
        "FLANK_T": c.exterior_x - c.flank_x, "SHOW_EDGE_R": c.show_edge_r,
        "POST_W": POST_W, "POST_D": POST_D, "POST_H": c.post_z[1] - c.post_z[0],
        "SLOT_W": SLOT_W, "SLOT_H": c.slot_z[1] - c.slot_z[0],
        "TONGUE_T": SLOT_W - fits.slip, "COVER_T": COVER_T, "COVER_AFT": COVER_AFT,
        "STRUCTURE_AFT": c.cover_y[1] - c.opening_y[1],
        "COVER_FORE": c.post_y[0] - fits.slip - c.cover_y[0],
        "COVER_Y": c.cover_y[1] - c.cover_y[0], "COVER_H": c.roof_z - c.floor_z,
        "TONGUE_AIR": fits.clearance(at_floor=True), "LAYER_TRANSITION": fits.layer_transition,
        "WINDOW_AFT": c.opening_y[1] - c.plate_y[1],
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
    if c.spring_pocket_y[1] - c.spring_pocket_y[0] <= 0.0:
        errors.append("the springs' bores leave no pocket in the tee wall")
    if c.spring_bore_y[1] > c.plate_y[1] - c.backing + 1e-9:
        errors.append("a spring bore leaves less than a backing behind its floor")
    if c.spring_land <= 0.0:
        errors.append("a spring bore opens into the end face's fore shoulder")
    for name, spring in springs(c).items():
        if not spring.isValid():
            errors.append(f"{name} is not a valid solid")
    if c.column_y[0] - release_travel() < c.opening_y[0] + fits.slip - 1e-9:
        errors.append("the openings stop the columns short of pressing the collets home")
    if c.post_z[0] + POST_W > c.slot_z[0] + 1e-9:
        errors.append("the post's corbel reaches into its slot")
    if c.cover_y[0] >= c.post_y[0] - fits.slip:
        errors.append("the cover leaves nothing fore of its post")
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
        mesh = enclosure._piece_mesh(part.val())
        if name == PLATE:
            # The plate meets each rounded column at a tangent edge. Resolve the coincident
            # tessellation there after rounding to the coordinates the STL can store.
            mesh = trimesh.boolean.union([enclosure._flute_skin.as_written(mesh)],
                                         engine="manifold", check_volume=False)
        mesh.export(str(stl))
        printed = trimesh.load_mesh(str(stl))
        if not printed.is_watertight or enclosure._flute_skin.non_manifold_edges(printed):
            raise ValueError(f"{name}'s print is not a closed manifold mesh")
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
