"""Manual M5 passage comparison; does not modify the enclosure or send a print."""
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / 'hardware/scripts'), str(ROOT / 'hardware/printed-parts/cadlib')]
import cadquery as cq
from _cadq_export import export_step
from print_mesh import write_print_stl

DIAMETERS = [n / 10 for n in range(48, 57)]
LENGTHS = [12.0, 40.0]
LEAD_IN = 0.6


def coupon(diameter, length):
    # Plain stock, with enough room beside the bore for its permanent top label.
    height = length + LEAD_IN
    body = cq.Workplane('XY').box(20, 14, height, centered=(True, True, False))
    hole = cq.Solid.makeCylinder(diameter / 2, height + 2,
                                 cq.Vector(-3, 0, -1), cq.Vector(0, 0, 1))
    # Exclude the first bed layers' hole-edge bulge from the measured bearing.
    mouth = cq.Solid.makeCone(diameter / 2 + LEAD_IN, diameter / 2, LEAD_IN,
                              cq.Vector(-3, 0, 0), cq.Vector(0, 0, 1))
    text = (cq.Workplane('XY').text(f'{diameter:.1f}', 4, .6, combine=False,
                                  font='Arial', kind='bold')
            .rotate((0, 0, 0), (0, 0, 1), 90).translate((5, 0, height - .6)))
    return body.cut(hole).cut(mouth).cut(text).val().clean()


def main():
    parts = HERE / 'parts'
    parts.mkdir(exist_ok=True)
    rows = []
    for length in LENGTHS:
        for diameter in DIAMETERS:
            name = f'm5-d{round(diameter * 10)}-h{round(length)}'
            solid = coupon(diameter, length)
            step, stl = parts / (name + '.step'), parts / (name + '.stl')
            export_step(solid, str(step))
            mesh = write_print_stl(solid, stl)
            rows.append(dict(name=name, diameter_mm=diameter, bearing_length_mm=length,
                             height_mm=length + LEAD_IN, underside_lead_in_mm=LEAD_IN,
                             bore_axis=[0, 0, 1], bore_center_xy_mm=[-3, 0],
                             bounds_mm=mesh.bounds.tolist(), cad_valid=solid.isValid(),
                             solid_count=len(solid.Solids()), mesh_watertight=bool(mesh.is_watertight),
                             stl=str(stl.relative_to(ROOT)),
                             stl_sha256=hashlib.sha256(stl.read_bytes()).hexdigest(),
                             step_sha256=hashlib.sha256(step.read_bytes()).hexdigest()))
    (HERE / 'geometry.json').write_text(json.dumps(dict(
        scope='Nominal passage comparison for the acquired SVLING M5x50 screws; physical fit is unmeasured.',
        screw_stock='hardware/ledger/inventory.md, Fab fixture: SVLING M5 x 0.8 x 50, B0GHNQFZYR',
        production_bore_mm=5.6, parts=rows), indent=2) + '\n')
    print(f'{len(rows)} labeled native coupons and print meshes written.', flush=True)


if __name__ == '__main__':
    main()
