"""Native cable continuity, lane containment and clearance witness."""
import ast
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("HSM_NO_BUILD_LOCK","1")
HERE=Path(__file__).resolve().parent
FAUCET=HERE.parent
sys.path[:0]=[str(FAUCET),str(FAUCET/"faucet-shell"),
             str(FAUCET.parents[1]/"faucet-layout")]
import cadquery as cq
import faucet_paths as p
import faucet_shell as f
import faucet_assembly as a


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


NAMES=("_ribbon_section","_ribbon_lower_frame","_ribbon_arc_frame",
       "_ribbon_transition","_ribbon_straight","_ribbon_constant_arc",
       "_ribbon_peeled_wires","_ribbon_span_solids","_ribbon_envelope",
       "_display_ribbon_sweep","_lower_signal_solid","_lower_signal_profile",
       "_lower_signal_stations","_tip_frame")


def ast_signature(path,names):
    tree=ast.parse(Path(path).read_text())
    selected={n.name:ast.dump(n,include_attributes=False) for n in tree.body
              if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name in names}
    assert set(selected)==set(names),(set(names)-set(selected))
    return hashlib.sha256(json.dumps(selected,sort_keys=True).encode()).hexdigest()


def main():
    start=time.time()
    bindings={"paths":sha(p.__file__),"shell":sha(f.__file__),
              "assembly":sha(a.__file__)}
    functions={"shell":ast_signature(f.__file__,NAMES),
               "assembly":ast_signature(a.__file__,("build_display_ribbon",))}
    records=[]
    final={}
    for clearance in (False,True):
        spans=f._ribbon_span_solids(clearance)
        record={"clearance_lane":clearance,"spans":[{
            "index":i,"cad_valid":s.isValid(),"solid_count":len(s.Solids()),
            "volume_mm3":s.Volume()} for i,s in enumerate(spans)]}
        body=f._ribbon_envelope(clearance).val()
        record.update({"fused_valid":body.isValid(),"fused_solid_count":len(body.Solids()),
                       "fused_volume_mm3":body.Volume()})
        records.append(record)
        final[clearance]=body
        print(json.dumps(record),flush=True)
    assembled=a.build_display_ribbon().val()
    outside=sum(s.Volume() for s in final[False].cut(final[True]).Solids())
    end_angle=f._path_total_rot-math.asin(
        (f.display_ribbon_join_s-f.gn_tip_straight_len)/(f.gn_bend1_r+f.signal_lane_center_n))
    end_s=(end_angle-p.JOINT_ANGLE)*p.WATER_RADIUS
    _,_,normal=p.station_plane(end_s-0.5)
    trimmed=final[False].intersect(f._split_plane_halfspace((0,0,39.3),(0,0,1),1).val())
    trimmed=trimmed.intersect(f._split_plane_halfspace(
        p.station_point(end_s-0.5,n=p.FACE_RIBBON_N),normal,-1).val())
    boundary=cq.Compound.makeCompound(final[True].Faces())
    gap=trimmed.distance(boundary)
    passed=(all(r["fused_valid"] and r["fused_solid_count"]==1 and
                all(s["cad_valid"] and s["solid_count"]==1 for s in r["spans"])
                for r in records) and assembled.isValid() and len(assembled.Solids())==1
            and outside<1e-5 and gap>=0.10-0.005)
    now_functions={"shell":ast_signature(f.__file__,NAMES),
                   "assembly":ast_signature(a.__file__,("build_display_ribbon",))}
    report={"check":"Native consumer-faucet cable and clearance lane",
            "source_sha256":bindings,"geometry_function_ast_sha256":functions,
            "geometry_functions_unchanged_during_check":now_functions==functions,
            "paths_unchanged_during_check":sha(p.__file__)==bindings["paths"],
            "component_records":records,"complete_cable_valid":assembled.isValid(),
            "complete_cable_solid_count":len(assembled.Solids()),
            "complete_cable_volume_mm3":assembled.Volume(),
            "actual_neck_cable_outside_clearance_lane_mm3":outside,
            "minimum_trimmed_cable_to_lane_boundary_gap_mm":gap,
            "lane_boundary_probe":"Native boundary faces versus actual cable; cable trimmed 0.5 mm from each axial end to exclude shared entrance/exit planes",
            "peeled_wire_nominal_maximum_jacket_diameter_mm":1.3,
            "peeled_wire_station_interval_mm":[p.SPREAD_END_S,p.CONVERGE_START_S],
            "scope":"Nominal cable geometry, component continuity and printed-lane clearance. The Ø1.3 peeled conductors are maximum-jacket clearance envelopes. Straight seal-bore seating, minimum-jacket contact, printed size, handling damage and containment are physical acceptance properties.",
            "passed":passed,"elapsed_seconds":time.time()-start}
    (HERE/"ribbon-native-check.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="component_records"}),flush=True)
    if not passed or now_functions!=functions:
        raise SystemExit(1)


if __name__=="__main__":
    main()
