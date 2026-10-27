"""Hand-author the illustrated jet drilling and welding bench guide.

No appliance build, print job or welding operation runs here. The numeric
inputs and source receipt belong to this document's on-demand review.
"""
from __future__ import annotations

import ast
import json
import operator
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools/assembly-guides"))
sys.path.insert(0, str(HERE))
from common import *
import jet_art as art

GUIDE = ROOT / "hardware/water-inlet-jet-guide"
PDF = ROOT / "output/pdf/water-inlet-jet-guide.pdf"
TITLE = "Water-inlet jet: drilling and welding"
N = 14
BASE = "https://homesodamachine.com"
REPO = "https://github.com/derekbreden/homesodamachine/blob/main/"
REFS = {
    "S1": ("JET-CAP-01 Rev A: finished cap", BASE+"/read/cold-core-layout/water-inlet-jet-cap-drawing.pdf"),
    "S2": ("Jet fabrication and elbow fit", REPO+"hardware/assembly/water-inlet-jet.md"),
    "S3": ("Drilling jaws and four-clamp setup", REPO+"hardware/printed-parts/fixtures/water-inlet-jet/README.md"),
    "M1": ("WEN 4208T drill press manual, pp. 5-6, 14, 16-17", "https://cdn.shopify.com/s/files/1/0012/0350/3168/files/4208T.manual.20220914.pdf?v=1664398265"),
    "M2": ("WEN BA4555 metal bandsaw manual", "https://cdn.shopify.com/s/files/1/0012/0350/3168/files/BA4555.manual.20211206.pdf?v=1649272733"),
    "M3": ("X1 Pro manual, installation, modes and red-dot alignment", "https://www.xlaserlab.com/pages/xlaserlab-x1-pro-instruction-manual"),
    "M4": ("X1 Pro shielding-gas installation", "https://eu.xlaserlab.com/blogs/academy/x1pro-laser-welder-unboxing-installation"),
    "M5": ("Norseman: drilling feeds and speeds", "https://www.norsemandrill.com/feeds-speeds-drill.php"),
    "M6": ("Nickel Institute 11026: stainless fabrication for water", "https://nickelinstitute.org/en/resources/technical-guides/fabricating-stainless-steels-for-the-water-industry-guidelines-for-achieving-top-performance-11026/"),
    "M7": ("BSSA: cleaning before passivation", "https://bssa.org.uk/bssa_articles/passivation-of-stainless-steels/"),
}
SOURCES = [
    "tools/water-inlet-jet-guide/build.py",
    "tools/water-inlet-jet-guide/jet_art.py",
    "tools/assembly-guides/common.py",
    "hardware/assembly/water-inlet-jet.md",
    "hardware/printed-parts/fixtures/water-inlet-jet/README.md",
    "hardware/printed-parts/fixtures/water-inlet-jet/water_inlet_jet_fixture.py",
    "hardware/cold-core-layout/_water_inlet_jet.py",
    "hardware/cold-core-layout/water_inlet_jet_cap_drawing.py",
    "hardware/cold-core-layout/water-inlet-jet-cap-drawing.pdf",
    "hardware/assembly/pressure-vessel.md",
    "hardware/assembly/acceptance-and-burn-in.md",
    "hardware/ledger/tools.md", "hardware/ledger/inventory.md",
]


def numbers(relative, names):
    """Read only this guide's simple scalar inputs without importing CAD."""
    tree=ast.parse((ROOT/relative).read_text())
    expr={target.id:node.value for node in tree.body if isinstance(node,ast.Assign)
          for target in node.targets if isinstance(target,ast.Name)}
    ops={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv}
    values={}
    def calc(node):
        if isinstance(node,ast.Constant) and isinstance(node.value,(int,float)):return node.value
        if isinstance(node,ast.Name):return get(node.id)
        if isinstance(node,ast.BinOp) and type(node.op) in ops:return ops[type(node.op)](calc(node.left),calc(node.right))
        raise ValueError(f"Review numeric input {relative}: {ast.dump(node)}")
    def get(name):
        if name not in values:values[name]=calc(expr[name])
        return values[name]
    return {name:get(name) for name in names}


