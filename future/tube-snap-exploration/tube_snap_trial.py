"""Three organizer-derived bore sizes in filled-root snaps on a 3 mm floor.

Run manually with tools/cad-venv/bin/python. X runs from the smallest bore
to the largest; Y is the tube axis. Z=0 is the floor's print-bed face.
The generator makes only this comparison coupon; no assembly is changed.
"""
from pathlib import Path
import hashlib
import json
import math

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ORGANIZER_BORE = 6.65
DIAMETER_STEP = .10
TUBE_OD = 6.35
FLOOR = (54., 14., 3.)
AXIS_ABOVE_FLOOR = 4.5
SPAN = 8.
SPRING = 1.44
CATCH_PER_JAW = .45
MOUTH = TUBE_OD - 2*CATCH_PER_JAW
SAMPLES = (("A", ORGANIZER_BORE-DIAMETER_STEP, -18.),
           ("B", ORGANIZER_BORE, 0.),
           ("C", ORGANIZER_BORE+DIAMETER_STEP, 18.))
PROVENANCE = (
    "hardware/printed-parts/faucet/umbilical-organizer/umbilical_organizer.py",
    "hardware/printed-parts/faucet/umbilical-organizer/physical-acceptance.json",
    "future/umbilical-organizer-exploration/prepare_increment_trial.py",
    "future/umbilical-organizer-exploration/diameter-increments-mark2/physical-result.json",
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def box(lo, hi):
    return cq.Solid.makeBox(*[b-a for a,b in zip(lo,hi)], cq.Vector(*lo))


def snap(diameter, x):
    """Constant 1.44 mm curved leaf, common 5.45 mm mouth and full-width root."""
    ri = diameter/2
    ro = ri + SPRING
    rm = (ri+ro)/2
    nose = SPRING/2
    tip = math.pi - math.asin((MOUTH/2+nose)/rm)
    centre_z = FLOOR[2] + AXIS_ABOVE_FLOOR
    plane = cq.Plane(origin=(x,-SPAN/2,centre_z), xDir=(1,0,0), normal=(0,1,0))

    def xy(r,t): return (r*math.sin(t), r*math.cos(t))
    def add(a,b): return tuple(u+v for u,v in zip(a,b))
    p0,p1,p2,p3 = xy(ro,-tip),xy(ro,tip),xy(ri,tip),xy(ri,-tip)
    cp,cn = xy(rm,tip),xy(rm,-tip)
    qp,qn = (math.cos(tip),-math.sin(tip)),(math.cos(-tip),-math.sin(-tip))
    c = (cq.Workplane(plane).moveTo(*p0).threePointArc((0,ro),p1)
         .threePointArc(add(cp,(nose*qp[0],nose*qp[1])),p2)
         .threePointArc((0,ri),p3)
         .threePointArc(add(cn,(-nose*qn[0],-nose*qn[1])),p0)
         .close().extrude(SPAN).val())
    root = box((x-ro,-SPAN/2,FLOOR[2]),(x+ro,SPAN/2,centre_z))
    bore = cq.Solid.makeCylinder(ri,SPAN+.2,cq.Vector(x,-SPAN/2-.1,centre_z),cq.Vector(0,1,0))
    body = c.fuse(root).cut(bore).clean()
    # Native cross-section at the tube centre: both bore and exterior walls.
    ray = cq.Edge.makeLine(cq.Vector(x-ro-1,0,centre_z),cq.Vector(x+ro+1,0,centre_z))
    measured = sorted(v.Center().x-x for v in body.intersect(ray).Vertices())
    expected = [-ro,-ri,ri,ro]
    if len(measured)!=4 or any(abs(a-b)>1e-5 for a,b in zip(measured,expected)):
        raise ValueError(f"Native bore/leaf section differs: {measured}")
    if not body.isValid() or len(body.Solids())!=1:
        raise ValueError("Snap must be one valid native solid")
    return body, dict(centre_x_mm=x, tube_axis_y_mm=[-SPAN/2,SPAN/2],
                      tube_axis_z_mm=centre_z, bore_diameter_mm=diameter,
                      nominal_radial_allowance_mm=(diameter-TUBE_OD)/2,
                      spring_wall_mm=SPRING, outer_radius_mm=ro,
                      mouth_width_mm=MOUTH, nose_radius_mm=nose,
                      tip_angle_deg=math.degrees(tip),
                      free_upper_curve_mm=rm*(tip-math.pi/2),
                      measured_mid_bore_section_x_mm=measured)


def build():
    floor = box((-FLOOR[0]/2,-FLOOR[1]/2,0),(FLOOR[0]/2,FLOOR[1]/2,FLOOR[2]))
    body = floor
    rows = []
    for label,diameter,x in SAMPLES:
        clip,row = snap(diameter,x)
        body = body.fuse(clip)
        rows.append(dict(label=label, **row))
    body = body.clean()
    if not body.isValid() or len(body.Solids())!=1:
        raise ValueError("The shared floor and three clips must be one valid solid")
    return body,rows


def main():
    parts = HERE/"parts"
    parts.mkdir(parents=True,exist_ok=True)
    shape,rows = build()
    stl,step = parts/"tube-snap-three-bores.stl",parts/"tube-snap-three-bores.step"
    cq.exporters.export(shape,str(stl),tolerance=.03,angularTolerance=.10)
    cq.exporters.export(shape,str(step))
    b = shape.BoundingBox()
    report = dict(scope="Physical fit and snap-survival trial; no production assembly update or accepted fit claim.",
                  source=str(Path(__file__).relative_to(ROOT)),source_sha256=sha(Path(__file__)),
                  floor_xyz_mm=list(FLOOR),tube_nominal_od_mm=TUBE_OD,
                  tube_axis_above_floor_mm=AXIS_ABOVE_FLOOR,
                  organizer_baseline_bore_mm=ORGANIZER_BORE,step_in_diameter_mm=DIAMETER_STEP,
                  provenance={path:sha(ROOT/path) for path in PROVENANCE},
                  samples=rows,identification="Facing the printer, smallest bore left, organizer bore centre, largest right. Keep this orientation when removing the one-piece floor; no labels or identification cuts are added.",
                  common_geometry="Filled lower root, constant spring wall, mouth width, tube-axis height and full 8 mm Y span. No pedestal or isolated attachment feet.",
                  print_pose="3 mm floor flat on bed; tube axes parallel to the bed along Y; openings face up.",
                  native=dict(valid=shape.isValid(),solids=len(shape.Solids()),volume_mm3=shape.Volume(),bounds_mm=[getattr(b,k) for k in ['xmin','ymin','zmin','xmax','ymax','zmax']]),
                  files={str(p.relative_to(ROOT)):sha(p) for p in [stl,step]},
                  evaluation="Compare push-in force, layer/root survival, seated grip, axial slide and removal on the actual 1/4-inch tube. The organizer's upright-bore fit does not establish horizontal snap fit. Short curved arms and cross-layer bending are part of this physical trial, not qualified performance.",
                  preparation_only=True)
    (HERE/"geometry-report.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2),flush=True)


if __name__=="__main__":
    main()
