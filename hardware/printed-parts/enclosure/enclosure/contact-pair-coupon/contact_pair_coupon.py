"""Contact-pair print coupon: the cartridge's two contact seats, each cut from its production piece.

The male coupon is front-top's bay bulkhead round the male seat: the mouth, the body, the two
M1.4 insert bores and the lead bore to the bulkhead's aft face, with the root of the fore valve
tray behind it and the root of the ridge wall on the crown. It prints the way front-top does,
building in +Z on its own cut base, and that base stands a whole number of layers above
front-top's bed, so every layer boundary falls where the piece lays it.

The female coupon is the pump clamp round the female seat: the mouth, the body, the two insert
bores, the lead slot open through the crown and the start of both crown grooves. It prints the way
the clamp does, on its crown, which is the clamp's own bed.

Each coupon is the production piece built from the declared enclosure box and intersected with
one box round its seat, so a seat that prints well here is the seat the piece carries. Each one's
machine-to-bed transform and the bed position of every feature a slice review looks for are in
`geometry-check.json`.

    tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/contact-pair-coupon/contact_pair_coupon.py
"""
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import cadquery as cq
import trimesh

HERE = Path(__file__).resolve().parent
ENC = HERE.parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
TOOLS = next(p for p in HERE.parents if (p / "tools" / "docgen").is_dir()) / "tools"
sys.path[:0] = [str(ROOT / "hardware/scripts"), str(ENC), str(TOOLS)]
import enclosure as e  # noqa: E402
import _box_spec  # noqa: E402
import flute_payload  # noqa: E402
from docgen import substitute_md  # noqa: E402
from materialize_pump_cartridge import _declared_box  # noqa: E402

# Material kept round each seat, past the mouth's round ends in X and past the lead passage.
SIDE = 6.0
# What each coupon keeps beyond the far end of its seat's features, so every face of the seat
# stands in the coupon's own stock rather than on its cut boundary.
BEYOND = 4.0
# The production profile's layer above its 0.20 mm first bed layer (`printed-parts/AGENTS.md`).
LAYER = 0.24
# How far each half's mating face may stand off its coupon face and still seat.
FLUSH_TOL = 0.1


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def coupons(box, pieces):
    """`{name: (piece, crop, turn, shift)}`: the crop `(x0, x1, y0, y1, z0, z1)` in the machine's
    frame, then the half turn about X a crown-bedded piece takes and the shift onto the bed."""
    plate, trays = box.pack.collet_plate, box.pack.pump_trays
    x, z = e.pump_contact_station(box)
    half = e._pogo.EAR_L / 2.0 + e.fits.slip + SIDE
    fixed, rides = e.bay_back_y(plate), e.pump_cartridge_aft_y(trays, plate)
    axis = e.pump_contact_lead_axis_z(box)
    seat_floor = z - (e._pogo.BODY_W / 2.0 + e.fits.slip) - e.fits.supported_surface
    crown = e.cap_crown_z(box)
    # Front-top beds on its seam rim; the coupon's base stands whole layers above it.
    bed = round(pieces["front-top"].BoundingBox().zmin, 4)
    floor = bed + math.floor((axis - e.pogo_lead_r - BEYOND - bed) / LAYER) * LAYER
    male_y = (fixed, plate["wall_aft_y"] + 2.0)
    female_y = (rides - (e._pogo.BODY_T + e.pogo_lead_run) - 3.0, rides)
    return {
        "male": ("front-top",
                 (x - half, x + half, fixed - 1.0, male_y[1], floor, box.pump_bay[2] + 1.0),
                 None, (-x, -(male_y[0] + male_y[1]) / 2.0, -floor)),
        # Turned about X, Y and Z change sign: the crown is the coupon's lowest face.
        "female": ("pump-cap",
                   (x - half, x + half, female_y[0], rides + 1.0, seat_floor - BEYOND, crown + 1.0),
                   ((1.0, 0.0, 0.0), 180.0), (-x, (female_y[0] + female_y[1]) / 2.0, crown)),
    }


def placed(point, turn, shift):
    """A machine-frame point carried onto the bed."""
    px, py, pz = point
    if turn is not None:
        py, pz = -py, -pz
    return tuple(round(v + s, 4) for v, s in zip((px, py, pz), shift))


