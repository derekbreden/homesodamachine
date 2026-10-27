"""Hand-author the jet build guide, including its drilling-fixture assembly.

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
import fixture_art as fixture

GUIDE = ROOT / "hardware/water-inlet-jet-guide"
PDF = ROOT / "output/pdf/water-inlet-jet-guide.pdf"
TITLE = "Build the water-inlet jet"
N = 14
BASE = "https://homesodamachine.com"
REPO = "https://github.com/derekbreden/homesodamachine/blob/main/"
REFS = {
    "S1": ("JET-CAP-01 Rev A: finished cap", BASE+"/read/cold-core-layout/water-inlet-jet-cap-drawing.pdf"),
    "S2": ("Jet fabrication and elbow fit", REPO+"hardware/assembly/water-inlet-jet.md"),
    "S3": ("Drilling jaws and four-clamp setup", REPO+"hardware/printed-parts/fixtures/water-inlet-jet/README.md"),
    "S4": ("JET-ELB-01 Rev A: complete welded jet elbow", BASE+"/read/cold-core-layout/water-inlet-jet-elbow-drawing.pdf"),
    "M1": ("WEN 4208T drill press manual, pp. 5-6, 14, 16-17", "https://cdn.shopify.com/s/files/1/0012/0350/3168/files/4208T.manual.20220914.pdf?v=1664398265"),
    "M2": ("WEN BA4555 metal bandsaw manual", "https://cdn.shopify.com/s/files/1/0012/0350/3168/files/BA4555.manual.20211206.pdf?v=1649272733"),
    "M3": ("X1 Pro manual, installation, modes and red-dot alignment", "https://www.xlaserlab.com/pages/xlaserlab-x1-pro-instruction-manual"),
    "M4": ("X1 Pro shielding-gas installation", "https://eu.xlaserlab.com/blogs/academy/x1pro-laser-welder-unboxing-installation"),
}
SOURCES = [
    "tools/water-inlet-jet-guide/build.py",
    "tools/water-inlet-jet-guide/jet_art.py",
    "tools/water-inlet-jet-guide/fixture_art.py",
    "tools/assembly-guides/common.py",
    "hardware/assembly/water-inlet-jet.md",
    "hardware/printed-parts/fixtures/water-inlet-jet/README.md",
    "hardware/printed-parts/fixtures/water-inlet-jet/water_inlet_jet_fixture.py",
    "hardware/printed-parts/fixtures/water-inlet-jet/water-inlet-jet-fixture-fixed.stl",
    "hardware/printed-parts/fixtures/water-inlet-jet/water-inlet-jet-fixture-loose.stl",
    "hardware/cold-core-layout/_water_inlet_jet.py",
    "hardware/cold-core-layout/water_inlet_jet_cap_drawing.py",
    "hardware/cold-core-layout/water-inlet-jet-cap-drawing.pdf",
    "hardware/cold-core-layout/water-inlet-jet-elbow-drawing.pdf",
    "hardware/assembly/pressure-vessel.md",
    "hardware/assembly/acceptance-and-burn-in.md",
    "hardware/ledger/tools.md", "hardware/ledger/inventory.md",
]


def numbers(relative, names, initial=None):
    """Read only this guide's simple scalar inputs without importing CAD."""
    tree=ast.parse((ROOT/relative).read_text())
    expr={target.id:node.value for node in tree.body if isinstance(node,ast.Assign)
          for target in node.targets if isinstance(target,ast.Name)}
    ops={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv}
    values=dict(initial or {})
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
FIXTURE = numbers("hardware/printed-parts/fixtures/water-inlet-jet/water_inlet_jet_fixture.py",
                  ["BASE_X","BASE_Y","BASE_T","JAW_X","JAW_DEPTH","GRIP_Z",
                   "HANDLING_BLANK_L","MIN_HANDLING_BLANK_L","OPEN_JAW_GAP",
                   "GROOVE_R","JAW_CLAMP_X","BASE_CLAMP_X"],{"JET_CAP_D":D})
fixture.FIXTURE=FIXTURE
fixture.ROD_D=D



def links(c, ids, n):
    footer(c,n,"Sources "+", ".join(ids)+" / links on p. 14",REFS[ids[0]][1])


