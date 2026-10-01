"""Native tree-supported receiver coupons with support blocked only in wing slots."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from shapely.geometry import Polygon, box

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import grip_cover as g
sys.path.insert(0, str(g.ROOT / "hardware/printed-parts/faucet"))
import refresh_print_project as writer


def main(printer):
    piece, trim = {"H2C": ("front", .18), "Mark2": ("back", .04)}[printer]
    name = f"grip-receiver-{piece}"
    stem = f"grip-{piece}-bridge-{printer.lower()}-v6"
    job = g.ROOT / ".cache/prints" / stem
    job.mkdir(parents=True, exist_ok=True)
    project = job / f"{stem}-input.3mf"
    if project.exists():
        raise FileExistsError("Keep reviewed slices immutable; use a new job directory.")
    profile = g.ROOT / "hardware/printed-parts/petgf.3mf"
    report = writer.refresh(profile, project, parts=((name, g.HERE / f"{name}.stl", 0.),),
                            offsets=((0., 0.),), z_trim=trim,
                            title=f"Grip {piece} receiver; wing-slot bridge; {printer}")
    with zipfile.ZipFile(project) as archive:
        members = {n: archive.read(n) for n in archive.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    settings.update(layer_height="0.24", initial_layer_print_height="0.2",
                    support_filament="1", support_interface_filament="1", flush_into_support="0",
                    brim_type="no_brim", brim_width="0", elefant_foot_compensation="0")
    assert settings["support_type"] == "tree(auto)"
    assert settings["wall_sequence"] == "inner wall/outer wall"
    assert settings["is_infill_first"] == "0" and settings["infill_wall_overlap"] == "15%"
    members[writer.SETTINGS_MEMBER] = json.dumps(settings, indent=2).encode()
    ranges = ET.Element("objects")
    obj = ET.SubElement(ranges, "object", id="1")
    band = ET.SubElement(obj, "range", min_z="35.0", max_z="41.5")
    ET.SubElement(band, "option", opt_key="layer_height").text = "0.24"
    ET.SubElement(band, "option", opt_key="wall_loops").text = "6"
    members["Metadata/layer_config_ranges.xml"] = ET.tostring(ranges, encoding="utf-8", xml_declaration=True)

    part, = report["parts"]
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    ET.register_namespace("", ns)
    tag = lambda name: "{" + ns + "}" + name
    tree = ET.fromstring(members[part["member"]])
    vertices = np.array([[float(v.get(a)) for a in ("x", "y", "z")]
                         for v in tree.iter(tag("vertex"))]) + part["source_center_mm"]
    triangles = list(tree.iter(tag("triangle")))
    points = vertices[np.array([[int(t.get(a)) for a in ("v1", "v2", "v3")] for t in triangles])]
    mouth = g.shell._handhold_y()[0 if piece == "front" else 1]
    ymin, ymax = ((mouth-g.shell.handhold_wall-.01, mouth+.01) if piece == "front"
                  else (mouth-.01, mouth+g.shell.handhold_wall+.01))
    xhalf = g.WING_SPAN/2 + g.WING_END_AIR
    blocked = box(g.X_CENTER-xhalf-.001, ymin, g.X_CENTER+xhalf+.001, ymax)
    paint_area, count = 0., 0

    def encode(p, depth=0):
        nonlocal paint_area
        polygon = Polygon(p[:, :2])
        if blocked.covers(polygon):
            paint_area += polygon.area
            return "8"
        if not blocked.intersects(polygon):
            return "0"
        if depth == 10:
            paint_area += polygon.area
            return "8"
        a,b,c = p
        ab,bc,ca = (a+b)/2, (b+c)/2, (c+a)/2
        return "".join(encode(np.array(q), depth+1) for q in
                       ((a,ab,ca),(ab,b,bc),(bc,c,ca),(ab,bc,ca))) + "3"

    for triangle, pts in zip(triangles, points):
        normal = np.cross(pts[1]-pts[0], pts[2]-pts[0])
        if normal[2] < 0 and np.max(np.abs(pts[:,2]-g.ROOF)) < .0001:
            polygon = Polygon(pts[:,:2])
            if blocked.intersects(polygon):
                triangle.set("paint_supports", encode(pts))
                count += 1
    assert count and 15 < paint_area < 17, (count, paint_area)
    members[part["member"]] = ET.tostring(tree, encoding="utf-8", xml_declaration=True)
    writer.archive_write(project, members)
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    report.update(printer_target=printer, requested_trim_mm=trim, project_sha256=sha(project),
                  settings_sha256=hashlib.sha256(members[writer.SETTINGS_MEMBER]).hexdigest(),
                  submitted=False, slot_bounds_cad_xy_mm=list(blocked.bounds),
                  slot_roof_cad_z_mm=g.ROOF, blocked_area_mm2=paint_area,
                  painted_source_triangles=count, source_sha256={str(p.relative_to(g.ROOT)):sha(p)
                      for p in (Path(__file__), profile, g.HERE/f"{name}.stl")})
    (job/"preparation.json").write_text(json.dumps(report, indent=2)+"\n")
    ready = job/"ready"
    ready.mkdir()
    command = ["/Applications/BambuStudio.app/Contents/MacOS/BambuStudio", "--slice", "0",
               "--arrange", "0", "--orient", "0", "--outputdir", str(ready),
               "--export-3mf", f"{stem}.gcode.3mf", str(project)]
    (job/"slice-command.json").write_text(json.dumps(command, indent=2)+"\n")
    with (ready/"slice.log").open("w") as log:
        rc = subprocess.run(command, cwd=ready, stdout=log, stderr=subprocess.STDOUT).returncode
    print(json.dumps({"printer":printer, "job":str(job), "slice_exit":rc,
                      "blocked_area_mm2":paint_area}), flush=True)
    return rc


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("printer", choices=("H2C", "Mark2"))
    raise SystemExit(main(parser.parse_args().printer))