def landmarks(box):
    """The features a slice review locates, each `(coupon, label, machine point)`."""
    plate, trays = box.pack.collet_plate, box.pack.pump_trays
    x, z = e.pump_contact_station(box)
    s, w = e.fits.slip, e._pogo.BODY_W / 2.0 + e.fits.slip
    fixed, rides = e.bay_back_y(plate), e.pump_cartridge_aft_y(trays, plate)
    axis = e.pump_contact_lead_axis_z(box)
    datum = e._pogo.ear_back()
    ear = max(e._pogo.ear_xs())
    apex = axis + e.pogo_lead_r / math.cos(math.radians(e.teardrop_roof_angle))
    groove_w, groove_d = e.pogo_groove
    # The +X groove's centreline, read clear of the slot it leaves: the slot runs deeper.
    fore = rides - (e._pogo.BODY_T + e.pogo_lead_run)
    start = (x + e.pogo_lead_half - groove_w / 2.0, fore + groove_w / 2.0)
    well = next((cx, cy + e.clamp_pump_y_shift) for cx, cy, _cz in trays if cx > x)
    run = math.hypot(well[0] - start[0], well[1] - start[1])
    along = e.pogo_lead_half + groove_w
    groove = (start[0] + (well[0] - start[0]) * along / run,
              start[1] + (well[1] - start[1]) * along / run)
    return [
        ("male", "seat face", (x, fixed, z)),
        ("male", "seat datum, the ear plate's bearing step", (x, fixed + datum, z)),
        ("male", "seat roof, the bridge", (x, fixed + datum / 2.0, z + w + e.fits.supported_surface)),
        ("male", "seat floor", (x, fixed + datum / 2.0, z - w)),
        ("male", "+X insert bore axis at the datum", (x + ear, fixed + datum, z)),
        ("male", "lead bore axis at the body's back", (x, fixed + e._pogo.BODY_T, axis)),
        ("male", "lead bore apex", (x, fixed + e._pogo.BODY_T, apex)),
        ("male", "lead bore exit floor, the tray's crown", (x, plate["wall_aft_y"], e._lead_bore_floor(box))),
        ("male", "bulkhead crown", (x, fixed + e._pogo.BODY_T, box.pump_bay[2])),
        ("female", "seat face", (x, rides, z)),
        ("female", "seat datum, the ear plate's bearing step", (x, rides - datum, z)),
        ("female", "seat roof in the print, the bridge", (x, rides - datum / 2.0,
                                                          z - w - e.fits.supported_surface)),
        ("female", "+X insert bore axis at the datum", (x + ear, rides - datum, z)),
        ("female", "+X crown groove floor, past the slot", (groove[0], groove[1],
                                                            e.cap_crown_z(box) - groove_d)),
        ("female", "crown, the bed", (x, rides - datum, e.cap_crown_z(box))),
    ]