def steps(c, items, start=561):
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


def bookmark(c,n,title):
    c.bookmarkPage(f"page-{n}")
    c.addOutlineEntry(f"{n:02d}  {title}",f"page-{n}",level=0)


def page(c,n,phase,title,subtitle,artist,caption,items,result_title,result,refs):
    begin_page(c);bookmark(c,n,title)
    header(c,n,title,subtitle,N,"JET BUILD / "+phase)
    panel(c,32,155,548,374)
    with Art(c,40,164) as a:artist(a)
    paragraph(c,caption,35,532,542,9.5,11.5,MUTED,24)
    steps(c,items)
    lower(c,result_title,result)
    links(c,refs,n);end_page(c)


def cover(c):
    begin_page(c);bookmark(c,1,TITLE)
    header(c,1,"Build the\nwater-inlet jet.",
           "Assemble the tools, drill and cut the cap, then weld it to the elbow.",N,"JET BUILD")
    panel(c,32,186,548,374)
    with Art(c,40,197) as a:fixture.build_map(a)
    for row,target in enumerate([2,6,9,11]):
        y=207+row*86
        c.linkRect("",f"page-{target}",(52,H-y-72,568,H-y),relative=1,thickness=0)
    paragraph(c,"<b>The finished jet has two parts:</b> one drilled 316 cap (HSM-000011) and one TAISHER elbow. Together they make HSM-000338.<br/>"
              "The jaws, clamps, holder and gas fittings stay at the bench.",
              35,580,541,12.2,16,max_height=65)
    lower(c,"START AT A / THE FIXTURE IS PART OF THIS BUILD",
          "Pages 2-5 show the two prints, rod placement and all four clamps. Each blue result box tells you what is assembled before the next page.")
    links(c,["S2","S3","S4"],1);end_page(c)


def references(c):
    begin_page(c);bookmark(c,14,"Drawings and supporting instructions")
    header(c,14,"Drawings and support","Use these references when you need a dimension, machine setting or post-build check.",N,"JET BUILD / REFERENCE")
    y=157
    for key,(label,url) in REFS.items():
        text(c,key,35,y+12,10.5,"PlexBold",BLUE)
        height=paragraph(c,label,72,y,500,10.8,13.2,BLUE)
        c.linkURL(url,(72,H-y-height,576,H-y),relative=1)
        y+=max(height,14)+10
    box(c,32,381,548,132,ICE,radius=7)
    text(c,"BEFORE THE JET GOES INTO SERVICE",46,403,11,"PlexBold",BLUE)
    paragraph(c,"The fabrication procedure (S2) carries the fitting measurements, sectioned trial weld, cleaning/passivation and flow checks. The actual small-joint laser settings and metal holding fixture are not qualified or dimensioned build packages.<br/>"
              "JET-CAP-01 controls the cap; JET-ELB-01 controls the complete welded elbow. A drill shank does not establish the finished bore tolerance.",
              46,416,515,10.6,13.3,max_height=87)
    text(c,"READ THE PICTURES",35,548,11,"PlexBold",BLUE)
    paragraph(c,"Coral shows the active tool, cut, tack or weld. Blue shows clamps, motion and labels. The jaw pictures on pp. 2-3 come from the issued STL files. Gun, purchased fitting and clamp profiles are setup schematics; sizes come from the drawings and actual hardware.",
              35,559,540,11,14,max_height=61)
    paragraph(c,"<b>Machine setup:</b> secure the work and keep gloves away from moving drill/saw tooling. Laser work uses the manufacturer's controlled area, specified PPE, extraction and working interlocks. Read the machine manuals before activation.",
              35,631,540,10.6,13.2,max_height=47)
    lower(c,"PRINT AND USE AT THE BENCH",
          "Letter, single sided, 100% / no scaling. Edition 2026-10-27. The drawings govern sizes; the assembly pictures explain placement and order.")
    links(c,["S1","S2","S3","S4"],14);end_page(c)


