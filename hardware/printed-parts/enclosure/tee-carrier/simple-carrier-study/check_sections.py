"""Native cross-section stock readings, explicitly not assembled stiffness."""
import json
from pathlib import Path
import cadquery as cq
from build_concept import build,box,sha

HERE=Path(__file__).resolve().parent


def section(shape,x):
    width=.02
    s=shape.intersect(box((x-width/2,x+width/2),(80,145),(160,225.025)))
    mass=s.Volume()
    inertia=cq.Shape.matrixOfInertia(s)
    return {"area_mm2":mass/width,
            "Iy_geometric_mm4":inertia[1][1]/width-mass/width*width*width/12,
            "Iz_geometric_mm4":inertia[2][2]/width-mass/width*width*width/12}


def main():
    M,I,plain,blank,L,R,Rrigid,*_=build()
    bm=json.loads((HERE/"inputs/screwed-baseline-manifest.json").read_text())
    orig=[]
    for row in bm.values():
        p=HERE/"inputs"/row["path"]
        assert sha(p)==row["sha256"]
        orig.append(cq.importers.importStep(str(p)).val())
    original=cq.Compound.makeCompound(orig)
    concept=cq.Compound.makeCompound([L,Rrigid])
    rows=[]
    for x in sorted(set((-55,-40,-28,-26.02,-25.98,-24,-22.35,-21.98,-16,-14.02,-13.02,-12.98,-12,-10,-9.52,-9.48,-6,-4,0,8,9.83,9.87,11,12.73,12.77,13.19,13.23,13.58,13.62,15,20,20.48,20.52,22.35,24,25.98,26.02,40,55))):
        rows.append({"x_mm":x,"screwed_reference":section(original,x),
                     "concept":section(concept,x),"continuous_blank":section(blank,x)})
    minima={}
    for name in ("screwed_reference","concept","continuous_blank"):
        minima[name]={key:min(({"x_mm":r["x_mm"],"value":r[name][key]} for r in rows),key=lambda r:r["value"])
                      for key in ("area_mm2","Iy_geometric_mm4","Iz_geometric_mm4")}
    report={"scope":"Geometric thin sections of the full beam through the structural upper cheek at Z225.025, excluding the flexible retaining wall. These are section stock/moment readings only. They assume all stock in one section can transfer load; interface slip and shelf-face engagement are not qualified. They do not prove more stiffness than any physical print.",
            "generator_sha256":sha(HERE/"build_concept.py"),"script_sha256":sha(__file__),
            "screwed_reference_manifest_sha256":sha(HERE/"inputs/screwed-baseline-manifest.json"),
            "beam_axis":"X across the carrier. For a beam along X, transverse Y force bends about Z (Iz), and transverse Z force bends about Y (Iy). The observed X-span bow does not identify force direction.",
            "section_width_mm":.02,"rows":rows,"sampled_minima":minima,
            "acceptance":"Observe the complete 215 mm carrier installed in the full enclosure, with the actual spring and tube loads, in both out-of-plane bending directions. Secure centre seating alone is insufficient."}
    (HERE/"section-stock-checks.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(minima,indent=2),flush=True)


if __name__=="__main__":main()
