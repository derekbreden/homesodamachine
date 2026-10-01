"""Verify the saved native slice, cover bed contact and per-part support bodies."""
import hashlib
import json
import sys
import zipfile

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

import prepare_print as prep
g=prep.g
sys.path[:0]=[str(g.HERE.parent/"nameplate"),str(g.ROOT/"hardware/scripts")]
from verify_mark2_print import segments
from verify_round_layer_band import wall_layers
from overhang_round import OUTWARD_PER_HEIGHT


def main():
    report=json.loads((prep.JOB/"preparation.json").read_text())
    project=prep.JOB/f"{prep.STEM}-input.3mf"
    archive=prep.JOB/"ready"/f"{prep.STEM}.gcode.3mf"
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    assert sha(project)==report["project_sha256"]
    for path,digest in report["source_sha256"].items():
        assert sha(g.ROOT/path)==digest,path
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        settings=json.loads(z.read("Metadata/project_settings.config"))
        gc=z.read("Metadata/plate_1.gcode")
        assert hashlib.md5(gc).hexdigest()==z.read("Metadata/plate_1.gcode.md5").decode().strip().lower()
        (g.HERE/"native-preview.png").write_bytes(z.read("Metadata/plate_1.png"))
    for k,v in {"initial_layer_print_height":"0.2","layer_height":"0.24",
                "wall_sequence":"inner wall/outer wall","is_infill_first":"0",
                "infill_wall_overlap":"15%","elefant_foot_compensation":"0"}.items():
        assert settings[k]==v,(k,settings[k])
    path=prep.JOB/"ready/plate_1.gcode";path.write_bytes(gc)
    support=prep.writer.slice_review(project,report,prep.JOB/"ready")
    (g.HERE/"support-audit.json").write_text(json.dumps(support,indent=2)+"\n")
    # All bodies, including ones lacking interface labels, stay below the
    # expanding exterior shoulder. Their two contacts serve the lip and ceiling.
    contact_envelope=max(tree["bbox_cad_xyz_mm"][5] for part in support["parts"][1:]
                         for tree in part["trees"])+float(settings["support_top_z_distance"])
    assert contact_envelope<g.ROOF
    roads=list(segments(path));part=report["parts"][0]
    cover=[r for r in roads if r["object"]==part["identify_id"]]
    assert cover and not any(r["feature"].startswith("Support") for r in cover)
    layers=wall_layers(archive,part["identify_id"])
    assert abs(layers[0][0]-.20)<.001
    assert all(h<=.081 for z,h in layers if z>g.THICK-g.TOUCH_R)
    first_z,second_z=sorted({r["layer"] for r in cover})[:2]
    first=unary_union([LineString((r["a"],r["b"])).buffer(r["width"]/2)
                       for r in cover if r["layer"]==first_z])
    second=[r for r in cover if r["layer"]==second_z]
    overlap=min(LineString((r["a"],r["b"])).buffer(r["width"]/2).intersection(first).area /
                LineString((r["a"],r["b"])).buffer(r["width"]/2).area for r in second)
    assert overlap>.50,overlap
    # Actual bead contact includes the normal gaps between first-layer roads.
    # Read outward edge growth separately, against the accepted taper's 0.12 mm
    # advance per 0.24 mm layer, without treating those internal gaps as an edge.
    assert first.geom_type=="Polygon"
    footprint=Polygon(first.exterior)
    upper=unary_union([LineString((r["a"],r["b"])).buffer(r["width"]/2) for r in second])
    allowed=OUTWARD_PER_HEIGHT*(second_z-first_z)
    assert footprint.buffer(allowed).covers(upper)
    low,high=0.,allowed
    for _ in range(16):
        mid=(low+high)/2
        if footprint.buffer(mid).covers(upper):high=mid
        else:low=mid
    cx,cy=part["plate_translation_mm"][:2]
    assert all(first.covers(Point(cx+sign*(g.LENGTH/2+g.WING_REACH/2),cy)) for sign in (-1,1))
    sliced=json.loads((prep.JOB/"ready/result.json").read_text())
    assert sliced["return_code"]==0
    plate,=sliced["sliced_plates"]
    assert not plate["warning_message"]
    checks={"native_archive_valid":True,"source_hashes_current":True,
            "cover_support_paths":0,"cover_layers_mm":layers,
            "both_wings_print_on_first_layer":True,
            "minimum_second_layer_bead_area_overlap_fraction":overlap,
            "maximum_second_layer_outward_advance_mm":high,
            "allowed_outward_advance_mm":allowed,
            "highest_support_contact_envelope_z_mm":contact_envelope,
            "show_transition_starts_at_z_mm":g.ROOF,
            "estimated_seconds":plate["total_predication"],
            "archive":str(archive.relative_to(g.ROOT)),"archive_sha256":sha(archive),
            "project_sha256":sha(project),"gcode_sha256":hashlib.sha256(gc).hexdigest(),
            "submitted":False,
            "status":"native_slice_reviewed_physical_trial_pending",
            "physical_scope":"Support removal, bending recovery, fit, retention, touch finish and lifting are unmeasured."}
    (g.HERE/"print-check.json").write_text(json.dumps(checks,indent=2)+"\n")
    print(json.dumps(checks,indent=2))


if __name__=="__main__":
    main()