def build():
    PDF.parent.mkdir(parents=True,exist_ok=True)
    c=canvas.Canvas(str(PDF),pagesize=(W,H),invariant=1,pageCompression=1)
    c.setTitle(TITLE);c.setAuthor("Home Soda Machine / Codex")
    cover(c)
    fixed=REPO+"hardware/printed-parts/fixtures/water-inlet-jet/water-inlet-jet-fixture-fixed.stl"
    loose=REPO+"hardware/printed-parts/fixtures/water-inlet-jet/water-inlet-jet-fixture-loose.stl"
    page(c,2,"A / DRILL FIXTURE","Print the two jaws","One fixed base/jaw and one loose jaw form the rod holder.",fixture.print_parts,
         "Issued STL geometry. The loose jaw is turned to show its groove. Both parts print on their flat Z=0 bottoms.",
         [f"Print one <link href='{fixed}' color='#1749D1'><u>fixed-base STL</u></link> and one <link href='{loose}' color='#1749D1'><u>loose-jaw STL</u></link>. The base and rear jaw are a single part.",
          "Use PET-GF15: <b>0.20 mm first layer, 0.24 mm normal layers, six walls, six top/bottom layers, 50% infill</b> as the fixture's starting profile.",
          "Clear whiskers from the grooves and flat bottoms. Turn the loose jaw so its half-round groove faces the fixed jaw's groove."],
         "YOU HAVE / THE TWO MATCHING PRINTS",f"The fixed base is {FIXTURE['BASE_X']:g} x {FIXTURE['BASE_Y']:g} mm. Both jaws support {FIXTURE['GRIP_Z']:g} mm of rod. Clamps join the parts; there are no assembly screws or inserts.",["S3"])
    page(c,3,"A / DRILL FIXTURE","Load the rod and loose jaw","The rod stands on the base floor; the loose jaw slides on that same floor.",fixture.load_jaws,
         "Exploded assembly: the loose jaw is offset to expose the seated rod. Set it on the base, then bring the two grooves together around the blank.",
         ["Saw a <b>50-60 mm handling blank</b> from the 9.5 mm rod and remove end burrs. Lay the fixed base on the wood backer at the drill table.",
          "Stand the blank in the fixed jaw's groove. Push it down onto the solid base floor; the blank projects above the jaws.",
          "Place the loose jaw flat on the base, groove inward. Slide it toward the rod so the two grooves surround the blank."],
         "YOU HAVE / A LOOSELY ASSEMBLED ROD HOLDER","One fixed base/jaw, one upright blank and one sliding loose jaw. The next page adds the two clamps that close it.",["S2","S3"])
    page(c,4,"A / DRILL FIXTURE","Close the jaws with two clamps","Use two of the four C-clamps here. Their screw axes run horizontally.",fixture.jaw_plan,
         "Top view. The A clamps press the front and rear outer jaw faces together, one on each side of the rod. Their frames wrap outward.",
         [f"Place one <b>A clamp on each side of the rod</b>, near the flat lands about {FIXTURE['JAW_CLAMP_X']:g} mm left and right of its axis.",
          "Put each pad on an outer jaw face. Turn the C-frame outward, away from the spindle; tighten the two clamps evenly.",
          "Keep the split between the flat jaw faces visible. The rod must resist turning, rocking and lifting by a firm hand check."],
         "YOU HAVE / THE ROD GRIPPED BETWEEN THE JAWS","The A clamps hold the rod. Leave them tightened while positioning the whole fixture under the stopped drill.",["S3","M1"])
    page(c,5,"A / DRILL FIXTURE","Attach the base to the table","The other two C-clamps fasten the base and wood backer to the drill table.",art.fixture,
         "A = the two horizontal jaw clamps already installed. B = the two vertical table clamps added here. The picture shows the complete setup.",
         ["Fit the <b>1/16-inch stub drill with power off</b>. After tightening the A clamps, move the whole fixture until the stopped tip meets the rod center.",
          f"Add one <b>B clamp on each base flange</b>, about {FIXTURE['BASE_CLAMP_X']:g} mm left/right of the rod. Clamp through the base and backer to a solid table edge.",
          "With the spindle stopped, lower the quill through the planned stroke and turn the chuck by hand. Check tool clearance and square approach from front and side."],
         "YOU HAVE / THE COMPLETE DRILLING FIXTURE INSTALLED","A grips the rod; B holds the base, backer and table together. Demonstrate the real grip and clearance on the first scrap blank.",["S3","M1"])
    page(c,6,"B / MAKE THE CAP","Set the drilling depth","The point passes beyond the cap's eventual back face.",art.depth,
         "Enlarged section. The orange cut plane marks the finished cap back face, not the bottom of the drill cone.",
         ["Touch the stopped drill tip to the rod's top face. Use that face as the <b>depth zero</b>.",
          "Set and prove the depth stop for <b>3-4 mm to the tip</b>. The full-diameter hole must extend past the eventual <b>2 mm cap</b> cut plane.",
          "Lock the stop. The drill ends inside the stock, well above the printed floor; it does not drill through the whole handling blank."],
         "YOU HAVE / THE AXIS AND DEPTH SET","Keep all four clamps in place. The next page makes the short hole in the long blank.",["S1","S2","M1"])
    page(c,7,"B / MAKE THE CAP","Drill the short passage","Cut chips, retract to clear them, then continue to the depth stop.",art.drilling,
         "The jaws stay clamped in all three pictures. Only the drill moves; the blank remains long enough to hold securely.",
         ["Unplug the press to set its belt to the <b>1100 rpm trial starting setting</b>. Close the cover, remove the chuck key and apply Tap Magic.",
          "Feed positively enough to cut chips. Retract to clear the flutes and renew fluid, then return to the proved stop without dwelling in one spot.",
          "Stop for rod or fixture movement, squeal, stalled cutting, excessive heat or wander. Let the spindle stop before brushing chips or making adjustments."],
         "YOU HAVE / A DRILLED END ON THE HANDLING BLANK","Release the jaws and take the rod to the saw. The small cap is cut off after drilling.",["S2","S3","M1"])
    page(c,8,"B / MAKE THE CAP","Cut off the drilled cap","Keep the retained rod in the vise; let the small cutoff fall free.",art.saw_finish,
         "The saw vise holds the retained stock. The larger drill at right is turned lightly by hand at each hole edge to remove a burr.",
         [f"Use the BA4555 and 24 TPI M42 blade at the low-speed trial setting. Account for the kerf and finish the cap to <b>{T:.2f} +/-{LIMIT['THICKNESS_TOL']:.2f} mm</b>.",
          f"Lightly remove the bore burrs at both ends: <b>{LIMIT['HOLE_EDGE_BREAK_MAX']:.2f} mm maximum edge break</b>. Keep the outside rim square for welding.",
          "The hole must be open at full diameter through both faces. Use JET-CAP-01 for the cap's finished limits before seating it on the elbow."],
         "YOU HAVE / THE FINISHED DRILLED CAP","For another cap, clear the jaw floor, reseat the rod and realign. Retire the handling blank below 40 mm, or sooner for chuck clearance.",["S1","S2","M2"])
    page(c,9,"C / WELD SETUP","Join the welding gas fittings","Assemble this temporary branch from the owned tee, adapters, tube and valve.",art.purge,
         "Connection order. The tee's straight run continues to the welder; its threaded branch reaches the elbow's female port through the metal fittings.",
         ["Close the cylinder and depressurize. Cut the regulated <b>6 mm hose</b> square, insert the tee and seat both hose ends fully.",
          "Thread the <b>FNPT coupling</b> onto the tee's male branch; add the first compression adapter. Join it to the needle valve with 1/4-inch OD stainless tube.",
          "Use the second tube link and adapter from the valve to the elbow's female port. Begin with the valve closed; the drilled jet is the open vent."],
         "YOU HAVE / THE GAS BRANCH ASSEMBLED","Set gentle internal flow and verify torch shielding with that branch open before welding. Operating details are in S2 and the X1 manual.",["S2","M3","M4"])
    page(c,10,"C / WELD SETUP","Seat the cap on the elbow","The cap goes on the male end that enters the carbonator.",fixture.cap_seating,
         "Two product parts and a local seating section. The purchased fitting profile is schematic; measure the actual bore and seating land.",
         ["Hold the bare elbow <b>male tip upward</b> in a metal fixture. Grip the body, keeping the threads and cap seating land accessible.",
          "Place the finished cap on the tip, centered and flat. Add a separate <b>metal cap restraint</b> clear of the jet hole and the tack locations.",
          "Connect the gas adapter at the female port and the X1 safety clip/interlock at the metal work. Keep the printed drilling fixture out of this station."],
         "HOLDING DETAIL TO RESOLVE","The body clamp and separate cap restraint are required. Their dimensions, hardware and fabrication details do not yet have an issued build package.",["S1","S2","S4","M3"])
    page(c,11,"D / WELD THE JET","Put the gun at the seam","The target is the cap-to-tip interface around the outside rim.",fixture.seam_closeup,
         "Enlarged joint. The drawn gun angle is for visibility; the actual nozzle, attitude and focus follow the machine setup for the trial joint.",
         ["Install the chosen nozzle. With output disabled, put the calibrated aim/focus at the <b>cap-to-tip seam</b> shown above.",
          "Rehearse access around the rim while the cap is restrained. Keep the wire endpoint at the joint and the small axial passage clear.",
          "Use the small-joint coupon settings for mode, power, swing, wire and travel. Keep shielding and the gentle internal flow established."],
         "YOU HAVE / THE GUN AIMED AT THE JOINT","The cap and elbow stay restrained while the first opposing tacks are made. Actual jet settings require the trial joint in S2.",["S2","S4","M3"])
    page(c,12,"D / WELD THE JET","Tack opposite sides","Join the first pair, then the other pair, while keeping the cap seated.",art.tacks,
         "Proposed handling order: top, opposite bottom, then right and opposite left. Black dots are completed tacks; coral marks the next location.",
         ["Make the first tack at <b>12 o'clock</b>. Release the trigger and check that the cap is still centered and seated.",
          "Tack opposite at <b>6 o'clock</b>, then make the <b>3 and 9 o'clock</b> pair. Reposition only with the trigger released.",
          "Keep the restraint clear of the active location. Stop if the cap lifts, shifts or the small jet opening changes."],
         "YOU HAVE / THE CAP LOCATED BY FOUR TACKS","The rim still needs the continuous circumferential weld on the next page. Keep the accepted tack order with the joint's settings.",["S2","S4","M3"])
    page(c,13,"D / WELD THE JET","Close the welded rim","Work opposing arcs, then connect the remaining sides and tie-ins.",art.weld,
         "Proposed travel order. Coral is the current arc; black is completed travel. Release the trigger before repositioning or changing the restraint.",
         ["Trace the seam at the selected focus, attitude, wire delivery and travel. Fuse the cap to the elbow while keeping the jet passage open.",
          "Work the opposing arc, then connect the other sides. Tie each restart into the existing fusion boundary until the rim is closed.",
          "The finished assembly is <b>JET-ELB-01 / HSM-000338</b>. Its cap projects into the carbonator headspace when the elbow is installed at top Port 2."],
         "YOU HAVE / THE WELDED WATER-INLET JET","The required fusion reaches the wetted root; a rim bead alone does not show it. Supporting qualification and post-build instructions are linked on p. 14.",["S2","S4","M3"])
    references(c);c.save()
    receipt={"geometry_mm":GEOM,"finished_limits_mm":LIMIT,"fixture_inputs_mm":FIXTURE,
             "primary_references":{k:{"title":v[0],"url":v[1]} for k,v in REFS.items()},
             "review_scope":"Jet and drilling-fixture assembly sequence; no physical build or qualification performed",
             "build_phases":{"drilling_fixture_pages":[2,3,4,5],"cap_pages":[6,7,8],"weld_setup_pages":[9,10],"welding_pages":[11,12,13],"support_page":14},
             "mesh_figures":{"pages":[2,3],"sources":["water-inlet-jet-fixture-fixed.stl","water-inlet-jet-fixture-loose.stl"]},
             "open_build_details":["dimensioned metal body holder and separate cap restraint"],
             "authored_trial_choices":["opposing four-tack handling sequence","alternating accessible quarter arcs; actual recipe depends on coupon"],
             "edition_date":"2026-10-27"}
    canonical=publish(PDF,GUIDE,TITLE,
          "14 illustrated Letter pages: assemble the drilling fixture, make the cap, set up and weld the jet",
          N,SOURCES,extra=receipt)
    (GUIDE/"guide-sources.json").write_text(PDF.with_suffix('.sources.json').read_text())
    print(f"Published {canonical} ({N} pages)")


if __name__ == "__main__":build()
