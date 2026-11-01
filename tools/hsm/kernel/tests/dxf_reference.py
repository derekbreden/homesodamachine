"""A laser outline drawn as a DXF, `fixtures/outline.dxf`, and what CadQuery's `importDXF` reads
from it, written to `dxf_reference.json` beside this file: the face's area, its outer wire's
length, its bounds and the volume of the plate extruded from it. The outline is a plate's — a
large arc closed by small corner arcs and straight runs, its entities out of order and some of
them drawn backwards — with a circle and a bulged polyline for holes. Plain CadQuery and ezdxf:
it imports no generator and takes no CAD lock.

    tools/cad-venv/bin/python tools/hsm/kernel/tests/dxf_reference.py
"""

import json
from pathlib import Path

import cadquery as cq
import ezdxf

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixtures" / "outline.dxf"
THICKNESS = 1.524


def draw():
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    big, corner = 27.275, 1.5
    centre = (3.275, 0.0)
    # The outer outline, counterclockwise: a big arc over the top, two corner arcs and three
    # straight runs across the bottom.
    left = (-7.8, -23.274342095964816)
    right = (13.8, -23.52817459982818)
    msp.add_arc(centre, big, 90.0, 244.55275106806357)
    msp.add_line((15.3, -23.52817459982818), (15.3, 5.449999999999999))
    msp.add_arc(left, corner, -115.44724893193639, 0.0)
    msp.add_arc(centre, big, -36.29174405863055, 90.0)
    msp.add_line((-6.3, 0.0), (-6.3, -23.274342095964816))
    msp.add_arc((0.0, 0.0), 6.3, 0.0, 180.0)
    msp.add_line((6.3, 0.0), (6.3, -25.37469211635877))
    msp.add_arc((7.8, -25.37469211635877), corner, 180.0, 280.11111506418746)
    msp.add_arc(centre, big, -79.88888493581254, -65.89931234150859)
    msp.add_arc(right, corner, -65.89931234150852, 0.0)
    msp.add_arc((18.925, 5.449999999999999), 3.625, 0.0, 180.0)
    msp.add_line((22.55, -15.256146302392358), (22.55, 5.449999999999999))
    msp.add_arc((24.05, -15.256146302392358), corner, 180.0, 323.7082559413694)
    msp.add_circle((-12.0, 8.0), 2.5)
    msp.add_lwpolyline([(-4.0, 14.0, 0.0), (2.0, 14.0, 0.6), (2.0, 18.0, 0.0), (-4.0, 18.0, -0.4)],
                       format="xyb", close=True)
    FIXTURE.parent.mkdir(exist_ok=True)
    doc.saveas(FIXTURE)


def main():
    draw()
    imported = cq.importers.importDXF(str(FIXTURE))
    face = imported.faces().val()
    plate = imported.wires().toPending().extrude(THICKNESS).val()
    bb = face.BoundingBox()
    out = {
        "area": face.Area(),
        "outer_length": face.outerWire().Length(),
        "holes": len(face.innerWires()),
        "bbox": [bb.xmin, bb.ymin, bb.xmax, bb.ymax],
        "thickness": THICKNESS,
        "volume": plate.Volume(),
    }
    path = HERE / "dxf_reference.json"
    path.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps(out, indent=1))
    print(f"wrote {path} and {FIXTURE}")


if __name__ == "__main__":
    main()
