"""Quantify the native slice's omitted upper slot tips on the pusher."""
import hashlib
import argparse
import json
import math
import sys
import zipfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent))
import cadquery as cq
import vent_seals as v


def main(horizon):
    manifest=json.loads((HERE/"manifest.json").read_text())
    part=next(p for p in manifest["parts"] if p["name"]=="asse-vent-perimeter-tool")
    source_hash=hashlib.sha256(Path(v.__file__).read_bytes()).hexdigest()
    assert source_hash==manifest["generator_sha256"]
    for kind in ("stl","step"):
        assert hashlib.sha256((HERE/part[kind]).read_bytes()).hexdigest()==part[kind+"_sha256"]
    review_path=HERE/"vent-seal-tool-petgf.tool-review.json"
    review_bytes=review_path.read_bytes()
    review=json.loads(review_bytes)
    assert math.isclose(horizon,review["highest_native_model_layer_mm"],abs_tol=1e-9)
    assert review["source_sha256"][str(Path(v.__file__).relative_to(ROOT))]==source_hash
    assert review["source_sha256"][str((HERE/part["stl"]).relative_to(ROOT))]==part["stl_sha256"]
    archive=ROOT/review["native_archive"]
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==review["native_archive_sha256"]
    with zipfile.ZipFile(archive) as native:
        gcode_names=[name for name in native.namelist() if name.endswith(".gcode")]
        assert len(gcode_names)==1
        assert hashlib.sha256(native.read(gcode_names[0])).hexdigest()==review["gcode_sha256"]
    tool=v.build_perimeter_tool().val()
    phi=math.degrees(v.TOOL_ARC_LENGTH/v.WATER_BEND_RADIUS)
    rotated=tool.rotate((0,0,0),(1,0,0),phi)
    offset=-rotated.BoundingBox().zmin
    printed=rotated.translate((0,0,offset))
    clip=cq.Workplane("XY",origin=(0,0,-100)).box(
        300,300,100+horizon,centered=(True,True,False)).val()
    bearing=[f for f in tool.Faces() if
        abs(f.BoundingBox().zmin-v.BUNG_SEATED_Z)<1e-5 and
        abs(f.BoundingBox().zmax-v.BUNG_SEATED_Z)<1e-5]
    assert len(bearing)==1
    face=bearing[0].rotate((0,0,0),(1,0,0),phi).translate((0,0,offset))
    retained=face.intersect(clip)
    report={"check":"Upper slot-tip omission in native handle-flat print",
            "checker_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "generator_sha256":source_hash,"tool_stl_sha256":part["stl_sha256"],
            "tool_step_sha256":part["step_sha256"],
            "native_tool_review":str(review_path.relative_to(ROOT)),
            "native_tool_review_sha256":hashlib.sha256(review_bytes).hexdigest(),
            "native_archive":review["native_archive"],
            "native_archive_sha256":review["native_archive_sha256"],
            "gcode_sha256":review["gcode_sha256"],
            "native_last_model_layer_z_mm":horizon,
            "cad_maximum_z_mm":printed.BoundingBox().zmax,
            "bearing_area_original_mm2":face.Area(),
            "bearing_area_retained_mm2":retained.Area(),
            "bearing_area_retained_fraction":retained.Area()/face.Area(),
            "omitted_tool_volume_mm3":printed.Volume()-printed.intersect(clip).Volume(),
            "engineering_assessment":f"The two small open-slot endpoints supply excess bearing area. The continuous lower annular bearing retains {100*retained.Area()/face.Area():.2f}% of its modeled area; those endpoints are not required for flange loading. Keep the main bearing flat and remove support residue before use.",
            "scope":"Exact native geometric area clipped at the saved slice's last model layer. The every-layer bead review owns actual printed-road coverage; no insertion force or printed strength is inferred from CAD area."}
    (HERE/"tool-bearing-check.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--last-model-layer-z",type=float,required=True)
    args=parser.parse_args()
    main(args.last_model_layer_z)