GEOM = numbers("hardware/cold-core-layout/_water_inlet_jet.py",["JET_CAP_D","JET_CAP_T","JET_PASSAGE_D"])
LIMIT = numbers("hardware/cold-core-layout/water_inlet_jet_cap_drawing.py",["OD_TOL","THICKNESS_TOL","BORE_PLUS","BORE_MINUS",
                          "RADIAL_OFFSET_MAX","AXIS_ANGLE_MAX","FACE_GAP_MAX",
                          "THICKNESS_VARIATION_MAX","HOLE_EDGE_BREAK_MAX"])
D,T,BORE=(GEOM[k] for k in ["JET_CAP_D","JET_CAP_T","JET_PASSAGE_D"])


def links(c, ids, n):
    source="Sources "+", ".join(ids)+" (links on p. 14)"
    footer(c,n,source,REFS[ids[0]][1])


def steps(c, items, start=541):
    y=start
    for k,item in enumerate(items,1):
        box(c,33,y,21,21,BLUE,radius=5)
        text(c,str(k),43.5,y+15,11.5,"PlexBold",PAPER,"center")
        height=paragraph(c,item,65,y,508,11.1,13.6)
        y+=max(height,21)+8
    if y>680:raise ValueError(f"Page action copy crosses lower panel: {y}")


def lower(c, title, body):
    box(c,32,688,548,54,ICE,radius=6)
    text(c,title,45,706,10.5,"PlexBold",BLUE)
    paragraph(c,body,45,712,520,10.2,12.3,max_height=27)


def page(c,n,title,subtitle,artist,caption,items,check_title,check,refs):
    begin_page(c)
    header(c,n,title,subtitle,N,"JET / DRILL + WELD")
    panel(c,32,155,548,374)
    with Art(c,40,164) as a:artist(a)
    paragraph(c,caption,35,532,542,9.5,11.5,MUTED,24)
    steps(c,items,start=561)
    lower(c,check_title,check)
    links(c,refs,n)
    end_page(c)


def cover(c):
    begin_page(c)
    header(c,1,"Drill the cap.\nWeld the jet.",
           "Visual bench guide for the 316 water-inlet jet at carbonator Port 2.",N,"JET / DRILL + WELD")
    panel(c,32,186,548,374)
    with Art(c,40,197) as a:art.overview(a)
    paragraph(c,"<b>Drilling: pp. 3-5.</b> Workholding, alignment, depth and the cutting motion.<br/>"
              "<b>Welding: pp. 8-11.</b> Hold the parts, aim at the seam, tack, close the circumference and inspect the root.",
              35,580,541,12.2,16,max_height=65)
    lower(c,"FIRST BUILD: QUALIFY A SPARE ELBOW",
          "The cap drawing defines the part. Elbow fit, the small-joint weld recipe and measured flow still need the coupon record on p. 13.")
    links(c,["S1","S2"],1)
    end_page(c)


def preparation(c):
    begin_page(c)
    header(c,2,"Fit and bench kit","Measure the actual purchased fitting before making a batch.",N,"JET / DRILL + WELD")
    panel(c,32,151,548,346)
    with Art(c,40,160,.93) as a:art.fit(a)
    rows=[
        ("DRILL", "WEN 4208T; 1/16-inch cobalt stub; Tap Magic EP-Xtra; printed jaws; four C-clamps; backer."),
        ("CUT / INSPECT", "WEN BA4555 + 24 TPI M42; caliper; magnifier; flat reference; suitable bore/face measurement tools."),
        ("WELD", "X1 Pro; actual TAISHER 316L elbow; 316 cap; ER316L .030 wire if used; metal fixture; argon branch."),
    ]
    y=511
    for label,body in rows:
        text(c,label,34,y+12,9.6,"PlexBold",BLUE)
        height=paragraph(c,body,127,y,449,10.6,13)
        y+=max(height,26)+10
    lower(c,"CONFIRM THE REAL FIT",
          "Cap covers the bore and seats flat; the whole weld can reach its bore-side root. Finished cap/weld passes the tapped plate and projects into headspace.")
    links(c,["S1","S2","M1","M3"],2)
    end_page(c)


