"""Author and bind the carbonator filming guide. Run by hand, outside the build.

    tools/cad-venv/bin/python tools/carbonator-filming-guide/build.py

Numbered HTML leaves and inline vector framing diagrams use the existing Letter
guide renderer. The PDF, cover, metadata and editable sources are committed.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image
from pypdf import PdfWriter
from pypdf.annotations import Link

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
GUIDE = ROOT / "hardware/carbonator-filming-guide"
OUT = GUIDE / "out"
PDF = GUIDE / "carbonator-filming-guide.pdf"
DELIVERY = ROOT / "output/pdf" / PDF.name
TITLE = "Carbonator weld filming guide"
BLUE, INK, PALE, CORAL = "#1749d1", "#202337", "#f5f8ff", "#d64050"


def text(x, y, value, size=38, color=INK, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
            f'text-anchor="{anchor}">{html.escape(value)}</text>')


def svg(body, label="FRAMING SKETCH"):
    return f'''<svg viewBox="0 0 1600 900" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label}">
    <defs><linearGradient id="steel"><stop stop-color="#c8cdd4"/><stop offset=".38" stop-color="#f4f6f8"/><stop offset="1" stop-color="#949da8"/></linearGradient>
    <marker id="arr" markerWidth="9" markerHeight="9" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="none" stroke="{CORAL}" stroke-width="2"/></marker></defs>
    <rect x="4" y="4" width="1592" height="892" rx="26" fill="{PALE}" stroke="#dce6ff" stroke-width="5"/>
    <g font-family="IBM Plex Sans, sans-serif" font-weight="500">{body}</g></svg>'''


def camera(x, y, label="A", scale=1):
    return f'''<g transform="translate({x} {y}) scale({scale})"><rect x="-72" y="-45" width="144" height="90" rx="14" fill="{BLUE}"/>
    <circle r="25" fill="white"/><circle r="13" fill="#dce6ff"/>
    <path d="M0 45V140M0 90L-65 200M0 90L65 200" stroke="{BLUE}" stroke-width="10"/>{text(0,-70,label,42,BLUE,"middle")}</g>'''


def rig(x=850, y=510, scale=1, cap=True, bead=False):
    seam = CORAL if bead else "#596273"
    return f'''<g transform="translate({x} {y}) scale({scale})">
    <path d="M-290 70L270 70L365 155L-365 155Z" fill="#353943"/>
    <path d="M-365 155H365V185H-365Z" fill="#232733"/><path d="M-330 185v30h75v-30M250 185v30h75v-30" fill="#232733"/>
    <ellipse cy="70" rx="235" ry="65" fill="#252932"/><path d="M-235 40H235V75Q0 150-235 75Z" fill="#434956"/>
    <path d="M-180-340H180V15Q0 100-180 15Z" fill="url(#steel)" stroke="#727c8a" stroke-width="3"/>
    <ellipse cy="-340" rx="180" ry="62" fill="#8c96a4" stroke="#d6dce3" stroke-width="8"/>
    {('<ellipse cy="-323" rx="161" ry="46" fill="#e4e8ed"/>' + f'<ellipse cy="-323" rx="161" ry="46" fill="none" stroke="{seam}" stroke-width="5"/>' + '<ellipse cx="-65" cy="-327" rx="19" ry="8" fill="#535b68"/><ellipse cx="65" cy="-327" rx="19" ry="8" fill="#535b68"/>') if cap else ''}
    <path d="M200 25L320 25L350 60L230 60Z" fill="#8f97a2"/><path d="M230 60H350V145H230Z" fill="#697381"/>
    <path d="M185 70L290 94L290 118L185 96" fill="#232733"/>
    <path d="M-200-80h-40v140h40" fill="#434956"/><path d="M-185-72h-25v85h25" fill="#b97751"/>
    </g>'''


def hand(x, y, flip=False, color="#657586"):
    return f'''<g transform="translate({x} {y}) scale({-1 if flip else 1} 1)">
    <path d="M-210-45L-55-45Q-20-90 25-65L75-10Q92 22 68 42L5 58L-55 35L-210 35Z" fill="{color}"/>
    <path d="M-50-34L-2 14M-20-53L25-7M5-55L45-18" stroke="#edf1f7" stroke-width="4" fill="none"/></g>'''


def wide(person=False, finished=False, empty=False):
    body = '<path d="M110 640H1490V720H110Z" fill="#cbd3df"/><path d="M160 720v125M1440 720v125" stroke="#748295" stroke-width="25"/>'
    if person:
        body += f'<path d="M220 8H650L700 370L600 520H200L165 340Z" fill="#62748c"/>'
        body += hand(615, 410) + hand(1180, 300, True)
        body += text(80, 75, "Frame starts below the shoulders", 38, BLUE)
    if not empty:
        body += rig(880, 470, .95, bead=finished)
    if person:
        body += '<path d="M1075 265L1015 320L930 205" stroke="#444c59" stroke-width="38" fill="none"/><path d="M930 205l-28-44" stroke="#b97751" stroke-width="22"/>'
    body += text(800, 815, "Steady composition - hands and work stay visible", 38, BLUE, "middle")
    return svg(body)


def joint(head=False, bead=False, issue=False):
    color = CORAL if bead else "#4b5565"
    body = '<path d="M75 90H1525V555Q800 300 75 555Z" fill="url(#steel)"/><path d="M75 555Q800 300 1525 555V820H75Z" fill="#e2e7ef"/>'
    body += f'<path d="M75 555Q800 300 1525 555" stroke="{color}" stroke-width="{14 if bead else 6}" fill="none"/>'
    if bead:
        for x in range(200, 1450, 65):
            y = 427 + .00023 * (x - 800) ** 2
            body += f'<path d="M{x-15} {y-10}q30 25 45 0" fill="none" stroke="#fbeaec" stroke-width="6"/>'
    body += text(250, 215, "Tube inner wall", 44) + text(1040, 730, "Cap face", 44)
    if head:
        body += '<path d="M1120 95L960 215L850 398" stroke="#4c5666" stroke-width="65" fill="none"/><path d="M850 398l-20 35" stroke="#b97751" stroke-width="34"/>'
        body += '<path d="M1450 330L1000 360L835 430" stroke="#8a6b38" stroke-width="10" fill="none"/>'
        body += text(1050, 295, "Actual head and wire pose", 34, BLUE)
    elif not bead:
        body += f'<path d="M1220 605L1050 448" stroke="{CORAL}" stroke-width="8" marker-end="url(#arr)"/>'
        body += text(1100, 650, "Keep this line sharp", 37, CORAL)
    if issue:
        body += f'<circle cx="780" cy="435" r="65" fill="none" stroke="{CORAL}" stroke-width="9" stroke-dasharray="16 12"/>'
        body += text(800, 850, "Frame the real feature you observed", 36, BLUE, "middle")
    else:
        body += text(200, 780, "Leave clear space for labels", 36, BLUE)
    return svg(body)


def overview(tacks=False, bead=False):
    body = '<ellipse cx="800" cy="440" rx="590" ry="320" fill="#9ba6b6"/><ellipse cx="800" cy="455" rx="550" ry="285" fill="#e1e6ee"/>'
    body += f'<ellipse cx="800" cy="455" rx="550" ry="285" fill="none" stroke="{CORAL if bead else INK}" stroke-width="7"/>'
    body += '<ellipse cx="605" cy="430" rx="55" ry="37" fill="#707c8d"/><ellipse cx="995" cy="430" rx="55" ry="37" fill="#707c8d"/>'
    if tacks:
        import math
        for a in range(0, 360, 45):
            x, y = 800 + 550 * math.cos(math.radians(a)), 455 + 285 * math.sin(math.radians(a))
            body += f'<circle cx="{x}" cy="{y}" r="13" fill="{CORAL}"/>'
    body += text(800, 810, "Whole cap and circular joint remain in frame", 42, BLUE, "middle")
    return svg(body)


def setup_art(detail=False):
    body = '<rect x="400" y="190" width="800" height="470" rx="20" fill="#e0e6ef" stroke="#a7b4c8" stroke-width="5"/>'
    body += '<circle cx="800" cy="440" r="140" fill="#9aa7b8"/><circle cx="800" cy="440" r="110" fill="#eef2f7"/>'
    for x, y, angle in [(305, 170, -30), (1300, 205, 30)]:
        body += f'<g transform="translate({x} {y}) rotate({angle})"><rect x="-80" y="-45" width="160" height="90" rx="10" fill="white" stroke="{BLUE}" stroke-width="6"/></g>'
    body += text(100, 80, "MAIN LIGHT", 35, BLUE) + text(1180, 80, "FILL LIGHT", 35, BLUE)
    if detail:
        body += camera(1110, 510, "B - DETAIL", .85)
        body += f'<path d="M1055 460L875 395M1055 510L910 510" stroke="{BLUE}" stroke-width="5" stroke-dasharray="13 11" fill="none"/>'
        body += text(200, 800, "Move the camera until the near rim clears the joint", 38, BLUE)
    else:
        body += camera(240, 590, "A - OVERALL", .85)
        body += f'<path d="M305 550L650 290M305 640L650 580" stroke="{BLUE}" stroke-width="5" stroke-dasharray="13 11" fill="none"/>'
        body += text(750, 790, "Operator works here", 38, BLUE, "middle")
    return svg(body)


def diagram(kind):
    if kind in ("wide", "finished", "work", "empty"):
        return wide(person=kind == "work", finished=kind == "finished", empty=kind == "empty")
    if kind in ("joint", "head", "bead", "issue"):
        return joint(head=kind == "head", bead=kind in ("bead", "issue"), issue=kind == "issue")
    if kind in ("overview", "tacks", "wholebead"):
        return overview(tacks=kind == "tacks", bead=kind == "wholebead")
    if kind in ("setup", "detail"):
        return setup_art(kind == "detail")
    if kind == "parts":
        return svg(rig(590, 500, 1, cap=False) + '<ellipse cx="1240" cy="580" rx="210" ry="100" fill="url(#steel)" stroke="#707b8a" stroke-width="5"/><ellipse cx="1170" cy="575" rx="23" ry="13" fill="#657080"/><ellipse cx="1310" cy="575" rx="23" ry="13" fill="#657080"/>' + text(800, 820, "Tube and the actual cap for this closure", 43, BLUE, "middle"))
    if kind in ("prep", "seat"):
        return svg(rig(840, 560, 1) + hand(650, 280) + hand(1130, 220, True) + text(800, 840, "Keep the contact area visible between your hands", 40, BLUE, "middle"))
    if kind == "dial":
        return svg('<path d="M1150 95V755" stroke="#a0acbc" stroke-width="190"/><circle cx="575" cy="375" r="220" fill="white" stroke="#465770" stroke-width="24"/><path d="M575 375L475 240" stroke="#1749d1" stroke-width="12"/><path d="M575 595v65h300l180-150" stroke="#465770" stroke-width="20" fill="none"/><circle cx="1055" cy="510" r="12" fill="#1749d1"/>' + text(575, 430, "DIAL", 45, BLUE, "middle") + text(800, 840, "Dial and contact point in the same view", 42, BLUE, "middle"))
    if kind == "shoe":
        return svg('<rect x="860" y="100" width="540" height="650" fill="url(#steel)"/><path d="M650 620H820V730H650Z" fill="#434956"/><rect x="810" y="290" width="50" height="350" fill="#b97751"/><path d="M180 560Q350 300 810 360" fill="none" stroke="#303948" stroke-width="24"/>' + text(1090, 245, "Tube", 48, BLUE, "middle") + text(470, 215, "Work lead", 42, BLUE) + text(460, 790, "Stationary copper shoe", 43, BLUE) + f'<path d="M640 735L820 585" stroke="{CORAL}" stroke-width="8" fill="none" marker-end="url(#arr)"/>')
    if kind == "belt":
        return svg('<circle cx="640" cy="430" r="250" fill="#434956"/><circle cx="640" cy="430" r="90" fill="#7e8a9c"/><circle cx="1270" cy="430" r="90" fill="#7e8a9c"/><path d="M640 180L1290 340Q1380 430 1290 520L640 680Q390 650 390 430Q390 210 640 180Z" fill="none" stroke="#202733" stroke-width="18"/>' + text(640, 445, "Table pulley", 42, "white", "middle") + text(1250, 675, "Motor pulley", 40, BLUE, "middle") + text(800, 820, "Frame both pulleys and the moving belt", 42, BLUE, "middle"))
    if kind == "pedal":
        return svg('<path d="M200 650H1400" stroke="#a3afc1" stroke-width="8"/><path d="M680 550l360-90 55 150-365 55Z" fill="#444f60"/><path d="M730 500l300-65 20 42-315 82Z" fill="#7c889b"/><path d="M440 160h200v235q170-20 250 75l-230 80-240-95Z" fill="#667a98"/>' + text(250, 740, "Approach", 40, BLUE) + text(730, 740, "Press and hold", 40, BLUE) + text(1240, 740, "Release", 40, BLUE, "middle"))
    if kind == "rotation":
        return svg(rig(800, 500, 1) + f'<path d="M300 650C290 830 1260 860 1290 650" stroke="{CORAL}" stroke-width="12" fill="none" marker-end="url(#arr)"/>' + text(800, 840, "One complete dry lap - record the actual direction", 37, BLUE, "middle"))
    if kind == "screen":
        return svg('<rect x="180" y="110" width="1240" height="660" rx="35" fill="#303949"/><rect x="250" y="170" width="1100" height="520" rx="12" fill="#dce6ff"/>' + text(800, 300, "ACTUAL SETTINGS", 68, BLUE, "middle") + text(800, 410, "Record the values used for this attempt", 40, INK, "middle") + '<path d="M365 495h870M365 575h870" stroke="#a6b8dc" stroke-width="18"/>' + text(800, 835, "Square-on view - readable text - no scrolling midway", 38, BLUE, "middle"))
    if kind in ("sound", "notes"):
        bars = ''.join(f'<path d="M{x} {440-(x%7)*30}V{440+(x%7)*30}" stroke="{BLUE}" stroke-width="15" stroke-linecap="round"/>' for x in range(350, 1280, 45))
        return svg(bars + text(800, 180, "VOICE NOTES" if kind == "notes" else "ROOM TONE", 66, BLUE, "middle") + text(800, 750, "DJI Mic Mini > iPhone Voice Memos", 42, INK, "middle"))
    if kind == "root":
        return svg('<path d="M130 110H1470V800H130Z" fill="#596779"/><ellipse cx="800" cy="430" rx="570" ry="300" fill="#b5bfcd"/><ellipse cx="800" cy="430" rx="510" ry="250" fill="#e6eaf0"/>' + text(800, 430, "Accessible interior", 55, BLUE, "middle") + text(800, 840, "Capture while the opposite end is still open", 42, BLUE, "middle"))
    if kind == "inspection":
        return svg(rig(750, 500, 1) + '<rect x="1140" y="430" width="235" height="170" rx="20" fill="white" stroke="#1749d1" stroke-width="8"/>' + text(1255, 495, "REAL", 43, BLUE, "middle") + text(1255, 555, "RESULT", 43, BLUE, "middle") + text(800, 840, "Show the procedure and the observed result", 42, BLUE, "middle"))
    if kind == "endpoints":
        return svg('<rect x="90" y="110" width="660" height="590" rx="20" fill="#e2e7ef"/><rect x="850" y="110" width="660" height="590" rx="20" fill="#e2e7ef"/>' + f'<path d="M140 440Q430 200 700 430M900 440Q1190 200 1460 430" stroke="{CORAL}" stroke-width="14" fill="none"/>' + text(420, 775, "START", 55, BLUE, "middle") + text(1180, 775, "FINISH / OVERLAP", 45, BLUE, "middle"))
    return wide()


SHOTS = [
    dict(title="Lay out the real parts", phase="Before welding", kind="parts", camera="A - GoPro", time="30 s", timing="5 s settle + 20 s clear view + 5 s tail", lede="Show what is being joined before the cap disappears into the tube.", steps=["Set the tube and this closure's cap side by side on a clean bench. Frame both completely, with enough room for your hands to enter.", "Start recording. After five seconds, place the cap beside the tube with its joint face visible. Withdraw your hands and leave the view still.", "Take one still photograph before moving anything. Keep names, shipping labels and unrelated screens outside the picture."], done="Both parts are sharp, their relative size is clear, and the cap is unobstructed.", use="Introduces the job and supplies a clean title image."),
    dict(title="Show the whole work area", phase="Before welding", kind="wide", camera="A - GoPro", time="25 s", timing="5 s settle + 15 s untouched + 5 s tail", lede="Give the viewer a map before moving into details.", steps=["With the tube in its normal fixture, show the whole rotator, tube and surrounding working space from a front corner of the bench.", "Set the top of the picture below shoulder level. Record the empty setup, then a short separate take of your hands entering the working position.", "Keep the camera still. Leave enough room around the rig to see that the head will stay in position while the work rotates."], done="The tube, nest and drive are identifiable, and your head stays outside the frame during entry and exit.", use="Establishes where each later closeup belongs."),
    dict(title="Record the preparation", phase="Before welding", kind="prep", camera="A - GoPro", time="Whole action", timing="5 s before + real action + 5 s after", lede="Show the preparation you actually perform for this attempt.", steps=["Move A closer for a medium view of your hands and the prepared joint area. Keep both sides of the work visible.", "Record a useful real cleaning or preparation action from beginning to end. Let the tool enter, do its job, then leave a clear finished view.", "Continue the fabrication procedure in its normal order. Capture another genuine operation if a second view is useful; preserve prepared surfaces."], done="The viewer can see the tool's contact and what your hands accomplished.", use="Bridges the loose parts to a prepared joint."),
    dict(title="Show the cap seating", phase="Before welding", kind="seat", camera="A - GoPro", time="Whole action", timing="5 s before + seating + 10 s settled", lede="Let the viewer see how the cap fits into the tube.", steps=["Aim slightly downward so the near rim does not hide the cap. Arrange the frame around the real seating operation before starting it.", "Record the complete seating action as the fabrication procedure calls for it. Keep the contact area visible between your hands.", "When the cap is in position, withdraw your hands if the setup permits and hold the view for ten seconds. Keep the accepted fit undisturbed."], done="The cap's final position inside the tube is visible, with an uninterrupted view of the real seating operation.", use="Explains the recessed end-cap arrangement."),
    dict(title="Show the circular joint", phase="Before tacking", kind="overview", camera="B - R50 V", time="30 s", timing="5 s settle + 20 s clear view + 5 s tail", lede="Show the entire path the weld must follow.", steps=["Use the detail position above and to one side of the tube. Zoom out toward 14 mm, or raise the camera, until the whole cap and joint fit.", "Focus on the cap and circular joint. Include the port features so the viewer has an orientation reference.", "Record without hands or tools covering the circle. Take a matching still photograph."], done="The whole circular joint is in frame and both cap and tube remain recognizable.", use="Supports a circular path graphic and the transition into the tight detail."),
    dict(title="Hold the unwelded detail", phase="Before tacking", kind="joint", camera="B - R50 V", time="40 s", timing="5 s settle + 30 s untouched + 5 s tail", lede="This is the key image for arrows and technical explanation.", steps=["Move B to one short arc of the joint. Zoom to 30 mm and start about 20-25 cm from the surface. Focus with the lens ring and peaking, then refine position and aperture until wall, cap and joint line are sharp.", "Let the joint occupy about half to two-thirds of the picture width. Leave a plain area beside it for labels and keep the bottom strip available for subtitles.", "Withdraw your hands. Record a completely still thirty-second hold, then take a full-resolution still. Note the tripod position for the matching result shot."], done="The joint line is sharp, reflections reveal both surfaces, and nothing moves through the clean hold.", use="A clean plate for a moving arrow, traced edge, freeze or inset."),
    dict(title="Record the real tacks", phase="After tacking", kind="tacks", camera="B - R50 V", time="30 s", timing="5 s settle + 20 s view + 5 s tail", lede="Show how the cap is held before the continuous pass.", steps=["Capture this view after the normal tacking operation, with emission disabled. Use the whole-cap framing from the circular joint shot.", "Show the actual tack positions. Hold a clear overall view, then record a separate detail of one useful tack if needed.", "Keep the pattern as it stands. Follow the fabrication procedure for securing the cap before any dry rotation."], done="The viewer can locate the tacks around the cap and relate them to the planned pass.", use="Explains the starting condition for the continuous weld."),
    dict(title="Place the disabled head", phase="Dry demonstration", kind="head", camera="B - R50 V", time="35 s", timing="5 s clear + 20 s pose + 10 s clear", lede="Show the head, wire and joint together without emission.", steps=["Keep the laser disabled. Reuse the unwelded joint detail and put the head and wire at the actual working pose.", "Arrange B so the nozzle and glove do not hide the wire endpoint or joint. Hold the pose for twenty seconds without operating the trigger.", "Withdraw the head and hand, then leave ten seconds of clear joint. Say a short note identifying what the wire and head positions show."], done="The relationship among nozzle, wire endpoint and joint is clear in one stable view.", use="Supports labels for the welding location and arriving material."),
    dict(title="Show the runout check", phase="During normal setup", kind="dial", camera="B - R50 V", time="One sweep", timing="5 s before + existing check + 5 s after", lede="Film the measurement already called for by the welding procedure.", steps=["Capture the real check when the procedure calls for it. Frame the dial and contact point together; use a wider locator view first if the contact is otherwise ambiguous.", "Focus on the dial face. Include a useful sweep during the normal check without blocking it with a hand.", "Record the actual reading in a spoken note or clip note. Keep the filming sequence subordinate to the fabrication sequence."], done="The dial can be read and the viewer can see which surface it measures.", use="Explains setup accuracy using the measurement actually observed."),
    dict(title="Show the copper contact", phase="Dry demonstration", kind="shoe", camera="B - R50 V", time="30 s", timing="5 s settle + 20 s view + 5 s tail", lede="Make the stationary work contact understandable.", steps=["With emission disabled, frame the copper shoe against the tube and show where the work lead attaches.", "Start with a clear stationary view. During an already planned dry run, record the tube moving past the stationary shoe if the contact remains visible.", "Keep your hand and the camera outside the moving mechanism. End with a settled view of the contact."], done="It is clear that the tube moves while the shoe and work lead remain stationary.", use="Shows how work contact is maintained through rotation."),
    dict(title="Show the belt moving", phase="Dry demonstration", kind="belt", camera="B - R50 V", time="30 s", timing="5 s settle + 20 s motion + 5 s tail", lede="Give the rotation mechanism its own readable detail.", steps=["Aim at the belt, motor pulley and turntable. Zoom B out, or back it away, enough to include their relationship.", "Record twenty seconds of an existing dry run. Keep the camera fixed so the belt supplies all the movement.", "Finish the take with a few seconds after the mechanism stops. Keep the lens, support and cables clear of the drive."], done="The moving belt and table are sharp and their connection is understandable.", use="A mechanism explanation and reusable process B-roll."),
    dict(title="Show the pedal action", phase="Dry demonstration", kind="pedal", camera="A - GoPro", time="25 s", timing="5 s clear + 15 s action + 5 s clear", lede="The pedal starts and stops rotation; it does not fire the laser.", steps=["Lower A to frame your foot and the whole pedal. Include enough floor to show the foot approaching and withdrawing.", "With the laser disabled, record five seconds with the foot clear. Approach, press and hold, release, then withdraw.", "Keep recording five seconds after the release. A separate dry lap shot shows the resulting table movement."], done="The press, hold and release are distinct, with clean picture before and after.", use="A cutaway explaining the rotation control."),
    dict(title="Record one dry lap", phase="Dry demonstration", kind="rotation", camera="A - GoPro", time="1 lap + 10 s", timing="5 s still + full revolution + 5 s still", lede="Let the viewer see what moves and how steadily it moves.", steps=["Frame the tube, nest and a recognizable index or port feature from a fixed view. Keep the laser disabled and the cap secured by the normal procedure.", "Record a complete revolution during the planned dry run. Keep hands and tools clear of the subject for the useful portion.", "Note the actual speed and direction used. At nominal 8 mm/s, one lap is about 48.6 seconds; let the observed return determine the end of this take."], done="The same reference returns to its start without a cut or camera move.", use="Supports direction arrows, timing and the stationary-head explanation."),
    dict(title="Record the actual settings", phase="Before the attempt", kind="screen", camera="B - R50 V", time="25 s / view", timing="5 s settle + 15 s readable + 5 s tail", lede="Collect legible values for the attempt being filmed.", steps=["Aim square-on at the welder display. Adjust distance and light angle until numbers are sharp and screen reflections are controlled.", "Record fifteen clear seconds of each relevant settings view. Change screens between takes, then remove your hand before each hold.", "For a computer console, save a screen recording or screenshot of the actual status. Identify which attempt the settings belong to."], done="Values are readable at full size and correspond to the recorded attempt.", use="Parameter callouts without relying on narration to remember numbers."),
    dict(title="Record the whole attempt", phase="Actual welding", kind="work", camera="A - protected view", time="Whole attempt", timing="About 10 s before + full attempt + 10 s after", lede="Keep an uninterrupted record of what actually happens.", steps=["Use the active-process camera arrangement established on page 7. Rehearse the framing with emission disabled; include hands, the welding head and tube movement below shoulder level.", "Start A and DJI audio before taking the working position. Clap once while both record, then carry out the normal welding procedure without camera adjustments.", "Keep recording through the finish and immediate aftermath. If work stops unexpectedly, follow the normal procedure and retain the real sequence."], done="The start, pass, finish and immediate response are present in one continuous recording.", use="The main process sequence and an honest account of the attempt."),
    dict(title="Record the fresh observation", phase="Immediately afterward", kind="notes", camera="DJI audio", time="30-60 s", timing="Pause briefly around each observation", lede="Keep the first useful account while the experience is fresh.", steps=["Once the equipment is safely stopped, leave the DJI mic in place and record into iPhone Voice Memos. The camera can hold on the part or stop.", "Say what you noticed: whether holding the head was easier, where the motion changed, and what happened at the finish.", "Describe the observation separately from a suspected cause. Keep the account in your own voice; a later voiceover can be more concise."], done="The observation is audible and identified with this attempt. Your face never needs to be filmed.", use="Narration, a reaction over the result, or notes for the edit."),
    dict(title="Show the whole bead", phase="After safe access", kind="wholebead", camera="B - R50 V", time="One inspection lap", timing="5 s still + complete useful sweep + 5 s still", lede="Show what was completed around the circumference.", steps=["With emission disabled and access safe, match the whole-cap view. Frame the whole joint and the same port references as before.", "Record the circumference during a normal safe inspection rotation. Keep camera and light fixed; stop and refocus between takes if needed.", "Leave a clear view at the end. Identify which closure and attempt the bead belongs to."], done="The circumference is visible without a hand obscuring the bead.", use="The overall result and context for the detail shots."),
    dict(title="Match the joint detail", phase="Before dressing", kind="bead", camera="B - R50 V", time="40 s", timing="5 s settle + 30 s untouched + 5 s tail", lede="Give the edit the same picture with the weld completed.", steps=["Return B to the unwelded detail position. Match the viewing angle, approximate scale and light direction using the earlier still.", "Focus on the actual bead, with adjacent wall and cap visible. Record thirty seconds with hands and tools clear.", "Take a full-resolution still before dressing or cleaning changes the surface. Keep this image paired with the unwelded still."], done="The two views can be compared directly and the actual bead is sharply visible.", use="Before-and-after comparison, annotations and a closing detail."),
    dict(title="Show start and finish", phase="Before dressing", kind="endpoints", camera="B - R50 V", time="30 s each", timing="For each: 5 s settle + 20 s clear + 5 s tail", lede="Capture the places where the continuous pass begins and closes.", steps=["Locate the actual start. Record a stable closeup with enough surrounding bead to show its position, then take a still.", "Locate the actual finish or overlap. Record the same duration at a similar scale and light angle, then take a still.", "Say which is which at the start of each recording, then pause before the clean hold. If both occupy one area, record a wider locator view too."], done="The clips are identified and each endpoint can be inspected without a pointer covering it.", use="Explains the transition into and out of the continuous pass."),
    dict(title="Record any trouble spot", phase="If present", kind="issue", camera="B - R50 V", time="30 s + still", timing="5 s settle + 20 s detail + 5 s tail", lede="Preserve a visible issue before changing its appearance.", steps=["If a real feature needs discussion, first show its position on the whole cap or bead. Keep the laser disabled and wait for safe access.", "Record a sharp detail with directional light. Hold a clean view before using a separate pointing take.", "Say what you can see and where it is. Photograph it before dressing or other alteration; follow the governing fabrication procedure for the next action."], done="The feature has both a locator view and a sharp detail. Skip this page when there is no feature to show.", use="An honest turning point, an inspection explanation or a question for the next attempt."),
    dict(title="Record the accessible root", phase="While the vessel is open", kind="root", camera="B - R50 V", time="30 s + still", timing="5 s settle + 20 s view + 5 s tail", lede="Get the interior view before final closure removes access.", steps=["Capture this as soon as the real interior is accessible and safe to film, before final closure. Follow fabrication order even when this page appears later in the book.", "Use a light through the open end and aim B at the actual root region. Keep the camera supported outside the vessel and refocus at that surface.", "Record a wider interior locator, then a useful detail and still if visible. If the surface cannot be seen, keep the explanation within what the footage establishes."], done="The visible interior is in focus and identifiable. Skip when the vessel is already closed.", use="Shows the accessible underside and why closing order matters."),
    dict(title="Record the real inspection", phase="When inspection occurs", kind="inspection", camera="A, then B", time="As performed", timing="Whole useful event, plus clear result holds", lede="Let inspection supply its own evidence.", steps=["Follow the pressure-vessel procedure. Frame the relevant work and instrument from A before the inspection begins.", "Record the real event. With access safe, use B for the actual surface condition, instrument reading or other observed result.", "Keep the result identified with this part and attempt. Describe only what the inspection establishes; a visual bead shot alone shows appearance."], done="The result is legible and its connection to this part is clear. Skip when inspection belongs to a later session.", use="A result sequence with the right scope for its claim."),
    dict(title="Hold the finished assembly", phase="Closing picture", kind="finished", camera="A - GoPro", time="30 s + still", timing="5 s settle + 20 s clear + 5 s tail", lede="Give the story a deliberate final image.", steps=["Set A for a three-quarter view of the tube and rig or safely supported completed article. Remove unrelated objects from the immediate background.", "Light the metal so the shape and finished joint read clearly. Record twenty seconds with hands out, then a separate take with one slow presentation movement if safe.", "Take a full-resolution still with clear space near the top for thumbnail text. Keep faces and reflections outside the frame."], done="The finished object is sharp and the clean hold has no interruption.", use="Closing narration, a thumbnail and a future episode's recap."),
    dict(title="Collect a quiet bench view", phase="Reusable B-roll", kind="empty", camera="A - GoPro", time="30 s", timing="5 s settle + 20 s still + 5 s tail", lede="Capture a little atmosphere while the lighting is already set.", steps=["Choose an empty lit bench, the waiting tube or prepared tools. Compose one clear subject and keep screens free of private messages.", "Record twenty seconds without panning, walking through or adjusting the light. The edit can use a gentle crop later.", "An extra twenty-second dry belt or tube hold can cover a longer explanation. Reuse the useful mechanism shots already captured."], done="The picture holds continuously and suits a sentence about this work.", use="A pause, title background or relevant picture under voiceover."),
    dict(title="Record the room tone", phase="Sound for the edit", kind="sound", camera="DJI audio", time="40 s total", timing="5 s settle + 30 s room tone + 5 s tail", lede="Give the audio edit a continuous shop background.", steps=["Keep the DJI mic at its normal speech position and settings. Start Voice Memos with the shop in its normal safe idle sound state.", "Wait five seconds, then stay silent and still for thirty seconds. Avoid walking, touching the mic or handling tools.", "If the background changes substantially, capture that state separately. Save a few isolated pedal clicks and dry motor starts with silence around each."], done="There are thirty uninterrupted seconds of the matching shop background.", use="Smooths narration cuts and preserves the sound of the room."),
]


def page(number, title, eyebrow, lede, content, cls=""):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{html.escape(title)}</title><link rel="stylesheet" href="style.css"></head>
    <body><article class="card {cls}"><header><div class="eyebrow">{eyebrow}</div><h1>{title}</h1><i class="rule"></i><p class="lede">{lede}</p></header>
    <main>{content}</main><footer><span>Carbonator weld - filming guide</span><span>Contents 02</span><span class="folio">{number:02d}</span></footer></article></body></html>'''


def actions(items):
    return '<ol class="actions">' + ''.join(f'<li>{i}</li>' for i in items) + '</ol>'


def figure(kind, caption):
    return f'<figure>{diagram(kind)}<figcaption>{caption}</figcaption></figure>'


def write_pages():
    GUIDE.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    pages = []

    def add(slug, title, eyebrow, lede, content, cls=""):
        number = len(pages) + 1
        path = GUIDE / f"{number:02d}-{slug}.html"
        document = page(number, title, eyebrow, lede, content, cls)
        path.write_text("\n".join(line.rstrip() for line in document.splitlines()) + "\n")
        pages.append((path, title.replace('<br>', ' ')))

    add("cover", "Carbonator weld<br>filming guide", "HOME SODA MACHINE", "Set up each shot. Record the work clearly.<br>Hands and below shoulder level throughout.",
        figure("work", "A practical capture sequence for the rotator-assisted carbonator weld.") + '<p class="cover-note">One shot per page - fixed views - narration afterward</p>', "cover")
    add("contents", "Follow the work", "START HERE", "Film the process in its real order. Use the page numbers to jump between camera positions.",
        '<table class="contents"><tr><td>03-07</td><td><b>Set up</b><br>Equipment, overall view, detail view, settings and active-process camera placement.</td></tr>'
        '<tr><td>08-14</td><td><b>Before welding</b><br>Parts, preparation, seating, unwelded geometry and tacks.</td></tr>'
        '<tr><td>15-21</td><td><b>Explain the mechanism</b><br>Disabled head, indicator, contact, belt, pedal, lap and settings.</td></tr>'
        '<tr><td>22-29</td><td><b>Attempt and result</b><br>Full attempt, fresh observation, bead, endpoints, interior and inspection.</td></tr>'
        '<tr><td>30-33</td><td><b>Finish the session</b><br>Closing image, atmosphere, room tone and original files.</td></tr></table>'
        '<div class="note"><b>If time is short</b><p>Prioritize pages 09, 13, 15, 20, 22, 25 and 32: overall view, clean joint, disabled head, dry lap, real attempt, matched result and room tone.</p></div>'
        '<div class="note"><b>Capture before access changes</b><p>The unwelded detail is page 13. The accessible interior is page 28: film it before final closure. Record the actual bead before dressing or cleaning changes it.</p></div>'
        '<p class="small">The drawings are framing sketches. They show what to include, not actual weld results or measured equipment positions. The PDF sidebar lists every shot; the footer returns to this page.</p>')
    add("equipment", "Put the kit on the bench", "SETUP 01", "Two cameras, two tripods and two lights. The GoPro holds the overall view; the Canon R50 V holds the detail.",
        '<div class="kit-grid"><div><span class="big-letter">A</span><h2>Overall position</h2><p>GoPro HERO13, stock protective lens, SmallRig CT-10 tripod.</p></div><div><span class="big-letter">B</span><h2>Detail position</h2><p>Canon EOS R50 V with its 14-30 mm kit lens, SmallRig CT25 overhead tripod.</p></div></div>'
        '<table><tr><td><a href="https://www.amazon.com/dp/B0F258T13X">Canon EOS R50 V + RF-S 14-30mm</a></td><td>Camera B</td></tr><tr><td><a href="https://www.amazon.com/dp/B0F8TDJH4J">SmallRig CT25</a></td><td>Holds B</td></tr><tr><td><a href="https://www.amazon.com/dp/B0B63VTW46">SmallRig CT-10</a></td><td>Holds A</td></tr><tr><td><a href="https://www.amazon.com/dp/B08TMBXLGD">NEEWER NL-192AI two-light kit</a></td><td>Main and fill light</td></tr><tr><td><a href="https://www.amazon.com/dp/B0G8LT6J46">SanDisk Extreme 128 GB SD</a> and <a href="https://www.amazon.com/dp/B07NW8RPYN">Anker card reader</a></td><td>B\'s card and its transfer</td></tr></table>'
        '<p>The two cameras can record at once: let A run through dry demonstrations and the attempt while B holds its detail. Keep the iPhone available for the DJI receiver and Voice Memos.</p>'
        '<div class="note"><b>Prepare before work starts</b><p>Charge both cameras, phone, mic and lights. Format the R50 V\'s card in the camera, clear the GoPro\'s card, clean lenses, silence notifications and keep lens covers nearby. The light kit includes stands and power adapters.</p></div>'
        '<p class="small">These cameras serve ordinary setup, detail and result footage; page 7 covers the separate active-process camera arrangement.</p>')
    add("overall-position", "Set the overall view", "SETUP 02 - CAMERA A", "Put the CT-10 on the floor, off one front corner of the bench. Keep the camera fixed.",
        figure("setup", "Top view. Blue dashed lines show the camera view; the diagram sets relationships, not distances.") + actions([
            "Mount the stock-lens GoPro on the tripod using its built-in 1/4-20 thread. Start around 1-1.5 m from the rig, then adjust to include the whole tube, nest and your working hands.",
            "Set the top edge below shoulder level, at upper chest or lower. Rehearse entering, reaching and leaving. Keep your head and shoulders out of every part of that movement.",
            "Keep enough downward angle to show the cap, while preserving the tube's rotation in the picture. Check shiny metal, windows and screens for face reflections."
        ]) + '<div class="finish"><b>Finished when</b><p>The viewer can see the hands, head of the tool and moving work. The picture stays below shoulder level throughout your movement.</p></div>')
    add("detail-position", "Set the detail view", "SETUP 03 - CAMERA B", "Use the CT25 to look into the joint without the near rim blocking it. Do this with emission disabled.",
        figure("detail", "Top view. Start close to the selected arc; refine the camera and lights from the recorded image.") + actions([
            "Mount the R50 V on the CT25, above and to one side. Zoom to 30 mm and start about 20-25 cm from the selected joint arc; the lens focuses as close as 15 cm. Set focus mode to MF and turn the lens ring until peaking outlines the edge.",
            "Use the overhead arm only as far as needed. Follow the tripod instructions for leg position and counterweight. Keep support and cables outside the work and drive areas.",
            "Start both lights at 5600 K, about 50 cm from the subject: main at 50%, fill at 20%. Move the main light until wall and cap separate clearly. Reduce fill if the corner loses definition."
        ]) + '<div class="finish"><b>Finished when</b><p>Wall, cap and joint are sharp together. The metal has visible detail, the near rim does not hide the line, and there is space for labels.</p></div>')
    add("recording-settings", "Set recording and focus", "SETUP 04", "Make the image predictable before the real work starts.",
        '<table><tr><td><b>A - GoPro</b></td><td>4K / 30 fps / 16:9 / Linear. Standard SDR, HDR off, Natural color, High bitrate, HyperSmooth off on the rigid tripod.</td></tr><tr><td><b>B - R50 V</b></td><td>Movie rec. size 3840x2160 / 29.97 fps / Standard (Long GOP). Movie rec. format XF-AVC S YCC420 8bit. Color mode: Picture Style Standard, HDR shooting (PQ) off. Movie digital IS off on the tripod.</td></tr><tr><td><b>Exposure at B</b></td><td>Movie manual exposure: 1/60 s, f/8 to start, the lowest ISO that exposes well, zebras on. White balance 5600 K to match the lights.</td></tr><tr><td><b>Focus at B</b></td><td>Focus mode MF. Turn the lens ring with MF peaking on and check the magnified view. Refocus after changing distance or zoom.</td></tr><tr><td><b>Speech</b></td><td>DJI receiver into iPhone. Voice Memos records the mic; camera audio supplies sync and shop sounds.</td></tr></table>'
        + actions(["Record a ten-second disabled sample with a representative hand movement, then a clear hold. Play it back at full size.", "Adjust camera or lighting if the joint is soft, a hand blocks it, reflections erase the edge, or a display flickers. If only a sliver of the joint is sharp, close B toward f/11 or move it back. On the GoPro, use shutter Auto as the first ordinary bench-light setting.", "For a static shot, start five seconds early and keep recording five seconds after the useful action. Name a clip aloud, then pause before the clean take."])
        + '<div class="note"><b>Focus and exposure are different</b><p>The lens ring sets focus. If a bright reflection is white and featureless, move the light or camera and reduce exposure as needed. Brightness settings do not establish laser protection.</p></div>'
        '<p class="small">Canon documents the R50 V\'s movie size, format, manual focus and peaking in its <a href="https://cam.start.canon/en/C021/manual/html/UG-04_Shooting_0040.html">online manual</a>; GoPro documents capture controls in <a href="https://community.gopro.com/s/article/HERO13-Black-Advanced-Protune-Controls-Explained?language=en_US">Protune support</a>.</p>')
    add("active-process", "Set the active-process view", "SETUP 05 - BEFORE EMISSION", "The detail pages are filmed with the laser disabled. Active welding uses a separate suitable camera arrangement.",
        figure("work", "Framing only. This sketch does not specify a laser-safe camera location or viewing barrier.")
        + actions(["Use A only from a camera position outside exposure or through a viewing arrangement specified for this laser and use. Get that arrangement from XLaserlab or a qualified laser-safety provider before exposing a camera to the process.", "With emission disabled, rehearse the whole working movement and check the picture. The top stays below shoulder level; your hands, the tool head and moving tube remain visible.", "Clear temporary filming props and restore normal guarding before emission. Start recording before taking your working position. Make camera adjustments only after emission is disabled."])
        + '<div class="note"><b>Picture exposure is not protection</b><p>A dark picture, photographic ND filter or ordinary welding glass does not establish protection. Keep an unprotected camera covered and outside exposure during emission, even when it is not recording.</p></div>'
        '<p class="small"><a href="https://www.xlaserlab.com/products/xlaserlab-x1-pro-laser-welder-cleaner-cutter">XLaserlab: Class 4 and laser-specific protection.</a> <a href="https://www.sony.co.uk/electronics/support/cameras-camcorders-camcorders-and-video-cameras/articles/00266583">Sony: direct and reflected laser exposure can damage sensors.</a> If a suitable active view is unavailable, use the dry demonstrations, actual observations and result footage to tell the story.</p>')

    for i, shot in enumerate(SHOTS, 1):
        status = "ACTUAL PROCESS - SEE PAGE 7" if i == 15 else "LASER DISABLED FOR CAMERA SETUP"
        content = f'<div class="capture"><div><small>CAMERA</small><b>{shot["camera"]}</b></div><div><small>RECORD</small><b>{shot["time"]}</b></div></div>'
        content += figure(shot["kind"], shot["timing"])
        content += actions(shot["steps"])
        content += f'<div class="finish"><b>Keep the take when</b><p>{shot["done"]}</p></div>'
        content += f'<p class="use"><b>In the edit:</b> {shot["use"]}</p>'
        add(f'shot-{i:02d}', shot["title"], f'SHOT {i:02d} / 25 - {shot["phase"].upper()}<span>{status}</span>', shot["lede"], content)

    add("save-and-reference", "Save the original files", "FINISH THE SESSION", "Keep the footage that makes later explanation possible.",
        actions(["Copy the R50 V's original files from its SD card through the card reader, and transfer the original GoPro clips, both at their recorded resolution. Save the original stills and the DJI Voice Memos audio alongside them. Make smaller edit copies separately.", "Label the useful clips: unwelded joint, disabled head, dry lap, actual attempt, bead before dressing, endpoints, interior and room tone. Identify the closure and attempt number.", "Keep matching unwelded and finished stills together. Note any actual speed, direction, settings and observations that will matter to narration."])
        + '<div class="note"><b>Four voiceover prompts</b><p>What was difficult? What did the rotator let you control? What did you actually observe? What comes next? Record the concise answers after watching the footage.</p></div>'
        '<h2>Working references</h2><p><a href="https://homesodamachine.com/read/weld-rotator-guide/weld-rotator-guide.pdf">Weld rotator build guide</a><br><a href="https://homesodamachine.com/read/assembly-letter-guide/assembly-drill-and-weld-letter.pdf">Carbonator fabrication guide</a></p>'
        '<p class="small">The repository procedures hardware/assembly/weld-rotation-rig.md and hardware/assembly/pressure-vessel.md govern fabrication. This filming guide determines camera coverage; record the real procedure in its normal order.</p>'
        '<p class="small">The 48.6-second nominal lap comes from the rotator procedure at 8 mm/s. Record the actual direction and setpoint used. The guide assumes the kit on page 3 and the hands-only, below-shoulder process style requested for this video.</p>')
    return pages


def bind(pages, selected=None):
    options = ["--size", "2550x3300", "--dpr", "1", "--pdf", "8.5x11in", "--page-timeout", "180000"]
    renderer = ["node", str(ROOT / "tools/render/render-card.js")]
    if selected:
        for number in selected:
            path, _ = pages[number - 1]
            subprocess.run(renderer + [str(path), str(OUT / path.with_suffix(".png").name)] + options, check=True)
    else:
        subprocess.run(renderer + ["--batch", str(GUIDE), str(OUT)] + options, check=True)
    writer = PdfWriter()
    for path, _ in pages:
        writer.append(str(OUT / path.with_suffix(".pdf").name))
    for i, (_, title) in enumerate(pages):
        writer.add_outline_item(f"{i+1:02d}  {title}", i)
        if i != 1:
            writer.add_annotation(i, Link(rect=(322, 17, 394, 42), target_page_index=1))
    writer.page_mode = "/UseOutlines"
    writer.compress_identical_objects()
    writer.add_metadata({"/Title": TITLE, "/Author": "Home Soda Machine", "/Subject": "Hands-only process filming, one shot per page"})
    with PDF.open("wb") as stream:
        writer.write(stream)
    cover = GUIDE / "carbonator-filming-guide.cover.png"
    with Image.open(OUT / pages[0][0].with_suffix(".png").name) as image:
        image.convert("RGB").resize((800, 1035), Image.Resampling.LANCZOS).save(cover, optimize=True)
    PDF.with_suffix(".pdf.json").write_text(json.dumps({"title": TITLE, "subtitle": "Hands-only filming - 25 shots, camera setup and timing, 33 Letter pages", "pages": len(pages), "cover": cover.name, "cover_size": [800, 1035]}, indent=2) + "\n")
    DELIVERY.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PDF, DELIVERY)
    sources = [Path(__file__).resolve(), GUIDE / "style.css", GUIDE / "README.md", ROOT / "marketing/video/carbonator-weld-shooting-plan.md", ROOT / "hardware/assembly/weld-rotation-rig.md", ROOT / "hardware/assembly/pressure-vessel.md"] + [p for p, _ in pages]
    DELIVERY.with_suffix(".sources.json").write_text(json.dumps({"pdf": PDF.name, "pages": len(pages), "page_inches": [8.5, 11], "artwork": "Authored vector framing sketches; not actual weld results or measured camera positions.", "pdf_sha256": hashlib.sha256(PDF.read_bytes()).hexdigest(), "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}, indent=2) + "\n")
    print(f"{PDF.relative_to(ROOT)}: {len(pages)} pages, {PDF.stat().st_size // 1024} KB")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pages", type=int, nargs="+", help="Re-render selected existing leaves before rebinding")
    args = parser.parse_args()
    bind(write_pages(), args.pages)
