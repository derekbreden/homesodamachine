"""Make the two manual dry-observation camera stages and Raynox cassettes.

Run by hand with tools/cad-venv/bin/python. This fabrication set is independent
of the appliance CAD build. Dimensions are mm. Purchased-camera bodies are
envelopes; only the plates, cassette and locating parts are fabrication geometry.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from pathlib import Path

import cadquery as cq
import ezdxf

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "hardware/printed-parts/fixtures/gun-positioner-observation"
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
sys.path.insert(0, str(ROOT / "hardware/scripts"))
from _cadq_export import export_assembly, export_dxf
from _material_base import M_ALUMINIUM, M_PETGF_BLACK, one_body

T = 6.35
RAIL_CENTER_HEIGHT = 22.5
BLOCK_TOP_HEIGHT = RAIL_CENTER_HEIGHT + 17.5
BLOCK_W, BLOCK_L = 41.0, 39.0
BLOCK_PITCH_Y, BLOCK_PITCH_X = 28.0, 26.0
CAMERA_W, CAMERA_D, CAMERA_H = 253.5, 144.0, 169.0
CAMERA_X = 18.0
CAMERA_PLATE_Z = T + BLOCK_TOP_HEIGHT
LENS_X = 106.35
LENS_Z_ABOVE_PLATE = 130.0
BASE_HEIGHT_GAP = 55.70
BLACK = cq.Color(0.12, 0.14, 0.17)
ALUMINUM = cq.Color(0.70, 0.74, 0.78)
STEEL = cq.Color(0.54, 0.59, 0.63)
BLUE = cq.Color(0.08, 0.37, 0.70)
GLASS = cq.Color(0.3, 0.6, 0.68, 0.45)
PARTS = {}


def plate(w, d, t=T):
    return cq.Workplane("XY").box(w, d, t, centered=(True, True, False))


def bore(shape, points, diameter):
    cutter = cq.Workplane("XY", origin=(0, 0, -1)).pushPoints(points).circle(diameter/2).extrude(100)
    return shape.cut(cutter)


def slot(shape, x, y, length, diameter, angle=0):
    cutter = cq.Workplane("XY", origin=(0, 0, -1)).center(x, y).slot2D(length, diameter, angle).extrude(100)
    return shape.cut(cutter)


def fixed_plate():
    p = plate(400, 300)
    p = bore(p, [(x, y) for x in (-180, 180) for y in (-135, 135)], 8.5)
    stop_holes = [(sign*(169.5+T-x), rail_y+dy)
                  for sign in (-1, 1) for x in (15, 40)
                  for rail_y in (-90, 90) for dy in (-24, 24)]
    p = bore(p, stop_holes, 5.5)
    # Return clamps align only in the forward (+100 mm) position.
    return bore(p, [(-30, -130), (-30, 130)], 5.5)


def carriage_plate():
    p = plate(300, 300)
    holes = [(bx+dx, by+dy) for bx in (-50, 50) for by in (-90, 90)
             for dx in (-13, 13) for dy in (-14, 14)]
    p = bore(p, holes, 5.5)
    p = slot(p, 5, 0, 90, 6.8)  # Adjustable 1/4-20 tripod fastening.
    # Upright's metal angle foot and return latch.
    p = bore(p, [(x, y) for x in (125, 145) for y in (-32, 32)], 5.5)
    p = bore(p, [(-130, -130), (-130, 130)], 5.5)
    return p


def lens_upright():
    # Flat blank XY becomes a vertical YZ plate in the assembly.
    p = plate(100, 200)
    p = p.cut(cq.Workplane("XY", origin=(0, 0, -1)).center(0, 22).rect(64, 150).extrude(10))
    for y in (-42, 42):
        p = slot(p, y, 25, 116, 5.5, 90)
    p = bore(p, [(y, z) for y in (-32, 32) for z in (-85, -65)], 5.5)
    return p


def cassette():
    # CAD local Z is the optical axis; rear lip is at Z=0.
    p = plate(96, 86, 18.0)
    p = p.cut(cq.Workplane("XY", origin=(0, 0, 2)).circle(53.4/2).extrude(30))
    p = bore(p, [(0, 0)], 43.6)
    p = bore(p, [(y, z) for y in (-42, 42) for z in (-30, 30)], 5.5)
    for y, z in ((-32, -32), (32, -32), (-32, 32), (32, 32)):
        p = bore(p, [(y, z)], 3.4)
        # Captive hex nuts at rear, with 0.2 mm fit allowance on flats.
        p = p.cut(cq.Workplane("XY").center(y, z).polygon(6, 6.0/math.cos(math.pi/6)).extrude(2.8))
    return p


def lens_retainer():
    p = plate(76, 76, 2.4)
    p = bore(p, [(0, 0)], 49.4)
    return bore(p, [(y, z) for y in (-32, 32) for z in (-32, 32)], 3.4)


def rail_stop():
    # A cut metal angle: a fork clears the supported shaft, while the upper
    # bridge stops the block below the underside of the carriage plate.
    bottom = cq.Workplane("XY").box(50.8, 60, T, centered=(False, True, False))
    back = cq.Workplane("XY").box(T, 60, 38, centered=(False, True, False))
    p = bottom.union(back)
    p = p.cut(cq.Workplane("XY").box(55, 34, 30.5, centered=(False, True, False)).translate((-1, 0, -1)))
    return bore(p, [(x, y) for x in (15, 40) for y in (-24, 24)], 5.5)


def shim_coupon():
    # 0.2 and 0.4 mm horseshoe shims; loosen retainer rather than squeeze optics.
    p = cq.Workplane("XY").circle(53.2/2).circle(49.5/2).extrude(.4)
    return p.cut(cq.Workplane("XY").center(0, 27).rect(15, 25).extrude(1))


def rail_proxy():
    base = plate(400, 30, 4)
    support = plate(400, 12, RAIL_CENTER_HEIGHT-4).translate((0, 0, 4))
    shaft = cq.Workplane("YZ").circle(6).extrude(400).translate((-200, 0, RAIL_CENTER_HEIGHT))
    return base.union(support).union(shaft)


def block_proxy():
    return plate(BLOCK_L, BLOCK_W, 28).translate((0, 0, BLOCK_TOP_HEIGHT-28))


def angle_proxy():
    # Two-inch x two-inch x quarter-inch aluminum angle; cut width80.
    bottom = plate(50.8, 80).translate((25.4, 0, 0))
    back = cq.Workplane("XY").box(T, 80, 50.8, centered=(False, True, False))
    p = bore(bottom.union(back), [(x,y) for x in (125-LENS_X,145-LENS_X) for y in (-32,32)],5.5)
    holes = cq.Workplane("YZ",origin=(-1,0,0)).pushPoints([(y,z) for y in (-32,32) for z in (15,35)]).circle(2.75).extrude(10)
    return p.cut(holes)


def camera_proxy():
    base = plate(CAMERA_D, CAMERA_W, 40)
    head = cq.Workplane("YZ").circle(40).extrude(116).translate((-58, 0, 130))
    yoke = cq.Workplane("XY").box(80, 120, 125, centered=(True, True, False)).translate((0, 0, 40))
    return base.union(yoke).union(head)


def assembly(retract=0, lens_inserted=True):
    if not 0 <= retract <= 200:
        raise ValueError("manual retraction must be between 0 and 200 mm")
    travel = 100-retract
    a = cq.Assembly(name="manual_camera_stage")
    a.add(fixed_plate(), name="stationary_plate", color=ALUMINUM)
    for x in (-180, 180):
        a.add(plate(40, 300, 40).translate((x, 0, -40-BASE_HEIGHT_GAP)), name=f"4040_riser_{x}", color=ALUMINUM)
        for y in (-135,135):
            stud=cq.Workplane("XY").circle(4).extrude(BASE_HEIGHT_GAP+30).translate((x,y,-BASE_HEIGHT_GAP-8))
            a.add(stud,name=f"M8_height_post_{x}_{y}",color=STEEL)
            for i,z in enumerate((-BASE_HEIGHT_GAP,-8.5,T,T+7)):
                nut=cq.Workplane("XY").polygon(6,13/math.cos(math.pi/6)).circle(4.2).extrude(6.5).translate((x,y,z))
                a.add(nut,name=f"height_locknut_{x}_{y}_{i}",color=STEEL)
    for y in (-90, 90):
        a.add(rail_proxy().translate((0, y, T)), name=f"rail_{y}", color=STEEL)
        for x in (-50, 50):
            a.add(block_proxy().translate((x+travel, y, T)), name=f"block_{x}_{y}", color=STEEL)
        for sign in (-1, 1):
            stop=rail_stop()
            if sign == 1:
                stop=stop.rotate((0, 0, 0), (0, 0, 1), 180)
            a.add(stop.translate((sign*(169.5+T), y, T)), name=f"metal_stop_{sign}_{y}", color=ALUMINUM)
    a.add(carriage_plate().translate((travel, 0, CAMERA_PLATE_Z)), name="camera_plate", color=ALUMINUM)
    if retract == 0:
        for y in (-130, 130):
            spacer=cq.Workplane("XY").circle(5).circle(3).extrude(40).translate((-30, y, T))
            a.add(spacer, name=f"return_spacer_{y}", color=STEEL)
    top = CAMERA_PLATE_Z + T
    a.add(camera_proxy().translate((CAMERA_X+travel, 0, top)), name="camera_envelope", color=BLACK)
    if lens_inserted:
        a.add(angle_proxy().translate((LENS_X+travel, 0, top)), name="metal_angle", color=ALUMINUM)
        # Upright local plane X/Y maps to Y/Z, optical direction+X.
        upright = lens_upright().rotate((0, 0, 0), (1, 1, 1), 120)
        a.add(upright.translate((100+travel, 0, top+100)), name="upright", color=ALUMINUM)
        c = cassette().rotate((0, 0, 0), (1, 1, 1), 120)
        a.add(c.translate((LENS_X+travel, 0, top+LENS_Z_ABOVE_PLATE)), name="lens_cassette", color=BLUE)
        r = lens_retainer().rotate((0, 0, 0), (1, 1, 1), 120)
        a.add(r.translate((LENS_X+18+travel, 0, top+LENS_Z_ABOVE_PLATE)), name="lens_retainer", color=BLACK)
        glass = cq.Workplane("YZ").circle(26.5).extrude(15.5).translate((LENS_X+2+travel, 0, top+LENS_Z_ABOVE_PLATE))
        a.add(glass, name="Raynox_envelope", color=GLASS)
    return a


def init_parts():
    """The same fabrication solids and flat-hole data used by guide templates."""
    if PARTS:
        return
    fixed_holes=[(x,y,8.5) for x in (-180,180) for y in (-135,135)]
    fixed_holes += [(sign*(169.5+T-x),rail_y+dy,5.5) for sign in (-1,1) for x in (15,40)
                    for rail_y in (-90,90) for dy in (-24,24)]
    fixed_holes += [(-30,-130,5.5),(-30,130,5.5)]
    carriage_holes=[(bx+dx,by+dy,5.5) for bx in (-50,50) for by in (-90,90)
                    for dx in (-13,13) for dy in (-14,14)]
    carriage_holes += [(x,y,5.5) for x in (125,145) for y in (-32,32)]
    carriage_holes += [(-130,-130,5.5),(-130,130,5.5)]
    specifications=[
        ("camera-fixed-plate",fixed_plate(),"metal",2,[400,300,T],fixed_holes,[],
         "Rail centers Y=±90; transfer-drill diameter3.5 from each actual rail. Do not assume longitudinal catalog hole phase."),
        ("camera-carriage-plate",carriage_plate(),"metal",2,[300,300,T],carriage_holes,[[5,0,90,6.8,0]],
         "Four blocks at X=±50,Y=±90; tripod slot gives X adjustment. Camera remains level."),
        ("lens-upright",lens_upright(),"metal",2,[100,200,T],
         [[y,z,5.5] for y in (-32,32) for z in (-85,-65)],[[y,25,116,5.5,90] for y in (-42,42)],
         "Cut64×150 window centered X=0,Y=22. Mount at optical X=100; cassette behind-facing lip clears metal window."),
        ("camera-rail-stop",rail_stop(),"metal",8,[50.8,60,38],[[x,y,5.5] for x in (15,40) for y in (-24,24)],[],
         "Cut from50.8×50.8×6.35 angle,60wide. Shorten upright to38. Remove34-wide center of foot and lower29.5 of upright; leave upper8.5 bridge. 3D STEP governs this angle."),
        ("lens-angle",angle_proxy(),"metal",2,[50.8,80,50.8],[],[],
         "Cut80mm wide from50.8×50.8×6.35 angle. Use separate lens-angle-foot and lens-angle-upright DXF projections; hole locations are local to each face."),
        ("lens-cassette",cassette(),"print",2,[96,86,18],[],[],
         "PET-GF; flat rear lip down. Pocket53.4; lip2; rear aperture43.6. Only hold metal lens rim."),
        ("lens-retainer",lens_retainer(),"print",2,[76,76,2.4],[],[],
         "PET-GF; flat down. Aperture49.4; four M3 screws and captive nuts. No force on glass."),
        ("lens-shim",shim_coupon(),"print",4,[53.2,53.2,.4],[],[],
         "Two0.20mm layers. Set axial clearance with shims and retainer screw adjustment; never squeeze the optical assembly."),
    ]
    for name,model,kind,qty,size,holes,slots,notes in specifications:
        PARTS[name]=dict(model=model,kind=kind,quantity=qty,material="aluminum" if kind=="metal" else "PET-GF",
                         blank_mm=size,holes=holes,slots=slots,notes=notes)
    PARTS["lens-upright"]["windows"]=[[0,22,64,150]]
    for name in ("camera-rail-stop","lens-angle"):
        PARTS[name]["stock_profile"]="50.8×50.8×6.35 aluminum angle; not a flat plate"


def write_plate_dxf(name, w, h, holes=(), slots=(), window=None):
    doc = ezdxf.new("R2010")
    doc.units = ezdxf.units.MM
    m = doc.modelspace()
    m.add_lwpolyline([(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)], close=True)
    for x, y, d in holes:
        m.add_circle((x, y), d/2)
    for x, y, length, d, angle in slots:
        half = (length-d)/2
        if angle == 0:
            m.add_line((x-half, y-d/2), (x+half, y-d/2))
            m.add_line((x-half, y+d/2), (x+half, y+d/2))
            m.add_arc((x+half, y), d/2, -90, 90)
            m.add_arc((x-half, y), d/2, 90, 270)
        else:
            m.add_line((x-d/2, y-half), (x-d/2, y+half))
            m.add_line((x+d/2, y-half), (x+d/2, y+half))
            m.add_arc((x, y+half), d/2, 0, 180)
            m.add_arc((x, y-half), d/2, 180, 360)
    if window:
        x, y, ww, hh = window
        m.add_lwpolyline([(x-ww/2,y-hh/2),(x+ww/2,y-hh/2),(x+ww/2,y+hh/2),(x-ww/2,y+hh/2)],close=True)
    export_dxf(doc, str(OUT/(name+".dxf")))


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    init_parts()
    printed={k:v["model"] for k,v in PARTS.items() if v["kind"]=="print"}
    metals={k:v["model"] for k,v in PARTS.items() if v["kind"]=="metal"}
    for name, shape in {**printed, **metals}.items():
        color = {"PET-GF": M_PETGF_BLACK, "aluminum": M_ALUMINIUM}[PARTS[name]["material"]]
        export_assembly(one_body(shape, name, color), str(OUT/(name+".step")))
        if name in printed:
            cq.exporters.export(shape, str(OUT/(name+".stl")), tolerance=.03, angularTolerance=.1)
    export_assembly(assembly(), str(OUT/"camera-stage-assembly.step"))
    export_assembly(assembly(lens_inserted=False), str(OUT/"camera-stage-startup.step"))
    export_assembly(assembly(retract=200), str(OUT/"camera-stage-retracted.step"))
    fixed_holes=[(x,y,8.5) for x in (-180,180) for y in (-135,135)]
    fixed_holes += [(sign*(169.5+T-x),rail_y+dy,5.5) for sign in (-1,1) for x in (15,40)
                    for rail_y in (-90,90) for dy in (-24,24)]
    fixed_holes += [(-30,-130,5.5),(-30,130,5.5)]
    write_plate_dxf("camera-fixed-plate",400,300,fixed_holes)
    holes=[(bx+dx,by+dy,5.5) for bx in (-50,50) for by in (-90,90) for dx in (-13,13) for dy in (-14,14)]
    holes += [(x,y,5.5) for x in (125,145) for y in (-32,32)]
    holes += [(-130,-130,5.5),(-130,130,5.5)]
    write_plate_dxf("camera-carriage-plate",300,300,holes,[(5,0,90,6.8,0)])
    write_plate_dxf("lens-upright",100,200,[(y,z,5.5) for y in (-32,32) for z in (-85,-65)],
                    [(y,25,116,5.5,90) for y in (-42,42)],window=(0,22,64,150))
    write_plate_dxf("lens-angle-foot",50.8,80,[(x-25.4,y,5.5) for x in (125-LENS_X,145-LENS_X) for y in (-32,32)])
    write_plate_dxf("lens-angle-upright",80,50.8,[(y,z-25.4,5.5) for y in (-32,32) for z in (15,35)])
    checks = {}
    for name, shape in {**printed, **metals}.items():
        solid=shape.val()
        b=solid.BoundingBox()
        checks[name]={"valid":solid.isValid(),"solids":len(shape.solids().vals()),"volume_mm3":solid.Volume(),
                      "bounds_mm":[b.xlen,b.ylen,b.zlen]}
        if not solid.isValid() or len(shape.solids().vals()) != 1:
            raise RuntimeError(f"invalid fabrication body {name}: {checks[name]}")
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir())
            if p.suffix in (".step",".stl",".dxf")}
    manifest={"schema":1,"scope":"Two manually retracted, level-camera dry-observation stages. No live-laser optical barrier.",
              "stage_quantity":2,"retraction_mm":200,"rail": {"type":"SBR12", "length_mm":400,"rails_per_stage":2,
                "blocks_per_stage":4,"shaft_center_height_mm":RAIL_CENTER_HEIGHT,"block_top_height_mm":BLOCK_TOP_HEIGHT,
                "height_status":"Prime listing drawing verified 2026-10-04",
                "source":"https://www.amazon.com/dp/B08913HVM7",
                "base_holes":"Transfer drill 3.5 mm from the actual rails; diameter4 mm catalog holes,22 mm transverse,100 mm longitudinal pitch."},
              "print_quantities":{"lens-cassette":2,"lens-retainer":2,"lens-shim":4},
              "metal_quantities":{"camera-fixed-plate":2,"camera-carriage-plate":2,"lens-upright":2,
                                   "camera-rail-stop":8,"upright-angle-80mm":2,"4040-riser-300mm":4},
              "fasteners":[
                  {"part":"M3x20 socket bolt","quantity":32,"joint":"rail base4 +fixedplate6.35 +washers/nut; actualholestransfer-drilled"},
                  {"part":"M3x20 socket bolt","quantity":8,"joint":"Retainer 2.4 + cassette 18; no head washer. Captive M3 hex nut seats in rear 2.8 mm pocket; check full nut engagement and screw tip clear of upright."},
                  {"part":"M3 hex nut","quantity":40,"joint":"32railbases +8retainerpockets"},
                  {"part":"M3 washer","quantity":64,"joint":"Both sides of 32 rail bolts; no lens-retainer head washers."},
                  {"part":"M5x16 socket bolt","quantity":32,"joint":"blocktopM5threads10deep;6.35plate+~1washer leaves8.65engagement; verifyreceivedwasher/depth"},
                  {"part":"M5x25 socket bolt","quantity":48,"joint":"32stopfeet +8anglefeet +8upright-angle; two6.35metalfaces, washersandnylocknuts"},
                  {"part":"M5x40 socket bolt","quantity":8,"joint":"cassette18 +upright6.35 +washers+nylocknut; opticalrearclearancecheck"},
                  {"part":"M5x70 socket bolt","quantity":4,"joint":"returnclamps:plate6.35+spacer40+plate6.35+washers+nylocknut"},
                  {"part":"M5 nylock nut","quantity":60,"joint":"48metalangles +8cassette +4returnclamps"},
                  {"part":"M5 washer","quantity":152,"joint":"32blockheads +twoeachof60throughjoints"},
                  {"part":"40mm steel spacer, ID6 OD12","quantity":4,"joint":"returnclamps, removablebeforeretraction"},
                  {"part":"M8x100 threaded stud","quantity":8,"joint":"heightposts;trimafteractualcameraalignment"},
                  {"part":"M8 nut","quantity":40,"joint":"32heightpostnuts +8benchnuts"},
                  {"part":"M8 washer","quantity":48,"joint":"24heightpost +8bracket/extrusion +16benchthroughboltfaces"},
                  {"part":"M8 slot8 T-nut","quantity":16,"joint":"8heightpostanchors +8cornerbracketanchors"},
                  {"part":"M8x16 socket bolt","quantity":8,"joint":"metal4040cornerbrackettoextrusion; checkselectedbracketthickness"},
                  {"part":"M8x75 through bolt","quantity":8,"joint":"cornerbrackettostationbenchtop18–50mm;washerandnut;verifyactualgripbeforedrilling"},
                  {"part":"40-series metal corner bracket","quantity":8,"joint":"fourbenchmountsperstage"},
                  {"part":"1/4-20x1/2inch tripod screw","quantity":2,"joint":"measureactualsocketdepthandfootstand-off;choosewasherstackwithoutbottoming"},
                  {"part":"1/4inch washer","quantity":2,"joint":"tripodscrewstacknominal1.52mm, verifyactualfit"}
              ],
              "limits":{"forward_carriage_center_x_mm":100,"retracted_carriage_center_x_mm":-100,
                        "block_span_mm":100,"block_edge_at_limit_mm":169.5,
                        "stop_top_above_rail_base_mm":38,"carriage_underside_above_rail_base_mm":40,
                        "return_clamp":"Two M5x70 bolts, 40 mm-long metal tubes OD>=10 ID5.5–6, washers and nuts per stage; remove both bolts and tubes before retraction."},
              "height_adjustment":{"posts_per_stage":4,"post":"M8x100 threaded steel rod, trim surplus after alignment",
                  "gap_above_4040_mm":[20,70],"default_gap_mm":BASE_HEIGHT_GAP,
                  "proxy_optical_height_above_bench_mm":40+BASE_HEIGHT_GAP+CAMERA_PLATE_Z+T+LENS_Z_ABOVE_PLATE,
                  "datum":"Keep fixed plate horizontal. Adjust four lower support nuts to actual seam image center with pan/tilt at zero; lock upper/lower nuts and extrusion-foot nuts. Camera130mm axis is a proxy, not a purchased fit dimension.",
                  "post_clearance":"Trim each post to no more than 22 mm above the fixed-plate underside. The carriage underside is 46.35 mm above that datum, or 40 mm above the rail base; deburr the post."},
              "parts":{k:{kk:vv for kk,vv in v.items() if kk!="model"} for k,v in PARTS.items()},
              "startup":"Remove the complete lens module: angle, upright, cassette and retainer. Power up the clear PTZ head, park the camera at zero pan/tilt, manual zoom/focus, then reinstall the lens module. Recalibrate after every restart or retraction.",
              "lens":{"outer_diameter_mm":53,"overall_axial_mm":18.5,"rear_thread_projection_mm":3,
                      "body_without_rear_thread_mm":15.5,"cassette_pocket_mm":53.4,"cassette_axial_mm":18,
                      "pocket_back_lip_mm":2,"front_optical_clearance_mm":49.4,
                      "working_distance_at_infinity_focus_mm":109,"working_distance_status":"Manufacturer reference, not achieved calibration."},
              "sources":{"camera_manual":"https://www.fomako.net/uploads/20250529/ce40713967c8ae0e137cabdd8a72ff1d.pdf",
               "lens_drawing":"https://raynoxdirect.securesite.jp/comparison/pdf/DCR150_DCR250_drawings.pdf"},
              "checks":checks,"sha256":hashes}
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps({"parts":len(printed)+len(metals),"checks_valid":all(v["valid"] for v in checks.values())}))


if __name__ == "__main__":
    build()