def inspection_record(c):
    begin_page(c)
    header(c,13,"Record the accepted setup","Bind the measured joint, settings, sections and flow to one coupon identity.",N,"JET / DRILL + WELD")
    text(c,"Coupon ID / date / operator",34,165,11,"PlexBold",BLUE)
    box(c,34,174,542,31,PAPER,RULE)
    sections=[
        ("PART AND FIT",["Rod OD / cap thickness / finished bore", "Elbow bore / tip OD / flat land / chamfer",
                         "Welded OD / tapped clearance / made-up projection"]),
        ("X1 PRO AND GAS",["Nozzle / focus-tube setting / mode / power %", "Swing Hz / swing width mm / wire status + mm/s",
                            "Pulse emission + interval (if used) / travel + tie-in sequence",
                            "Shielding check / purge valve setting / restraint arrangement"]),
        ("RESULT",["Sections: axis + tack/restart azimuth / photo IDs / root readable",
                   "Thread fit / exit bore / oxide + residue removal / cleaning record",
                   "Flow: inlet pressure / water temperature / time / mass / repeat runs"]),
    ]
    y=224
    for title,fields in sections:
        text(c,title,34,y,10.5,"PlexBold",BLUE);y+=10
        for field in fields:
            text(c,field,40,y+12,9.4,"Plex",MUTED)
            box(c,34,y+18,542,14,PAPER,RULE)
            y+=38
        y+=9
    lower(c,"RELEASE THE RECIPE WITH THE EVIDENCE",
          "Retain settings, cap and elbow identities, photographs and section pieces. Production parts repeat the accepted setup and checks.")
    links(c,["S2","M3"],13)
    end_page(c)


def references(c):
    begin_page(c)
    header(c,14,"References and picture key","Editable vector guide / edition 2026-10-26 / Letter, single sided.",N,"JET / DRILL + WELD")
    y=158
    for key,(label,url) in REFS.items():
        text(c,key,35,y+12,10.5,"PlexBold",BLUE)
        height=paragraph(c,label,72,y,500,10.8,13.2,BLUE)
        c.linkURL(url,(72,H-y-height,576,H-y),relative=1)
        y+=max(height,14)+11
    box(c,32,454,548,118,ICE,radius=7)
    text(c,"READ THE PICTURES",46,476,11,"PlexBold",BLUE)
    paragraph(c,"<b>Coral:</b> drill, fresh cut, active tack or weld.<br/>"
              "<b>Blue:</b> clamp, gas route, alignment, motion or measurement.<br/>"
              "<b>Steel:</b> existing workpiece. Root pictures are idealized comparison sections.<br/>"
              "Clamps, gun and fitting profiles are setup schematics. Measurements and JET-CAP-01 govern.",
              46,488,515,10.8,14,max_height=76)
    paragraph(c,"<b>Use the machine manuals at the bench.</b> Powered drill/saw: secure the work, remove the chuck key, use eye protection and keep gloves away from moving tooling. Laser work: establish the controlled area, specified laser PPE, extraction and working interlocks before activation.",
              35,594,540,11.1,14,max_height=75)
    lower(c,"WHAT THIS GUIDE ESTABLISHES",
          "It explains the current drilling/welding sequence and inspection targets. The coupon supplies the actual fit, weld settings and acceptance evidence.")
    links(c,["S1","S2","M1","M3"],14)
    end_page(c)


