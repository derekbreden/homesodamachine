"""Contact-pair print coupon: the cartridge's two contact seats, each cut from its production piece.

The male coupon is front-top's bay bulkhead round the male seat: the mouth, the body, the two
M1.4 insert bores and the lead bore to the bulkhead's aft face, with the root of the fore valve
tray behind it and the root of the ridge wall on the crown. It prints the way front-top does,
building in +Z on its own cut base.

The female coupon is the pump clamp round the female seat: the mouth, the body, the two insert
bores, the lead slot open through the crown and the start of both crown grooves. It prints the way
the clamp does, on its crown.

Each coupon is the production piece built from the declared enclosure box and intersected with
one box round its seat, so a seat that prints well here is the seat the piece carries.

    tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/contact-pair-coupon/contact_pair_coupon.py
"""
import hashlib
import json
import os
from pathlib import Path
import sys

import cadquery as cq
import trimesh

HERE = Path(__file__).resolve().parent
ENC = HERE.parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
sys.path[:0] = [str(ROOT / "hardware/scripts"), str(ENC)]
import enclosure as e  # noqa: E402
import _box_spec  # noqa: E402
import flute_payload  # noqa: E402
from materialize_pump_cartridge import _declared_box  # noqa: E402

# Material kept round each seat, past the mouth's round ends in X and past the lead passage.
SIDE = 6.0
# What each coupon keeps beyond the far end of its seat's features, so every face of the seat
# stands in the coupon's own stock rather than on its cut boundary.
BEYOND = 4.0


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def crops(box):
    """`{name: (piece, (x0, x1, y0, y1, z0, z1), print_up)}` in the machine's frame."""
    plate, trays = box.pack.collet_plate, box.pack.pump_trays
    x, z = e.pump_contact_station(box)
    half = e._pogo.EAR_L / 2.0 + e.fits.slip + SIDE
    fixed, rides = e.bay_back_y(plate), e.pump_cartridge_aft_y(trays, plate)
    axis = e.pump_contact_lead_axis_z(box)
    seat_floor = z - (e._pogo.BODY_W / 2.0 + e.fits.slip) - e.fits.supported_surface
    return {
        # The bulkhead from its bay face to 2 mm past its aft face, from under the lead bore to
        # 1 mm over the crown, where the ridge wall stands.
        "male": ("front-top",
                 (x - half, x + half, fixed - 1.0, plate["wall_aft_y"] + 2.0,
                  axis - e.pogo_lead_r - BEYOND, box.pump_bay[2] + 1.0),
                 e.PIECE_PRINT_UP["front-top"]),
        # The clamp from past the lead slot to past its aft face, from under the seat to over the
        # crown it prints on.
        "female": ("pump-cap",
                   (x - half, x + half,
                    rides - (e._pogo.BODY_T + e.pogo_lead_run) - 3.0, rides + 1.0,
                    seat_floor - BEYOND, e.cap_crown_z(box) + 1.0),
                   e.PIECE_PRINT_UP["pump-cap"]),
    }


def to_bed(solid, up):
    """The coupon turned so the piece's own build direction is +Z, standing on Z = 0."""
    if up < 0:
        solid = solid.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), 180.0)
    bb = solid.BoundingBox()
    return solid.translate((-(bb.xmin + bb.xmax) / 2.0, -(bb.ymin + bb.ymax) / 2.0, -bb.zmin))


def main():
    box, bounds, box_path = _declared_box(_box_spec, e)
    e.BOUNDS[:] = bounds
    e._last_box[0] = box
    pieces = {"front-top": e.build_piece(box, "front", "top").val(),
              "pump-cap": e.build_pump_cap(box).val()}
    report = {"box": str(box_path.relative_to(ROOT)), "coupons": {}}
    for name, (piece, (x0, x1, y0, y1, z0, z1), up) in crops(box).items():
        cut = pieces[piece].intersect(e._ybox(x0, x1, y0, y1, z0, z1))
        if len(cut.Solids()) != 1 or not cut.isValid():
            raise ValueError(f"the {name} coupon is {len(cut.Solids())} solids, valid={cut.isValid()}")
        bed = to_bed(cut, up)
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
        bb = bed.BoundingBox()
        report["coupons"][name] = {
            "piece": f"enclosure-{piece}", "print_up": up,
            "crop_in_machine_frame": [round(v, 3) for v in (x0, x1, y0, y1, z0, z1)],
            "print_size_mm": [round(bb.xlen, 2), round(bb.ylen, 2), round(bb.zlen, 2)],
            "volume_mm3": round(bed.Volume(), 2), "stl_facets": len(written.faces),
            "outputs": {p.name: sha(p) for p in (step, stl, step.with_suffix(".step.mesh"))},
        }
        print(f"{stem}: {bb.xlen:.1f} × {bb.ylen:.1f} × {bb.zlen:.1f} mm, "
              f"{bed.Volume() / 1000.0:.2f} cm³, {len(written.faces)} facets")
    sources = [Path(__file__), box_path, ENC / "enclosure.py",
               ROOT / "hardware/reference/yyfkgcp-pogo-4p/yyfkgcp_pogo_4p.py"]
    report["source_sha256"] = {str(p.resolve().relative_to(ROOT)): sha(p) for p in sources}
    (HERE / "geometry-check.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
