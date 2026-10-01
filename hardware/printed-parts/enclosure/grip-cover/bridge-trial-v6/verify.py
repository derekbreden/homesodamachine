"""Read native receiver G-code, including every labelled or unlabelled support road."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from shapely.geometry import LineString, Polygon, box
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import grip_cover as g
sys.path.insert(0, str(g.ROOT / "hardware/scripts"))
from enclosure_support_audit import audit, _WORD
sys.path.insert(0, str(g.ROOT / "hardware/printed-parts/enclosure/nameplate"))
from verify_mark2_print import segments


def all_roads(path):
    """Extrusion roads without an object-label prerequisite, for support exclusion."""
    x = y = e = width = 0.
    layer = None
    feature = ""
    absolute, relative_e = True, True
    for line in path.read_text().splitlines():
        if line.startswith("; Z_HEIGHT:"):
            layer = float(line.split(":", 1)[1]); feature = ""
        elif line.startswith("; FEATURE:"):
            feature = line.split(":", 1)[1].strip()
        elif line.startswith("; LINE_WIDTH:"):
            width = float(line.split(":", 1)[1])
        code = line.split(";", 1)[0].strip()
        if not code:
            continue
        command = code.split()[0]
        v = {k:float(n) for k,n in _WORD.findall(code)}
        if command in ("G90", "G91"):
            absolute = command == "G90"
        elif command in ("M82", "M83"):
            relative_e = command == "M83"
        elif command == "G92":
            x,y,e = (v.get(k,old) for k,old in zip("XYE", (x,y,e)))
        elif command in ("G0", "G1", "G2", "G3"):
            nx,ny = (v.get(k,old) if absolute else old+v.get(k,0)
                     for k,old in zip("XY", (x,y)))
            de = v.get("E",0) if relative_e else v.get("E",e)-e
            if layer is not None and de > 1e-9 and (nx != x or ny != y):
                assert command in ("G0", "G1"), "Arc fitting must remain disabled"
                yield {"a":(x,y), "b":(nx,ny), "width":width,
                       "layer":layer, "feature":feature}
            x,y = nx,ny
            if "E" in v:
                e = e+v["E"] if relative_e else v["E"]


def verify(printer):
    piece, trim = {"H2C":("front",.18), "Mark2":("back",.04)}[printer]
    stem = f"grip-{piece}-bridge-{printer.lower()}-v6"
    job = g.ROOT / ".cache/prints" / stem
    output = HERE / printer.lower()
    output.mkdir(exist_ok=True)
    preparation = json.loads((job/"preparation.json").read_text())
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    for name,digest in preparation["source_sha256"].items():
        assert sha(g.ROOT/name) == digest, name
    geometry = json.loads((g.HERE/"geometry-check.json").read_text())
    assert geometry["status"] == "pass"
    for name,digest in geometry["artifacts_sha256"].items():
        assert sha(g.HERE/name) == digest, name
    project = job/preparation["project"]
    assert sha(project) == preparation["project_sha256"]
    with zipfile.ZipFile(project) as z:
        assert hashlib.sha256(z.read("Metadata/project_settings.config")).hexdigest() == preparation["settings_sha256"]
        ranges = ET.fromstring(z.read("Metadata/layer_config_ranges.xml"))
        obj, = list(ranges); band, = list(obj)
        assert band.attrib == {"min_z":"35.0", "max_z":"41.5"}
        assert {n.get("opt_key"):n.text for n in band} == {"layer_height":"0.24", "wall_loops":"6"}
    archive = job/"ready"/f"{stem}.gcode.3mf"
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        settings = json.loads(z.read("Metadata/project_settings.config"))
        gcode = z.read("Metadata/plate_1.gcode")
        assert hashlib.md5(gcode).hexdigest() == z.read("Metadata/plate_1.gcode.md5").decode().strip().lower()
        (output/"preview.png").write_bytes(z.read("Metadata/plate_1.png"))
    path = job/"ready/plate_1.gcode"
    path.write_bytes(gcode)
    expected = {"initial_layer_print_height":"0.2", "layer_height":"0.24",
                "enable_support":"1", "support_type":"tree(auto)",
                "support_object_xy_distance":"0.4", "support_top_z_distance":"0.45",
                "support_bottom_z_distance":"0.3", "support_filament":"1",
                "support_interface_filament":"1", "flush_into_support":"0",
                "wall_sequence":"inner wall/outer wall", "is_infill_first":"0",
                "infill_wall_overlap":"15%", "elefant_foot_compensation":"0",
                "brim_type":"no_brim", "filament_colour":["#000000"],
                "filament_nozzle_map":["0"], "nozzle_diameter":["0.4","0.4"],
                "enable_arc_fitting":"0", "curr_bed_type":"Textured PEI Plate"}
    for k,v in expected.items():
        assert settings[k] == v, (k,settings[k],v)
    with zipfile.ZipFile(g.ROOT/preparation["settings_source"]) as z:
        baseline = json.loads(z.read("Metadata/project_settings.config"))
    assert all(settings[k] == baseline[k] for k in baseline if "speed" in k)
    trims = [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+\d.]+)",gcode,re.M)]
    assert np.allclose(trims,[0.,trim-.02])
    part, = preparation["parts"]
    assert part["rotation_x_degrees"] == 0 and part["watertight"] and part["body_count"] == 1
    shift = np.array(part["plate_translation_mm"]) - part["source_center_mm"]
    slot = box(*preparation["slot_bounds_cad_xy_mm"])
    slot_floor = g.BACK-g.WING_THICK-g.BEARING_AIR
    roads = list(all_roads(path))
    model = [r for r in segments(path) if r["object"] == part["identify_id"]
             and not r["feature"].startswith("Support")]
    supports = [r for r in roads if r["feature"].startswith("Support")]
    assert supports
    def bead(r, cad=False):
        delta = shift[:2] if cad else 0.
        return LineString([np.array(r["a"])-delta,np.array(r["b"])-delta]).buffer(r["width"]/2)
    intrusion = sum(bead(r,True).intersection(slot).area for r in supports
                    if slot_floor+.001 < r["layer"]-shift[2] < g.ROOF)
    assert intrusion < .001, intrusion
    bridge = [r for r in model if r["feature"] == "Bridge"
              and g.ROOF < r["layer"]-shift[2] < g.ROOF+.30
              and bead(r,True).intersects(slot)]
    assert len(bridge) >= 8
    coverage = unary_union([bead(r,True) for r in bridge]).intersection(slot).area/slot.area
    # The slicer labels the perimeter roads separately from the bridge infill.
    # Both are part of the first roof layer; require nearly complete coverage.
    roof_z = min(r["layer"] for r in bridge)
    roof = [r for r in model if abs(r["layer"]-roof_z)<.001]
    roof_coverage = unary_union([bead(r,True) for r in roof]).intersection(slot).area/slot.area
    assert roof_coverage > .95, roof_coverage
    support = audit(path, part["name"], g.ROOT/part["source"], project,
                    include_unlabelled_support=True)
    (output/"support-audit.json").write_text(json.dumps(support,indent=2)+"\n")
    z1,z2 = sorted({r["layer"] for r in model})[:2]
    assert abs(z1-.2)<.001 and abs(z2-.44)<.001
    first = unary_union([bead(r) for r in model if r["layer"] == z1])
    second = [r for r in model if r["layer"] == z2]
    wall_overlap = min(bead(r).intersection(first).area/bead(r).area
                       for r in second if "wall" in r["feature"].lower())
    assert wall_overlap > .5
    assert first.geom_type == "Polygon"
    assert Polygon(first.exterior).buffer(.12).covers(unary_union([bead(r) for r in second]))
    result = json.loads((job/"ready/result.json").read_text())
    plate, = result["sliced_plates"]
    assert result["return_code"] == 0 and not plate["warning_message"]
    report = {"status":"pass", "verified_at_utc":datetime.now(timezone.utc).isoformat(),
              "printer":printer, "archive":str(archive.relative_to(g.ROOT)), "archive_sha256":sha(archive),
              "gcode_sha256":hashlib.sha256(gcode).hexdigest(), "preparation":preparation,
              "geometry_check_sha256":sha(g.HERE/"geometry-check.json"),
              "support_audit_sha256":sha(output/"support-audit.json"),
              "settings_verified":expected, "saved_speeds_preserved":True,
              "requested_trim_mm":trim, "emitted_g29_1_z_mm":trims,
              "slot_support_intrusion_mm2":intrusion, "slot_roof_bridge_roads":len(bridge),
              "slot_roof_bridge_coverage_fraction":coverage,
              "slot_roof_all_roads_coverage_fraction":roof_coverage,
              "first_two_layer_heights_mm":[z1,z2], "second_layer_minimum_wall_support_fraction":wall_overlap,
              "estimate_seconds":plate["total_predication"], "filaments":plate["filaments"],
              "launch_options":{"timelapse":"On","bed_leveling":"On","flow_calibration":"Auto",
                                "nozzle_offset_calibration":"Auto"}, "submitted":False}
    (output/"preflight.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in ("status","printer","estimate_seconds",
                     "slot_support_intrusion_mm2","slot_roof_bridge_coverage_fraction")}),flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("printer",choices=("H2C","Mark2"))
    verify(parser.parse_args().printer)