def build():
    PDF.parent.mkdir(parents=True,exist_ok=True)
    c=canvas.Canvas(str(PDF),pagesize=(W,H),invariant=1,pageCompression=1)
    c.setTitle(TITLE);c.setAuthor("Home Soda Machine / Codex")
    cover(c);preparation(c)
    page(c,3,"Clamp the long blank","Two clamps close the jaws. Two more attach the base to the drill table.",art.fixture,
         "Isometric setup. A = horizontal jaw clamps; B = vertical table clamps. Real clamp frames must clear the stopped chuck and quill.",
         ["Seat a flat-ended <b>50-60 mm blank</b> on the fixture floor. Tighten both A clamps evenly; the rod cannot turn, rock or lift and the jaw split stays visible.",
          "Align the stopped drill <b>after closing the jaws</b>. Tighten both B clamps over the base and backer against a solid table edge.",
          "Lower the stopped quill through the full planned stroke. Check the chuck, drill and all four clamps from front and side."],
         "PHYSICAL GRIP COMES FIRST","The fixture's CAD is checked; its real grip and clamp clearance must be demonstrated on a scrap blank.",["S2","S3","M1"])
    page(c,4,"Align and set the depth","The drill point goes deeper than the cap's final back face.",art.depth,
         "Enlarged section, not to scale. The cone is the drill point; only the cylindrical part of the hole gives the full passage diameter.",
         ["Mark the rod center. With power off, bring the stopped <b>1/16-inch stub drill</b> to that mark and use this end face as the depth zero.",
          "Set/prove <b>3-4 mm to the drill tip</b>. Confirm the full-diameter portion extends below the eventual <b>2 mm cap</b> cut plane.",
          "Lock the depth setting and verify it on the trial. The bit remains in the metal, well above the printed fixture floor."],
         "PROVE THE STOP ON THE TRIAL","After cutting, both faces must expose the full bore. A remaining drill cone or membrane fails the through-hole requirement.",["S1","S2","M1"])
    page(c,5,"Cut, retract, clear","Use the 1100 rpm belt setting as the recorded trial starting point.",art.drilling,
         "Action sequence with the rod still clamped. The clamp bodies below the cutting end stay fixed while the drill advances and retracts.",
         ["With the press unplugged, set the belt for <b>1100 rpm</b>, tension it and close the cover. Remove the chuck key; apply Tap Magic.",
          "Feed enough to <b>cut chips</b>. Retract to clear chips and renew fluid, then continue to the proved stop; avoid rubbing in one spot.",
          "Stop for squeal, stalled cutting, excessive heat, wander or work movement. Let the spindle stop before brushing chips or adjusting anything."],
         "RECORD WHAT CUTS THIS STOCK","1100 rpm is a trial start, not a proved production recipe. Keep the accepted speed, drill and fixture setup with the coupon record.",["S2","S3","M1","M5"])
    page(c,6,"Saw, face and deburr","Expose and inspect both ends of the tiny passage before welding.",art.saw_finish,
         "Clamp the retained blank in the saw vise; leave the cutoff free into a tray. The larger drill shown is turned lightly by hand for a burr only.",
         [f"Use the BA4555 at its low-speed trial setting with the <b>24 TPI M42</b> blade. Finish the cap to <b>{T:.2f} ±{LIMIT['THICKNESS_TOL']:.2f} mm</b>.",
          f"Inspect both faces. Hole-edge break is <b>{LIMIT['HOLE_EDGE_BREAK_MAX']:.2f} mm MAX</b>; keep the square OD weld rim. Wash away chips/fluid and dry.",
          f"Verify JET-CAP-01: OD {D:.2f} ±{LIMIT['OD_TOL']:.2f}; bore <b>{BORE-LIMIT['BORE_MINUS']:.4f}-{BORE+LIMIT['BORE_PLUS']:.4f} mm</b>. Use suitable gauges or optical measurement for this tiny bore."],
         "A DRILL SHANK IS ONLY A QUICK CLEARANCE CHECK","It does not measure the finished hole tolerance. Retire the handling blank below 40 mm, or earlier if chuck clearance requires.",["S1","S2","M2"])
    page(c,7,"Purge through the elbow","The tee feeds torch shielding and a needle-controlled internal purge.",art.purge,
         "Gas-flow schematic. The metal branch enters the female port and vents through the jet. Clamp the elbow tip-up for welding, as on p. 8.",
         ["Close the cylinder and depressurize before cutting the regulated <b>6 mm hose</b>. Assemble the metal branch and fit its final adapter in the elbow's female port.",
          "Begin with the needle valve shut. Restore argon, check joints, then crack the valve for a <b>gentle flow out the jet</b>; keep that vent open.",
          "Verify torch shielding while the purge flows. The shared upstream meter reads both branches; record the torch check and purge setting."],
         "THE PURGE MUST NOT MOVE THE CAP","Use the X1 Pro gas supply requirements and the lowest component rating. No numeric jet-purge flow setting has been established.",["S2","M3","M4"])
    page(c,8,"Hold it. Aim at the seam.","Restrain the cap and body before bringing the gun to the joint.",art.aim,
         "Metal holding concept and enlarged joint. Aim/focus is at the cap-to-tip seam. Drawn gun angle is for visibility; set the actual nozzle/focus per its manual.",
         ["Clamp the bare elbow body/hex to a metal fixture. Hold the cap flat and concentric with a separate metal restraint clear of the seam and jet passage.",
          "Fit the chosen welding nozzle and check calibrated aim/focus. With laser output disabled, rehearse access around the whole seam while keeping nozzle and wire position consistent.",
          "Establish shielding/purge and the X1 safety-clip/interlock connection. Remove the printed drilling jaws and production plastic fittings from this setup."],
         "ROOT FUSION IS THE TARGET","A rim bead alone is insufficient. The coupon must show fusion through the cap/tip interface to the bore-side root (p. 11).",["S2","M3"])
    page(c,9,"Tack opposite sides","Use the sacrificial elbow to establish the small-joint setup.",art.tacks,
         "Proposed coupon handling sequence: top, opposite bottom, then right and opposite left. Black dots are completed tacks; coral is the next location.",
         ["Select/record the X1 stainless setup for the actual joint. Record <b>mode, power, swing Hz/width, wire status/feed</b> and pulse emission/interval if used.",
          "Place the first tack, stop and check seating. Tack the opposite side, check again, then make the other opposing pair shown.",
          "Keep the cap centered, flat and the hole clear. Release the trigger before changing grip, restraint or fixture position."],
         "THE JET RECIPE IS STILL A COUPON RESULT","The large vessel-closure settings and the manual's example screen values do not establish this small joint's settings.",["S2","M3"])
    page(c,10,"Close the circumference","Keep each accessible arc and restart under control.",art.weld,
         "A proposed trial path alternates opposite arcs before connecting the remaining sides. Every start/stop is included in the coupon's inspection evidence.",
         ["Trace the seam with constant selected focus, angle, wire delivery and travel. Fuse the cap edge to the elbow tip while keeping the axial passage open.",
          "Release the trigger to reposition. Re-establish the same setup, tie into the existing fusion boundary, and continue until the circumference is closed.",
          "Check distortion and cap seating between segments. Record the exact tack/arc/restart sequence and any filler; change one trial variable at a time."],
         "VERIFY BEFORE COPYING TO PRODUCTION","Complete thread fit and headspace projection checks, then section the sacrificial joint. Save only settings tied to an acceptable root.",["S2","M3"])
    page(c,11,"Read the welded root","Section the coupon; judge the bore-side interface, not just the outer bead.",art.roots,
         "Idealized comparison sections. Coral shows fusion or a defect location, not a predicted penetration profile. The real cap/tip overlap comes from measured fit.",
         ["Secure the coupon body for cutting. Make an axial section through the jet and a second azimuth through a tack/restart region; dress the faces on a flat support.",
          "Inspect and photograph the cap, root and bore. Require readable fusion to the bore-side root, with no water-connected lap crevice, crack, black scale or obstruction.",
          "Retain sections with settings and fit readings. If saw/abrasive smear hides the root, resolve the preparation or examination before accepting the recipe."],
         "ONE GOOD-LOOKING BEAD OR STREAM IS NOT ROOT EVIDENCE","Sectioning samples the circumference. Repeatability and inspection coverage remain part of the weld qualification record.",["S2","M6"])
    page(c,12,"Clean, flow-check, install","Make the production elbow with the accepted joint and settings.",art.flow,
         "Clean and passivate the accessible jet elbow separately. Water exits the installed cap below the top plate's inside face, into the CO2 headspace.",
         ["Remove the temporary purge adapter. Flush both ways; inspect the bore. Remove weld oxide/heat tint by the qualified method before the citric bath, rinse and dry.",
          "At recorded inlet pressure and water temperature, collect for a measured time and weigh the water; repeat. Record mass/time and reject perimeter leakage.",
          "Repeat loose-plate fit, thread and projection checks. Install at <b>Port 2</b> after the bare vessel's hydro/passivation steps; verify clear downward jet travel."],
         "FLOW LIMITS COME FROM THE QUALIFIED GEOMETRY","Open-air collection is not pressurized refill performance. Current citric process is about 4%, 30-60 min; cleaning/passivation acceptance remains in the procedure.",["S2","M7"])
    inspection_record(c);references(c)
    c.save()
    receipt={"geometry_mm":GEOM,"finished_limits_mm":LIMIT,
             "primary_references":{k:{"title":v[0],"url":v[1]} for k,v in REFS.items()},
             "review_scope":"Illustrated work sequence; no physical trial, welding or qualification performed",
             "visual_focus":{"drilling_pages":[3,4,5],"welding_pages":[8,9,10,11]},
             "authored_trial_choices":["opposing four-tack handling sequence","alternating accessible quarter arcs; final recipe depends on coupon"],
             "edition_date":"2026-10-26"}
    canonical=publish(PDF,GUIDE,TITLE,
          "14 illustrated Letter pages · drilling setup and depth, gun aim, tack sequence and welded-root inspection",
          N,SOURCES,extra=receipt)
    (GUIDE/"guide-sources.json").write_text(PDF.with_suffix('.sources.json').read_text())
    print(f"Published {canonical} ({N} pages)")


if __name__ == "__main__":build()
