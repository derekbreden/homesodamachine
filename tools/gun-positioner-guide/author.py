"""Author the positioner's one-operation-per-page HTML shop guide.

Fabrication dimensions belong to the mechanical kit; electrical nets belong
to its controller manifest. This module adds assembly order, hand operations
and checks that make the build reviewable and repeatable.
"""
from __future__ import annotations

import html
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GUIDE = ROOT / "hardware/gun-positioner-guide"
PAGES: list[dict] = []


def load_geometry(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    module.init_parts()
    return module


def page(slug, title, lede, *, section, art=None, caption="", add="", tools="",
         actions=(), gate="", rows=(), headers=(), console="", note="", mind="",
         figure="", style="", fail="", mind_label="Keep this clear", gate_label="Ready when"):
    record = dict(slug=slug, title=title, lede=lede, section=section,
                  art=art, caption=caption, add=add, tools=tools,
                  actions=list(actions), gate=gate, rows=list(rows), headers=list(headers),
                  console=console, note=note, mind=mind, figure=figure, style=style)
    record.update(fail=fail,mind_label=mind_label,gate_label=gate_label)
    PAGES.append(record)
    return record


def foundation():
    page("cover", "Gun positioner<br>assembly guide",
         "Build one six-axis screw positioner and its camera observation station.",
         section="Home Soda Machine / Bench instructions", art="hero.png",
         caption="A complete mechanism for loaded dry commissioning. Motion is checked with the gun, liner and umbilical attached.",
         style="cover", note="170 mm XYZ · yaw/roll ±20° · pitch −20…+10° · Letter / actual size")
    page("what-you-build", "One gun, six axes",
         "Three guided translations carry a three-axis gimbal. The existing rotator supplies the tube's circumferential travel.",
         section="Before assembly", art="hero.png", figure="tall",
         caption="X, Y and Z translate the carriage. U, V and W extend the yaw, pitch and roll screws. The gun stays clamped during calibration and dry rotation.",
         mind="This kit assembles a mechanism for loaded dry commissioning. Nominal step spacing is 2.5 µm per full motor step. Attained 5 µm motion and live weld tracking require observed results. The controller has no laser, wire-feed or rotator output.",mind_label="Dry motion is this build's scope")
    page("read-the-pictures", "Read the pictures",
         "Each operation shows the part you add and the assembly that receives it. The ready check states what lets you continue.",
         section="Before assembly", art="visual-key.svg", figure="short",
         caption="Coral changes from page to page. It marks the present operation, not the permanent color of the part.",
         actions=["Sort hardware into the ADD tray before starting the operation.",
                  "Use the matching part IDs in the fabrication drawings and print filenames.",
                  "Read the ready check before installing a part that would hide the joint.",
                  "Print the book on Letter at actual size. Pictures are not drilling templates."],
         gate="The plate drawings and cut list set the dimensions. Electrical figures show named connections; their layout does not set physical connector pin order.",
         fail="If a part ID or connection differs, stop and reconcile it with the governing manifest before assembling that joint.")


def kit_and_preparation(gp,opt):
    page('whole-build','Build in this order',
         'Prove the inexpensive interfaces first. Add the gun only after the guides, transmission and independent retention are assembled.',
         section='Before assembly',art='whole-exploded.png',figure='short',
         caption='The major groups are separated for identification. The plate templates and individual steps set the assembly directions.',
         rows=[('Preparation','Coupon, printed parts, metal blanks, hubs and cut stock'),
               ('Transmission','Six supported screw drives and captured overload links'),
               ('Structure','Common base, X/Y/Z guides, yaw/pitch/roll gimbal'),
               ('Retention','Three friction retainers, crash release and independent catch'),
               ('Control','Metered power, drivers, loops, firmware and fault checks'),
               ('Observation','Two retracting camera stages and lens cassettes'),
               ('Dry commissioning','Loaded retention, actual response and repeated dry laps')],
         headers=['Group','What closes this dependency'],
         gate='A tube is removed and laser emission is disabled during initial assembly and retention checks.',
         fail='Adding a vessel before the loaded fault sweep is accepted can put it inside the mechanism\'s fall path. Keep the work area empty.')
    printed=[(n,d) for n,d in gp.PARTS.items() if d['kind']=='print']
    printed += [(n,d) for n,d in opt.PARTS.items() if d['kind']=='print']
    page('print-inventory','Print the named parts',
         'The filenames are the part IDs. Quantities below build one positioner and two observation stages, plus the fitting and drilling tools.',
         section='Kit / printed parts',art='print-parts.png',figure='short',style='reference',
         caption='Positioner parts shown flat on their fabrication plane. Camera cassette and retainer pictures appear in the observation chapter.',
         rows=[(f'<code>{n}</code>',str(d['quantity']),d['material']) for n,d in printed],
         headers=['Part / STL basename','Qty','Material'],
         note='Positioner STLs: <code>hardware/printed-parts/fixtures/gun-positioner/stl/</code>. Observation STLs: <code>hardware/printed-parts/fixtures/gun-positioner-observation/</code>.')
    metals=[(n,d) for n,d in gp.PARTS.items() if d['kind']=='metal' and d.get('blank_mm')]
    metals += [(n,d) for n,d in opt.PARTS.items() if d['kind']=='metal']
    for group_index in range(0,len(metals),12):
        chunk=metals[group_index:group_index+12]
        page(f'metal-inventory-{group_index//12+1}',f'Metal kit / {group_index//12+1}',
             '6061 aluminum dimensions are finished blank sizes. Bought angles remain angles; shafts, bearings and guide blocks are separate purchased parts.',
             section='Kit / fabrication',art=f'metal-kit-{group_index//12+1}.png',figure='short',style='reference',
             caption='Pictured rows, left to right, follow the table below. Each actual CAD part uses its own display scale; table dimensions and hole coordinates govern.',
             rows=[(f'<code>{n}</code>',str(d['quantity']),' × '.join(f'{v:g}' for v in d['blank_mm'])) for n,d in chunk],
             headers=['Part','Qty','Finished blank / mm'],
             note='Use <code>gun-positioner-drill-templates.pdf</code> at actual size. The 3D STEP and registered projections govern formed angles and hub faces.')
    joints=json.loads((ROOT/'hardware/printed-parts/fixtures/gun-positioner/fasteners.json').read_text())
    for first in range(0,len(joints),12):
        chunk=joints[first:first+12]
        page(f'fastener-inventory-{first//12+1}',f'Mechanism fasteners / {first//12+1}',
             'These are installed joint counts. Purchase packs are counted in the Prime checklist; the camera fasteners are listed in its own assembly operations.',
             section='Kit / joint hardware',art='visual-key.svg',figure='short',style='reference',
             rows=[(j['joint'],j['fastener'].replace('x',' × '),str(j['quantity'])) for j in chunk],
             headers=['Joint / schedule ID','Fastener','Qty'],
             note='The fastener schedule also records washers, nut type, grip and thread projection. Temporary service bolts explicitly marked for reuse are counted once in purchases.')
    page('purchase-kits','Sort the purchased kits',
         'Use the Prime purchase checklist for pack quantities and stock credit. These are the assembly counts of the main purchased interfaces.',
         section='Kit / purchases',art='gimbal.png',figure='short',style='reference',
         caption='Metal bearings support each gimbal output independently of its screw transmission.',
         rows=[('SBR12 × 400 mm supported rails / blocks','10 rails / 20 blocks','6/12 positioner; 4/8 cameras'),
               ('NEMA17 / TMC2209','6 / 6','One motor and driver per screw'),
               ('TR8×2 metal nuts',str(gp.PARTS['tr8x2-nut']['quantity']),'Two fixed-end + one driven nut per screw'),
               ('F8-16M thrust bearings','12','Two opposed bearings per drive'),
               ('KP08 screw radial bearings','9','Six fixed ends + three XYZ floating ends'),
               ('12 mm output bearings','6','Two per gimbal axis'),
               ('GT2 20T pinions / 6 mm belts','6 / 6','4:1 with six printed 80T pulleys'),
               ('Spring friction retainers','3','Z, pitch and roll; separate torque windows'),
               ('FoMaKo K20UH / Raynox DCR-250','2 / 2','Dry observation')],
         headers=['Interface','Assembly count','Use'],
         note='Purchase checklist: <code>hardware/gun-positioner/purchases.md</code>. Buy pack quantities there; do not buy this table a second time.')
    page('tools','Put the tools at the bench',
         'The existing drill press, metal saw, caliper, scale, soldering station and meter cover the work. The purchase checklist identifies additional cutting sizes.',
         section='Kit / tools',art='hub.png',figure='short',style='reference',
         caption='The hub fixture positions a blank for marking. Metal stock is independently clamped before any drilling or reaming.',
         rows=[('WEN metal saw / file / deburrer','Square stock cuts, edges and threaded-screw ends'),
               ('WEN drill press / vise / clamps','Template holes, angle holes and square hub bores'),
               ('Drills / 12 mm reamer','Clearance sizes in the templates; shaft-hub bore'),
               ('M5 × 0.8 tap / wrench / 4.2 mm drill','Eight centered blind shaft-end threads'),
               ('25 in-lb cam-over tool / H3 bit','Controlled two-bolt hub clamp setting'),
               ('NEIKO caliper / square / rule','Stock size, bolt grip, rail spacing and neutral marks'),
               ('Hex keys 2.5 / 3 / 4 / 5 / 6 mm','M3, M4, M5, M6 and M8 socket screws'),
               ('Wrenches / sockets 5.5 / 7 / 8 / 10 / 13 mm','M3, M4, M5, M6 and M8 nuts'),
               ('Smart Weigh scale / 100 mm torque lever','Brake breakaway mass'),
               ('500 N gauge / vertical backing plate','Spring-rate grading and opposed overload-trip calibration'),
               ('Hakko iron / ferrule crimper / wire stripper','Fixed control backplane and harness'),
               ('AstroAI meter / existing indicator','Electrical checks and coarse displacement checks')],headers=['Tool','Operation'],
         gate='Each drill/driver size named in the fabrication kit is present before its part is cut.',
         fail='A close imperial drill is not a fit specification. Obtain the listed size or update the mating joint and its template together.')
    page('coupon','Start with the pulley sector',
         'One short print checks whether the purchased 6 mm GT2 belt seats in the printed tooth geometry before six pulleys occupy the printer.',
         section='Preparation / print',art='coupon.png',
         caption='The coupon is cut from the actual 80-tooth pulley. Its broad fabrication face is down on the print bed.',
         add='1 pulley-sector-coupon · purchased 6 mm GT2 belt',tools='Hardened 0.4 mm nozzle · 0.20 mm layer · caliper',
         actions=['Slice the coupon flat in PET-GF with the same profile used for the pulleys.',
                  'Let it cool flat, then clear loose strands without filing the tooth flanks.',
                  'Wrap the belt onto the sector and seat adjacent teeth with light finger pressure.',
                  'Check that the belt sits at one consistent depth and lifts away without catching.'],
         gate='Adjacent teeth seat together without forcing, gaps or a raised belt section.',
         fail='A belt that bridges or rocks indicates a profile/print-fit error. Correct that interface and repeat the coupon before printing the pulleys.')
    page('print-recipe','Print the carriers and guards',
         'Printed pieces locate and cover metal joints. Their flat fabrication face belongs on the bed; the guide pictures show the assembly pose separately.',
         section='Preparation / print',art='print-parts.png',figure='short',
         caption='Print the open guard facing up. Pulley flanges, motor plates, spacers and locator tools lie flat.',
         add='All PET-GF parts from the print inventory',tools='Hardened 0.4 mm nozzle · PET-GF filament profile',
         rows=[('Layer / walls','0.20 mm / 6'),('Top / bottom','6 layers / 6 layers'),('Infill','40% gyroid; 100% for ≤4 mm parts'),
               ('Support','None on the flat fabrication orientation'),('Bed','Broad fabrication face down; dry filament before printing')],headers=['Starting recipe','Setting'],
         actions=['Keep holes and nut pockets free of brim and loose strands.',
                  'Reject a lifted motor plate, cracked pulley flange or separated wall.',
                  'Fit metal nuts and fasteners by hand before duplicating the part.'],
         gate='Each part sits flat on its mating metal face and its fasteners pass without splitting the wall.',
         fail='A forced fit changes alignment and can crack the part. Correct print compensation at that interface; do not use screw force as the fit tool.',
         note='This is a fabrication starting recipe. It does not establish heat resistance, wear or an axial load rating for the prints.')
    mount=json.loads((ROOT/'hardware/gun-positioner/mounting/manifest.json').read_text())
    page('controller-print-kit','Print the fixed controller mounts',
         'The control board uses unfilled clear PETG as its electrical insulator. Three supplied models provide the blank, board clearance and guarded fan support.',
         section='Preparation / controller prints',art='controller-print-parts.png',figure='short',style='compact',
         caption='Actual fabrication solids: 300 × 300 × 6 mm blank, one 6 mm spacer shown of 28, and the 90 mm fan stand. Assembly poses differ from their print orientations.',
         rows=[('<code>'+p['id']+'.stl</code>',str(p['quantity']),p['print_orientation']) for p in mount['parts']],
         headers=['File / mounting directory','Qty','Bed face'],
         tools='Owned SunTop unfilled clear PETG · H2C · 0.4 mm nozzle',
         actions=['Use 0.20 mm first / 0.24 mm normal layers, four walls, six top/bottom layers; 40% gyroid panel/stand and solid spacers.',
                  'Use a 5 mm brim. Print the blank separately: its 310 × 310 mm brim footprint fits the conservative 325 × 320 mm H2C envelope.',
                  'Use the supplied fan-stand STL with its rear wall on the bed and airflow bore vertical. Inspect each part’s own slice.'],
         gate='The cooled blank is flat, spacer bores are clear and all supplied orientations print without supports.',
         fail='Warp, split spacers or a changed bed envelope fails this mounting set. Correct the material/profile/orientation before drilling.',
         note='Files: <code>hardware/gun-positioner/mounting/</code>. Use unfilled clear PETG B0FP34MJ94 for these fixed insulators; their 50°C installed thermal gate remains required.')
    page('prepare-blanks','Prepare the metal blanks',
         'Finished blank sizes are in the metal inventory. Drill holes from the actual-size template and transfer the catalog mounting patterns called out by the part.',
         section='Preparation / metal',art='metal-preparation.png',figure='short',
         caption='Actual X bed, drive bulkhead, shaft hub and formed angle at independent display scales. The named templates and STEP files govern dimensions.',
         add='6061 plate blanks · metal angle blanks',tools='Saw · square · caliper · file · templates at 100%',
         actions=['Cut and label every blank by its part ID; deburr both faces and all edges.',
                  'Print the required template tiles at actual size and measure each 50 mm check bar.',
                  'Align the red registration crosses, tape the tiles and center-punch the hole centers.',
                  'Clamp the stock at the drill press. Drill the stated diameters; finish slots and windows to the template.'],
         gate='The 50 mm scale bar measures 50 mm, the blank matches its named dimensions and no burr props a mating face apart.',
         fail='A scaled template moves every hole. Correct the print setting and use a new template before drilling the blank.')
    page('prepare-hubs','Make seven clamping hubs',
         'The reamed bore centers a plain 12 mm shaft. Two grade 12.9 clamp bolts close the split hub; each assembled joint receives a measured torque proof before carrying a frame.',
         section='Preparation / metal',art='hub.png',
         caption='38.1 × 38.1 × 25 mm metal hub. Four mounting holes form a 26 × 20 mm rectangle. The shaft stays free of transverse holes.',
         add='7 shaft-hub blanks · plain 12 mm shafts',tools='Drill press · 12 mm reamer · actual-size face projections · vise',
         actions=['Drill and ream the central bore square to the hub\'s broad face.',
                  'Drill the four 5.5 mm holes on the 26 × 20 mm rectangle from the fabrication drawing.',
                  'Deburr the reamed bore without rounding its locating surface. Remove swarf from every hole.',
                  'Trial-fit and label the plain shaft/hub pair. Keep the four mounting holes clear of the split and clamp passages.'],
         gate='The plain shaft enters the square bore by hand without rocking or being driven into it.',
         fail='A loose, tapered or skewed bore fails the locating fit. Correct the metal hub before closing its clamp.')
    page('hub-clamps','Close the split hub clamps',
         'Two bolts tighten the same split bore onto its plain shaft. Hand fit and controlled tightening precede the assigned torque proof of each hub in both directions.',
         section='Preparation / metal',art='hub-clamps-exploded.png',
         caption='Coral shows both M4 × 50 bolts, four washers and two locking nuts separated along their actual X insertion axes. Each bolt passes through a head-side washer, the hub, a far-side washer and its nut; use the purchased socket-head hardware.',
         add='14 M4 × 50 grade 12.9 clamp bolts · 28 flat washers · 14 locking nuts',tools='Metal saw · 4.2 mm drill · independently clamped metal stock · 3 mm hex / 7 mm wrench',
         actions=['Cut the 1.5 mm slit from the +Y edge 2 mm into the bore, so it opens fully. Keep it clear of the four plate holes.',
                  'Drill both 4.2 mm passages through the hub at Y = 16 mm, Z = 6 and 19 mm from its registered side-face projection.',
                  'Clean the bore and shaft, fit the assigned plain shaft and start both grade 12.9 bolts with washers and locking nuts.',
                  'Confirm both bolt passages cross only the hub’s split side; keep the plain shaft/hub pairs labeled for controlled tightening.'],
         gate='The slit and both clamp passages are clear, the plain shaft fits its bore and both bolts are ready for controlled tightening.',
         fail='A rocking bore, cracked hub, closed slit without grip or distorted shaft fit fails assembly. Correct the machined fit before applying proof load.')
    page('hub-tightening','Set both clamp bolts with the torque tool',
         'A controlled bolt setting precedes the measured hub proof. Increasing bolt torque to rescue a slipping hub exceeds this build’s clamp setting.',
         section='Preparation / metal',art='hub-clamps-fitted.png',
         caption='Both actual clamp sets are fitted at Y = 16 mm, Z = 6 and 19 mm. The plain shaft has no transverse hole; separate end retainers capture its axial position. Tighten at the socket head while holding its nut.',
         add='No new parts',tools='LEXIVON cam-over torque screwdriver · H3 metric bit · 7 mm wrench · supplied calibration certificate',
         rows=[('Tool setting','25 in-lb / 2.8246 N·m'),
               ('Clockwise tool upper bound','2.9376 N·m at +4%; below 3.0 N·m ceiling'),
               ('Grip qualification','Every hub: its assigned complete torque interval, both signs')],
         headers=['Property','Required setting / record'],
         actions=['Record the tool’s supplied calibration certificate and serial; confirm its clockwise accuracy and setting units.',
                  'Fit the H3 bit and hold each locking nut stationary with the wrench. Drive clockwise at the bolt head.',
                  'Alternate the two bolts through 10, 20 and finally 25 in-lb settings; let the cam-over tool trip at each setting.',
                  'Record both bolts’ setting and add witness marks. Nylock drag is included in the indicated torque and reduces clamp preload.'],
         gate='Both bolts have recorded controlled settings, the shaft fit remains smooth and the joint is ready for supported torque proof.',
         fail='A failed tool certificate, damaged bit, distorted bore or later failed grip proof rejects this setting/joint. Correct the fit or replace the hub; never raise clamp torque to obtain a pass.')


def shaft_qualification(gp):
    required=json.loads((ROOT/'hardware/printed-parts/fixtures/gun-positioner/requirements.json').read_text())
    taps=required['fabrication']['shaft_end_threads']
    proof=required['shaft_hub_qualification']
    capture=required['shaft_axial_capture']
    capture_geometry=capture['fixture_geometry']
    page('shaft-end-taps','Tap eight centered shaft ends',
         'The four plain shafts receive blind axial threads for their positive end retainers. Complete the end holes before proving a hub on its final shaft seat.',
         section='Preparation / shaft ends',art='shaft-end-threads.svg',figure='short',style='compact',
         caption='The shaft body stays free of transverse holes. Only the end-centered M5 × 0.8 keeper threads are added.',
         add='Four 12 mm shafts: '+', '.join(f'{v:g}' for v in taps['shaft_cuts_mm'])+' mm · eight M5 × 12 keeper screws',
         tools='4.2 mm drill · depth stop · M5 × 0.8 tap and wrench · metal vise · caliper / depth probe',
         rows=[('Each end pilot',f'Ø{taps["pilot_diameter_mm"]:g} × {taps["pilot_depth_mm"]:g} mm deep'),
               ('Usable full thread',f'≥{taps["usable_full_thread_depth_mm"]:g} mm; pilot depth includes the tap lead'),
               ('Nominal screw reach','12 − 2 − 0.8 = 9.2 mm; measure the actual washer stack')],
         headers=['Feature','Required finished result'],
         actions=['Cut, square and deburr the four lengths. Clamp each shaft independently; center-punch its end and drill the centered pilot with a depth stop.',
                  'Tap square to the end with cutting fluid; advance and back off to clear chips. Finish usable threads to the measured depth, then remove all swarf and fluid.',
                  'Check each actual screw through its 2 mm steel keeper and 0.8 mm flat washer: ≥8 mm engagement and ≥0.8 mm bottom margin. Label both ends and the shaft.'],
         gate='All eight centered threads have verified usable depth and keeper reach without bottoming; shaft/hub contact remains clean and dry.',
         fail='A skewed, unmeasurable or incomplete tap fails positive capture. Correct or replace the shaft before applying its final-seat hub proof.')
    page('shaft-capture-tubes','Finish fourteen metal capture tubes',
         'Tubes connect metal hubs and plates to bearing inner races and end washers. Their actual finished lengths establish captured axial movement without loading seals or outer races.',
         section='Preparation / shaft capture',art='yaw-shaft-capture.png',figure='short',style='reference',
         caption='Actual yaw shaft capture, highlighted in coral; the backplate is omitted to expose the shaft. The measured delivered inner-race faces set the final fit.',
         add=f'{capture["pieces"]} tubes from 20 OD / 12 ID aluminum stock · 12.5 mm finished bore',
         tools='Metal saw · 12.5 mm drill · caliper · file / deburrer · actual bearings',
         rows=[(axis,' · '.join(f'{v:g}' for v in lengths)) for axis,lengths in capture['nominal_lengths_mm_by_shaft'].items()],
         headers=['Shaft / local stack','Nominal tube lengths / mm'],
         actions=['Bore stock to 12.5 mm before cutting. Cut and label the source lengths; deburr both ends without rounding a load face.',
                  'Fit each tube against its actual metal face. Relieve/chamfer its 20 mm OD to touch only the delivered bearing inner race.',
                  'Finish the metal stack for ≤0.5 mm one-sided freedom and ≤1 mm total captured excursion. Do not force a bearing housing into alignment by tightening an end bolt.'],
         gate='Every tube has metal face contact, clears the seal/outer race/housing and permits free rotation with its captured movement bounded.',
         fail='A rubbing tube, outer-race load or unknown end clearance fails the stack. Finish the actual spacer contact before restoring an end keeper.')
    page('hub-proof-support','Build the supported hub proof fixture',
         'Every hub is tested as the ungripped specimen on its own final marked shaft seat. A companion hub reacts torque through a metal plate gripped in the vise.',
         section='Preparation / hub qualification',art='hub-clamp-proof.png',figure='short',style='compact',
         caption='Actual fixture: the horizontal beam and one borrowed bearing support the completed shaft. The vise envelope marks the free reaction-plate grip; it must clear both hubs and bare shaft.',
         add='Reuse 500 mm test column · one KP001 / pitch-bearing-foot · companion hub · angular-lever reaction plate · source support fasteners',
         tools='Bolted vise · independent noncontact catches · indicator · source actual-seat table',
         actions=['Secure the horizontal 4040 column to the bench. Bolt the vise through its actual factory slots with the temporarily reused bench anchors.',
                  'Mount KP001 on the borrowed foot with two 10 mm metal risers / M6 × 40 screws. Attach the foot with two M8 × 16 / slot8 joints; position its bearing from the next page’s table.',
                  'Bolt the reaction plate to a companion hub with four M5 × 45 screws. Grip only its free metal area in the vise; keep the shaft and both hubs clear of vise pressure.',
                  'Keep a visible 1 mm gap between hub faces. Remove or visibly clear all end keepers/tubes from the proof lever, specimen and companion; position independent catches without contact.'],
         gate='The shaft is supported, the beam/vise cannot move and torque can pass from proof lever through the specimen clamp only.',
         fail='Hub-face contact, keeper contact, shaft grip or catch load bypasses the clamp. Unload and correct the actual fixture before recording a proof.')
    page('hub-proof-seats','Place each hub on its actual final seat',
         'All dimensions run along the completed shaft from the same marked end. Shift or reflect the canonical fixture; each of the seven hubs must become the specimen.',
         section='Preparation / hub qualification',art='hub-proof-joint.png',figure='short',style='reference',
         caption='Canonical terminal setup: specimen 0…25, companion 26…51 mm, reaction plate 51…57.35 mm and bearing center 66.35 mm. Keep the 1 mm gap visible.',
         rows=[(r['hub'],str(r['shaft_length_mm']),f'{r["specimen_mm"][0]:g}…{r["specimen_mm"][1]:g}',
                f'{r["companion_mm"][0]:g}…{r["companion_mm"][1]:g}',f'{r["bearing_center_mm"]:g}') for r in proof['actual_seats']],
         headers=['Specimen hub','Shaft / mm','Specimen / mm','Companion / mm','Bearing center / mm'],
         actions=['Mark the final shaft/hub seat and its orientation before changing the temporary support position.',
                  'Check the actual lever, companion plate, bearing body and end-clearance stack at every shifted/reflected setup.',
                  'Record every specimen separately. Serving only as a reaction hub does not qualify that hub’s grip.'],
         gate='All seven recorded specimens use their own final marked seats on the completed end-tapped shafts.',
         fail='A proof on a different shaft surface, unmarked seat or interference in a reflected fixture does not accept the installed contact. Correct and repeat that specimen.')
    page('hub-proof-lever','Attach the dedicated 140 mm proof lever',
         'The balanced proof lever and its metal saddle place the gauge force in the lever’s axial midplane. The separate 100 mm service lever stays reserved for installed load measurement.',
         section='Preparation / hub qualification',art='hub-proof-joint.png',
         caption='300 × 30 × 6.35 mm proof lever: ±140 mm load holes, 12.5 mm center clearance and four M5 mounting holes on 26 × 20 mm. The saddle straddles the lever.',
         add='hub-proof-lever · hub-proof-load-saddle · two borrowed metal angles · four M5 × 45 · two M5 × 20 · one M5 × 25',
         tools='Hex keys / wrenches · caliper · specimen joint at qualified clamp setting',
         actions=['Attach the proof lever to the specimen with four M5 × 45 bolts; the shaft center stays clear of the 12.5 mm bore.',
                  'Transfer two 25.4 mm metal angles to the saddle. Use the M5 × 25 cross tie through the selected 140 mm load hole.',
                  'Join the bridge to both angle feet with the two M5 × 20 screws. Confirm the gauge contact plane lies at the lever’s axial midplane.',
                  'Measure actual pivot-to-force radius and prepare the opposite load hole for the second torque sign. Keep catch/keeper/companion clearance visible.'],
         gate='Only the specimen hub connects the proof lever to its shaft, and the metal saddle carries the aligned load at the measured radius.',
         fail='An offset bolt-end contact, central shaft contact or overlapping hub face changes the bending/torque fixture. Unload and correct the metal load path.')
    page('hub-proof-gauge','Mount the proof gauge under the quill',
         'The gauge points down onto the saddle. A metal angle cap receives the quill load and the rear mounting screws retain the gauge body; the drill motor stays unplugged.',
         section='Preparation / hub qualification',art='hub-proof-gauge.png',
         caption='Actual gauge backing, four 7 mm rear spacers and formed angle cap. The blue gauge body is its catalog envelope; received screw-depth and physical alignment checks remain required.',
         add='500 N gauge · 70 × 110 backing · four 7 mm spacers / M4 rear screws · proof-gauge-quill-cap · two M5 × 25',
         tools='Unplugged drill press · metal vise support · depth check · force calibration / uncertainty record',
         actions=['Fit four 7 mm rear spacers and the dedicated proof set of four M4 × 25 screws, with its eight large washers. Finish to actual socket depth; keep the shorter ordinary-backing set separate.',
                  'Attach the cap to the backing with two M5 × 25 bolts. Verify all heads/spacers clear the received case; no quill force touches its plastic enclosure.',
                  'Center the quill on the horizontal cap leg and the downward M6 compression probe on the saddle, with force tangential to the lever.',
                  'Tare and check the gauge, record total force/alignment/radius uncertainty and verify every noncontact catch before advancing the quill.'],
         gate='The complete force path is quill → metal cap → gauge load cell/probe → metal saddle → proof lever, with no bypass contact.',
         fail='A loaded case, skewed probe, uncertain force bound or fixture contact fails this setup. Unload and correct it before torque qualification.')
    page('hub-proof-acceptance','Prove each clamp in both torque signs',
         'Advance the manual quill slowly, record the complete force bracket and hold for ten seconds. Qualification accepts the entire measured torque interval inside the assigned band.',
         section='Preparation / hub qualification',art='hub-clamp-proof.png',figure='short',style='compact',
         tools='Force / radius / tangency records · indicator baselines · visible witness marks · 10 second timer',
         rows=[('Pitch drive-lever / negative-side pitch output','30…32.5 N·m','About 224 N at 140 mm'),
               ('Other five hubs','25.2…27.5 N·m','About 188 N at 140 mm')],
         headers=['Specimen group','Full accepted interval','Nominal target only'],
         actions=['Record baseline shaft/lever indicator readings and hub/clamp witnesses. Increase force quasi-statically without impact; hold ten seconds.',
                  'Use the actual radius, tangency and total uncertainty to bound torque. Move saddle/gauge to the opposite load hole and repeat the other sign.',
                  'Unload after each sign and repeat the same before/after indicator reading. Record all seven specimens and both signed results.'],
         gate='Each complete torque interval lies inside its band, with no slip, changed witness, catch/fixture contact, crack or resolved residual twist/runout change.',
         fail='Any failed interval or permanent shaft change rejects the specimen. Replace a changed shaft or correct/refabricate the hub; never raise clamp torque or motor current for a pass.',
         note='The existing 0.013 mm indicator is a coarse no-set screen. Restore metal capture, qualified clamp settings and witnesses after proof. Warm reproof follows 50 supervised reversals; this is assembly screening, not lifetime acceptance.')
    page('shaft-capture-proof-seats','Choose the capture interface face',
         'Use the nearer shaft end from this source table and point that end upward. Test every real hub path with its completed shaft, output plate, bearings, tubes and end keepers.',
         section='Preparation / shaft qualification',art='shaft-capture-joint.png',figure='short',style='reference',
         caption='Canonical 85 mm positive-pitch shaft: the symmetric bridge extends beyond its chosen terminal end. The real output plate stays installed.',
         rows=[(r['hub'],f'{r["face_u_mm"]:g}',f'{r["nearest_end_u_mm"]:g}',
                '−u' if r['outward_sign']<0 else '+u') for r in capture['interface_face_by_hub']],
         headers=['Actual hub path','Face u / mm','Nearest end u / mm','Outward'],
         actions=['Use the shaft’s same marked local u datum from its service capture table; mirror the retained fixture for the chosen outward face.',
                  'Retain the real output plate. If it occupies the chosen face, stack the separate interface outside it with the measured through-joint grip.',
                  'Record every hub and both signed capture results. Neither another shaft surface nor only the terminal output path accepts an internal drive hub.'],
         gate='The selected near end and actual interface face match this shaft’s installed capture path.',
         fail='A substituted plate, omitted tube or proof of a different path fails this preparation. Reassemble the actual service stack before qualification.')
    page('shaft-capture-proof-support','Build the axial capture proof fixture',
         'Prove the actual end washers, threads, tubes and bearing inner races before carrying a frame. The complete bare axis uses its real output plate; the gun and gravity payload stay independently supported.',
         section='Preparation / shaft qualification',art='shaft-capture-proof.png',figure='short',style='compact',
         caption='Canonical positive-pitch shaft, actual capture tubes/keepers and output plate. The braced column supports the bearing foot; a symmetric bridge applies gauge force coaxially beyond the terminal end.',
         add='Reuse completed bare axis / 500 mm column · two capture-bearing-riser tubes · joined catch plates / two 7.85 mm tubes / two borrowed M5 × 35',
         tools='Both supplies unplugged · drill motor unplugged · independent catches · actual-axis source dimensions',
         actions=[f'Brace the reused 500 mm column vertically. The canonical 85 mm shaft uses bearing center u = 65 mm, two {capture_geometry["bearing_risers_mm"]:g} mm metal risers, M6 × 40 bearing bolts and M8 × 16 / slot8 foot joints; other axes retain their actual bearing separation.',
                  'Install the actual output plate, shaft and finished service tubes/keepers. Restore measured end-bolt reach and the bounded axial clearance.',
                  'Join drive-test-foot and capture-catch-upper at their far ends with the two 7.85 mm tubes / M5 × 35 joints. Grip only the joined far metal in the anchored vise. Set nominal 0.75 mm gaps above/below the interface, clear of shaft and keeper.',
                  'Grade catch gaps so actual capture plus elastic movement clears them and their secondary bound is ≤1 mm. After securing this support, loosen hub clamps / bearing setscrews enough to remove axial friction grip.',
                  'Verify smooth free movement within the recorded capture gap. Record bearing positions and keeper witnesses; the actual end keepers and every service tube stay installed.'],
         gate='Axial force can pass through the actual plate, retained metal stacks, end threads and inner races; clamp friction, support and catch carry no proof load.',
         fail='A substitute plate, eccentric contact, friction bypass or fixture/case contact fails the setup. Support/unload the axis and correct its actual reaction path.')
    page('shaft-capture-proof-bridge','Fit the symmetric capture bridge',
         'The bridge applies force on the shaft axis beyond the terminal end. Its interface opening clears the end keeper; its four ties remain outside the hub mounting pattern.',
         section='Preparation / shaft qualification',art='shaft-capture-joint.png',figure='short',style='compact',
         caption='100 × 60 mm interface and closed bridge, separated by four 75 mm metal tubes. The central Ø22 interface clearance surrounds the complete OD20 keeper.',
         add='shaft-capture-interface · shaft-capture-bridge · four 75 mm capture-bridge-spacer tubes · four borrowed M3 × 100 ties · four borrowed M5 × 80 joints',
         tools='Hex keys / wrenches · caliper · actual captured travel / thread-projection check',
         rows=[('Interface clearance','Ø22 around OD20 keeper, flat and socket head'),
               ('Bridge ties','60 × 40 mm; outside 26 × 20 mm hub pattern'),
               ('Nominal tie stack','92.7 mm; verify actual grip and two full projecting threads')],
         headers=['Feature','Source dimension / fitting gate'],
         actions=['Keep the real service plate installed. Attach the interface to the hub face with the four temporarily borrowed M5 × 80 joints.',
                  'Join the closed bridge through four 75 mm metal 8 OD / 6 ID tubes with the borrowed M3 × 100 ties, washers and nuts.',
                  'Leave 0.2 mm locating slack so the ties do not preload capture. Verify all tie tails, fittings and the complete keeper/head envelope stay visibly clear throughout captured travel.'],
         gate='The symmetric bridge is retained, the central keeper clears and load can enter the hub/service plate through metal without touching the shaft end.',
         fail='Bridge, tie, head or spacer contact with a keeper or shaft bypasses capture. Unload and correct the measured clearance before applying force.')
    page('shaft-capture-proof-gauge','Guide the gauge for push and pull',
         'Compression moves the gauge body toward the bridge with the manual quill. Tension moves the freely guided body away with the M6 jack; both paths pass through the load cell.',
         section='Preparation / shaft qualification',art='shaft-capture-gauge.png',figure='short',style='compact',
         caption='Rear view with fixed column omitted: the slotted backing slides on two metal guide joints. The bridge, steel coupling and gauge shaft stay connected for both signs.',
         add='500 N gauge · installed-Z-gauge-back / proof-gauge-quill-cap · proof rear-screw set / four 7 mm tubes · two 9.825 mm guide tubes / M6 × 25 · M6 × 16 / 1 mm washer / steel coupling',
         tools='Unplugged drill press · 10 mm wrench · thread-depth marks · gauge zero / force-uncertainty record',
         actions=['Use the dedicated four proof M4 rear screws, four 7 mm tubes and two 12 OD washers per screw on the 70 × 160 slotted backing. Measure its 15.35 mm external grip, ≥4 mm engagement and no bottoming in the actual gauge sockets.',
                  'Install the cap and existing manual jack. The two 9.825 mm metal guide tubes / M6 × 25 joints retain the backing laterally while its slots slide freely; keep the column braces tight.',
                  'Fit M6 × 16 through the closed bridge with one 1 mm washer. Hand-fit the steel M6 × 1 coupling to this captured bolt and the gauge shaft; mark ≥6 mm engagement each end without bottoming or thread-end contact. Keep this connection for both signs.',
                  'Keep the case, backing, cap and jack clear of hub, shaft, keeper and catch. Record force sign, zero/check and total uncertainty before either load.'],
         gate='The received threads fit freely, both force paths are coaxial, the gauge body feeds smoothly and the chuck has ≥10 mm downward travel above the metal cap.',
         fail='A forced thread, short engagement, loaded case, stuck guide or insecure press/column position fails the fixture. Unload onto the independent support and correct it; keep the braces tight.',
         note='The CAD column-base datum is a fixture reference. With the press unplugged and quill near mid-stroke, anchor the column below the press work-surface datum as needed using the matched brackets / kit joints. Place the cap under the chuck with ≥10 mm downward travel. Positively anchor press, fixture support and independent catch; no loose blocks or hand support.')
    page('shaft-capture-proof-load','Prove both axial capture directions',
         'Increase the force quasi-statically and hold ten seconds. Accept the entire measured interval, including gauge, fixture, alignment, gravity/baseline, load-step and hold uncertainty.',
         section='Preparation / shaft qualification',art='shaft-capture-proof.png',figure='short',style='compact',
         tools='Force-gauge log · 10 second timer · caliper / indicator baselines · independent catch',
         rows=[('Complete proof interval','450…500 N, each capture direction'),
               ('Captured movement','≤0.5 mm one-sided freedom; ≤1 mm total'),
               ('Load line','Coaxial through the symmetric bridge; clear of terminal keeper')],
         headers=['Property','Acceptance / source geometry'],
         actions=['Record baseline straightness/runout, keeper witnesses and free axial movement. Withdraw the jack; feed the quill against the cap for compression, keeping the coupling connected. Hold the accepted force interval ten seconds, then unload completely.',
                  'Withdraw the quill for tension, keeping the coupling connected. Hold the lower jack nut, loosen the upper lock nut, advance ≤1/12 turn (0.0833 mm) and relock before each reading. Hold ten seconds, then unload.',
                  'Repeat the same baseline observations after each sign. Stop immediately on deformation, loss of support, fixture/catch contact or force outside the band.',
                  'Test every actual hub capture path in both signs. Restore service joints, both qualified clamp settings, bearing setscrews, keepers and witnesses; reprove disturbed grip and observe a fresh datum before motion.'],
         gate='Both complete force intervals pass with no yielding, release, catch contact, excessive movement or resolved residual shaft/washer/tap/plate change.',
         fail='Any failed stack or unbounded uncertainty rejects capture. Replace a deformed shaft/keeper or correct the metal fit; restore a passing grip/capture record and fresh physical datum before motion.',
         note='Repeat after the warm/cycled hub check. These static proofs accept the recorded assembled paths and temperature; they do not establish bearing life, fatigue life or micrometer positioning accuracy.')


def drive_assembly():
    page('drive-metal-floor','Build the metal drive foundation',
         'A metal floor and paired metal stanchions support the motor and thrust bulkhead. Their angles carry the transmission reaction into the parent bed or clevis.',
         section='Screw drives / six copies',art='drive-foundation.png',
         caption='Coral identifies the metal motor/thrust legs and their angle joints on the 150 × 150 mm floor. The motor plate and bulkhead follow on their measured axes.',
         add='Per drive: linear-drive-support · 2 motor-support-leg · 2 thrust-support-leg · 8 plain angles / guard-thrust-angle-minus / guard-thrust-angle-plus; angular drives also 2 thrust-angle-pad',tools='Named fabrication drawings · square · caliper · M5 angle-joint hardware',
         actions=['Identify the floor and the 100 mm motor legs / 42.65 mm thrust legs. Transfer each actual angle’s pattern onto its named metal stations.',
                  'Build both motor legs with their lower and upper metal angles. Keep the top slot-support faces parallel and square to the floor.',
                  'Build both thrust legs and their post angles. Use the minus/plus guard-angle pair for the right-side upper feet. Fit shared M6 posts through Ø6.5 holes; retain Ø5.5 in the other legs.',
                  'Seat thrust foot angles on the XYZ bed pad or the angular drive’s 6.35 mm metal pads. Keep every reaction path metal-backed.'],
         gate='Floor, stanchions and angle faces form one retained metal foundation, without a floating printed plate or skewed slot-support face.',
         fail='An unsupported leg, wrong pad or bent angle changes the screw/motor axes. Rebuild that metal foundation before fitting the transmission.')
    page('drive-thrust','Build the metal thrust stack',
         'The bulkhead and two opposed thrust bearings retain the screw axially. The radial housing guides it; the printed pulley and cover carry no thrust preload.',
         section='Screw drives / six copies',art='drive-thrust.png',
         caption='Coral identifies the bulkhead, opposed bearing sets and two fixed retention nuts. Steel washer stacks clear the brass nut bodies.',
         add='Per drive: drive-bulkhead · 2 F8-16M · 2 TR8×2 fixed nuts · 10 M10 steel washers · Loctite 243',tools='Hand wrenches · soft screw support · axial movement check',
         actions=['Trial-fit one nut, five M10 washers, complete thrust bearing, bulkhead, opposite complete bearing, five washers and second nut in CAD order.',
                  'Measure both five-washer stack lengths; seat the correct shaft/house races on metal. Bring axial clearance out without adding a tight spot.',
                  'Clean and dry the retention threads, apply Loctite 243 according to its label and restore the proven axial adjustment.',
                  'Allow the governed 24-hour cure before transmitting torque; add witness lines across both nut/screw joints.'],
         gate='After cure, the screw turns fully without binding or visible axial movement, and both witness-marked nuts remain fixed to it.',
         fail='A moving nut, incomplete cure, rubbing brass body or binding race fails axial retention. Support the screw and rebuild that measured metal stack before loading it.')
    page('drive-supports','Support the fixed cartridge on metal',
         'The KP08 housing sits on two metal risers. The built thrust legs receive the bulkhead’s four shared M6 posts and the retained axes’ extended spring-seat posts.',
         section='Screw drives / six copies',art='drive-radial.png',
         caption='Coral is the fixed-end radial housing. Align its actual shaft center to the thrust stack without distorting either metal support.',
         add='Per drive: KP08 · 2 metal fixed risers · 2 M4 × 35 / washers / nuts · 4 M6 bulkhead posts on 24 × 44 mm pattern',tools='Received bearing · metal shims · caliper · hand rotation',
         actions=['Transfer the received KP08 holes into its floor. Start both M4 × 35 joints on the two nominal 11.35 mm metal risers.',
                  'Finish riser height to the actual bearing center: screw datum is 26.35 mm above floor. Use ≥10 mm OD M4 washers to bridge the 8 mm spacer bore; never pull a misaligned housing down.',
                  'Prepare twelve retained-axis M6 × 80 posts: cut/deburr to 72.5 mm under-head length and chase each cut thread with a nut.',
                  'Use M6 × 25 posts for X/Y/yaw; use M6 × 80 finished to 72.5 mm for Z/pitch/roll, reserving their extensions for spring seats.',
                  'Seat the shared bulkhead post-angle joints and radial housing progressively while the screw still turns freely by hand.'],
         gate='Radial and thrust centers agree, the bulkhead has a complete metal support and hand rotation has no tight region or housing twist.',
         fail='A skewed housing or unsupported bulkhead fails the cartridge. Correct its shim/support arrangement before adding a nut, belt or carried load.')
    page('drive-nuts','Build the single driving-nut cartridge',
         'One brass nut carries drive force through a metal face. Four metal spacers tie the two face plates together; the printed shell only locates the enclosure.',
         section='Screw drives / six copies',art='drive-nuts.png',
         caption='Coral is the single driving nut and its metal face. The screw passage through the second face is unthreaded and clear.',
         add='Per drive: 2 nut-face · 1 TR8×2 driving nut · paired-nut-spacer · 4 × 30 mm metal spacers · 4 M3 × 20 flange bolts',tools='2.5 mm hex · wrenches · hand rotation',
         actions=['Seat the single nut flange against its metal face and start all four M3 × 20 through-bolts.',
                  'Thread this nut onto the screw; place the second metal face with its clear central passage in CAD order.',
                  'Fit four 30 mm metal spacers and the 29 mm printed shell. The long face/cage ties are installed with the force link.',
                  'Seat the flange bolts in opposite pairs. Turn the screw in both directions while restraining the cartridge by hand.'],
         gate='The driving flange seats on metal and hand rotation remains continuous. No second threaded nut forces the screw against uncertain lead phasing.',
         fail='A binding face, wrong nut orientation or print carrying structural tie preload fails the cartridge. Correct alignment and the metal spacer path before joining its cage.')
    page('drive-pulley','Bolt the pulley to its hub',
         'The rotating metal nut flange is the 80T pulley\'s hub. Four through-bolts carry the torque; the print does not clamp the threaded screw crest.',
         section='Screw drives / six copies',art='drive-pulley.png',
         caption='Coral is the printed 80T pulley at the fixed-end nut flange. Its 10.5 mm passage clears the TR8 screw.',
         add='Per drive: 1 pulley-80t · 4 M3 × 16 · washers and locking nuts',tools='2.5 mm hex · 5.5 mm wrench',
         actions=['Seat the pulley against the metal flange and align all four holes.',
                  'Start all four M3 × 16 screws before tightening any; tighten in opposite pairs.',
                  'Hold the flange while bringing each nut seated; do not twist the thrust adjustment.',
                  'Turn the screw and watch the pulley flange clear the nearby metal stack for one full turn.'],
         gate='All four bolts retain the pulley and neither flange rubs the bulkhead or a stationary bracket.',
         fail='Rubbing is an axial-placement error. Correct the metal stack or pulley seat; do not abrade a flange to make room.')
    page('drive-motor','Mount the motor and pinion',
         'The slotted motor plate gives belt tension adjustment. The 20T pinion is metal and sits on the motor\'s 5 mm shaft with its teeth aligned to the 80T pulley.',
         section='Screw drives / six copies',art='drive-motor.png',
         caption='Coral is the motor and printed tension plate. The plate attaches to the metal drive supports through its two slots.',
         add='Per drive: NEMA17 · motor-tension-plate · four M3 × 12 · 20T pinion · two M5 mounting bolts',tools='2.5 / 4 mm hex · pinion setscrew key · caliper',
         actions=['Start four M3 × 12 screws into the motor face, then seat them in opposite pairs.',
                  'Put the pinion on the shaft with one setscrew on the shaft flat; leave its axial setting adjustable.',
                  'Start both M5 slot bolts into the metal support and slide the motor inward.',
                  'Align the two tooth tracks using the belt\'s straight edges, then secure the pinion.'],
         gate='The two pulley tracks are coplanar and the motor plate can still move through its tension slots.',
         fail='A tilted plate or offset track walks the belt sideways. Seat the plate and realign the pinion before tensioning.')
    page('drive-belt','Seat and tension the belt',
         'The belt supplies the 4:1 reduction. Tension must keep the teeth seated without bending the screw, motor plate or bearing supports.',
         section='Screw drives / six copies',art='drive-belt.png',
         caption='The same motor adjustment sets all six drives. The brake is adjusted separately on Z, pitch and roll.',
         add='Per drive: 1 closed GT2 / 6 mm belt',tools='Hand rotation · motor-slot hex key',
         actions=['Loop the belt over the 20T and 80T pulleys while the motor is inboard.',
                  'Slide the motor outward until slack is removed and the belt teeth stay seated.',
                  'Hold the plate square while seating both M5 slot fasteners.',
                  'Rotate the 80T pulley slowly through two turns in each direction; watch both belt edges.'],
         gate='The belt stays centered and the screw turns without a periodic catch in both directions.',
         fail='A migrating belt or repeated catch requires alignment/profile correction. Release tension and fix that cause before fitting the guard.')


def structure():
    page('station','Square the common station',
         'The metal rectangle carries the positioner and the existing rotator. Keep the full translating and camera envelopes inside a supported bench area.',
         section='Structure / base',art='station.png',
         caption='Two 750 mm longitudinal members and six 460 mm transverse members. Two pairs directly support the rotator platform and X-bed mounting stations.',
         add='4040: two × 750 mm, six × 460 mm · metal corners · 325 × 300 mm rotator-platform',tools='Square · caliper · 6 mm hex · bench clamps',
         actions=['Lay the members flat; start all metal corner fasteners before tightening.',
                  'Compare the two diagonals and bring the frame square; seat corners in opposite pairs.',
                  'Bolt the rotator platform to both inner crossmembers. Transfer-drill its mounting holes from the existing rotator feet.',
                  'Through-bolt the station to the bench and install the existing rotator on the platform.'],
         gate='All feet are supported, both diagonals agree within 1 mm, and pushing the frame by hand cannot shift it on the bench.',
         fail='A rocking or sliding frame invalidates the camera datum. Correct bench support and metal corner seating before installing guides.')
    page('x-bed','Install the X bed',
         'The 450 × 199 mm plate sits flat on the station. Its long direction is the X screw direction.',
         section='Structure / X',art='x-bed.png',
         caption='Coral is the X bed. The remaining station parts are already installed.',
         add='1 x-bed · metal plate-to-4040 fasteners',tools='4 / 6 mm hex · square',
         actions=['Orient the named fabrication face upward and match its location to the station CAD.',
                  'Start every mounting screw with a washer before seating any screw.',
                  'Seat the plate against the metal supports in opposite pairs. Keep it flat; do not pull a bowed plate down with bolt force.'],
         gate='The plate rests on its metal supports without a gap and its long edge is square to the station transverse members.',
         fail='A cocked or bent bed twists both rails. Re-seat or correct the metal supports before rail installation.')
    for axis in ('X','Y','Z'):
        a=axis.lower()
        if axis=='Y':
            page('y-bed','Build the raised Y deck',
                 'Four 40 mm metal spacers leave room for the X transmission. The Y bed is rotated 90° relative to X.',
                 section='Structure / Y',art='y-bed.png',
                 caption='Coral is the Y bed and its four metal spacers. The X carriage supports this deck.',
                 add='1 y-bed · four 40 mm metal tube spacers / 10 mm OD · four M5 × 70 through-bolts, washers and locking nuts',tools='4 mm hex · 8 mm wrench · square',
                 actions=['Place the four narrow metal spacers on the X carriage’s 180 × 180 mm mounting pattern, at X/Y = ±90 mm.',
                          'Lay the Y bed on the spacers with its rail direction perpendicular to X.',
                          'Start all four through-bolts; place washers under heads and nuts.',
                          'Seat opposite corners progressively. Check that all four spacers remain square and supported.'],
                 gate='Every spacer bears on both plates and each locking nut has at least two full threads beyond it.',
                 fail='A floating spacer or short bolt weakens the raised deck. Correct the metal stack or bolt grip before installing the Y rails.')
        if axis=='Z':
            page('z-mast','Brace the metal Z mast',
                 'The vertical guides mount to a metal bed carried by two 600 mm uprights. Assemble the mast with its load supported.',
                 section='Structure / Z',art='z-mast.png',
                 caption='Coral is the pair of uprights and Z bed. The upright metal corners transmit the carried gimbal load to the Y deck.',
                 add='Two 4040 × 600 mm · 1 z-bed · metal corner joints',tools='Square · 6 mm hex · clamps / temporary support',
                 actions=['Clamp both uprights to the Y deck in the CAD positions; start their metal corners loosely.',
                          'Start the Z bed fasteners against both uprights.',
                          'Square the bed to the Y carriage in both planes, then seat opposed corner joints.',
                          'Keep a support under the future moving head until Z retention is accepted.'],
                 gate='The metal mast does not rock at its deck joints and the Z bed is square to the Y carriage in both planes.',
                 fail='Printed brackets or friction against one upright are not the specified mast joints. Correct the metal structure before loading it.')
        page(f'{a}-rails',f'Align the {axis} guide pair',
             'Two supported SBR12 rails carry four blocks. Their 140 mm center spacing and 128 mm block spacing come from the matching plate drawings.',
             section=f'Structure / {axis}',art=f'{a}-rails.png',
             caption=f'Coral is the pair of {axis} rails and four blocks. The rail base-to-block-top stack is 40 mm.',
             add='2 SBR12 × 400 mm rails · 4 SBR12UU blocks · rail-foot through-bolts',tools='Caliper · straightedge · small hex keys · temporary support for Z',
             actions=['Use one straight bed edge as the rail-direction datum; start all rail-foot fasteners loosely.',
                      'Set rail centers 140 mm apart. Transfer the received rail-foot hole phase to the bed; do not assume the catalog hole phase.',
                      'Slide two blocks onto each rail with their mounting holes facing the carriage.',
                      'Seat the datum rail first. Leave the second rail free to align under the carriage in the next operation.'],
             gate='All four blocks slide by hand and the rail pair matches the carriage hole pattern without pulling either rail sideways.',
             fail='A block that binds or a forced hole match indicates spacing/parallelism error. Release the second rail and correct the bed pattern before continuing.')
        page(f'{a}-carriage',f'Attach the {axis} carriage',
             'Sixteen block screws join the metal carriage to four guide blocks. The carriage establishes parallelism before the second rail is locked.',
             section=f'Structure / {axis}',art=f'{a}-carriage.png',
             caption=f'Coral is the {axis} carriage. Each of four blocks receives four screws through the plate.',
             add=f'1 {a}-carriage · 16 M5 block screws with washers',tools='4 mm hex · caliper depth check · support for Z',
             actions=['Measure the received blocks\' usable tapped depth before choosing the governed screw grip.',
                      'Start all sixteen block screws by hand. Seat them in opposite pairs across the four blocks.',
                      'Move the supported carriage slowly through its intended travel while seating the second rail\'s feet.',
                      'Repeat the travel after rail fasteners are seated. Keep screw drive and motor belt uncoupled for this check.'],
             gate='The carriage traverses the full ±85 mm intended range without a tight region; every screw clamps the plate before bottoming in a block.',
             fail='A tight region or bottomed screw must be corrected mechanically. Do not use the motor to overcome a rail-alignment error.')
        page(f'{a}-screw',f'Fit the {axis} screw drive',
             'The drive cartridge joins the carriage while the fixed-end metal bulkhead takes thrust. The opposite radial bearing leaves the screw axially free.',
             section=f'Structure / {axis}',art=('x-complete.png' if axis=='X' else 'xy-complete.png' if axis=='Y' else 'z-complete.png'),
             caption='Coral is the screw and single-nut force-link output. The floating end remains axially free; Z fixed thrust is at the top.',
             add='1 prepared 400 mm screw drive · linear-drive-support · opposite KP08 · carriage cartridge fasteners',tools='4 mm hex · hand wrenches · support for Z',
             actions=['Start the metal fixed-end support and bulkhead joints; align the screw with the carriage cartridge.',
                      'Start the cartridge-to-carriage fasteners before seating either joint.',
                      'Install the opposite KP08 on its two nominal 5 mm metal risers, finishing height to the received center. Use M4 × 30 with ≥10 mm OD washers; add no outer axial nut.',
                      'With belt released, hand-turn the screw through the intended travel; seat supports only while the screw remains free.'],
             gate='Hand rotation moves the carriage without cocking the cartridge, a tight region or end thrust at the floating bearing.',
             fail='A skewed cartridge or trapped floating end adds unintended load. Re-align its metal joints before fitting or powering the belt.')
    page('z-head','Join the head support',
         'The head support is metal extrusion and metal corner joints. It brings the yaw bearing backplate to the gimbal datum.',
         section='Structure / head',art='z-head.png',
         caption='Coral is the 225 mm upright, 180 mm crossbeam, metal diagonal and flat yaw adapter attached to the Z carriage.',
         add='4040 × 225 mm · 4040 × 180 mm · z-head-diagonal · yaw-head-adapter · metal corner joints',tools='Square · 6 mm hex · temporary head support',
         actions=['Support the Z carriage so it cannot fall while its belt is disconnected.',
                  'Start the upright, crossbeam, metal diagonal and flat adapter at their CAD mounting stations.',
                  'Square both members to the carriage and seat opposite joints progressively.',
                  'Keep the support in place while the bearing backplate is assembled.'],
         gate='Pushing the unloaded crossbeam by hand reveals no loose metal joint or unsupported end.',
         fail='Any movement at a bolted corner is a failed structure check. Correct that joint before hanging the gimbal.')


def overload_links():
    page('force-fixture','Mount the gauge vertically under the quill',
         'The drill press supplies slow manual travel while its motor is unplugged. The force gauge is in series with the loose link, and the two platens contact different load-path members.',
         section='Screw drives / calibration fixture',art='force-fixture.svg',
         caption='Blue is the gauge/quill fixture. The gauge is vertical with its M6 flat compression head upward; its display is not laid face-up.',
         add='500 N push-pull gauge · 70 × 110 × 6.35 backing plate · supplied four M4 screws · metal test platens',tools='PONY drill vise · drill motor unplugged · quill indicator · continuity meter',
         actions=['Mount the gauge back to the plate using its 41 × 73 mm four-hole pattern and supplied M4 screws.',
                  'Clamp the plate vertically in the drill vise. Fit the M6 compression head pointing up and a flat-ended pusher in the chuck; align both force axes.'],
         gate='Gauge load axis is vertical, the backing plate is rigidly clamped and the pusher approaches its head squarely.',
         fail='A face-up gauge or angled head invalidates the fixture. Correct the vertical metal mounting before loading a spring or link.',
         note='Gauge specification ±1% of reading; use ±5–8 N total allowance for fixture/alignment unless a better independent uncertainty record is established.')
    page('force-load-path','Separate the two force-link reactions',
         'The gauge must read the entire applied output force. Its test platen touches the fixed cage while the quill pusher contacts only the moving shuttle.',
         section='Screw drives / calibration fixture',art='force-calibration.png',
         caption='The actual metal cage and output are separate. The preceding schematic shows the gauge arrangement; this CAD detail identifies the link members.',
         add='force-test-platen · loose link · controlled quill pusher',tools='Drill motor unplugged · quill indicator · continuity meter',
         actions=['Attach the test platen at the fixed cage outer ties only; keep its central clearance open.',
                  'Align the gauge head with that reaction platen. The upper pusher bears only on the shuttle output attachment.',
                  'Advance manually while recording force, shuttle motion and NC transition; lock the quill for a static reading.',
                  'Reverse the loose link and repeat the arrangement for the opposite direction.'],
         gate='Cage reaction and shuttle load form one series path through the gauge, with no clamp/platen bridging the moving joint.',
         fail='A rigid bypass or off-axis load invalidates the reading. Rebuild the controlled metal contact path before accepting a trip force.')
    page('grade-springs','Grade the actual spring pairs',
         'Source rate is a setup estimate. Measure the received springs over their used compression range, then match each directional pair before closing a force cage.',
         section='Screw drives / spring grading',art='spring-grade.svg',figure='medium',
         add='24 force springs · 3 friction springs · 4 crash springs · numbered result sheet',tools='Controlled gauge fixture · quill indicator · guarded metal platen',
         actions=['Number every spring. Seat it between parallel metal platens and record free length and a low-force zero.',
                  'Compress slowly through the working range; record force and travel at repeated points and unload to check return.',
                  'Fit each local slope Δforce/Δtravel, preserve uncertainty and match the two springs in every directional pair.',
                  'Use each axis/direction’s preload in the force-settings table. Set it with measured metal spacers and grade the finished link.'],
         gate='Each assigned spring has a measured usable force/deflection range, returns freely and stays clear of coil bind at maximum captured travel.',
         fail='An unknown rate, nonreturning spring or coil-bind approach fails grading. Replace/reassign it or correct the metal compression setting before assembling the link.')
    page('force-settings','Use the measured force bands by direction',
         'The gravity-bearing directions use different seated preloads. Static trip bands accept the complete force interval; powered values are upper ceilings, with no minimum force requirement.',
         section='Screw drives / force settings',art='spring-grade.svg',figure='short',style='compact',
         rows=[],headers=['Axis / force direction','Pair preload / N','Static trip / N','Powered peak + U / N'],
         gate='Every link is labeled by axis/direction, and the actual spring-rate, seat, trip and capture records agree with its assigned table row.',
         fail='A reversed Z pair or generic angular setting fails this allocation. Correct the label/spacers and regrade before loading.',
         note='Controller +Z moves upward and shortens its screw. Downward gravity is positive screw extension. Angular trip is near ±0.30 mm; XYZ near ±0.75 mm; capture is ±1.0 mm.')
    page('force-spacers','Finish the measured preload spacers',
         'Metal spacer lengths set spring preload. The central spacer independently fixes captured travel, so changing spring rate must never change the capture gap.',
         section='Screw drives / spring grading',art='force-cage.png',figure='short',style='compact',
         tools='Measured directional pair rates · caliper · metal tube cutter / facing tool · metal shims',
         rows=[('Compression C','Desired pair preload / (measured k1 + k2)'),
               ('Outer force spacer','20 − C + 1.5 mm washer; correct for measured free length'),
               ('Outer nut spacer','Outer force spacer − 10.825 mm'),
               ('Central spacer','8.35 mm; keep unchanged for ±1.0 mm capture')],
         headers=['Setting','Measured construction'],
         actions=['Use the named force-settings table for both directional preloads. Downward Z is positive screw extension; controller +Z shortens the screw. Record each matched pair separately.',
                  'Finish matched metal tube lengths or metal shim stacks on all four ties; keep both faces square.',
                  'At capture, C + 1.0 mm must remain below 8.0 mm and below actual free minus solid length minus 1.0 mm clearance.'],
         gate='Measured force/travel and finished metal spacer lengths agree; spring bind remains clear and the central 8.35 mm capture spacer is unchanged.',
         fail='An unmatched stack or spring that cannot meet force and travel together fails the link. Replace/regrade the spring pair or finish a new outer spacer set.')
    page('force-cage','Build the captured nut-side cage',
         'The guided metal force link sits between each screw nut cartridge and its carriage or clevis output. Its shoulders keep the output captured after a trip.',
         section='Screw drives / six force links',art='force-cage.png',
         caption='Coral is the fixed cage attached to the single driving-nut cartridge. The central output shuttle is installed in the next operation.',
         add='Per link: metal end/shoulder plates · four outer M5 ties / metal tube spacers · single driving-nut cartridge',tools='4 mm hex · wrenches · square',
         actions=['Build the two nut faces around the 29 mm printed shell and four 30 mm metal spacers.',
                  'Start the outer metal cage ties and their metal tubes around the cartridge middle.',
                  'Seat the end/shoulder plates square to the screw axis in opposite pairs.',
                  'Keep the central opening clear for the guided output shuttle; no tie or bracket may bypass the springs.'],
         gate='The metal cage is attached to the single driving nut and every structural clamp bears on metal spacers, leaving the printed shell unloaded by tie preload.',
         fail='A direct rigid bypass to the output defeats overload detection. Correct that load path before adding the shuttle.')
    page('force-shuttle','Fit the guided spring shuttle',
         'Bronze bushings guide the output. Opposed spring pairs respond to both load directions while the metal shoulders limit shuttle movement to ±1.0 mm.',
         section='Screw drives / six force links',art='force-shuttle.png',
         caption='Coral is the shuttle, guides and opposed springs. The cage belongs to the nuts; the shuttle belongs to the carriage or angular clevis.',
         add='Per link: shuttle · bronze bushings · metal boss halves · smooth M8 guides · four pressure washers · four 20 mm springs',tools='3 / 6 mm hex · wrenches · caliper',
         actions=['Fit the bronze bushings to the shuttle. Close each pair of metal boss halves around its guide with four M3 × 30 bolts.',
                  'Insert the smooth M8 guides, four metal pressure washers and four 20 mm springs in their paired CAD order.',
                  'Install the end plates and metal spacers; bring directional spring preload to the governed measured setting.',
                  'Fit both opposed overload NC switches. Move the shuttle in each direction by hand before fixing the output attachment.'],
         gate='The shuttle moves freely in both directions, opens a distinct NC contact before each ±1.0 mm captured shoulder and cannot escape the metal cage.',
         fail='A binding bushing, spring bypass or switch after shoulder contact fails overload protection. Correct the guided metal path before force calibration.')
    page('force-calibration','Calibrate each overload trip by force',
         'The force tool measures each directional trip at the actual output load. The switch position is adjusted to measured force; nominal shuttle distance is a setup aid.',
         section='Screw drives / six force links',art='force-calibration.png',
         caption='The nut-side cage is fixed and a controlled load is applied to the output shuttle through the force tool. Power stays disconnected.',
         tools='Measured force tool / rigid loading fixture · continuity meter · supported axis',
         actions=['Mount the loose link in the accepted vertical gauge fixture; cage reaction and shuttle load remain separate.',
                  'Increase load gradually in one direction while recording force, shuttle travel and the COM/NC transition.',
                  'Set the trip to its axis/direction’s force-settings band, with the complete gauge/fixture uncertainty inside it; verify downward Z’s lower seat-lift bound is ≥390 N.',
                  'Record both trips, reset position and force-tool uncertainty for all six links. Recheck after mounting to the axis.'],
         gate='Both directions trip inside their force band before the ±1.0 mm capture. Nominal trip travel is ±0.75 mm XYZ / ±0.30 mm angular; peak travel/force is recorded.',
         fail='An out-of-band trip, a captured-stop contact before trip or an unsupported force reading fails calibration. Correct preload/guide/switch adjustment and repeat both directions.')


def gimbal(gp):
    required=json.loads((ROOT/'hardware/printed-parts/fixtures/gun-positioner/requirements.json').read_text())
    keeper=required['fabrication']['shaft_end_threads']['steel_retainer_washer_mm']
    bearing_ops=[
        ('yaw','yaw-bearings','Build the yaw bearing support','yaw-bearing-back · two KP001 12 mm bearings · 175 mm shaft','Both bearings attach to the fixed backplate; the shaft is vertical.','Align the two housings before securing their bearing inserts. The shaft must turn without housing twist.'),
        ('pitch','pitch-bearings','Install the pitch bearing pair','Two pitch-bearing-foot · two KP001 · 130 / 85 mm shaft stubs','The bearing feet attach to the yaw frame. The two stubs share one horizontal pivot axis.','Use the common pivot datum to align both stubs; do not force the pitch frame between misaligned bearings.'),
        ('roll','roll-bearings','Install the roll spindle','roll-bearing-foot · two KP001 · 165 mm shaft','Two spaced bearings support the rear roll spindle. The gun enters the open cradle from above.','Align both housings to the rear spindle. The bearings carry the cradle independently of the roll screw.'),
    ]
    frame_ops=[
        ('yaw','yaw-frame','Bolt the yaw frame','yaw-output-hub · yaw-crossbar · two yaw-side','The qualified clamping hub carries the crossbar and two metal side members.','Fit the qualified shaft hub. Start all plate and corner bolts, then seat opposite pairs with the side members square.'),
        ('pitch','pitch-frame','Join the pitch frame','Two pitch-output-hub · two pitch-side · two pitch-rear-crossbar','The two hubs and rear crossbars make one rigid pitch frame.','Fit both matched shaft hubs, start the frame fasteners, and square the side members before seating the rear crossbars.'),
        ('roll','roll-cradle','Build the open roll cradle','roll-output-hub · roll-cradle-back · two roll-cradle-side','The rear spindle and qualified clamping hub support the open metal cradle.','Fit the qualified output hub and rear plate; start both side members and square them before seating all frame joints.'),
    ]
    for b,f in zip(bearing_ops,frame_ops):
        axis,art,title,add,caption,action=b
        page(f'{axis}-bearings',title,
             'Metal bearing housings support the output independently of the screw and belt. Assemble each axis while its load is supported.',
             section=f'Gimbal / {axis}',art=f'{art}.png',caption=caption,
             add=add+' · metal bearing through-bolts, washers and locking nuts',tools='5 mm hex · wrenches · straight shaft / datum · support',
             actions=['Start every housing and backing-plate fastener before seating a housing.',action,
                      'Turn the unloaded shaft by hand in both directions, then seat the housing fasteners in opposite pairs.',
                      'Fit the governed metal spacer stacks and tapped-end washer retainers; measure axial movement without preloading a housing by shifting its base.'],
             gate='The output rotates freely and there is no loose housing, shaft end movement or misaligned pivot.',
             fail='A forced shaft or distorted bearing base is an alignment error. Release and re-seat the housings before adding the frame.')
        axis,art,title,add,caption,action=f
        page(f'{axis}-frame',title,
             'Qualified two-bolt split hubs carry torque on plain shafts. Metal plate corners close the frame around the supported output.',
             section=f'Gimbal / {axis}',art=f'{art}.png',caption=caption,
             add=add+' · paired M4 × 50 grade 12.9 clamps · plate fasteners and metal corners',tools='3 / 4 mm hex · 7 / 8 mm wrenches · square',
             actions=[action,'Start every joint before tightening; bring opposed corners seated progressively.',
                      'Restore each qualified clamp joint with both retained bolts and witness marks. Repeating its proof is required after disturbing its grip.',
                      'Rotate the supported unloaded frame through its range: yaw/roll ±20°, pitch −20…+10°. Examine each corner clearance.'],
             gate='Each hub has a passing torque-proof record and retained axial stack; the unloaded frame has no loose corner or contact inside its intended range.',
             fail='A contacting or loose frame is a failed fit. Correct its metal geometry before attaching a screw actuator.')
        keys=[key for key in gp.CAPTURE_STACKS if key.startswith(axis)]
        ends=2*len(keys)
        page(f'{axis}-shaft-capture',f'Capture the {axis} shaft axially',
             'Bolted end washers and metal tubes bound the shaft, terminal hubs and inner races. Clamp friction and bearing setscrews cannot replace this retained metal stack.',
             section=f'Gimbal / {axis} capture',art=f'{axis}-shaft-capture.png',figure='short',style='reference',
             caption='Coral identifies actual capture tubes, washers and end screws. '+('Yaw backplate omitted for visibility. ' if axis=='yaw' else '')+'Local tube starts run along each completed shaft from its marked end.',
             add=f'{ends} M5 × 12 screws · {ends} steel OD{keeper["OD"]:g} / ID{keeper["ID"]:g} × {keeper["thickness"]:g} keepers · {ends} M5 flats · named capture tubes',
             tools='Power disconnected · independent frame support · caliper / indicator · source shaft marks',
             rows=[(key,f'{start:g}',f'{length:g}') for key in keys for start,length in gp.CAPTURE_STACKS[key]],
             headers=['Shaft','Local tube start / mm','Nominal length / mm'],
             actions=['Support the frame. Fit each labeled metal tube to the delivered hub/plate/inner-race faces, clearing seals and outer races.',
                      'Fit both end keepers with their 0.8 mm flat washers and M5 × 12 screws. Verify actual thread reach and no bottoming; do not preload a skewed housing.',
                      'Measure ≤0.5 mm one-sided freedom and ≤1 mm total captured excursion. Hand-turn both ways and complete the independent axial capture proof before removing load support.'],
             gate='The complete stack captures shaft and hubs through metal, rotates freely and has bounded axial movement with a passing capture-proof record.',
             fail='Rubbing, seal load, excessive movement or an unqualified end thread fails capture. Support the load and correct/reprove the actual stack before powering the axis.')
    page('angular-anchors','Tie each base clevis to its parent frame',
         'Paired flat metal webs connect the fixed end of each actuator to the frame that carries that axis. The roll actuator uses its shared metal anchor plate.',
         section='Gimbal / actuator anchors',art='angular-anchors.png',
         caption='Coral identifies the yaw, pitch and roll base webs and shared roll anchor. Every fixed actuator reaction returns to its parent frame through metal.',
         add='Three paired base-web sets · roll anchor plate · governed metal through-bolts',tools='Square · hex keys / wrenches · independent frame support',
         actions=['Identify the parent frames: fixed yaw support, yaw frame for pitch and pitch frame for roll.',
                  'Start each pair of metal webs at its parent-frame mounting stations and fixed clevis cheeks.',
                  'Install the shared roll anchor plate with both roll webs; keep all reaction joints metal-backed.',
                  'Seat opposite web joints progressively, then push each unloaded fixed clevis by hand to check its complete metal reaction path.'],
         gate='No fixed actuator end floats or shifts; each base clevis has two retained metal webs connected to its own parent frame.',
         fail='A moving or unsupported base cannot carry actuator force. Correct the web/anchor joints before installing its screw or removing frame support.')
    page('angular-drives','Pin the three screw actuators',
         'Each screw swings on metal clevises as its 150 mm lever rotates. The neutral pin-to-pin length is 180 mm for yaw, pitch and roll.',
         section='Gimbal / actuators',art='angular-clevis.png',
         caption='Coral is the metal lever and clevis pair. The drive rotates on its pins; the screw is not forced to bend as the lever swings.',
         add='Three prepared 300 mm screw drives · three angular-lever · twelve clevis-cheek · three qualified lever hubs',tools='Caliper · datum square · 4 mm hex · pin wrenches',
         actions=['At the supported central pose, install each matched lever hub and 150 mm arm.',
                  'Join the fixed and moving metal clevis cheeks with their pivot bolts. Keep the pivot freely rotating after the locking nuts are secured.',
                  'Set pin-to-pin drive length to 180 mm using fixed datum faces and a rule/caliper transfer setup.',
                  'Hand-turn each supported angular screw through its local range: U/W ±20°, V −20…+10°. Check clevis swing and the retained load path.'],
         gate='Each clevis rotates without spreading its cheeks and positive screw extension moves its named angle positively.',
         fail='A binding clevis or incorrect neutral length changes the angular law. Correct the joint and repeat the supported hand sweep before referencing it.')
    page('linear-stops','Install the linear stop pairs',
         'The switch opens before the metal stop receives the carriage. Soft travel is ±85 mm; switches are near ±89 mm and metal stops are at ±94 mm.',
         section='Travel / X Y Z',art='limits-linear.png',
         caption='Coral is one axis\'s metal stops and adjustable switch brackets. Transfer the received switch body holes; repeat for X, Y and Z.',
         add='6 backed metal stops · 6 NC switches and brackets · metal mounting fasteners',tools='Rule · caliper · continuity meter · hand screw rotation',
         actions=['Install both metal angle-backed stops; the carriage must strike metal at ±94 mm.',
                  'Fit each switch so it opens at ±89 mm and still has overtravel before its metal stop.',
                  'With belt uncoupled and load supported, approach each end slowly by hand while metering COM/NC.',
                  'Mark the physical central datum halfway between the established end datums; record the actual switch positions.'],
         gate='Both switches open before either metal contact, and every block remains on its full rail support through the metal-stop position.',
         fail='A switch used as the load stop or a block leaving the rail is a failed travel layout. Relocate the backed stop/switch and repeat the sweep.')
    page('angular-stops','Set the angular stop pairs',
         'Yaw and roll switch at ±21° and stop at ±22°. Pitch switches at −21/+11° and stops at −22/+12°, outside its −20…+10° commanded range.',
         section='Travel / U V W',art='limits-angular.png',
         caption='Coral is the stop and switch-bracket pair around one actual 150 mm lever. Fit the received switches in each local plane.',
         add='6 angular metal stops · 6 NC switches and brackets · metal fasteners',tools='Lever datum · rule/caliper · continuity meter',
         actions=['Mark the neutral lever vector and both angular end vectors from the fabrication layout.',
                  'Set U/W switches at ±21° and stops at ±22°. Set V switches at −21/+11° and stops at −22/+12°.',
                  'Hand-turn each supported actuator toward each limit, metering its switch.',
                  'Record the observed sign and clearance of all three axes at both ends.'],
         gate='Every angular switch opens before metal contact; screw clevises, brake and gun envelope remain clear through yaw/roll ±20° and pitch −20…+10°.',
         fail='A contacting part or reversed switch order reduces the usable workspace. Correct the stop geometry and keep that path uncommanded until rechecked.')


def retention_and_payload():
    page('friction-washers','Fit three independent friction retainers',
         'Z, pitch and roll retain gravity through a dry steel washer on a rotating brass flange. The retained screw remains connected when its belt or motor power is absent.',
         section='Retention / metal assembly',art='friction-washer.png',
         caption='Coral is the steel washer and central spring, separated along their insertion axis. The dry annulus is downstream of the printed pulley.',
         add='Per retained axis: friction-washer · friction-spring · friction-spring-seat · 4 M6 × 80 posts · two M3 × 50 guide pins',tools='Power unplugged · wrenches · rigid load support',
         actions=['Drill two Ø3.4 mm guide holes on 30 mm pitch in each purchased steel washer using its drilling projection; preserve the contact face.',
                  'Keep the carried frame supported and its belt released. Verify cured nut/screw witness marks before loading the flange.',
                  'Clean the contact annulus and steel washer; keep lubricant away from this dry friction pair.',
                  'Place the washer and axial spring in their CAD order; start the metal spring seat on all four posts.',
                  'Fit the two anti-rotation guide pins. The washer must slide and tilt freely while its pins prevent rotation.'],
         gate='The spring bears centrally on the dry washer, which overlaps the brass annulus and follows runout without binding its guide pins.',
         fail='Off-center spring force, an oily contact or trapped washer fails retention assembly. Correct the actual metal contact path before measuring torque.')
    page('friction-preload','Set and lock the spring seats',
         'A measured soft spring provides axial preload. Four metal post nuts hold the seat square; the three axes use different breakaway windows.',
         section='Retention / preload',art='friction-preload.png',
         caption='Coral is the metal preload seat and its four posts. Nut position is a setting; measured breakaway decides acceptance.',
         add='Per retained axis: 8 M6 seat jam nuts · washers · spring-rate record',tools='Wrenches · measured spring grading · supported frame',
         actions=['Grade each received friction spring in the controlled gauge fixture; record its actual force/deflection over the used range.',
                  'Set the seat parallel to the bulkhead, advancing opposite post nuts in small equal increments.',
                  'Start with light drag and hand-turn the screw through a full revolution. The spring remains seated without approaching solid height.',
                  'Lock paired nuts at each post while holding its setting. Complete the full-turn torque procedure after the redirect is characterized.'],
         gate='The spring/seat remain centered, the steel washer follows the entire rotation and the four locked post settings remain unchanged.',
         fail='A skewed seat, coil bind or changing post setting fails preload. Correct the metal arrangement and regrade before assigning a holding torque.')
    page('torque-redirect','Characterize the cord redirect first',
         'A direct hanging weight grades a horizontal screw on the bench. The redirect turns a vertical hanging load into a tangential pull for an installed or inclined screw.',
         section='Retention / torque fixture',art='torque-redirect.png',
         caption='Blue is the vise-held metal bracket, 608ZZ bearing and cord pulley. The cord must leave the lever tangent to its rotation and perpendicular to the screw axis.',
         add='Cord pulley / bearing cap · 608ZZ · M8 × 50 smooth-shank axle / metal contact tubes · 2 M3 × 20 · metal bracket · two 200 g cups',tools='Metal vise · scale · cord · catch for both cups',
         actions=['Clamp only the metal contact tubes and 608 inner race on the smooth M8 axle. Retain the outer race with its cap / two M3 × 20 joints; verify the pulley turns freely.',
                  'Hang equal complete 200 g loads on both cord ends, including cups and cord attachment.',
                  'Add at most 5 g to either side in separate trials; both directions must move freely. Record the actual threshold.',
                  'Place the redirect to give a tangential horizontal cord at the installed lever and a vertical load after the pulley; repeat the calibration before each torque check.'],
         gate='Both directions move with ≤5 g imbalance, bounding redirect loss to ≤0.049 N or ≤0.0049 N·m at the 100 mm arm.',
         fail='A larger or inconsistent imbalance fails the redirect. Correct its bearing, cord track and alignment; do not assign holding torque from an uncharacterized pulley.')
    page('brake-torque','Measure each axis around a full turn',
         'The rigid metal tool has a 100 mm force arm. Measure each brake in both directions around its full turn before loading the gun.',
         section='Retention / torque',art='brake-torque.png',
         caption='Blue is the removable torque fixture. Load is applied perpendicular to its 100 mm arm; it is removed before powered rotation.',
         add='1 brake-torque-lever · known masses / force tool · result sheet',tools='Scale · 100 mm metal arm · supported mechanism',
         actions=['With load supported, remove the belt/pulley and bolt the balanced lever to its fixed metal flange. Bench-grade with screw horizontal and lever load hole horizontal.',
                  'Weigh the complete hanging mass, including its container/sling. Add mass gradually until motion starts; catch the lever.',
                  'Repeat both directions at eight screw positions spaced 45° apart; use the characterized tangential redirect whenever the load hole is not horizontal. Record breakaway and running drag.',
                  'For installed Z, accept the complete torque interval inside 0.20–0.23 N·m. A 0.205–0.225 indicated guard is usable only if total uncertainty is ≤0.005 N·m; otherwise narrow it. Remove tools and restore the pulley.'],
         rows=[],
         headers=['Axis','Accepted breakaway','Ideal mass / 100 mm'],figure='short',style='compact',
         gate='Every recorded direction/phase lies inside its axis window after accounting for mass, lever and alignment uncertainty; the witness marks remain aligned.',
         fail='An out-of-window value or periodic bind fails the setting. Correct contact alignment/preload and repeat all phases; display resolution is not tool uncertainty.',
         note='Torque = mass in kg × 9.80665 × 0.100 m. Account for the tool\'s own moment and load alignment; use the force-tool procedure if that contribution is not canceled.')
    page('crash-guides','Install the four ground guide rods',
         'Two parallel guides per pod carry the detachable mount without using the locating collars as spring thrust stops. Metal supports and bronze guides establish the sliding path.',
         section='Payload / captured crash mount',art='crash-guides.png',
         caption='Coral identifies the four uncut 8 × 100 mm rods and metal supports. Lower guide bushings are separated 40 mm along the load direction.',
         add='4 ground rods · 4 integrated 40 × 80 mm pod ends · 2 fixed crossbars · 4 bronze guide blocks · 8 split collars · metal angles',tools='Caliper · square · hex keys · rigid cradle support',
         actions=['Join the two fixed metal crossbars to the cradle with metal angles. Start each pod’s integrated end plates on the crossbars.',
                  'Align both rod holes in each end plate, placing the two guide axes 30 mm apart.',
                  'Fit the 8 × 100 mm ground rods without cutting or forcing them. Add the lower bronze guides at their 40 mm separation.',
                  'Seat metal support fasteners progressively while the guided members still slide freely.',
                  'Fit the split collars only to locate rods. Keep working spring reaction on the fixed shoulder/tie structure.'],
         gate='Both pods have freely sliding parallel guides, while the seated output has no perceptible rocking under a reversible working-load hand check.',
         fail='A tight sliding guide or loose seated output fails the mount. Correct alignment/bushing fit; collar friction cannot replace a missing metal thrust path.')
    page('crash-pods','Close the two captured axial pods',
         'Each pod has a guided central output, opposed seated pressure washers and two springs. Metal shoulders capture either axial sign within ±1.0 mm.',
         section='Payload / captured crash mount',art='crash-pods.png',
         caption='Coral is the axial pod structure. Fixed shoulders receive spring load; the central boss and shuttle carry the detachable output.',
         add='2 shuttles · 4 shoulders · 4 boss halves · 4 graded crash springs · metal tie/spacer sets',tools='Graded spring record · caliper · continuity meter · support',
         actions=['Grade the actual four crash springs for free length, solid length and rate over the used preload region.',
                  'Install bronze-guided boss/shuttle assemblies, seated pressure washers and opposed spring pairs in CAD order.',
                  'Build the metal shoulders and end plates on matched metal ties/spacers, preserving ±1.0 mm capture.',
                  'Set light initial directional preload; final adjustment includes the actual gun/cable gravity baseline and measured 20–30 N added nozzle release.'],
         gate='Both signs remain captured, springs stay clear of coil bind and every spring reaction returns through fixed metal shoulders.',
         fail='A floating reaction, rigid bypass or spring-bind approach fails the pod. Rebuild that metal/spring path before mounting the release plate.')
    page('crash-carriers','Join the tapered output carriers',
         'The paired metal carriers join the axial pod outputs to the registered magnetic backplate. Their rear taper clears the fixed pitch frame.',
         section='Payload / captured crash mount',art='crash-carriers.png',
         caption='Coral is the left/right carrier pair and magnetic backplate. The gun tray detaches from this supported output.',
         add='2 crash-output-wall · left / right crash-carrier · crash-magnet-back · metal angles and through-bolts',tools='Actual-size contour templates · square · hex keys · support',
         actions=['Identify the left and right contours; keep the tapered rear inside the pitch side plates.',
                  'Join each lower bronze guide block and upper shuttle to its metal output wall; attach the tapered carrier to that moving wall.',
                  'Start the rear magnetic backplate joints and square it before seating opposite fasteners.',
                  'Move the captured output through both small axial signs by hand; no bracket may bridge from output to a fixed pod shoulder.'],
         gate='The output moves through its captured path and the paired carriers remain rigid, with no fixed-frame bypass or pitch-frame contact.',
         fail='A bypass or contacting taper defeats release. Correct the metal contour/joint placement before fitting the seated gun tray.')
    page('crash-seats','Register three hardened V seats',
         'Three hardened balls seat against three pairs of hardened dowels. The metal contact geometry defines repeatable seating; aluminum is kept out of the ball contact.',
         section='Payload / transverse release',art='crash-seats.png',
         caption='Coral identifies the six 4 × 20 mm dowels and three 8 mm hardened balls. Metal keepers retain the paired dowels.',
         add='Gun-release-back / tray · 3 hardened balls · 6 dowels · 3 steel ball backing washers · metal keepers · locating compound',tools='Clean metal faces · washer drilling projection · clamped cure fixture',
         actions=['Mount paired dowels at the three governed seat stations with 6 mm center spacing; retain them with the metal keepers.',
                  'Drill each steel backing washer’s two Ø3.4 mm keeper holes on 18 mm pitch. Its existing 6 mm bore supports the 8 mm ball; mount it behind the release-back pocket.',
                  'Locate the balls against their steel backing seats. Cure locating compound according to its label with the assembly supported.',
                  'Bring the tray into all three V seats by hand; check full metal contact without forcing the backplates.',
                  'Lift and reseat repeatedly before magnets are adjusted. Record any rocking or contact that changes with reseating.'],
         gate='All three balls contact their hardened dowel pairs simultaneously and the supported tray returns without rocking.',
         fail='A ball touching aluminum, loose dowel or inconsistent seat fails registration. Correct the contact geometry/keeper before assigning release force.')
    page('crash-magnets','Fit the three magnetic retainers',
         'Steel cup magnets pull the registered seats together. Their air gaps are adjusted only after the balls and dowels are fully seated.',
         section='Payload / transverse release',art='crash-magnets.png',
         caption='Coral is the cup-magnet / carbon-steel striker hardware. Catalog contact pull does not set the nozzle release threshold.',
         add='3 steel cup magnets · 3 M5 × 25 countersunk screws · 3 carbon-steel 25 OD × 2 mm strikers · metal shims',tools='Hex key · caliper · independent tray support',
         actions=['Through-bolt each 25 × 7.7 mm steel cup with its M5 × 25 countersunk screw; verify the head seats flush in the actual cup.',
                  'Fit the three carbon-steel strikers on the opposite plate at their matching stations.',
                  'Fully seat all hardened ball/dowel contacts, then adjust matched metal pole-gap shims without separating those contacts.',
                  'Begin with a lightly retained supported tray. Qualify actual added nozzle release in all directions after gun/cable installation.'],
         gate='The registered seat closes fully, all cup/striker fasteners are retained and the air gap can be adjusted without moving the hardened contact datum.',
         fail='An aluminum striker, proud screw or magnet preventing seat closure fails the retainer. Correct the steel interface before force testing.')
    page('crash-contacts','Mount the two independent crash channels',
         'Each channel opens for either axial sign or a missing magnetic tray. One belongs to the relay coil; the other belongs to the logic STOP sense loop.',
         section='Payload / crash detection',art='crash-contacts.png',
         caption='Coral is the four independent switch mounts. Fit received axial COM–NC contacts and plate-presence COM–NO contacts held pressed when seated.',
         add='4 switches · separate CH1 / CH2 mounting tabs and terminal labels',tools='Continuity meter · power unplugged · tray catch installed',
         actions=['Set each axial flat-dwell cam to open its COM–NC contact for either sign near 0.25 mm, before ±1.0 mm capture.',
                  'Set each plate-presence switch so the fully seated tray holds its COM–NO closed; remove the tray to verify it opens.',
                  'Wire one axial and one presence contact in series as CH1. Repeat independently as CH2.',
                  'Meter both channels for seated, positive axial, negative axial and removed-tray cases. Closing a channel never authorizes motion.'],
         gate='CH1 and CH2 each close only with the mount healthy and seated, and independently open for every tested release/missing-tray case.',
         fail='A shared terminal, wrong NO/NC choice or overtravel-damaged switch defeats detection. Correct both independently metered channels before routing power.')
    page('umbilical-boom','Support the umbilical independently',
         'The metal boom carries cable weight above the gun workspace. Gentle slack follows motion without pulling the gun or moving either camera.',
         section='Payload / independent support',art='fiber-boom.png',
         caption='Coral is the independent 900 mm post, 750 mm top arm and padded saddles. The envelope is routing geometry, not a fiber bend qualification.',
         add='4040 × 900 mm post · 4040 × 750 mm arm · metal corners · 2 fiber-saddle · straps',tools='6 mm hex · gun cable manufacturer bend guidance',
         actions=['Through-bolt the post\'s metal base joints to the bench outside the motion/camera frame.',
                  'Join the arm with metal corners and place the two padded saddles on it.',
                  'Route the umbilical with loose supported loops using the gun manufacturer\'s minimum bend radius.',
                  'Move the supported empty cradle through the intended local poses and adjust slack before clamping the gun.'],
         gate='The umbilical does not carry frame load, pull a camera or tighten at an intended pose. Its permitted bend radius is documented.',
         fail='Cable tension or an undocumented bend can dominate corrections or damage the cable. Correct the support path before loading the gun.')
    page('umbilical-swivels','Fit the two free-turning saddles',
         'The fixed metal axle clamps the bearing inner race. The saddle rotates with the outer race, retained by its open printed cap.',
         section='Payload / independent support',art='fiber-swivel.png',figure='short',style='compact',
         caption='The bearing cap and its bolts are separated down the actual assembly axis for access. All contact tubes remain metal.',
         add='2 swivel bases / saddles / caps · 2 608ZZ · 8 ten-mm base spacers / M6 × 30 · 2 M8 × 50 axles · 4 M3 × 20 cap bolts',
         tools='Slot-8 M6 T-nuts · washers / locking nuts · caliper · supported actual cable',
         actions=['Mount each base over four 10 mm metal spacers using four M6 × 30 joints. Verify T-nut reach without bottoming.',
                  'Fit its fixed lower/upper metal contact tubes and the 608 inner race on the smooth portion of the M8 × 50 axle.',
                  'Seat the saddle around the outer race; fit the cap with two M3 × 20 through-joints, washers and locking nuts. Keep its 14.5 mm opening clear of the inner race.',
                  'Tighten the axle only onto metal tubes / inner race. Verify free rotation with the supported actual cable, cold and warm.'],
         gate='Both saddles turn freely, the caps retain only their outer races, and no axial clamp load crosses a rotating printed wall.',
         fail='A pinched outer race, touching contact tube or unstable base fails support. Correct the measured stack before routing cable weight through it.')
    page('gun-jaws','Pad the metal jaw bars',
         'Four metal bars carry clamp load. Four TPU pads protect the gun body; each pad is backed by metal.',
         section='Payload / clamp',art='metal-jaws.png',
         caption='Two lower and two upper 25 × 130 × 6.35 mm bars. Pad locations are adjusted to broad unobstructed gun-body surfaces.',
         add='4 gun-jaw · 4 gun-jaw-pad · 4 M5 × 80 through-bolts, washers and locking nuts',tools='4 mm hex · 8 mm wrench · gun on soft bench support',
         actions=['Install the lower metal bars and their pad faces on the open roll cradle.',
                  'Identify broad gun-body clamping surfaces clear of controls, vents, wire-guide attachment and cable strain relief.',
                  'Place the disabled gun on the lower pads while holding it independently.',
                  'Fit upper pads/bars and start all four through-bolts loosely.'],
         gate='Every planned contact is a pad on metal backing, and no bar or bolt obstructs the gun\'s required openings.',
         fail='The blue gun envelope does not establish fit. If the real body has no clear contact pair, adapt the jaw metal/pad positions before tightening it.',
         mind='Laser emission disabled; tube removed. Keep the gun supported until the clamp and independent catch are checked.',mind_label='Gun installation setup')
    page('gun-clamp','Seat the adjustable gun clamp',
         'Progressive opposed tightening keeps the body centered without relying on a shaped print matching an unmeasured gun.',
         section='Payload / clamp',art='gun-clamp.png',
         caption='Coral is the metal-backed clamp. Blue is an illustrative gun envelope; inspect the actual gun and wire guide at every contact.',
         tools='4 mm hex · 8 mm wrench · independent support',
         actions=['Bring opposite nuts into pad contact in small alternating increments.',
                  'Stop when the body cannot shift under a gentle hand check. Do not crush the body or compress a control.',
                  'Install the independent gun tether/catch to metal anchors, keeping it clear of the wire path.',
                  'Verify clamp and tether with the gun supported; label the observed gun/tool transform for later calibration.'],
         gate='The actual gun cannot slide in the padded metal clamp, and its independent catch arrests a released load before any collision.',
         fail='Movement, body distortion or a catch outside the fall envelope fails payload installation. Correct the metal/pad/catch arrangement before removing support.',
         mind='Laser emission remains disabled; the workpiece is removed. Every catch attachment is metal-backed.',mind_label='Gun remains cold')
    page('scale-reference','Check the scale with reference weights',
         'The owned scale reads to 0.1 g and holds 2 kg. Reference checks bound error over that range before aliquots are combined into a larger test load.',
         section='Payload / release-force fixture',art='weighed-loads.svg',figure='short',style='compact',
         add='1 kg M1 weight · M2 weight set totaling 1 kg · result sheet',tools='Owned scale · level rigid bench · two-minute warmup',
         actions=['After warmup, check 0, 500, 1000, 1500 and 2000 g ascending and descending, for three complete cycles.',
                  'Require every reference result within ±0.3 g and unloaded zero 0.0 ±0.1 g. If needed, span-calibrate at 1 kg and repeat every check.',
                  'Record stated weight classes and certificate status: combined reference MPE at 2000 g is 0.224 g; resolution alone is not accuracy.',
                  'Repeat zero and 1 kg checks each session. Assign a conservative 1.0 g uncertainty to every weighed aliquot after passing.'],
         gate='All three ascending/descending cycles and the current session zero/span check pass; the scale never exceeds its 2 kg capacity.',
         fail='An excessive error, drifting zero or overload fails the mass record. Correct/calibrate the scale and repeat before calculating force.')
    page('crash-load-fork','Build the temporary nozzle loading fork',
         'A separate padded body clamp carries a metal fork around the gun. Its cord stud applies load at the observed nozzle datum without touching the nozzle.',
         section='Payload / release-force fixture',art='crash-loading.png',
         caption='Blue identifies the temporary loading fixture and cord direction. Keep its contact clear of the trigger, vents, wire and nozzle optics.',
         add='2 spare jaw bars / TPU pads · 2 nozzle-test-fork-arm · nozzle-test-bridge · 4 metal angles · M6 × 40 cord stud / 2 jam nuts',
         tools='Laser key off · wire retracted · tube removed · independent tether / catch · accepted redirect',
         actions=['Clamp the two spare padded jaw bars on a safe gun-body surface. Join the two 210 mm metal fork arms outside the gun at Y = ±80 mm with the rear angle joints.',
                  'Join the 180 mm front bridge using both front angles. Cross-drill the grade-8.8 M6 × 40 stud Ø3.5 mm, 5 mm from under its head; lock it against both bridge faces.',
                  'Align and observe the cord-hole centroid at the actual nozzle datum; its illustrative model projects 5 mm behind the bridge. Keep it clear of every gun opening.'],
         gate='The fork is rigid at its padded body contacts, and its measured cord-hole position reaches the actual nozzle datum without loading an optic/control.',
         fail='A moving clamp, wrong load point or obscured opening fails the loading fork. Correct its metal/pad geometry before applying a test force.')
    page('crash-load-fixture','Apply load at the calibrated nozzle datum',
         'Use the real gun, liner and supported cable. Gravity and routing remain at their working baseline as a characterized redirect turns added force toward the selected direction.',
         section='Payload / release-force fixture',art='crash-loading.png',figure='short',
         caption='The actual source fixture places its cord hole at an illustrative nozzle endpoint. Measure the installed endpoint, cord angle and catch clearance.',
         tools='Accepted loading fork · laser key off · tube absent · tether / catch · accepted redirect',
         actions=[
                  'Arrange the cord along the selected added-force direction; a redirect changes direction while the load hangs vertically.',
                  'Characterize redirect loss in both directions at the actual 2–3 kg test load, using separately weighed aliquots to form complete equal loads.',
                  'Record the unloaded gravity/cable baseline, cord alignment and catch clearance before increasing added force.'],
         gate='The applied force reaches the stated nozzle datum, baseline/catch are recorded and actual-load redirect loss is bounded in both directions.',
         fail='A loaded control/optic surface, unknown redirect loss or changing cable baseline invalidates release measurement. Correct the fixture before hanging test masses.')
    page('crash-release-force','Grade release in every used direction',
         'The mount remains seated through 20 N added nozzle load and releases before 30 N. A complete uncertainty interval decides this narrow gate.',
         section='Payload / release qualification',art='weighed-loads.svg',figure='short',style='compact',
         tools='Accepted mass / redirect records · weighed aliquots · both-channel meter · guarded containers',
         actions=['Weigh each complete cup/cord attachment and every aliquot individually below 2 kg. Sum masses and sum their 1.0 g uncertainty bounds linearly.',
                  'Add load gradually; record the last seated mass and first releasing mass. Include the force-step bracket and any dynamic overshoot.',
                  'Calculate F = grams × 0.00980665. Add mass, measured redirect-loss, cord-angle and load-step/dynamic allowances conservatively to U.',
                  'Repeat +axial, −axial and both transverse signs under actual gravity/cable baseline. Both CH1 and CH2 must open; support, reseat and recalibrate after each release.'],
         gate='Every directional release interval [F − U, F + U] lies wholly inside 20–30 N; the mount stays seated through 20 N and the independent catch retains every released load.',
         fail='A too-early/late release, unresolved force interval, surviving channel or missed catch fails that direction. Adjust graded pod preload or seated magnet gaps and repeat.',
         note='The 500 N gauge’s uncertainty is too large for this gate. During dry release tests the operator also stops the existing independent pedal rotator; no live integration is qualified.')
    page('installed-z-load-fixture','Brace the installed Z load fixture',
         'The gauge supports the moving head through a metal platen. Its separate test column reacts into the station and does not carry a powered travel command.',
         section='Retention / actual load',art='installed-z-load-bound.png',figure='short',style='compact',
         caption='Blue identifies the source-built temporary fixture. The gauge body is a catalog envelope; the received probe height sets the final mount position.',
         add='500 mm 4040 column · 2 spare matched corners / 4 M8 × 16 · 70 × 160 gauge back · 2 ten-mm metal spacers / M6 × 25 · 60 × 40 platen',
         tools='Actual 500 N gauge · 4 measured-depth rear M4 screws · slot-8 T-nuts / washers · independent catch',
         actions=['Brace the test column independently to the station with both metal corners; use four M8 × 16 joints with washers and matching T-nuts.',
                  'Mount the gauge vertically on its 41 × 73 mm rear-hole rectangle. Verify received screw depth and engagement before seating all four M4 screws.',
                  'Fit the backing’s two vertical slots with two M6 × 25 guide bolts, washers and 10 mm metal spacers. Clear the rear gauge screw heads.',
                  'Align its upward compression probe below the moving Z-head upright through the platen. Set an independent catch within 1 mm.'],
         gate='The column is separately braced; gauge/platen contact only the moving head. The catch is within 1 mm and no fixed mast or actuator shares the gauge reaction.',
         fail='An unstable column, wrong probe axis or parallel load path invalidates this fixture. Correct it while the head remains independently supported.')
    page('installed-z-feed-jack','Fit the metal feed jack',
         'A screw feeds the gauge backing in small restrained increments. The backing guides retain it laterally while allowing smooth axial travel.',
         section='Retention / actual load',art='installed-z-jack.png',figure='short',
         add='installed-Z-jack-angle · 2 M6 × 16 / slot-8 T-nuts / washers · fully threaded M6 × 80 / 2 nuts / 2 washers',
         tools='10 mm wrench · camera / indicator · head supported · catch within 1 mm',
         actions=['Mount the metal jack angle 60 mm below the gauge-back lower edge with both M6 × 16 joints.',
                  'Fit the fully threaded feed screw so its tip reacts only on the metal backing edge. Fit the lower working nut and upper lock nut at the angle.',
                  'Leave visible axial clearance under the guide washers so both slots slide. The complete head force must enter only through the probe/platen.',
                  'Hold the lower nut, loosen the upper lock nut and feed at most 1/12 turn: 0.0833 mm. Relock after every increment.'],
         gate='The screw controls smooth backing feed and the independent catch remains within 1 mm. Column braces stay tight; the moving head touches only the platen.',
         fail='A stuck guide or jump fails feed. Unload onto the independent support and correct it. Never loosen braces or lift the head by hand to obtain a reading.')
    page('actual-z-load','Bound the actual carried Z load',
         'The carried metal, bearings, hardware, gun and cable all contribute. Their measured weight and vertical cable pull set the installed gravity bound.',
         section='Retention / actual load',art='installed-z-load-bound.png',figure='short',style='compact',
         tools='Accepted scale record · 500 N gauge / rigid fixture · actual gun / liner / supported cable · independent catches',
         actions=['Keep the complete head supported. Weigh carried parts separately below the scale’s 2 kg capacity; use the 500 N gauge for heavier subassemblies.',
                  'Include every plate, bearing, spring, fastener, wire and gun attachment. Record mass/force uncertainty and preserve the assembled-load inventory.',
                  'Take the full head load through gauge/platen before disconnecting its actuator output. Record supported load and controlled onset in both feed directions through the accepted cable poses.',
                  'Include rail stiction, vertical cable pull and complete uncertainty in the worst load. Restore actuator hardware and a fresh observed datum before motion.'],
         gate='The complete actual upper Z load is ≤300 N and the downward seat’s measured lower lift threshold is ≥390 N; no load is omitted or double-counted.',
         fail='An excessive or unbounded load fails this configuration. Add passive support/counterbalance or redesign the carried mass before loaded motor motion.',
         note='The 300 N screen includes physical load uncertainty. CAD density estimates and printed settings do not accept the actual assembly weight.')
    page('actual-angular-load','Measure signed gravity and cable moments',
         'An endpoint pull alone cannot bound a cable’s free couple. A separate drive-lever hub lets a balanced test lever measure shaft moment while the output hub carries the actual gun and cradle.',
         section='Retention / actual load',art='angular-load-lever.png',figure='short',
         caption='The angular-load-lever has a 12.5 mm bore and 26 × 20 mm four-M5 pattern. The small-radius retainer lever is a separate service part.',
         add='angular-load-lever · reuse 4 M5 × 45 drive-lever hub bolts · gauge backing / vise or characterized redirect',tools='Gun / cable at actual baseline · independently clamped catch / support',
         actions=['Park and restrain the gun independently. Let the clamped gauge or characterized cord restrain the angular rotor before disconnecting its actuator clevis.',
                  'Transfer the lever to the separate angular drive-lever hub using its four M5 × 45 bolts. Keep actual payload on the output hub; retain both qualified clamp bolts and the shaft’s metal axial-capture stack.',
                  'Let the gauge/cord take the rotor reaction, then clear normal supports from the measured moment path. Retain the immediately nearby independent catch.',
                  'At every accepted pose, measure signed tangential onset in both directions at the actual 100 mm radius. Reverse the gauge reaction side; use weighed cord loads for small roll forces.',
                  'Stop at onset, before catch/capture contact. Record the larger absolute force, complete uncertainty, alignment and actual lever radius.'],
         gate='Every permitted pose has a restrained signed onset record, and its conservative moment upper bound includes gravity, cable and bearing resistance.',
         fail='An unrestrained rotor, unknown force line or changing cable baseline invalidates the moment bound. Restore support and correct the fixture before releasing a clevis.')
    page('actual-backdrive-bound','Compare measured load with passive holding',
         'A measured upper actuator force and a measured lower friction torque establish the holding margin. The loose powered test fixture measures another property.',
         section='Retention / actual load',art='angular-law.svg',figure='short',style='compact',
         rows=[('Moment upper bound','(largest absolute onset force + U) × measured force arm'),
               ('Angular screw force','Moment upper / minimum measured dL/dθ over the accepted path'),
               ('Ideal backdrive torque','Force upper × 0.002 / (2π) N·m')],headers=['Bound','Use the installed measurement'],
         actions=['Verify physical clevis datums before using the conservative 133.60 mm minimum geometry lever. Include actual radius, force and path uncertainty.',
                  'For Z use its complete actual weight/cable force upper bound; for pitch/roll use their measured moment-to-screw bounds.',
                  'Require each retainer’s measured lower torque ≥2 × its actual backdrive upper bound.',
                  'Restore clevis/hub hardware, split-clamp preload and witness marks. Establish a fresh observed physical datum.'],
         gate='All three installed gravity axes have the required 2× passive margin with measured bounds and correctly restored metal joints.',
         fail='A failed inequality or unobserved force couple prevents loaded use. Improve retention/support or reduce the permitted path/load; raising motor current does not fix passive holding.',
         note='At the 100 N pitch screen, measured lower drag must reach at least 0.0637 N·m within its 0.06–0.08 band. Target 0.070; a 0.060 result does not accept that load.')
    page('loaded-retention','Prove retention with the real load',
         'The brakes must carry the actual gun, wire guide and supported umbilical when motor power or belt support disappears.',
         section='Retention / loaded check',art='hero.png',figure='short',
         caption='A catch immediately below the supported load limits test motion. No tube is inside the fall envelope.',
         tools='Accepted torque records · secondary support/catch · camera / indicator log',
         actions=['Record the loaded central pose and each intended extreme pose with its cable routing.',
                  'Position a secondary support immediately beneath the load. Remove motor power and observe the retained pose.',
                  'Separately release belt drive support while preserving the screw brake. Observe for runaway or collision.',
                  'Repeat after initial dry cycling; record any movement and invalidate the coordinate reference if it occurs.'],
         gate='The load stays supported inside its measured catch/clearance envelope. Lower measured brake torque is at least twice the upper bound of actual gravity/cable backdrive torque.',
         fail='A slipping load or failed torque margin stops loaded motion. Improve passive support/retention and repeat; more motor current cannot repair power-off holding.',
         mind='Laser disabled; tube removed; secondary support present. The test accepts recoverable load support, not 5 µm power-off pose retention.',mind_label='Retention test setup')


def electrical_preparation():
    page('control-backplane','Lay out the fixed control backplane',
         'Six labeled carriers, the Pico adapter and power distribution stay on a fixed insulated board outside the motion and optics envelopes.',
         section='Controller / preparation',art='control-backplane.svg',
         caption='This is a placement map. Each carrier still needs its own received-pin verification before a driver is inserted.',
         add='300 × 300 clear-PETG blank · received carrier / Pico / fuse / DIN footprints · labels',tools='Brick and USB unplugged · caliper · drill · clearance check',
         actions=['Lay out two columns of three carriers: X/Y/Z on UART A, U/V/W on UART B. Place the Pico, fuse block and DIN rail beside them.',
                  'Fit the clipped buck, relay, end stops and at most nine selected terminal blocks on the 203.2 mm rail; confirm actual footprint and service access.',
                  'Keep the 24 V distribution and motor leads away from the GPIO, UART and loop terminals.',
                  'Transfer only actual mounting holes onto clear blank lands: Ø3.4 mm components, Ø6.5 mm frame holes with ≥12 mm edge distance. Drill the blank alone.'],
         gate='Received footprints fit with plug, meter and fuse access, and every drilled board/washer position preserves copper isolation.',
         fail='A forced layout or an unmapped trace at a mounting point fails this blank. Correct the unpowered placement before drilling or fitting electronics.')
    page('controller-board-mounts','Mount the boards above the blank',
         'Four 6 mm insulating spacers support every carrier and the Pico adapter. The remaining fixed components fasten directly to the blank.',
         section='Controller / mounting',art='controller-mounts.png',figure='short',style='compact',
         caption='The blank and spacers are actual CAD. This clearance illustration leaves electronic footprints for transfer from the received boards.',
         add='28 printed spacers · 36 M3 × 25 · 36 M3 locknuts · 72 M3 washers',tools='All power unplugged · small hex / nut driver · continuity meter',
         rows=[('Carriers / Pico','24 / 4 bolts; four spacers under each board'),
               ('DIN / fuse / fan base','2 / 4 / 2 bolts; direct blank mounting')],headers=['Allocation','Installed hardware'],
         actions=['Use a washer at both ends of each M3 × 25 joint and a locking nut; keep the carrier/Pico copper clear of metal washers.',
                  'Keep the 6 mm board standoff. Unplug USB and 24 V before trimming excess leads; verify visible clearance from the blank and all mounting metal, then recheck cold isolation.',
                  'Measure the actual stack; retain two full threads beyond each nut. Re-meter every mounted carrier’s net isolation.'],
         gate='All 36 joints are seated, every board remains insulated and clear, and the unpopulated sockets still pass the received-pin continuity map.',
         fail='A board bend, copper-to-fastener connection or short projection fails mounting. Unplug and correct the actual spacer/washer/hole stack before wiring.')
    page('controller-fan-mount','Fit the fan and both guards',
         'The 80 mm fan blows along the two driver columns. The printed stand keeps the airflow opening clear and carries guards on both open faces.',
         section='Controller / mounting',art='controller-fan-stand.png',figure='short',
         caption='Coral is the actual 90 mm stand. The 76 mm opening establishes airflow clearance; the received fan establishes its four drilled holes.',
         add='80 mm / 24 V fan · 2 guards · 4 M4 × 50 / 4 locknuts / 8 washers · 2 allocated M3 × 25 base bolts',tools='Fan unplugged · Ø4.5 mm drill · ruler · small hex',
         actions=['Center the received fan on the stand and transfer its four holes. Drill Ø4.5 mm only in sound wall outside the 76 mm opening; remove the fan first.',
                  'Fit one guard on each open face with M4 × 50 through both guards, the fan and 4 mm stand; use a washer at both ends and locking nut.',
                  'Measure the received stack and leave two full threads beyond each nut. Keep projecting tips clear of wires and verify free blade rotation.',
                  'Bolt the stand base to the blank at X = ±32, Y = 20 mm. Aim its airflow along both heatsink columns.'],
         gate='Both fan faces are guarded, blades and wires are clear and the installed stand directs real airflow over all six heatsinks.',
         fail='A hole crossing the airflow bore, trapped blade or unguarded face fails this support. Correct the stand/stack before applying fan power.')
    page('controller-fixed-mount','Attach the backplane to fixed metal',
         'The horizontal blank and fan stand stay outside every moving carriage, camera and catch path. Wire strain relief ends on fixed structure.',
         section='Controller / mounting',art='control-backplane.svg',figure='short',
         add='4 M6 × 16 · 4 slot-8 M6 T-nuts · 4 M6 washers · fixed cable strain relief',tools='All power unplugged · 5 mm hex · intended workspace sweep',
         actions=['Attach the blank at all four fixed 4040 points; measure actual slot engagement and prevent screw bottoming.',
                  'Keep the board horizontal with the fan stand base on it. Tighten only enough to seat the insulating panel.',
                  'Mount MOTOR POWER and the latched stop within reach outside travel. Retain every cable before it reaches a terminal or socket.',
                  'Sweep the unpowered motion, optics and catch envelopes; no carried cable may pull the controller.'],
         gate='Fixed mounts are seated without panel bending, controls remain reachable and no moving item reaches the board or its wiring.',
         fail='Bottoming, panel deflection or moving wire load fails the fixed installation. Correct the metal mounting route before electrical commissioning.')
    page('driver-pin-map','Map the received driver pins',
         'A TMC2209 module and its carrier must agree on every named pin. A trimmer position or an A4988 carrier label does not establish that agreement.',
         section='Controller / received parts',art='driver-map.svg',
         caption='The named connection map is logical. Photograph the received module and carrier; mark their actual socket orientation separately.',
         add='6 BIGTREETECH TMC2209 V1.3 modules · received pin drawings',tools='Power unplugged · continuity meter · close photograph',
         actions=['Photograph each module label and both R110 sense resistors.',
                  'Fit two eight-position female sockets per module to its actual spacing. Map every P1A pin using the next page, including CLK to GND.',
                  'Meter the carrier\'s power rails and terminal labels before inserting a module.',
                  'Record the socket map for all six axes. Leave modules out until the cold continuity page is passed.'],
         gate='The selected module drawing, board labels and metered carrier routes agree on all named pins; both resistors read R110 by marking.',
         fail='An unmapped pin or different sense resistor stops that carrier. Repair its map or rebuild the governed settings before applying power.')
    mapping=json.loads((ROOT/'hardware/gun-positioner/wiring-manifest.json').read_text())['module_socket_map']
    page('driver-socket-table','Verify the BTT V1.3 socket map',
         'This is the manufacturer P1A numbering. Match the actual received view and socket spacing, then mark the VM end before insertion.',
         section='Controller / received socket map',art='driver-map.svg',figure='short',style='reference',
         caption='The illustration names nets. The supplier drawing and actual marked board establish the physical view.',
         rows=[(str(pin),mapping['P1A'][str(pin)]) for pin in range(1,17)],headers=['P1A pin','Required function / route'],
         note='P1B pins 17 INDEX and 18 DIAG stay unconnected; pin 19 VREF is the measured test point. No SPREAD header: R7 and R10 remain NC. <a href="'+mapping['source']+'">BTT V1.3 schematic</a>.',
         gate='Every socket contact meters to its named route, CLK reaches GND, UART uses P1A5 and P1A4 stays unconnected.',
         fail='A reversed view, shared pad or bridged factory strap fails this interface. Keep modules removed and correct the individual routes before power.')
    page('harness-connectors','Separate motor power from logic plugs',
         'Two connector sizes keep the 24 V crash-coil circuit physically separate from the GPIO sense circuit. Meter numbered contacts in both mating views.',
         section='Controller / harness',art='harness-connectors.svg',figure='short',style='compact',
         caption='Named pin numbers govern. This is a net map; the actual connector’s solder view can be mirrored relative to its mating face.',
         add='7 GX16-4 matched pairs · 8 GX12-2 matched pairs · axis / STOP / CH1 / CH2 labels',tools='All power unplugged · continuity meter · strain relief',
         rows=[('6 motor GX16-4','1 A1 · 2 A2 · 3 B1 · 4 B2'),
               ('Crash CH1 GX16-4','1 coil-chain input · 2 return to COIL+ · 3/4 unused'),
               ('6 axis GX12-2','1 GPIO input · 2 GND return; four contacts in series'),
               ('STOP sense GX12-2','1 GP26 route · 2 through STOP NC2 toward CH2'),
               ('Crash CH2 GX12-2','1 from STOP NC2 · 2 GND return')],
         headers=['Labeled pair','Contact allocation'],
         gate='CH1 has no GND pole, unused contacts stay isolated and no 24 V connector can mate with a GPIO loop. Both ends meter to their recorded numbered contacts.',
         fail='A reversed solder view, crossed pair or logic/power cross-mating defeats isolation. Correct the complete unplugged pair and meter it before use.')
    page('motor-pairs','Identify the two motor windings',
         'A bipolar motor has two isolated continuity pairs. Record the received colors rather than assigning winding identity by color alone.',
         section='Controller / motor harness',art='motor-pairs.svg',
         caption='A1/A2 is one winding; B1/B2 is the other. Between pairs the unplugged motor is open circuit.',
         add='6 GX16-4 motor pairs · paired motor wires · axis labels',tools='All power unplugged · ohmmeter · ferrule crimper',
         actions=['Unplug the motor from every driver. Find exactly two finite-resistance continuity pairs.',
                  'Assign one pair A1/A2 and the second B1/B2; record actual colors and plug positions.',
                  'Crimp/land each complete pair at its named driver outputs. Twist the wires within each pair.',
                  'Label both ends by axis and secure a service loop clear of travel.'],
         gate='Each motor has two winding pairs and no continuity between those pairs or from a winding to its case.',
         fail='A crossed pair or case connection fails the winding map. Correct the unplugged harness before driver insertion; never hot-plug a motor.')
    page('local-bypass','Fit the local motor capacitors',
         'Local bypass keeps the current path short at each carrier. The bulk capacitor sits at the switched motor distribution.',
         section='Controller / bypass',art='local-bypass.svg',
         caption='Electrolytic plus lands on VM. The striped negative lead lands on motor 0 V. The diagram does not qualify supply transients.',
         add='6 × ≥100 µF / ≥35 V · 1 × ≥470 µF / ≥35 V · insulated terminals',tools='Brick unplugged · polarity labels · meter',
         actions=['Place one local capacitor directly across VM/GND at each carrier.',
                  'Place the bulk capacitor across the switched VM distribution and common 0 V.',
                  'Keep VM/GND routes short and observe the module maker\'s carrier guidance.',
                  'Meter polarity and absence of a VM-to-GND short after the soldering is inspected.'],
         gate='All seven electrolytics have correct polarity and voltage rating, and no exposed lead can touch another net.',
         fail='A reversed capacitor or short fails the power assembly. Disconnect and replace/correct it before plugging in the adapter.')


def electrical():
    page("motor-power", "Switch the motor bus",
         "The latched stop and released gun crash mount each open the relay coil circuit. Their separate contacts report the same fault to the powered controller.",
         section="Controller / power", art="stop-power.svg",
         caption="The fuse precedes the relay and logic-buck branches. Relay NO closes only while its coil is energized. Logic remains alive when motor VM is removed.",
         add="24 V adapter · 5 A main, 6 × 1 A motor and 500 mA coil fuses · 24 V relay · stop · toggle · 1N4007",
         tools="Adapter unplugged · meter · ferrule crimper",
         actions=["Wire adapter + through the 5 A fuse, then split to relay COM and the coil control route.",
                  "Wire the 500 mA coil branch → MOTOR POWER toggle → STOP NC1 → BREAKAWAY CH1 → coil +. Coil - and adapter - go to common 0 V.",
                  "Route relay NO through one 1 A fuse per VM branch. Put the diode's band at coil +.",
                  "Label separate STOP NC2 / BREAKAWAY CH2 sense contacts. Their wires belong only to the logic loop; absent crash contacts stay open."],
         gate="Both pressing STOP and releasing the crash mount interrupt coil continuity independently. Every driver's VM feed passes through its fuse and relay NO.",
         fail="A bypassed fuse, NC/NO mix-up or shared stop terminal defeats the cutoff. Disconnect the adapter and trace the named routes again.")
    page("logic-power", "Keep the controller alive",
         "USB loss must leave the controller powered long enough to detect its watchdog timeout. The unswitched buck supplies that independent logic power.",
         section="Controller / power", art="logic-power.svg",
         caption="The 1N5819 band points toward Pico VSYS. The Pico's onboard diode isolates USB power; external 5 V never lands on VBUS.",
         add="24 V → 5 V buck, ≥0.5 A · 500 mA branch fuse · 1N5819 · VSYS / GND wires",
         tools="USB disconnected · motor VM disconnected · voltmeter",
         actions=["Connect buck input + after F0 through its separate 500 mA fuse; input - goes to the common 0 V star.",
                  "Power the buck by itself. Adjust and meter its output to 5.0 V, then unplug 24 V.",
                  "Route output + → 1N5819 → Pico VSYS, physical pin 39; band faces VSYS.",
                  "Connect buck output - to GND. Keep all buck output wiring clear of Pico VBUS."],
         gate="VSYS receives power through the Schottky diode, and 3V3 is present with USB absent while 24 V is on. VBUS has no external buck wire.",
         fail="Missing 3V3 defeats USB-loss protection. Disconnect 24 V and correct buck voltage, diode direction and VSYS/GND routing.")
    page("step-direction", "Route STEP and DIR",
         "Each driver receives its own motion pair. The shared ENN signal holds every driver disabled until the controller permits motion.",
         section="Controller / motion", art="step-dir.svg",
         caption="These are logical nets. Locate pins from the carrier's printed labels before landing any wire.",
         add="12 STEP/DIR wires · one ENN bus · one 10 kΩ pull-up",
         tools="USB and 24 V unplugged · fine solder tip · meter",
         rows=[("X", "GP2 pin 4 / GP3 pin 5"), ("Y", "GP6 pin 9 / GP7 pin 10"), ("Z", "GP8 pin 11 / GP9 pin 12"),
               ("U yaw", "GP10 pin 14 / GP11 pin 15"), ("V pitch", "GP12 pin 16 / GP13 pin 17"), ("W roll", "GP14 pin 19 / GP15 pin 20")],
         headers=["Axis", "Pico STEP / DIR (physical pin)"],
         gate="GP16 reaches all six ENN pins. One 10 kΩ resistor pulls this shared node to 3.3 V. Each STEP/DIR pair reaches one driver only.", style="compact",
         fail="Crossed pairs or an absent ENN pull-up can move the wrong axis at boot. Meter and correct the route before installing drivers.")
    page("uart-buses", "Make two readable buses",
         "X, Y and Z share UART0. U, V and W share UART1. Each bus has addresses 0, 1 and 2.",
         section="Controller / diagnostics", art="uart-buses.svg",
         caption="One 330 Ω resistor belongs in each TX route. RX connects directly to that bus's PDN_UART node.",
         add="Two 330 Ω series resistors · two 1.8 kΩ pull-ups · six address strap pairs",
         tools="Power unplugged · meter · carrier pin labels",
         actions=["Connect GP0 through 330 Ω to bus A; connect GP1 directly to bus A.",
                  "Connect GP4 through 330 Ω to bus B; connect GP5 directly to bus B.",
                  "Land X/Y/Z on bus A and U/V/W on bus B; pull each bus to 3.3 V through 1.8 kΩ.",
                  "Set the address straps to 0/1/2 within each bus. Label every driver by its axis."],
         gate="A driver appears on one bus and one address. There is no fourth axis sharing either 0/1/2 address.",
         fail="A duplicate address cannot be diagnosed independently. Correct MS1/MS2 straps while unpowered; verify all six by UART before motion.")
    page("travel-loops", "Wire six closed loops",
         "Four normally closed contacts serve each axis: two travel ends and two opposed force-link trips. Opening any contact or wire stops every axis.",
         section="Controller / limits", art="limit-loop.svg",
         caption="Travel low/high and overload −/+ are one series chain per axis. The operator stop and gun crash release have separate chains.",
         add="12 travel + 12 overload NC switches · six 10 kΩ pull-ups · six labeled loops",
         tools="USB and 24 V unplugged · meter in continuity mode",
         actions=["For X, route GP17 → low travel COM/NC → high travel COM/NC → overload− COM/NC → overload+ COM/NC → GND.",
                  "Repeat independently on Y GP18, Z GP19, U GP20, V GP21 and W GP22.",
                  "Add a separate 10 kΩ pull-up from each input to 3.3 V.",
                  "Press each switch separately while metering its loop; release it and check continuity returns."],
         gate="Each of the 24 switches opens its assigned loop by itself. All six loops are closed at the seated central pose.",
         fail="A switch that does not open its loop is bypassed or uses NO. Correct COM/NC routing; do not bridge the failed loop.")
    page("logic-stop", "Land the logic stop",
         "The operator stop and seated gun crash contact both carry 3.3 V logic in this chain. Either reports a stop even when USB remains powered.",
         section="Controller / stop", art="logic-stop.svg",
         caption="Crash CH2 has an axial COM/NC in series with a plate-presence COM/NO held closed only by the seated plate. CH1 is an independent matching chain.",
         add="STOP NC2 + BREAKAWAY CH2 → GP26 / GND · one 10 kΩ pull-up",
         tools="Power unplugged · continuity meter",
         actions=["Route GP26 → STOP NC2 → BREAKAWAY CH2 → GND; add the 10 kΩ pull-up to 3.3 V.",
                  "Wire CH2 axial COM/NC → plate-presence COM/NO. Meter continuity only with stop released, axial pod neutral and plate fully seated.",
                  "Verify no NC2 terminal has continuity to adapter +, relay COM or relay NO.",
                  "Leave uninstalled crash terminals open; preserve electrically separate CH1/CH2 routes through the removable mount."],
         gate="Axial travel and removal of the plate each open both independent crash channels; STOP also opens both chains. No logic terminal reaches 24 V positive.",
         fail="Any 24 V route into NC2 can destroy GPIO26. Keep power disconnected and separate the two contact blocks before continuing.")
    page("motor-bus-sense", "Measure switched voltage",
         "The divider tells the controller whether the motor bus is present. It also exposes loss of power while USB stays on.",
         section="Controller / sensing", art="voltage-divider.svg",
         caption="The 100 kΩ / 10 kΩ divider reduces 24 V to about 2.18 V. The 100 nF capacitor quiets the ADC node.",
         add="100 kΩ · 10 kΩ · 100 nF · GP27 sense wire",
         tools="Driver power disconnected · voltmeter",
         actions=["Connect 100 kΩ from switched VM to the sense node and 10 kΩ from that node to GND.",
                  "Connect 100 nF between the sense node and GND. Leave GP27 disconnected.",
                  "Power the adapter with the stop released; meter the node against GND.",
                  "Unplug the adapter after the reading, then connect the node to GP27."],
         gate="The sense node is approximately VM ÷ 11 and remains below 3.3 V. Pressing the stop removes power; the sense reading falls with VM.",
         fail="An incorrect ratio or a node at VM can damage the Pico. Disconnect the adapter; meter resistor values and correct the divider before GP27 is connected.")
    page('driver-fan','Add guarded cross-flow cooling',
         'One fixed 80 mm fan moves air across all six driver heatsinks during powered hold and motion. It runs from switched VM through its own fuse.',
         section='Controller / cooling',art='fan-power.svg',
         caption='Fan power is independent of GPIO. A finger guard and fixed mount keep wiring and hands clear of the blades.',
         add='24 V / 80 mm fan, ≤0.2 A · guard · fixed mounting bolts · 500 mA branch fuse',tools='Brick unplugged · polarity labels · fixed backplane',
         actions=['Mount the guarded fan so its airflow crosses all six heatsinks without a blocked intake.',
                  'Route switched VM → FFAN 500 mA → fan +; fan - lands at the 0 V star.',
                  'Strain-relieve both wires away from blades and STEP/UART connections.',
                  'Verify airflow when motor power is present; thermal commissioning uses this installed configuration.'],
         gate='The fan starts with switched VM, clears every wire and moves air across the six driver heatsinks.',
         fail='An unguarded, stalled or obstructed fan fails the cooling setup. Remove motor power and correct the mount/route before a loaded thermal trial.')


def cold_checks_and_software():
    page('continuity-gate','Meter before connecting power',
         'Keep USB and the brick unplugged and drivers out of their sockets. These continuity results close the cold wiring check.',
         section='Controller / cold checks',art='driver-map.svg',figure='short',style='reference',
         caption='Follow each named net to its received socket pin. Capacitors may charge during a resistance check; a sustained short is a failure.',
         tools='Continuity / resistance meter · labeled socket maps',
         rows=[('Must reach the named node','Each VM branch → its fused switched feed; every GND → 0 V star'),
               ('Must reach the named node','VIO → Pico 3V3; each STEP/DIR pair → exactly one axis'),
               ('Must be isolated','VM → VIO / VSYS / VBUS / STEP / DIR'),
               ('Must be isolated','NC2 → 24 V positive; motor winding A → winding B / case'),
               ('Must open separately','Each of 24 travel/overload switches; each of 6 unplugged axis loops'),
               ('Must open separately','STOP NC1/NC2; both axial crash NC and plate-presence NO pairs; STOP connector'),
               ('Must block coil power','MOTOR POWER OFF, STOP latched, or gun crash mount released'),
               ('Must match polarity','7 electrolytics; flyback band at coil +; Schottky band at VSYS')],
         headers=['Meter result','Named test'],
         gate='Every route, isolated pair and switched loop passes and its result is recorded before modules are inserted.',
         fail='An unexpected short or unopened loop fails cold assembly. Leave both supplies disconnected and repair that named route.')
    page('insert-drivers','Seat the six verified modules',
         'Both supplies remain unplugged. The received socket map sets orientation; pressing a reversed module into a carrier can connect motor voltage to logic.',
         section='Controller / module installation',art='driver-map.svg',figure='short',
         add='6 mapped modules · supplied heatsinks · six axis labels',tools='Brick and USB unplugged · received socket map',
         actions=['Compare VM, both GND positions and VIO on the module to the metered carrier map again.',
                  'Align both complete header rows before pressing each module straight into its socket.',
                  'Attach its supplied heatsink at the manufacturer\'s identified surface without bridging pins.',
                  'Keep motor plugs disconnected and belts removed for the first powered checks.'],
         gate='Every pin is in its matching socket and each axis label agrees with its carrier, UART bus and address.',
         fail='A shifted row or conflicting map fails installation. Lift the module with power disconnected and reconcile every named pin before reseating it.')
    page('flash-bench','Load the bench controller image',
         'The bench image configures low current for uncoupled motor checks. A firmware upload never establishes the physical central datum.',
         section='Controller / firmware',art='software-banner.svg',figure='short',
         caption='The Pico starts inhibited and unreferenced. The host opens one explicitly chosen USB port.',
         add='gun-positioner-bench.uf2 · Micro-USB data cable',tools='24 V unplugged · belts removed · supports engaged',
         actions=['Hold BOOTSEL on Pico while connecting USB. Release it when the RPI-RP2 drive appears.',
                  'Copy <code>firmware/src_gun_positioner/assets/gun-positioner-bench.uf2</code> to RPI-RP2.',
                  'Wait for its reboot. Record the USB serial port shown by the computer.',
                  'Keep motor power off while installing the host client on the next page.'],
         gate='The Pico reboots as a serial device. No motor motion occurs and physical reference remains invalid.',
         fail='If no serial device appears, check the data cable and named UF2. Do not reconnect 24 V to diagnose a USB upload.')
    page('host-client','Install and inspect the host client',
         'The host client logs command identity, issued counts and timing. It sends the heartbeats required for an armed session.',
         section='Controller / host',art='software-banner.svg',figure='short',style='compact',
         caption='Use the actual Pico port from the preceding page in place of PORT. The simulation opens no physical port.',
         tools='Computer · supplied source kit · Micro-USB data cable',
         console='python3 -m venv /tmp/gun-positioner-host\n/tmp/gun-positioner-host/bin/pip install -r firmware/src_gun_positioner/host/requirements.txt\n/tmp/gun-positioner-host/bin/python firmware/src_gun_positioner/host/positioner.py simulate --output /tmp/positioner-sim.jsonl\n/tmp/gun-positioner-host/bin/python firmware/src_gun_positioner/host/positioner.py inspect --port PORT',
         gate='Inspection identifies the intended Pico and reports unreferenced/inhibited state. Simulation writes a policy_simulation log.',
         fail='A simulation log is not physical motion evidence. If inspection fails, correct the selected port/cable before starting any motor-power session.')
    page('first-voltage','Check both supply paths',
         'Measure logic first and motor voltage second. The buck must keep logic alive with USB absent; the stop must remove VM without removing logic.',
         section='Controller / first power',art='logic-power.svg',figure='short',style='compact',
         tools='Voltmeter · supported mechanism · motors disconnected',
         actions=['USB only: meter 3V3 at every VIO node and HIGH at ENN. Firmware must remain inhibited.',
                  'MOTOR POWER OFF: connect 24 V, verify buck near 5.0 V and Pico 3V3 stable. Unplug USB and verify 3V3 remains present.',
                  'Reconnect USB; release STOP and turn MOTOR POWER ON. Meter switched VM near 24 V and GP27 near VM/11.',
                  'Latch STOP. VM must fall while Pico 3V3 stays present. Turn MOTOR POWER OFF before resetting STOP.'],
         gate='Logic persists on either supply path, motor VM appears only through relay NO, and GP27 stays below 3.3 V.',
         fail='Missing logic, unexpected VM or an overvoltage fails first power. Unplug 24 V and correct its source route before connecting motors.')
    page('fuse-startup','Qualify the selected cold-start fuses',
         'The adapter, buck, VM capacitors, fan and fuses are tested as one actual configuration before motor coupling or reference.',
         section='Controller / inrush screen',art='fan-power.svg',figure='short',
         tools='Existing voltmeter · contact temperature tool · selected installed fuses',
         actions=['Keep host USB connected and motor plugs disconnected through 30 brick cold starts; log each boot token, fuse and voltage result.',
                  'Perform 30 MOTOR POWER cycles, waiting for switched VM below 1 V between cycles.',
                  'Record actual fuse types/ratings, brick hiccups, Pico resets and holder/connection temperature.',
                  'Repeat this gate after changing a supply, buck, VM capacitor or fuse.'],
         gate='Every start is normal with USB preserving the Pico boot token: no fuse opening, brick hiccup, unexpected reset or overheated holder/connection.',
         fail='Any failed start changes fuse time-current selection or requires engineered inrush limiting. Do not silently raise a fuse rating; correct the actual combination and repeat.',
         note='Added electrolytics plus the six modules’ C1/C2 total nominal 1190 µF, about 0.343 J at 24 V, before fan/buck capacitance. This functional check does not measure millisecond peaks or overshoot.')
    page('reset-current','Check reset fallback and ENN',
         'Digital UART settings set working current. A reset driver can fall back to its VREF trimmer and straps, so verify the received module\'s minimum fallback and disable level.',
         section='Controller / reset behavior',art='driver-map.svg',figure='short',
         tools='Motor plugs disconnected · firmware inhibited · VREF drawing · voltmeter',
         actions=['With VM restored and ENN HIGH, identify the received VREF test point from its drawing.',
                  'Measure VREF against module GND and adjust its trimmer to the measured minimum; record each voltage.',
                  'Hold Pico RUN low and meter shared ENN with all six modules seated.',
                  'Separately enter BOOTSEL and repeat the ENN measurement; preserve physical supports and disconnected motors.'],
         gate='ENN remains above 0.7 × measured VIO in RUN-low and BOOTSEL, and each module\'s minimum VREF is recorded.',
         fail='A carrier pull-down, wrong test point or surviving high fallback current fails reset protection. Remove power and correct the received module/carrier interface before coupling.')
    page('isolated-motors','Test one uncoupled motor at a time',
         'Belts remain removed and motors are fixed to their mounts. This temporary reference identifies channels and sign; it is not a machine-coordinate reference.',
         section='Controller / bench motion',art='drive-motor.png',figure='short',style='compact',
         caption='A paper mark on the 20T pinion shows the nominal 28.8° motor rotation from a 0.0400 mm screw request.',
         tools='Bench image · supported mechanism · console log · shaft mark',
         console='/tmp/gun-positioner-host/bin/python firmware/src_gun_positioner/host/positioner.py console --port PORT --log /tmp/positioner-bench.jsonl\nclear\nstatus\nreference central\narm\njog X 0.0400 1000\njog X -0.0400 1000',
         gate='Status reports profile bench, six current_scales 10, six microsteps 16, 6400 counts/mm and max_rate 2000. Only the named motor moves and reverses.',
         fail='A wrong channel, unhealthy driver or stationary motor fails this check. Stop, unplug 24 V and correct the mapped winding/driver before coupling belts.')
    page('all-six-motors','Verify all six channels and UART',
         'Repeat the signed motor test on Y, Z, U, V and W. Then verify a six-channel request and the diagnostic response to a missing UART bus.',
         section='Controller / bench motion',art='uart-buses.svg',figure='short',style='compact',
         actions=['Run the same +0.0400 / −0.0400 pair on each remaining motor; record connector, sign and completion counts.',
                  'Issue the six-axis request below. Observe each requested sign and no unsolicited channel.',
                  'Disarm; unplug 24 V and disconnect one UART bus. Restore power and issue <code>clear</code>; it must refuse a healthy ready state.',
                  'Unplug 24 V, restore the bus, stop the session and remove the temporary electrical reference.'],
         console='move6 0.0025 -0.0025 0.0025 0.0025 -0.0025 0.0025 500\nstatus\ndisarm',
         gate='All six channels match the harness labels; a missing bus prevents readiness and restore alone produces no motion.',
         fail='Wrong direction is corrected with all power removed by reversing one identified winding pair or a governed DIR inversion. Record the choice and repeat the affected channel.')
    page('unarmed-vm-cycle','Test power loss before arming',
         'This bench test preserves Pico power while resetting the motor drivers. A temporary reference must not survive an OFF→ON motor-supply cycle even when no move is active.',
         section='Controller / reset interlock',art='stop-power.svg',figure='short',style='compact',
         tools='Bench image · belts removed · motors fixed · USB keeps Pico alive · controller log',
         actions=['With UART restored and MOTOR POWER ON, issue <code>clear</code> and <code>reference central</code> for this uncoupled bench test. Do not arm.',
                  'Issue <code>status</code>; record readiness and vm_epoch. Turn MOTOR POWER OFF, wait for VM to disappear, then turn it ON while USB keeps Pico powered.',
                  'Issue <code>status</code>: reference and driver verification must be lost, and vm_epoch must change. Issue <code>arm</code>; it must refuse authority.',
                  'Issue <code>clear</code>, restore the temporary bench datum and reference again before later bench arming. End with <code>stop</code>; no temporary reference is a machine datum.'],
         gate='The unarmed supply cycle invalidates reference/readiness, changes vm_epoch and makes arm refuse until clear plus a fresh reference.',
         fail='Surviving reference, verified drivers or accepted arm fails the reset interlock. Leave motor power off and correct control behavior before coupling belts.')
    page('recover-session','Recover an ambiguous session explicitly',
         'An ambiguous mutating reply triggers the client\'s STOP/STATUS resynchronization and a latched host failure. Explicit recovery clears that failure; it never retries the movement.',
         section='Controller / recovery',art='software-banner.svg',figure='short',style='compact',
         tools='Supported load · MOTOR POWER access · actual physical datum · log',
         actions=['Support the load, remove motor power and inspect the logged ambiguous command and observed position.',
                  'Issue <code>recover</code> to stop/resynchronize the link; preserve the ambiguous record and do not resend its movement.',
                  'Correct the cause and physically restore the central datum. Restore motor power and run the sequence below.',
                  'Check profile, six driver readbacks and zero counts; accept fresh observations before another bounded request.'],
         console='recover\nclear\nreference central\narm\nstatus',
         gate='Recovery has an explicit stop record, the actual datum is restored and arming completes fresh six-driver checks without moving.',
         fail='A command replay, arbitrary zero or automatic restart fails recovery. Leave motor power off until the uncertain outcome and fault are resolved.')
    page('fit-drive-guards','Couple the belts and fit guards',
         'Return every physical axis to its central datum before coupling its belt. The three screw brakes remain applied; the guard covers the belt without touching it.',
         section='Controller / mechanical closure',art='drive-guard.png',
         caption='Coral is one drive\'s removable belt guard. Hand rotation verifies clearance before power.',
         add='6 belt-guard · guard fasteners',tools='24 V and USB unplugged · support under load · small hex key',
         actions=['Support gravity loads and restore X/Y/Z central marks and all three 180 mm actuator lengths.',
                  'Couple each belt with the tension/track check from its transmission page.',
                  'Transfer the two registered Ø3.4 guard holes from the bulkhead through the matching top angle feet; deburr them and verify M6 washer clearance.',
                  'Start each guard fastener loosely. Include the 3.175 mm angle foot in its measured grip and require two full threads beyond the locking nut; seat the guard without bending it.',
                  'Hand-turn each supported screw through two turns in each direction.'],
         gate='Every belt remains centered and the guards clear belt edges, pulley flanges and brake parts through full rotation.',
         fail='A rubbing guard or shifted datum fails closure. Correct fit mechanically; do not power a rubbing transmission.')
    page('flash-loaded','Load the fixed loaded-development image',
         'Use this image only after passive retention passes with the real gun and supported umbilical. It increases fixed current and reduces peak issued rate.',
         section='Controller / loaded configuration',art='software-banner.svg',figure='short',
         add='gun-positioner-loaded-development.uf2',tools='24 V unplugged · secondary support/catch · BOOTSEL',
         actions=['Copy <code>firmware/src_gun_positioner/assets/gun-positioner-loaded-development.uf2</code> to RPI-RP2 using BOOTSEL.',
                  'Reconnect the explicitly chosen host port and log a new loaded trial series.',
                  'With supported load, restore motor power and issue <code>clear</code>, then inspect <code>status</code>.',
                  'Leave it unreferenced until the actual physical central datums are set.'],
         gate='The named bound image reports its configured currents/VSENSE, matching verified VSENSE and microsteps, and the intended maximum rate. Motion remains inhibited until fresh reference/arming.',
         fail='A wrong or null reading fails verification. Stop and load the named bound image; do not tune current by the module trimmer.',
         note='Internal-reference/resistor tolerance arithmetic is a screen; actual current, running torque and force remain physically uncalibrated.')
    page('physical-reference','Establish the physical central datum',
         'Counts become meaningful only after the supported mechanism is at its documented central pose. Stops, faults and disarm erase that reference.',
         section='Controller / referencing',art='gimbal.png',figure='short',style='compact',
         tools='Actual central datum faces/marks · supports · loaded image · host console',
         actions=['Laser disabled, no tube: align X/Y/Z to their measured central marks.',
                  'Set all three neutral lever vectors and their 180 mm pin-to-pin lengths using the fixed datum setup.',
                  'Check all six four-contact axis loops and STOP/crash sense chain are closed, then execute the sequence below.',
                  'Record camera images of the physical datum and the controller count/status log.'],
         console='clear\nreference central\narm\nstatus',
         gate='The physical datum is observed and all counts are zero in the intended central pose. Arming does not itself move an axis.',
         fail='Never assign zero at an arbitrary stopped pose. Support/unplug and restore the actual datum before repeating the sequence.')


def observation_station():
    page('camera-height-base','Build two adjustable metal camera bases',
         'Each fixed plate sits above two horizontal 4040 risers on four steel height posts. Raising the whole level stage aligns it to the seam without tilting the camera.',
         section='Observation / two stages',art='camera-base.png',
         caption='Coral is the fixed plate and four locked height posts. The nominal 55.70 mm gap is a starting height for the illustrative optical-axis envelope.',
         add='Per stage: fixed plate · 2 risers · 4 M8 × 100 posts · 20 M8 nuts / 24 washers · 8 T-nuts · 4 corners / M8 × 16 / M8 × 75',tools='6 mm hex · 13 mm wrench · level · rule',
         actions=['Through-bolt both risers to the bench with their metal corners. Start all four height posts in the governed metal T-nut anchors.',
                  'Set the lower support nuts to one level height, starting at a 55.70 mm plate-to-riser gap.',
                  'Fit the fixed plate with washers and lock its upper/lower nuts at all four posts.',
                  'Keep the post height adjustment accessible until the actual camera and seam are visible.'],
         gate='The fixed plate is horizontal, all four posts are locked at the riser and plate, and its adjustable gap is within 20–70 mm.',
         fail='An unlocked or tilted plate moves the optical datum. Correct the metal post stack before adding rails.')
    page('camera-rails','Align the manual camera rails',
         'Two 400 mm SBR12 rails guide each stage. The carriage moves 200 mm manually; camera and lens always move together.',
         section='Observation / two stages',art='camera-rails.png',
         caption='Rail centers are at Y = ±90 mm. Four blocks lie at X = ±50 mm on the carriage.',
         add='Per stage: 2 SBR12 × 400 mm · 4 blocks · 16 M3 × 20 / 32 washers / 16 locking nuts',tools='Caliper · straightedge · small hex keys',
         actions=['Set the rail centers 180 mm apart and keep one rail straight to the plate edge.',
                  'Transfer the received rail foot hole phase into the fixed plate and start all through-bolts.',
                  'Slide two blocks onto each rail with their plate holes facing up.',
                  'Seat the datum rail; leave the second rail free to align under the carriage.'],
         gate='The carriage hole pattern matches the four blocks without forcing the rail spacing.',
         fail='A mismatched pattern or binding block fails the guide fit. Re-align the second rail before locking its feet.')
    page('camera-carriage','Attach the level camera carriage',
         'The 300 × 300 mm plate bolts to all four blocks. Its tripod slot faces along the rail direction.',
         section='Observation / two stages',art='camera-carriage.png',
         caption='Coral is the moving plate. The rail base-to-carriage underside is 40 mm.',
         add='Per stage: camera-carriage-plate · 16 M5 × 16 block screws and washers',tools='4 mm hex · block tapped-depth check',
         actions=['Start all sixteen block screws by hand with washers.',
                  'Seat opposite pairs across the four blocks while keeping the plate flat.',
                  'Slide the carriage by hand through its 200 mm path; progressively secure the second rail.',
                  'Recheck the full path after every rail-foot fastener is seated.'],
         gate='The plate stays level and moves through its full manual path without binding; screws clamp before bottoming.',
         fail='A skewed plate or tight region fails the camera datum. Release and re-align the guide joint before adding optics.')
    page('camera-stop-fabrication','Cut eight forked metal stops',
         'The stops are formed angles with a relieved foot and upright. Their 3D bridge clears the supported rail while retaining its guide block.',
         section='Observation / fabrication',art='camera-stop-detail.png',
         caption='Coral is one actual formed stop. STEP and its fabrication note govern both legs; there is no flat-blank replacement template.',
         add='8 pieces of 50.8 × 50.8 × 6.35 mm aluminum angle, cut 60 mm wide',tools='Metal saw · vise / clamps · file · caliper · received rail / block',
         actions=['Cut the angle 60 mm wide and shorten the upright to 38 mm from its mounting base.',
                  'Remove the center 34 mm fork through the foot and lower 29.5 mm of upright; preserve the upper 8.5 mm bridge.',
                  'Deburr and keep both remaining feet flat. Transfer the four foot mounting holes from the STEP face layout.',
                  'Trial-fit over the actual supported rail: bridge intercepts the block and stays below the moving plate.'],
         gate='The 3D fork clears the rail support and has an intact 8.5 mm bridge at 38 mm height; both mounting feet remain metal and flat.',
         fail='A cut bridge, distorted foot or plate-contacting height fails retention. Fabricate a correct formed stop before drilling its fixed plate.')
    page('camera-stops','Install four metal camera stops',
         'Preformed metal angles stop the blocks before they leave the rail. Their fork clears the rail support while the 38 mm upright stays below the carriage.',
         section='Observation / two stages',art='camera-stops.png',
         caption='Coral is the actual 3D forked stop geometry. Fabricate it from angle stock; do not replace it with a flat printed stop.',
         add='Per stage: 4 camera-rail-stop · 16 M5 × 25 / 32 washers / 16 locking nuts',tools='3D STEP / fabrication note · 4 mm hex · hand slide',
         actions=['Place each completed forked stop over its rail at the two end stations.',
                  'Align its four foot holes with the fixed plate; keep the 38 mm upright square to the rail.',
                  'Fit both end stops to each rail and start all four foot bolts per stop.',
                  'Slide the carriage to both ends by hand; confirm blocks contact metal before reaching rail ends.'],
         gate='Both rails have metal stops at both ends; the carriage clears every 38 mm stop and no block can leave the rail.',
         fail='A stop striking the plate or missing the block fails retention. Correct the 3D angle geometry and bolt location before mounting the camera.')
    page('camera-return','Fit the two forward clamp bolts',
         'Two through-bolts and 40 mm metal tubes rigidly lock each stage in its forward working position. They are completely removed before manual retraction.',
         section='Observation / two stages',art='camera-return.png',
         caption='Forward carriage center is +100 mm. The return tubes bridge fixed and moving plates at the two outside clamp stations.',
         add='Per stage: 2 M5 × 70 · 2 metal tubes, 40 mm long, OD ≥10 mm / ID 5.5–6 mm · washers / nuts',tools='4 mm hex · 8 mm wrench',
         actions=['Slide the empty carriage to its +100 mm forward datum.',
                  'Place both metal tubes between plates at the matching return holes.',
                  'Start both bolts with washers and nuts before tightening either.',
                  'Seat both clamps progressively without changing plate level.'],
         gate='Both clamps are metal-to-metal and the forward carriage cannot slide under a gentle hand check.',
         fail='One clamp or a compressed printed tube permits optical movement. Correct the two metal clamps before calibration.')
    page('camera-mount','Mount each camera by its tripod base',
         'The camera is level and fixed by its 1/4-20 tripod mount. The sliding slot sets lens working-distance placement without attaching anything to the PTZ head.',
         section='Observation / cameras',art='camera-only.png',
         caption='Blue is the FoMaKo K20UH envelope from its manual, 253.5 × 144 × 169 mm. The real tripod socket depth sets the screw length.',
         add='2 FoMaKo K20UH · 1/4-20 tripod screws / washers · USB data and camera power leads',tools='Tripod screw driver · socket-depth check · no lens module installed',
         actions=['Measure the actual tripod socket\'s allowable insertion depth; use the selected screw/washer stack that clamps before bottoming.',
                  'Start the screw through the slot into the tripod socket and align the camera forward along the rails.',
                  'Seat the tripod screw while holding the base square. Support cables at the fixed plate with a moving service loop.',
                  'Check the clear PTZ head can complete its startup sweep before the lens stand is fitted.'],
         gate='The base is clamped without socket bottoming and the clear PTZ head has no contact during its self-test.',
         fail='A rocking base, bottomed screw or restricted head fails the mount. Correct the metal attachment before installing a lens.')
    page('lens-cassette','Capture the lens by its metal rim',
         'The cassette holds a Raynox DCR-250 by its 53 mm outer metal rim. The rear projection and clear optical apertures stay unobstructed.',
         section='Observation / lens modules',art='lens-cassette.png',
         caption='Coral is the cassette and retainer; blue translucent geometry is the lens envelope. Shims set axial clearance without force on glass.',
         add='Per view: lens-cassette · lens-retainer · DCR-250 · 4 M3 × 20 / captive nuts · no head washers · 0.40 mm lens-shim where needed',tools='Small hex · clean soft support · no camera power',
         actions=['Remove the four local pocket-ceiling supports through their open rear pockets. Verify flat nut seating, then insert the four captive nuts.',
                  'Place the lens rim into its 53.4 mm pocket with the rear projection toward the aperture.',
                  'Print each 0.40 mm shim as two 0.20 mm layers. Four supplied shims include setup spares; use only where measured rim clearance requires, then place the retainer.',
                  'Use M3 × 20 without head washers. Start all four screws and seat opposite pairs gently without squeezing the lens assembly.'],
         gate='The lens is retained without rim distortion; apertures stay clear and all four screw tips end inside the rear plane, with full captive-nut engagement.',
         fail='A forced rim fit or retainer loading glass fails the optical mount. Correct the cassette/shim fit before using the lens.')
    page('lens-stand','Assemble the removable lens stand',
         'A preformed aluminum angle and windowed upright support the cassette separately from the camera. Vertical slots align it to the parked level optical axis.',
         section='Observation / lens modules',art='lens-stand.png',
         caption='Coral is the angle/upright connection. The 64 × 150 mm window clears the lens; the two 116 mm slots permit height adjustment.',
         add='Per view: angle / upright · 8 M5 × 25 / 16 washers / 8 nuts · 4 M5 × 40 cassette bolts / 8 washers / 4 nuts',tools='Angle face projections · 4 mm hex · 8 mm wrench',
         actions=['Transfer the separate foot/upright projections onto the intact 50.8 mm metal angle; drill each face separately.',
                  'Bolt the upright to the angle and start all four joints before seating opposite pairs.',
                  'Start the cassette\'s four slot bolts loosely with washers; set it to the parked camera center height.',
                  'Keep this entire angle/upright/cassette module off the camera carriage until startup has completed.'],
         gate='The module stays rigid on its angle and its optical openings clear the real lens throughout slot adjustment.',
         fail='A flat substitute angle, blocked aperture or tilted cassette fails the stand. Correct its metal geometry before installation.')
    page('camera-startup','Start the PTZ with its path clear',
         'Remove the entire lens module before every startup. The PTZ startup sweep needs the angle, upright, cassette and retainer outside its path.',
         section='Observation / startup',art='camera-startup.png',
         caption='The lens module is shown removed as one group. No part remains bonded or clamped to the moving PTZ head.',
         tools='Lens module removed · camera power / USB · manual optics controls',
         actions=['Remove and set aside the whole angle/upright/cassette/retainer module.',
                  'Start both cameras with clear head travel and identify each physical view by its native camera identity.',
                  'Park pan and tilt at the level forward measurement orientation. Fix zoom, manual focus and exposure.',
                  'Reinstall the complete lens module after parking; bring its cassette coaxial without commanding another head sweep.'],
         gate='Startup completes without contact and the parked camera remains level with fixed manual optics settings.',
         fail='A restart or PTZ movement changes the datum and can collide with the stand. Remove the module, re-park and recalibrate before measurement.')
    page('camera-align','Raise the level stages to the seam',
         'The model\'s camera optical center is an envelope. Align the real image center by adjusting all four metal height posts together, with the PTZ level.',
         section='Observation / physical alignment',art='camera-forward.png',
         caption='Both complementary views are aimed at the actual dot, protruding wire endpoint and seam. A 109 mm lens working distance is a manufacturer reference, not a measured calibration.',
         tools='Actual seam / wire endpoint · camera images · level · 13 mm wrench',
         actions=['With laser disabled, place the real wire endpoint and seam reference in the dry observation workspace.',
                  'Adjust all four lower post nuts equally until the real camera image center reaches the seam; keep the plate horizontal.',
                  'Lock all post nuts, then trim/deburr surplus stud to no more than 22 mm above the fixed-plate underside.',
                  'Set camera/lens spacing and manual focus at the working distance; lock tripod, cassette slots and both return clamps.'],
         gate='Both views resolve the required features with rigid locked mounts, no PTZ tilt, no protruding post contact and complementary geometry.',
         fail='An unclear wire endpoint or obstructed view fails observability. Change mount spacing/height or illumination and calibrate again before a response trial.')
    page('camera-retract','Retract cameras by hand',
         'The camera and lens module travel together by 200 mm. Manual retraction clears the dry workspace and invalidates the old camera calibration.',
         section='Observation / handling',art='camera-retracted.png',
         caption='The carriage moves from +100 to −100 mm. Both return bolts and both 40 mm tubes are removed before it moves.',
         tools='4 mm hex · 8 mm wrench · supported camera service loops',
         actions=['Stop motion, remove the tube from the handling path and support both camera cables.',
                  'Remove both return bolts, nuts, washers and both metal tubes completely.',
                  'Slide each camera/lens carriage backward by hand until its rear metal stops engage.',
                  'To return, slide forward, reinstall both tube/bolt clamps and recalibrate before recording measurement frames.'],
         gate='Retraction does not stretch a cable or strike optics, and return clamps are absent during every manual slide.',
         fail='A retained tube/bolt or taut cable blocks safe travel. Stop the hand move and remove the obstruction before continuing.',
         mind='These cameras and lens mounts are for dry observation. No live-laser optical barrier or filter is qualified by this assembly.',mind_label='Observation scope')


def commissioning():
    page('powered-force-fixture','Build the powered force fixture',
         'The spare short screw and metal fork put the gauge in series with the shuttle while the fixed drive foot reacts independently to the bench.',
         section='Dry commissioning / powered force',art='powered-force-fixture.png',
         caption='The gauge load axis points down at the fork bridge. The fork clears the screw tip and touches only the output shuttle.',
         add='Spare 200 mm TR8×2 screw · test foot · two output arms / bridge · graded link · accepted driver profile',tools='Vertical gauge backing / vise · independently clamped drive foot · recorded force uncertainty',
         actions=['Remove the vessel and real gun; leave every gravity load supported. Clamp the fixed metal test foot independently to the table.',
                  'Fit the spare screw and selected graded link. Attach both fork arms only to the shuttle, outside the fixed cage, with the bridge ahead of the screw tip.',
                  'Clamp the gauge backing vertically with its load axis down; its compression button contacts the bridge center.',
                  'Meter the link’s two overload contacts and verify the force path has no rigid output/cage bypass. Reverse the cartridge and fork to test the other sign.'],
         gate='Drive-foot reaction and gauge/output reaction are separate, the fork clears fixed ties and the gauge reads the complete output force.',
         fail='A bridging clamp, off-axis gauge or unsupported fixed foot invalidates powered force measurement. Correct that fixture before motion.')
    page('powered-force-ceiling','Measure the powered force ceiling',
         'Static switch force and powered motor force are different records. A motor can stall below the static trip setting; record that observed outcome and stop it.',
         section='Dry commissioning / powered force',art='powered-force-fixture.png',figure='short',style='compact',
         tools='Loaded profile / stated rate · gauge peak mode · controller log · accessible STOP',
         actions=['Create a temporary fixture reference at its unloaded center; label this as a test reference, never a gun/tool datum.',
                  'Advance one small bounded request at a time while observing force, shuttle travel and actual motion. Start at one-second moves.',
                  'Record peak + uncertainty against the named axis/direction ceiling table, before ±1.0 mm capture. Keep the 500 N gauge itself inside range.',
                  'If the switch opens, all axes must inhibit. If motion stalls first, issue STOP, record “stall”, abort and do not retry or raise current to force a trip.'],
         gate='Both signs at every used rate/load stay below their complete upper force bound, with no shoulder impact or lost load. Separate controlled switch tests prove all-axis latching.',
         fail='Excess force, capture impact, continued motion after an open loop or an unacknowledged stall fails the setting. Support/unplug, correct it and start a new trial.',
         note='After every trip/stall, support and deenergize, recenter/inspect the link and restore an actual physical datum. Discard the temporary fixture reference before mounting its drive.')
    page('loaded-small-motion','Observe the first loaded correction',
         'Issued STEP edges identify the request. Actual movement, settling and direction are observed with the gun, wire guide and supported umbilical fitted.',
         section='Dry commissioning / response',art='gun-clamp.png',figure='short',style='compact',
         tools='Loaded image · accepted retention · fresh reference · two camera views',
         console='jog X 0.0025 1000\njog X -0.0025 1000\nstatus',
         actions=['Begin at one second per 16-count request. Record before/after frames, actual sign and settling.',
                  'Repeat separately on all six coordinates at the same local pose. Positive Z must raise the carriage from its fixed top thrust.',
                  'If a small request is indistinguishable, label it unresponsive; do not stack blind corrections.',
                  'Use one bounded 0.0400 mm diagnostic request when needed to separate no-motion from below-resolution response.'],
         gate='Each larger diagnostic request produces the expected signed observed change with no unhealthy driver or unexplained jump.',
         fail='Stuck movement, inconsistent sign or a failed diagnostic move stops the series. Correct drive preload, cable support or fixed current/speed and start a new recorded series.',
         mind='Laser emission disabled; tube removed; catch/support remains in place. Nominal 2.5 µm is command spacing, not measured physical travel.',mind_label='First-motion setup')
    page('fault-loops','Trip every travel and stop loop',
         'Test inputs while armed and stopped with the loaded catch in place. Closing a loop must never restart motion.',
         section='Dry commissioning / fault response',art='limit-loop.svg',figure='short',style='reference',
         tools='Supported load · host log · MOTOR POWER access',
         rows=[('24 separate switch tests','Actuate each travel/overload contact','All axes inhibited; reference invalid'),
               ('6 separate loop unplug tests','Unplug each axis loop connector','All axes inhibited; reference invalid'),
               ('STOP pressed','Latch the mushroom','All axes inhibited; switched VM removed'),
               ('STOP connector unplugged','Open the NC2 logic connector','All axes inhibited; reference invalid'),
               ('Gun crash release','Release seated mount with catch engaged','Both independent healthy-closed channels open; VM removed; reference invalid'),
               ('Input restored','Release/reconnect the tested input','No motion or automatic recovery')],
         headers=['Case','Operation','Required observed result'],
         gate='Every listed case has its own recorded passing response. Recovery requires clear, the actual central datum and reference/arm.',
         fail='A bypassed input, surviving reference or restart fails fault behavior. Remove motor power and repair the loop/firmware before another loaded trial.')
    page('fault-supplies','Test USB loss and motor-power loss',
         'The dual supply preserves logic while the two fault paths remove motion authority. Measure the real stop outcome; the programmed timeout is not stop-distance evidence.',
         section='Dry commissioning / fault response',art='stop-power.svg',figure='short',style='compact',
         tools='Secondary catch/support · two-view recording · controller log · voltmeter',
         actions=['During one small dry move, unplug host USB while 24 V stays on. Pico 3V3 must remain present from the buck and the controller must inhibit after heartbeat loss.',
                  'Reconnect USB and inspect status. It must require a fresh physical reference.',
                  'During a separate small move, remove 24 V while USB remains. Status must survive, VM must become absent and passive retention must carry the load.',
                  'Reset the controller separately. Startup must remain inhibited and unreferenced; record observed travel and catch clearance for each test.'],
         gate='All three tests inhibit motion, invalidate reference and retain the load inside its accepted clearance/catch envelope.',
         fail='Lost logic on USB unplug, runaway load or automatic restart fails commissioning. Support the load, unplug motor power and correct the source/retention/fault path.')
    page('thermal-hold','Measure loaded motion and hold temperatures',
         'Fixed-current acceptance includes the motor cases, driver heatsinks and retained brake setting under a repeated loaded sequence and prolonged hold.',
         section='Dry commissioning / thermal',art='drive-motor.png',figure='short',
         tools='Contact thermometer · documented uncertainty · controller/camera logs',
         actions=['Record each motor-case and driver-heatsink contact temperature at startup.',
                  'Repeat the accepted low-speed loaded sequence and holds. Record temperatures every five minutes.',
                  'Continue through three consecutive five-minute intervals (15 minutes) with no increasing trend exceeding documented instrument/contact uncertainty.',
                  'After the first 30 minutes and hot/cold settling, repeat full-turn brake drag and loaded power-cut checks.'],
         gate='Every surface reading plus its uncertainty is ≤50°C; the 15-minute trend, signed response and retention gates all pass.',
         fail='Warning, continued heating, changing drag, lost motion or an unexplained feature jump fails the trial. Stop; a cooling/current/mechanical adjustment starts a new fixed-setting trial series.',
         note='A ±2°C tool cannot establish a 1°C plateau. This ceiling protects handling and nearby printed parts; it is not a chip temperature rating.')
    page('warm-hub-proof','Recheck hub grip after settling',
         'Fifty supervised reversals and settled temperatures precede the warm proof. Repeat both torque signs on the same marked seats without exceeding the accepted temperature envelope.',
         section='Dry commissioning / joint settling',art='hub-clamp-proof.png',figure='short',style='compact',
         tools='Independent load supports · both supplies disconnected · proof fixture · temperature / uncertainty log',
         actions=['Complete 50 reversals within the physically accepted dry subset. Record settled surface readings and their uncertainty; each upper bound stays ≤50°C.',
                  'Support the actual carried masses and deenergize. Repeat every hub’s ten-second signed proof on its recorded final seat, using the same clamp setting and complete assigned torque intervals.',
                  'Record specimen temperature during proof. If dismantling/cooling prevents the intended warm condition, leave that temperature range unqualified.',
                  'Restore all service tubes, keepers, actuator joints and witnesses. Recheck free rotation/axial capture and establish fresh observed physical datums.'],
         gate='Every recorded warm specimen passes both signs without slip or permanent set; restored capture/retention and fresh datums pass before further motion.',
         fail='A changed grip, shifted seat, witness movement or failed temperature/proof result rejects that condition. Correct and qualify again; repeated settling checks do not establish fatigue life.')
    page('linear-scale','Screen the three linear scales',
         'The existing 12.7 µm-graduation indicator can detect a gross lead/ratio error over 5 mm. It does not establish micrometer positioning accuracy.',
         section='Dry commissioning / nominal geometry',art='linear-gauge.svg',figure='short',style='compact',
         tools='Existing indicator on fixed metal frame · supported load · loaded image',
         actions=['Align the probe to a rigid carriage face at least 5 mm from a switch; set it near midrange and note a fresh zero.',
                  'From the actual central datum, issue the +5 mm target below. The client divides it into ≤0.1 mm segments.',
                  'Record the actual total span and stick-slip, then restore 0. Repeat from the same approach direction on X, Y and Z.',
                  'Record the indicator setup repeat readings and uncertainty limit.'],
         console='target X 5 1000\ntarget X 0 1000',
         gate='The coarse 5.00 mm span is within ±0.10 mm. At 85 mm half-travel this uses 1.70 mm of the 4 mm soft-to-switch margin.',
         fail='An outside result requires lead/ratio, loose-pulley or step-loss diagnosis. Restrict travel if the combined actual uncertainty/stop budget does not fit.',
         note='Remaining 2.30 mm must cover independently bounded datum error, spatial variation/backlash/compliance, measurement uncertainty and stop excursion. A local span alone never qualifies full travel.')
    page('angular-law','Screen the three clevis laws',
         'Measure pin-coordinate changes in each local lever plane. At 150 mm radius, a 5° probe changes the tangential coordinate by about 13 mm.',
         section='Dry commissioning / nominal geometry',art='angular-law.svg',figure='short',style='compact',
         tools='Caliper · fixed datum faces · neutral vector record · supported collision-free path',
         actions=['Record each shaft center, neutral lever vector and measured radius from fixed metal datums.',
                  'Issue +5°, restore 0, issue −5° and restore 0 on U; repeat separately on V/W.',
                  'Measure the lever-pin coordinate changes rather than an 180 mm span beyond the six-inch caliper.',
                  'Calculate angle from atan2 of the measured vector; record setup repetition and sign.'],
         console='angle U 5 1000\nangle U 0 1000\nangle U -5 1000\nangle U 0 1000',
         gate='Residual is ≤0.20° with demonstrated setup uncertainty ≤0.05°. The combined 0.25° allocation is within the 1° soft-to-switch margin.',
         fail='If the setup cannot support 0.05°, record the law as unverified and improve its datum fixture. A different measured law requires explicit calibration before using angular limits.')
    page('observation-install','Prepare the native observation kit',
         'The kit includes the built arm64 GPOCapture app. Install its Python dependencies into the same isolated host environment and create a private setup directory.',
         section='Dry commissioning / observation setup',art='software-banner.svg',figure='short',style='compact',
         tools='This Mac · complete kit · same terminal for the next setup pages',
         console='/tmp/gun-positioner-host/bin/pip install -r tools/gun-positioner-observation/requirements.txt\nGP_OBS=tools/gun-positioner-observation\nGP_PY=/tmp/gun-positioner-host/bin/python\nGP_SETUP=~/gpo-setup\nmkdir -p "$GP_SETUP"\nls "$GP_OBS/helper/build/GPOCapture.app"',
         actions=['Run from the extracted kit/repository root. Keep the same terminal variables for the following pages.',
                  'Keep setup files and camera sessions outside the public repository.',
                  'Use the shipped app; source rebuild instructions are in the toolkit README if its source or platform changes.'],
         gate='Dependencies install, the named app is present and the private setup directory is writable.',
         fail='A missing app or incomplete installation fails acquisition preparation. Restore the complete kit before identifying cameras.')
    page('camera-identities','Identify camera A, then camera B',
         'The two cameras can share a product name. Identify each by the inventory change when its labeled USB cable is connected.',
         section='Dry commissioning / camera identity',art='camera-startup.png',figure='short',style='compact',
         caption='Startup is done with both complete lens modules set aside. Keep each camera on its assigned USB port.',
         console='$GP_PY $GP_OBS/observe.py cameras --save "$GP_SETUP/cams-none.json"\n$GP_PY $GP_OBS/observe.py cameras --new-since "$GP_SETUP/cams-none.json" --save "$GP_SETUP/cams-a.json"\n$GP_PY $GP_OBS/observe.py cameras --new-since "$GP_SETUP/cams-a.json"',
         actions=['Unplug both camera USB cables and run the first inventory command.',
                  'Plug in only A and run the second command. Record the one new unique_id and name.',
                  'Plug in B and run the third command. Record its one new unique_id and name; label both cables/ports.'],
         gate='Each connection introduces exactly its intended device, with a distinct recorded unique ID.',
         fail='Multiple new devices or a reused ID makes assignment ambiguous. Repeat that connection/inventory step before capturing frames.')
    page('camera-config','Make the two-camera configuration',
         'Copy the shipped templates into the private setup directory. Actual identity is sufficient for a diagnostic capture; measurements require the remaining receipts.',
         section='Dry commissioning / camera configuration',art='software-banner.svg',figure='short',style='compact',
         console='cp "$GP_OBS/examples/cameras.example.json" "$GP_SETUP/cameras.json"\ncp "$GP_OBS/examples/operator-optics.example.json" "$GP_SETUP/cam_a-optics.json"\ncp "$GP_OBS/examples/operator-optics.example.json" "$GP_SETUP/cam_b-optics.json"\n$GP_PY $GP_OBS/observe.py validate-config "$GP_SETUP/cameras.json"',
         actions=['Fill each camera entry\'s unique_id and name from the recorded inventory.',
                  'Label its physical stage/view. Keep both cameras parked level and lens modules clear until startup completes.',
                  'Validate identity before the diagnostic capture. No diagnostic frame is accepted as a measurement.'],
         gate='The identity configuration validates and assigns exactly A and B to their intended entries.',
         fail='An unfilled or duplicated identity fails setup. Correct the copied private configuration; preserve the shipped templates as the reusable schema.')
    page('camera-format','Measure the native capture format',
         'The format report is observed on this Mac with these cameras. Manufacturer resolution claims do not fill the measured-format receipt.',
         section='Dry commissioning / camera format',art='camera-forward.png',figure='short',style='compact',
         caption='Park level/manual optics and install the lens modules before selecting the actual measurement view.',
         console='$GP_PY $GP_OBS/observe.py capture --config "$GP_SETUP/cameras.json" --root ~/gpo-sessions --label format-check --seconds 10 --every-n 100\n$GP_PY $GP_OBS/observe.py format-report SESSION_DIR',
         actions=['Grant GPOCapture camera access when macOS requests it during this first capture.',
                  'Use the actual directory printed by capture for SESSION_DIR. Cover B\'s lens briefly to confirm its recorded frames are the B view.',
                  'Copy each report\'s verified_format block into its camera entry, including measured time/source.',
                  'Inspect both wire endpoint/dot/seam views at the recorded native mode before optical calibration.'],
         gate='Both identities match their images and verified_format records the actual native 3840 × 2160 mode required by the supplied measurement configuration.',
         fail='A different format or swapped view fails that configuration. Diagnose capture/cable/mode support; never substitute a manual specification for the measured receipt.')
    page('optics-clock-gate','Validate optics and the host clock',
         'Each camera needs its own filled fixed-optics receipt or complete VISCA source. The clock receipt binds this Python and the helper build to the session timeline.',
         section='Dry commissioning / measurement gate',art='software-banner.svg',figure='short',style='compact',
         console='$GP_PY $GP_OBS/observe.py optics check "$GP_SETUP/cam_a-optics.json" --camera-id cam_a\n$GP_PY $GP_OBS/observe.py optics check "$GP_SETUP/cam_b-optics.json" --camera-id cam_b\n$GP_PY $GP_OBS/observe.py clock-check --out "$GP_SETUP/clock-check.json"\n$GP_PY $GP_OBS/observe.py validate-config "$GP_SETUP/cameras.json" --measurement',
         actions=['Fill each operator receipt from actual focus/exposure/tracking/zoom/white-balance/lens settings, with identity, time and method.',
                  'Choose operator or VISCA in each configuration entry, with only its selected transport/source fields populated.',
                  'Point clock_check to clock-check.json. Recheck after changing Python, helper build, camera position, lens or optics.'],
         gate='Both optics checks, clock bracket and measurement configuration pass; no required unfilled field or unknown/automatic optics state remains.',
         fail='A stale/wrong-camera receipt, unknown optics or changed clock binding fails measurement readiness. Record actual settings and renew the affected receipt before capture.')
    page('native-observation','Record native paired observations',
         'Use the supplied observation package for frame identity, timestamps, fixed optics and exclusions. Controller JSONL accompanies the dataset; it does not replace the image record.',
         section='Dry commissioning / observation',art='software-banner.svg',figure='short',style='compact',
         tools='Two fixed camera views · native capture helper · observation configuration',
         console='$GP_PY $GP_OBS/observe.py capture --config "$GP_SETUP/cameras.json" --root ~/gpo-sessions --label dry-measure --seconds 10 --measure\n$GP_PY $GP_OBS/observe.py check SESSION_DIR',
         actions=['Use each camera\'s actual unique ID in the supplied camera configuration; keep session data outside the public repository.',
                  'Lock and record resolution, zoom, focus, exposure, lighting and calibrated mounts.',
                  'Record frame gaps, image dimensions, clock mapping and optics snapshots; check the actual printed SESSION_DIR.',
                  'Verify the wire endpoint, dot and seam features in complementary views before accepting a response trial.'],
         gate='The native record validates and the measurement gate accepts both views, their fixed optics and temporal pairing.',
         fail='A gap, changed setting, unresolved endpoint or unsupported timing/scale invalidates that trial. Preserve its failure record and fix acquisition before fitting corrections.')
    page('learning-files','Define the actual image features',
         'The templates name the dot, wire tip and seam in each view. Regions and thresholds come from stored native frames, with room for the entire planned jog excursion.',
         section='Dry commissioning / learning setup',art='software-banner.svg',figure='short',style='compact',
         console='GP_RUN=~/gpo-sessions; GP_SIM=~/gpo-sim\ncp "$GP_OBS/examples/features.example.json" "$GP_SETUP/features.json"\ncp "$GP_OBS/examples/target.example.json" "$GP_SETUP/target.json"\n$GP_PY $GP_OBS/observe.py export-frame SESSION_DIR --camera cam_a --out "$GP_SETUP/cam_a.png"\n$GP_PY $GP_OBS/observe.py export-frame SESSION_DIR --camera cam_b --out "$GP_SETUP/cam_b.png"',
         actions=['Use the accepted format-check directory as SESSION_DIR and inspect both exported native frames.',
                  'Fill all regions, detector thresholds, frames_per_observation, min_valid_fraction and settle_s from observed images and timing.',
                  'Keep every feature inside its region throughout the planned local excursion. Shipped FILL_ME fields intentionally refuse measurement.'],
         gate='Both saved views resolve their named dot, wire and seam; copied feature settings describe those actual regions and settling.',
         fail='A missing feature or cropped excursion invalidates its steps. Correct the optical view/region before starting probes.')
    page('learning-targets','Check the target and feature files',
         'A target states a measured relationship: one value, the difference of two values, or a point’s signed distance from a seam line. Only its observable axes may move.',
         section='Dry commissioning / learning setup',art='software-banner.svg',figure='short',style='compact',
         console='$GP_PY $GP_OBS/observe.py learn check --features "$GP_SETUP/features.json" --target "$GP_SETUP/target.json" --cameras "$GP_SETUP/cameras.json"\n$GP_PY $GP_OBS/observe.py learn record --backend cameras --cameras "$GP_SETUP/cameras.json" --features "$GP_SETUP/features.json" --target "$GP_SETUP/target.json" --root "$GP_RUN"',
         actions=['Fill desired quantities, tolerances and allowed axes. Use pixels until independent px_per_mm and its calibration record justify millimeters.',
                  'List no more moved axes than independent target quantities. Use printed quantity noise/error and feature-summary.json to refine settings.',
                  'Require every feature in every observation during this stationary record before learning a motion response.'],
         gate='learn check exits 0 and the camera-only record resolves every feature with the recorded target values.',
         fail='Unknown fields, lost detections or unsupported physical scale fail setup. Correct the actual files/view before fitting a model.')
    page('learning-rehearsal','Rehearse one-axis probing',
         'The simulator defaults allow the complete command sequence to be checked before a controller is connected. Its fit qualifies software execution only.',
         section='Dry commissioning / rehearsal',art='software-banner.svg',figure='short',style='compact',
         console='$GP_PY $GP_OBS/observe.py learn plan --out "$GP_SETUP/jog-plan.json" --axes X\n$GP_PY $GP_OBS/observe.py learn jog --plan "$GP_SETUP/jog-plan.json" --features "$GP_SETUP/features.json" --root "$GP_SIM"\n$GP_PY $GP_OBS/observe.py learn fit SIM_JOG_DIR --features "$GP_SETUP/features.json" --out "$GP_SIM/analysis"\n$GP_PY $GP_OBS/observe.py learn validate SIM_JOG_DIR --model "$GP_SIM/analysis/model.json" --split "$GP_SIM/analysis/split.json" --out "$GP_SIM/analysis"',
         actions=['Begin with X only. Use the simulator jog directory printed by the second command as SIM_JOG_DIR.',
                  'Inspect trial bounds and engagement counts in jog-plan.json. Each request is ≤640 counts; twice engagement stays ≥400 default maximum dead-band.',
                  'Read the held-out validation report. Rehearsal motion and pixel accuracy are separate from loaded hardware acceptance.'],
         gate='The simulated session completes, fit writes its model/split, and validation-report.txt starts VALIDATION: PASS.',
         fail='An invalid plan or failed software rehearsal stops the hardware step. Fix its files/model before connecting motor power.')
    page('learning-hardware-jogs','Run observed controller jog trials',
         'The real backend needs the explicit hardware flag, accepted camera configuration and physical central datum. It sends no setup command until the operator uses its prompt.',
         section='Dry commissioning / local probes',art='software-banner.svg',figure='short',style='compact',
         console='$GP_PY $GP_OBS/observe.py learn jog --backend controller --port /dev/cu.usbmodemPICO --cameras "$GP_SETUP/cameras.json" --features "$GP_SETUP/features.json" --plan "$GP_SETUP/jog-plan.json" --root "$GP_RUN" --i-understand-this-moves-hardware',
         actions=['Replace the port with the inspected controller port. Start with the accepted loaded setting, supported cable, removed tube and clear local excursion.',
                  'At the prompt type clear; establish the actual datum, then reference central, arm and go. Go requires healthy verified drivers with the bound profile, currents, VSENSE and 16 microsteps.',
                  'Observe engagement, positive/negative probes and zero-motion holds. The plan grows steps only after two changes exceed eight noise units.',
                  'Preserve frames and named MOVE6 command/ACK/completion receipts. An unverified receipt halts motion; leaving sends STOP and invalidates reference.'],
         gate='The session completes its bounded, settled one-axis trials with physical response, paired features and valid receipts.',
         fail='A refusal, missing feature, stall, switch opening or incomplete move halts the session. Support/stop, preserve the record and restore the actual datum before another run.')
    page('learn-response','Fit and validate the loaded local response',
         'Direction-dependent response and reversal take-up are learned from actual completed trials. Validation holds out whole trials, so a fit cannot qualify itself on its training moves.',
         section='Dry commissioning / local model',art='software-banner.svg',figure='short',style='compact',
         console='$GP_PY $GP_OBS/observe.py learn fit REAL_JOG_DIR --features "$GP_SETUP/features.json" --out "$GP_RUN/analysis"\n$GP_PY $GP_OBS/observe.py learn validate REAL_JOG_DIR --model "$GP_RUN/analysis/model.json" --split "$GP_RUN/analysis/split.json" --out "$GP_RUN/analysis"',
         actions=['Use the actual printed jog directory as REAL_JOG_DIR. Inspect exclusions, dead-band intervals, held-out RMS/bias/skill and every axis-direction verdict.',
                  'Probe additional needed axes one at a time using a newly bounded plan. Corrections use only independently observable, validated directions.',
                  'Keep pose, fixed current, temperature, cable route and optical settings with the model; a changed local response needs new trials.'],
         gate='validation-report.txt starts VALIDATION: PASS and each subsequently used axis-direction has held-out coverage and acceptable response.',
         fail='A deficient fit, excessive outliers or unobserved direction fails that correction. Improve features/probes or reduce the local range before using it.',
         note='Observed ≤0.010 mm requirement / 0.005 mm target still need independent image-to-work uncertainty. Pixel improvement alone leaves physical micrometer accuracy unqualified.')
    page('learning-proposal','Review a fresh correction proposal',
         'Record the actual target again after the accepted fit. A proposal reports bounded counts and reasons; it never moves the mechanism.',
         section='Dry commissioning / correction review',art='software-banner.svg',figure='short',style='compact',
         console='$GP_PY $GP_OBS/observe.py learn record --backend cameras --cameras "$GP_SETUP/cameras.json" --features "$GP_SETUP/features.json" --target "$GP_SETUP/target.json" --root "$GP_RUN"\n$GP_PY $GP_OBS/observe.py learn propose --model "$GP_RUN/analysis/model.json" --validation "$GP_RUN/analysis/validation.json" --features "$GP_SETUP/features.json" --target "$GP_SETUP/target.json" --session RECORD_DIR --out "$GP_RUN/proposal.json"',
         actions=['Use this newly printed record directory as RECORD_DIR. Inspect quantity values, desired values, noise and axis sensitivity in proposal.json.',
                  'Choose only independently observable allowed axes. Bring the gun near with accepted coarse console moves if the target exceeds four trust regions.',
                  'Begin with the default 64-count / 0.01 mm per-screw trust region. A zero proposal with reasons is a gate to diagnose.'],
         gate='The review-only proposal is locally bounded and supported by the validated sensitivities and fresh target observation.',
         fail='Staleness, noise, missing features or a zero refusal prevents correction. Resolve its stated reason instead of forcing nonzero counts.')
    page('learning-execute','Confirm each observed correction',
         'The execution session reobserves after arming and after every move. The previously reviewed proposal is never replayed after its observation becomes stale.',
         section='Dry commissioning / correction trial',art='software-banner.svg',figure='short',style='compact',
         console='$GP_PY $GP_OBS/observe.py learn execute --backend controller --port /dev/cu.usbmodemPICO --cameras "$GP_SETUP/cameras.json" --features "$GP_SETUP/features.json" --target "$GP_SETUP/target.json" --model "$GP_RUN/analysis/model.json" --validation "$GP_RUN/analysis/validation.json" --root "$GP_RUN" --i-understand-this-moves-hardware',
         actions=['At the prompt clear, restore the physical central datum, reference central, arm and go. Its initial engagement probes are real bounded motion.',
                  'Review each fresh proposed move and type y only while its physical path remains clear. The first gate refusal or incomplete move halts the session.',
                  'Observe the next settled pair before any further correction. Record precision-floor, decline or fault outcomes; leaving sends STOP.'],
         gate='Fresh observed error improves within the declared target tolerance and every move remains inside accepted local motion/uncertainty bounds.',
         fail='Unresponsive motion, growing error, feature loss or a fault stops correction. Preserve the result and rebuild the affected datum/view/model; never accumulate blind commands.')
    page('dry-laps','Track repeated dry rotator laps',
         'Fresh observations correct a smooth learned phase trajectory. The existing rotator pedal and controller remain independent.',
         section='Dry commissioning / rotation',art='station.png',figure='short',
         tools='Registered tube seam · accepted local model · rotator pedal · paired observations',
         actions=['Register this tube\'s seam and a fixed table fiducial or characterized phase encoder on the observation timeline.',
                  'Start at the rotator\'s accepted 8 mm/s dry speed and preserve its pedal behavior.',
                  'Learn phase-indexed feedforward from repeated laps, then reserve subsequent laps for held-out evaluation.',
                  'Log achieved residual and uncertainty, feature visibility, observe/move/settle delay, saturation and every abort.'],
         gate='Observed tracking stays inside its accepted local workspace with measured correction authority and recoverable fault behavior.',
         fail='Visibility loss, unexplained residual, saturation or an unqualified stop path fails the dry run. Stop with the pedal and correct the model/clearance before another lap.',
         mind='No laser emission or wire feeding is authorized by this guide. Live optical protection, detection uncertainty, deterministic process interlocks and weld development require their own physical acceptance.',mind_label='Dry rotation scope')
    page('start-and-finish','Use the same start and shutdown order',
         'One consistent sequence preserves the physical datum, camera calibration and fault response between dry sessions.',
         section='Use / per session',art='software-banner.svg',figure='short',style='reference',
         rows=[('Before power','Tube clear; laser disabled; inspect metal joints, catch, cable slack and full screw-turn retainer drag'),
               ('Camera startup','Remove complete lens modules; power cameras; park level/manual optics; reinstall; calibrate'),
               ('Logic first','Connect USB host; MOTOR POWER OFF; verify supported physical central datum'),
               ('Motor power','Release STOP; motor toggle ON; clear; status; reference central; arm'),
               ('Operate','One bounded move; fresh observations; no automatic retry of an unacknowledged move'),
               ('Finish','Stop/disarm; support load; MOTOR POWER OFF; unplug 24 V; end host; disconnect USB'),
               ('Camera handling','Remove return bolts/tubes; retract by hand; recalibrate after forward return'),
               ('Any fault','Support load; motor power off; preserve log; recover if command outcome is ambiguous; correct cause and restore actual datum')],
         headers=['Order','Action'],
         gate='Every startup has a fresh physical reference and valid camera calibration; shutdown leaves a passively supported load.',
         fail='An arbitrary zero or reused calibration after movement fails session preparation. Restore the physical datum and recalibrate before arming.')


def references():
    page('numbers','Keep these numbers at the bench',
         'These values describe the fabricated nominal geometry and conservative controller envelope. Physical measurements still decide usable motion.',
         section='Reference / nominal settings',art='angular-law.svg',figure='short',style='reference',
         rows=[('XYZ intended travel','±85 mm / 170 mm total'),('XYZ switches / metal stops','±89 mm / ±94 mm'),
               ('Yaw / roll envelope','±20° soft; ±21° switch; ±22° stop'),
               ('Pitch envelope','−20…+10° soft; −21/+11° switch; −22/+12° stop'),
               ('Angular lever / neutral clevis','150 mm / 180 mm'),('Lead / belt / motor','2 mm / 80:20 = 4:1 / 200 full steps'),
               ('Issued scale','16 external microsteps; 6400 counts/mm'),('Nominal full-step extension','0.0025 mm / 2.5 µm / 16 counts'),
               ('XYZ soft counts','−544000…+544000'),('U/W soft counts','−326307…+329471'),('V soft counts','−326307…+166782'),
               ('Command envelope','≤0.1 mm each screw; 100–2000 ms duration'),
               ('Bench current scales','10/10/10/10/10/10; 0.337 A RMS'),
               ('Loaded X/Y/Z/U/V/W','Configured scales / currents from the bound image manifest'),
               ('Loaded VSENSE','1/1/0/1/1/1; Z uses VSENSE0'),
               ('Retainer breakaway / N·m','Measured windows from the governed mechanical requirements')],headers=['Property','Nominal value'])
    page('asset-index','Keep the complete build kit together',
         'The PDF, fabrication files, settings, source receipts and firmware form one reproducible package. The named manifests govern their respective interfaces.',
         section='Reference / files',art='visual-key.svg',figure='short',style='reference',
         rows=[('This book / templates','hardware/gun-positioner-guide/gun-positioner-guide.pdf<br>hardware/gun-positioner-guide/gun-positioner-drill-templates.pdf'),
               ('Plan / Prime purchases','hardware/gun-positioner/README.md<br>hardware/gun-positioner/purchases.md'),
               ('Mechanics','hardware/printed-parts/fixtures/gun-positioner/<br>parts.json · fasteners.json · requirements.json · STEP / STL / DXF'),
               ('Camera fabrication','hardware/printed-parts/fixtures/gun-positioner-observation/<br>manifest.json · STEP / STL / DXF'),
               ('Fixed controller prints','hardware/gun-positioner/mounting/<br>manifest.json · STEP / STL · clear-PETG blank, spacers and fan stand'),
               ('Electrical / qualification','hardware/gun-positioner/wiring-manifest.json<br>control.md · commissioning.md'),
               ('Controller images / host','firmware/src_gun_positioner/assets/ · host/<br>gun-positioner-bench.uf2 · gun-positioner-loaded-development.uf2'),
               ('Native observation','tools/gun-positioner-observation/<br>capture helper · record schema · local response fit / proposals'),
               ('Source verification','hardware/gun-positioner-guide/source-receipt.json<br>CAD scene source hashes and final PDF digest')],
         headers=['Asset','Location'],
         gate='All named assets and source receipts are present in the downloaded kit; part IDs agree across the guide and fabrication manifests.',
         fail='A missing or mixed-revision file fails build preparation. Obtain the matching complete kit before drilling or powering that interface.')


def bind_specs():
    """Use the governed joint schedule rather than repeating draft grips."""
    schedule=json.loads((ROOT/'hardware/printed-parts/fixtures/gun-positioner/fasteners.json').read_text())
    joints={j['joint']:j for j in schedule}
    by_slug={p['slug']:p for p in PAGES}
    def fastener(joint):
        return joints[joint]['fastener'].replace('x',' × ')
    replacements={
        'drive-nuts': [('M3 × 20',fastener('single-moving-nut-to-face'))],
        'drive-pulley':[('M3 × 16',fastener('pulley-to-fixed-nut'))],
    }
    for slug,pairs in replacements.items():
        for old,new in pairs:
            for field in ('add','caption','tools','gate','fail','note'):
                by_slug[slug][field]=by_slug[slug][field].replace(old,new)
            by_slug[slug]['actions']=[s.replace(old,new) for s in by_slug[slug]['actions']]
    for axis in ('x','y','z'):
        by_slug[axis+'-rails']['add']='2 SBR12 × 400 mm · 4 blocks · 16 '+fastener('rails-to-bed')+' · two washers / locking nut per bolt'
        by_slug[axis+'-carriage']['add']='1 '+axis+'-carriage · 16 '+fastener('blocks-to-carriage')+' · one washer per screw'
        by_slug[axis+'-screw']['add']+=' · fixed KP08: 2 '+fastener('fixed-screw-radial-bearings')+' · floating KP08: 2 '+fastener('floating-screw-radial-bearings')+' / two washers / locking nut'
    for axis in ('yaw','pitch','roll'):
        by_slug[axis+'-bearings']['add']+=' · 4 '+fastener('gimbal-pillow-bearings')+' / two washers / locking nut'
        by_slug[axis+'-frame']['add']=by_slug[axis+'-frame']['add'].replace('M4 × 50 grade 12.9',fastener('shaft-two-station-split-clamps'))
        hubs=2 if axis=='pitch' else 1
        by_slug[axis+'-frame']['add']+=' · '+str(hubs*4)+' '+fastener('shaft-hub-mount')+' / two washers / locking nut'
    by_slug['angular-drives']['add']+=' · 12 '+fastener('shaft-hub-mount')+' hub bolts · 12 '+fastener('hinge-smooth-stubs')+' pivot stubs / metal spacers'
    by_slug['angular-anchors']['add']='6 base webs · roll anchor · 12 '+fastener('angular-base-cheek-to-web')+' cheek bolts · 4 '+fastener('pitch-web-to-yaw-side')+' pitch ties · 4 '+fastener('roll-foot-through-anchor')+' roll joints'
    by_slug['linear-stops']['add']='Per axis: 2 metal stops / backed angles · 8 '+fastener('linear-stop-face-and-foot')+' face/foot bolts · washers / locking nuts · 2 NC switches'
    by_slug['force-cage']['add']='Per link: 2 end / 2 shoulder plates · 8 '+fastener('inner-nut-frame-and-outer-cage-ties')+' / two washers / locking nuts · measured metal tube set'
    by_slug['force-shuttle']['add']='Per link: shuttle / 2 bronze guides / 4 boss halves · 8 '+fastener('main-force-boss-pairs')+' · 2 '+fastener('main-smooth-guide-bolts')+' · 4 springs / pressure washers'
    by_slug['crash-pods']['add']='2 shuttles / 4 shoulders / 4 boss halves · 4 springs / pressure washers · 8 '+fastener('crash-cage-ties')+' · 8 '+fastener('crash-force-boss-pairs')
    by_slug['crash-contacts']['add']='4 switches · 8 '+fastener('switch-body-to-print')+' · 4 '+fastener('switch-bracket-to-metal')+' / governed washers / nuts'
    by_slug['crash-carriers']['add']+=' · 8 '+fastener('crash-lower-guide-blocks')+' lower-guide bolts / washers / locking nuts'
    by_slug['crash-seats']['add']+=' · 6 '+fastener('crash-ball-steel-backing')+' backing bolts · 12 '+fastener('V-seat-metal-keepers')+' keeper bolts'
    by_slug['crash-magnets']['add']+=' · 3 '+fastener('crash-cup-strikers')+' striker bolts / washers / nuts'
    by_slug['gun-jaws']['add']='4 metal jaw bars / 4 TPU pads · 4 '+fastener('lower-jaws-to-released-tray')+' lower mounts · 4 '+fastener('gun-clamp-and-temporary-test-clamp')+' through-bolts / two nuts each / two washers'
    by_slug['gun-jaws']['actions'][0]='Bolt the two lower metal bars to the released tray with four M5 × 25 mounts, a washer at both ends and locking nuts; fit their pad faces.'
    by_slug['crash-load-fork']['add']+=' · 2 '+fastener('gun-clamp-and-temporary-test-clamp')+' temporary clamp bolts / two nuts each / two washers'
    by_slug['drive-supports']['add']='Per drive: KP08 · 2 metal fixed risers · 2 '+fastener('fixed-screw-radial-bearings')+' / ≥10 mm OD washers / nuts · 4 M6 bulkhead posts on 24 × 44 mm pattern'
    by_slug['fit-drive-guards']['add']='6 belt-guards · 12 '+fastener('belt-guards')+' / governed washers / locking nuts'
    req=json.loads((ROOT/'hardware/printed-parts/fixtures/gun-positioner/requirements.json').read_text())
    links=req['overload_links'];pre=links['seated_preload_N'];trip=links['accepted_static_trip_N'];ceil=links['powered_peak_ceiling_N']
    force_rows=[('X / Y, both signs','X_Y','X_Y_Z_up'),
                ('Z upward / −screw length','Z_up_negative_screw_length','X_Y_Z_up'),
                ('Z downward / +screw length','Z_down_positive_screw_length','Z_down'),
                ('U yaw / W roll, both signs','yaw_roll','yaw_roll'),
                ('V pitch, both signs','pitch','pitch')]
    by_slug['force-settings']['rows']=[(label,str(pre[p]),f'{trip[b][0]}–{trip[b][1]}','≤'+str(ceil[b])) for label,p,b in force_rows]
    by_slug['powered-force-ceiling']['rows']=[(label,'≤'+str(ceil[b])+' N') for label,p,b in force_rows]
    by_slug['powered-force-ceiling']['headers']=['Axis / direction','Measured peak plus uncertainty']
    ret=req['retention']['accepted_breakaway_Nm']
    by_slug['brake-torque']['rows']=[(label,f'{ret[key][0]:.2f}–{ret[key][1]:.2f} N·m',f'{ret[key][0]/.000980665:.1f}–{ret[key][1]/.000980665:.1f} g') for label,key in [('Z','z'),('Pitch V','pitch'),('Roll W','roll')]]
    firmware=json.loads((ROOT/'firmware/src_gun_positioner/assets/build-manifest.json').read_text())
    profiles={p['name']:p for p in firmware['profiles']};loaded=profiles['loaded-development']
    scales='['+','.join(map(str,loaded['current_scales']))+']'
    sense='['+','.join(map(str,loaded['configured_vsense']))+']'
    currents=loaded['nominal_R110_current_rms_A']
    by_slug['flash-loaded']['gate']=f'Status reports loaded-development, current_scales {scales}, configured_vsense {sense}, matching verified vsense, six microsteps {loaded["microsteps"]} and max_rate {loaded["max_rate_count_s"]}. Fresh physical reference and arming checks remain required.'
    by_slug['flash-loaded']['note']=f'Nominal RMS: Z {currents[2]:.3f} A (VSENSE0), V {currents[4]:.3f} A, others {currents[0]:.3f} A. Tolerance arithmetic screens the setting; current, running torque and force remain physically uncalibrated.'
    by_slug['numbers']['rows']=[(label,'/'.join(map(str,loaded['current_scales']))+f'; Z {currents[2]:.3f} A, V {currents[4]:.3f} A, others {currents[0]:.3f} A') if label=='Loaded X/Y/Z/U/V/W' else
                             (label,'; '.join(f'{k} {v[0]:.2f}–{v[1]:.2f}' for k,v in ret.items())) if label=='Retainer breakaway / N·m' else
                             (label,value) for label,value in by_slug['numbers']['rows']]
    recipe=req['print_recipe']
    by_slug['coupon']['tools']='Abrasive-resistant '+str(recipe['nozzle_mm'])+' mm nozzle · '+str(recipe['first_layer_mm'])+' mm first / '+str(recipe['normal_layer_mm'])+' mm normal layer · caliper'
    by_slug['print-recipe']['rows'][0]=('First / normal layer; walls',f'{recipe["first_layer_mm"]:.2f} / {recipe["normal_layer_mm"]:.2f} mm; {recipe["walls"]}')
    by_slug['print-recipe']['note']='Governed starting recipe: <code>fixtures/gun-positioner/requirements.json</code>. Rigid parts are PET-GF15; jaw pads are TPU90A. These settings do not establish fit, wear or load capacity.'
    by_slug['prepare-blanks']['gate']='Every 50 mm scale bar is within ±0.25 mm, finished blanks within ±0.5 mm and registered hole centers within ±0.25 mm; mating faces are deburred.'
    by_slug['loaded-retention']['actions'][1]='With tube removed and cameras retracted, fit a steel catch tether and rigid stand no more than 5 mm below the cradle; keep ≥10 mm from fixed metal. Remove motor power.'
    by_slug['loaded-retention']['actions'][2]='Use the 12.7 µm-graduation indicator on rigid metal; record at 0, 1, 5 and 10 minutes. Separately release belt drive support while preserving the screw brake.'
    by_slug['loaded-retention']['gate']='No indicator-resolved growth or camera-visible jump/slip occurs and the catch is not contacted. Lower measured brake torque is at least twice the upper bound of actual backdrive torque.'
    by_slug['loaded-retention']['note']='This ten-minute test screens coarse gravity retention; it does not establish 5 or 10 µm work-coordinate accuracy.'


def add_contents():
    page('contents','Find the next operation',
         'Finish each group’s ready checks before continuing. The printed page ranges and PDF bookmarks use the same operation order.',
         section='Before assembly',art='visual-key.svg',figure='short',style='reference',
         headers=['Group','First operation','Pages'],
         note='Templates are a separate actual-size PDF. Print only the named fabrication tiles, then measure their 50 mm check bars.')
    content=PAGES.pop();PAGES.insert(3,content)
    groups=[]
    for number,p in enumerate(PAGES,1):
        key=p['section'].split(' / ')[0]
        if key=='Home Soda Machine':continue
        if not groups or groups[-1]['group']!=key:
            groups.append(dict(group=key,title=p['title'].replace('<br>',' '),first=number,last=number))
        else:groups[-1]['last']=number
    content['rows']=[(g['group'],g['title'],f'{g["first"]}–{g["last"]}') for g in groups]


def html_page(record, number, total):
    e = html.escape
    body=[]
    if record["add"] or record["tools"]:
        body.append(f'<div class="tray"><div><strong>Add</strong>{record["add"] or "No new parts"}</div><div><strong>Tools / setup</strong>{record["tools"]}</div></div>')
    if record["art"]:
        body.append(f'<figure class="{e(record["figure"])}"><img src="art/{e(record["art"])}" alt="{e(record["caption"])}"><figcaption>{record["caption"]}</figcaption></figure>')
    if record["rows"]:
        body.append('<table class="small">')
        if record["headers"]:
            body.append('<thead><tr>'+''.join(f'<th>{v}</th>' for v in record["headers"])+ '</tr></thead>')
        body.append('<tbody>'+''.join('<tr>'+''.join(f'<td>{v}</td>' for v in row)+'</tr>' for row in record["rows"])+ '</tbody></table>')
    if record["actions"]:
        body.append('<ol class="actions">'+''.join(f'<li>{a}</li>' for a in record["actions"])+ '</ol>')
    if record["console"]:
        body.append(f'<pre>{e(record["console"])}</pre>')
    if record["mind"]:
        body.append(f'<div class="mind"><strong>{record["mind_label"]}</strong><p>{record["mind"]}</p></div>')
    if record["gate"]:
        if not record['fail']:raise ValueError(f'Missing failure clause for {record["slug"]}')
        body.append(f'<div class="gate"><strong>{record["gate_label"]}</strong><p>{record["gate"]} <span class="fail">{record["fail"]}</span></p></div>')
    if record["note"]:
        body.append(f'<p class="note">{record["note"]}</p>')
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{e(record["title"].replace("<br>"," "))}</title><link rel="stylesheet" href="style.css"></head>
<body><article class="card {e(record["style"])}">
<header><div class="eyebrow"><b>{record["section"]}</b><span>{number:02d} / {total:02d}</span></div><h1>{record["title"]}</h1><i class="rule"></i><p class="lede">{record["lede"]}</p></header>
<main>{''.join(body)}</main>
<footer><span>Gun positioner · assembly guide</span><span>LETTER / {number}</span></footer>
</article></body></html>
'''


def write(input_hashes):
    GUIDE.mkdir(parents=True, exist_ok=True)
    total=len(PAGES)
    names=[]
    for number, record in enumerate(PAGES,1):
        name=f'{number:02d}-{record["slug"]}.html'
        names.append(name)
        (GUIDE / name).write_text(html_page(record,number,total))
    for stale in GUIDE.glob("[0-9]*-*.html"):
        if stale.name not in names:
            stale.unlink()
    (GUIDE / "page-manifest.json").write_text(json.dumps({
        "title": "Gun positioner assembly guide", "pages":total,
        "input_sha256": input_hashes,
        "leaves":[{"file":name, "title":r["title"].replace("<br>"," "),
                   "art":r["art"], "section":r["section"]}
                  for name,r in zip(names,PAGES)]
    },indent=2)+"\n")
    print(f"Authored {total} Letter pages")


if __name__ == "__main__":
    governed=[
        'hardware/printed-parts/fixtures/gun-positioner/gun_positioner.py',
        'hardware/printed-parts/fixtures/gun-positioner/fasteners.json',
        'hardware/printed-parts/fixtures/gun-positioner/requirements.json',
        'tools/gun-positioner-optics/mounts.py',
        'hardware/printed-parts/fixtures/gun-positioner-observation/manifest.json',
        'hardware/gun-positioner/wiring-manifest.json',
        'hardware/gun-positioner/mounting/generate.py',
        'hardware/gun-positioner/mounting/manifest.json',
        'hardware/gun-positioner/control.md', 'hardware/gun-positioner/commissioning.md',
        'hardware/gun-positioner/observation.md',
        'tools/gun-positioner-observation/README.md',
        'tools/gun-positioner-observation/observe.py',
        'tools/gun-positioner-observation/gpobs/learn.py',
        'tools/gun-positioner-observation/examples/cameras.example.json',
        'tools/gun-positioner-observation/examples/operator-optics.example.json',
        'tools/gun-positioner-observation/examples/features.example.json',
        'tools/gun-positioner-observation/examples/target.example.json',
        'firmware/src_gun_positioner/assets/build-manifest.json',
        'tools/gun-positioner-guide/author.py','hardware/gun-positioner-guide/style.css',
    ]
    input_hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in governed}
    gp=load_geometry(ROOT/governed[0],'positioner_guide_specs')
    opt=load_geometry(ROOT/governed[3],'positioner_guide_optics_specs')
    foundation()
    kit_and_preparation(gp,opt)
    shaft_qualification(gp)
    drive_assembly()
    overload_links()
    structure()
    gimbal(gp)
    retention_and_payload()
    electrical_preparation()
    electrical()
    cold_checks_and_software()
    observation_station()
    commissioning()
    references()
    add_contents()
    bind_specs()
    changed=[p for p,h in input_hashes.items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    if changed:raise RuntimeError(f'Governing inputs changed while authoring: {changed}')
    write(input_hashes)