def main():
    box, bounds, box_path = _declared_box(_box_spec, e)
    e.BOUNDS[:] = bounds
    e._last_box[0] = box
    pieces = {"front-top": e.build_piece(box, "front", "top").val(),
              "pump-cap": e.build_pump_cap(box).val()}
    report = {"box": str(box_path.relative_to(ROOT)), "layer": LAYER, "coupons": {}}
    plan = coupons(box, pieces)
    for name, (piece, (x0, x1, y0, y1, z0, z1), turn, shift) in plan.items():
        cut = pieces[piece].intersect(e._ybox(x0, x1, y0, y1, z0, z1))
        if len(cut.Solids()) != 1 or not cut.isValid():
            raise ValueError(f"the {name} coupon is {len(cut.Solids())} solids, valid={cut.isValid()}")
        bed = cut if turn is None else cut.rotate((0.0, 0.0, 0.0), *turn)
        bed = bed.translate(shift)
        bb = bed.BoundingBox()
        if abs(bb.zmin) > 1e-3:
            raise ValueError(f"the {name} coupon stands {bb.zmin:.4f} mm off the bed")
        stem = f"contact-pair-{name}-coupon"
        step, stl = HERE / f"{stem}.step", HERE / f"{stem}.stl"
        os.environ["HSM_SKIP_MESH_PAYLOAD"] = "1"
        e.export_assembly(e.one_body(cq.Workplane(obj=bed), stem, e.PIECE_COLORS[piece]), str(step))
        os.environ.pop("HSM_SKIP_MESH_PAYLOAD", None)
        mesh = e._piece_mesh(bed)
        mesh.export(str(stl))
        written = trimesh.load_mesh(str(stl))
        if not written.is_watertight or e._flute_skin.non_manifold_edges(written):
            raise ValueError(f"{stl.name} is not one closed mesh a slicer takes")
        flute_payload.cut(step, stl)
        report["coupons"][name] = {
            "piece": f"enclosure-{piece}", "print_up": e.PIECE_PRINT_UP[piece],
            "crop_in_machine_frame": [round(v, 4) for v in (x0, x1, y0, y1, z0, z1)],
            "machine_to_bed": {
                "turn": None if turn is None else {"axis": list(turn[0]), "degrees": turn[1]},
                "then_shift": [round(v, 4) for v in shift],
            },
            "print_size_mm": [round(bb.xlen, 3), round(bb.ylen, 3), round(bb.zlen, 3)],
            "volume_mm3": round(bed.Volume(), 2), "stl_facets": len(written.faces),
            "outputs": {p.name: sha(p) for p in (step, stl, step.with_suffix(".step.mesh"))},
            "landmarks": [],
        }
        print(f"{stem}: {bb.xlen:.2f} × {bb.ylen:.2f} × {bb.zlen:.2f} mm, "
              f"{bed.Volume() / 1000.0:.2f} cm³, {len(written.faces)} facets")
    for name, label, point in landmarks(box):
        _piece, _crop, turn, shift = plan[name]
        report["coupons"][name]["landmarks"].append(
            {"feature": label, "machine": [round(v, 4) for v in point],
             "bed": list(placed(point, turn, shift))})
    male_floor = plan["male"][1][4]
    front_bed = round(pieces["front-top"].BoundingBox().zmin, 4)
    report["coupons"]["male"]["bed_layers_above_front_top_bed"] = round(
        (male_floor - front_bed) / LAYER)
    sources = [Path(__file__), box_path, ENC / "enclosure.py",
               ROOT / "hardware/reference/yyfkgcp-pogo-4p/yyfkgcp_pogo_4p.py"]
    report["source_sha256"] = {str(p.resolve().relative_to(ROOT)): sha(p) for p in sources}
    (HERE / "geometry-check.json").write_text(json.dumps(report, indent=2) + "\n")

    plate, trays = box.pack.collet_plate, box.pack.pump_trays
    kiss = e.bay_back_y(plate) - e.pump_cartridge_aft_y(trays, plate)
    press = e._pogo.PIN_PROUD - kiss
    sizes = {n: report["coupons"][n]["print_size_mm"] for n in ("male", "female")}
    substitute_md(HERE / "README.md", {
        "COUPON_MALE_SIZE": " × ".join(f"{v:.1f}" for v in sizes["male"]) + " mm",
        "COUPON_FEMALE_SIZE": " × ".join(f"{v:.1f}" for v in sizes["female"]) + " mm",
        "COUPON_LAYER": f"{LAYER:g} mm",
        "COUPON_BED_LAYERS": f"{report['coupons']['male']['bed_layers_above_front_top_bed']}",
        "COUPON_FLUSH_TOL": f"±{FLUSH_TOL:g} mm",
        "COUPON_KISS": f"{kiss:.4g} mm",
        "COUPON_PRESS": f"{press:.4g} mm",
        "COUPON_STROKE": f"{e._pogo.STROKE:g} mm",
        "COUPON_PRESS_RANGE": f"{press - 2.0 * FLUSH_TOL:.3g}–{press + 2.0 * FLUSH_TOL:.3g} mm",
        "COUPON_KISS_MIN": f"{kiss - 2.0 * FLUSH_TOL:.3g} mm",
        "COUPON_FULL_PRESS": f"{e._pogo.PIN_PROUD:g} mm",
    })


if __name__ == "__main__":
    main()
