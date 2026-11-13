"""PET-GF, shaping parts so they print: the enclosure and the faucet taken as designed objects.
Each function returns one Page; `pages()` puts the front-bottom part study first."""
import json
import math
import os
import struct
from array import array

import bookkit as b
import svgkit as k
from bookkit import Page
from chapters import _mine
from proj import projector

E = "printed-parts/enclosure/enclosure/"
ENC = "hardware/printed-parts/enclosure/enclosure/"
PRINTS = ENC + "prints/"
FAUCET = "hardware/printed-parts/faucet/"
SLATE = "#3a4654"


# ----------------------------------------------------------------------------- parts as they lie on the bed
# The renderer lights a scene from its own +Z, so a part drawn upside down by turning the camera
# comes out lit from underneath. These helpers turn the part instead: they write a scene pointer
# that places the part's own mesh in its print pose with the plate at z = 0, and hand it to the
# renderer as the job's `payload`.
def _head(raw):
    n = struct.unpack("<I", raw[:4])[0]
    return json.loads(raw[4:4 + n]), 4 + n


def _rx(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]]


def _rz(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]]


def _mul(a, c):
    return [[sum(a[i][n] * c[n][j] for n in range(3)) for j in range(3)] for i in range(3)]


class _Pose:
    """One printed part turned by `rot` (a 3x3 matrix) and set down on the plate, its footprint
    centred on `at`. Calling the pose with a model point gives where that point stands on the bed."""

    def __init__(self, step, rot, at=(0.0, 0.0)):
        self.step = step
        head, _ = _head((b.ROOT / "hardware" / (step + ".mesh")).read_bytes())
        self.nodes = head["meshes"]
        lo, hi = [math.inf] * 3, [-math.inf] * 3
        for node in self.nodes:
            if node.get("transform"):
                raise ValueError(f"{step} is an assembly; pose its parts one at a time")
            path = b.ROOT / ".cache/meshes/scene-assets" / (node["asset"] + ".mesh")
            if not path.exists():
                raise FileNotFoundError(f"{path} is missing; any `hsm where` on the part brings it back")
            raw = path.read_bytes()
            mesh, start = _head(raw)
            for row in mesh["meshes"]:
                at0, count = row["pos"]
                pts = array("f")
                pts.frombytes(raw[start + at0:start + at0 + count * 4])
                xs, ys, zs = pts[0::3], pts[1::3], pts[2::3]
                for i in range(3):
                    r = rot[i]
                    vals = [r[0] * x + r[1] * y + r[2] * z for x, y, z in zip(xs, ys, zs)]
                    lo[i], hi[i] = min(lo[i], min(vals)), max(hi[i], max(vals))
        shift = [at[0] - (lo[0] + hi[0]) / 2, at[1] - (lo[1] + hi[1]) / 2, -lo[2]]
        self.frame = [rot[i] + [shift[i]] for i in range(3)]
        self.size = [hi[i] - lo[i] for i in range(3)]
        self.at = at

    def __call__(self, p):
        return [sum(self.frame[i][j] * p[j] for j in range(3)) + self.frame[i][3] for i in range(3)]

    def footprint(self, margin=0.0):
        """The plate rectangle under the part: x0, y0, x1, y1."""
        return (self.at[0] - self.size[0] / 2 - margin, self.at[1] - self.size[1] / 2 - margin,
                self.at[0] + self.size[0] / 2 + margin, self.at[1] + self.size[1] / 2 + margin)


def _scene(name, poses):
    """Writes the pointer for some posed parts and returns its path for a render job's `payload`."""
    b.META.mkdir(parents=True, exist_ok=True)
    nodes = []
    for pose in poses:
        for node in pose.nodes:
            nodes.append({**node, "transform": pose.frame})
    text = json.dumps({"meshes": nodes, "v": 4}, separators=(",", ":")).encode()
    text += b" " * (-len(text) % 4)
    path = b.META / f"{name}.posed.mesh"
    data = struct.pack("<I", len(text)) + text
    if not path.exists() or path.read_bytes() != data:
        path.write_bytes(data)
    return str(path.relative_to(b.ROOT))


def _discs(marks, proj):
    """Numbered discs over a model picture. marks: (number, bed point, class)."""
    return "".join(f'<span class="num on-model {c}" style="left:{proj(pt)[0]:.0f}px; top:{proj(pt)[1]:.0f}px">{n}</span>'
                   for n, pt, c in marks)


def _legend(items, size=32, gap=26):
    """The numbered key under a part study: (number, class, name, landing, text)."""
    return "".join(
        f'<div style="display:flex; gap:24px; align-items:flex-start; margin-bottom:{gap}px; break-inside:avoid"><span class="num {c}">{n}</span>'
        f'<div><p style="margin:0 0 4px; font:650 40px/1.2 \'IBM Plex Sans\'; color:var(--ink)">{t} <span class="mono" style="font-size:25px; font-weight:400; letter-spacing:.08em; color:var(--muted); margin-left:10px">{land.upper()}</span></p>'
        f'<p class="tiny" style="margin:0; font-size:{size}px; color:var(--text)">{d}</p></div></div>'
        for n, c, t, land, d in items)


def _note(text, style=""):
    return f'<p class="mono" style="position:absolute; margin:0; font-size:27px; line-height:1.5; letter-spacing:.08em; color:var(--muted); {style}">{text}</p>'


# ----------------------------------------------------------------------------- orientation
def _fit(cam, boxes, size, pad=0.0, up=(0, 0, 1)):
    """A look-at point and an orthographic half-height that frame some bed boxes (x0, y0, z0, x1, y1, z1)
    from the direction cam, centred in a picture of the given size."""
    norm = lambda v: [x / math.sqrt(sum(c * c for c in v)) for x in v]
    cross = lambda a, c: [a[1] * c[2] - a[2] * c[1], a[2] * c[0] - a[0] * c[2], a[0] * c[1] - a[1] * c[0]]
    f = norm([-c for c in cam])
    r = norm(cross(f, list(up)))
    u = cross(r, f)
    pts = [[bx[i], bx[j], bx[n]] for bx in boxes for i in (0, 3) for j in (1, 4) for n in (2, 5)]
    rs = [sum(a * c for a, c in zip(p, r)) for p in pts]
    us = [sum(a * c for a, c in zip(p, u)) for p in pts]
    cr, cu = (min(rs) + max(rs)) / 2, (min(us) + max(us)) / 2
    span = max((max(us) - min(us)) / 2, (max(rs) - min(rs)) / 2 * size[1] / size[0]) + pad
    return [cr * r[i] + cu * u[i] for i in range(3)], span


def _box(pose, margin=0.0):
    x0, y0, x1, y1 = pose.footprint(margin)
    return (x0, y0, 0.0, x1, y1, pose.size[2])


def _plates(proj, rects, w, h):
    """The patches of bed under some parts, drawn behind their picture. Each rect is x0, y0, x1, y1."""
    d = "".join("M" + " L".join(f"{k.n(x)} {k.n(y)}" for x, y in [proj([x, y, 0.0]) for x, y in ((r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3]))]) + " Z"
                for r in rects)
    return k.svg(w, h, f'<path d="{d}" fill="{k.WASH}" stroke="{k.INK}" stroke-width="3" stroke-linejoin="round"/>',
                 "The print bed under the part", style="position:absolute; left:0; top:0")


def orientation():
    quads = [
        ("front-bottom", "Front-bottom", "Floor down", _rx(0), [0.72, 0.86, 0.62],
         "The floor slab.",
         "The walls. Flutes and vent slots run straight up the build.",
         "Two rail catches on short trees. The handhold roofs lean at 45°."),
        ("back-bottom", "Back-bottom", "Floor down", _rx(0), [0.72, -0.86, 0.62],
         "The floor slab.",
         "The rear wall and its raised warning letters, each raked 45° underneath.",
         "Two rail catches, the handhold mouths and the seam lips, on trees."),
        ("front-top", "Front-top", "Mouth down", _rx(0), [0.62, -0.8, 0.56],
         "The rim that meets front-bottom. A ring.",
         "The roof and display surround, printed last. Their rounds close inward and carry themselves.",
         "The rail channels close as 45° gables. The pump mount is solid to the roof."),
        ("back-top", "Back-top", "Ceiling down", _rx(180), [-0.7, 0.74, 0.6],
         "The whole outer roof, as the first layer.",
         "The roof, flat and textured by the plate.",
         "Few. What hung from the ceiling stands on it. Catches bridge. Rails take support."),
    ]
    W, H = 517, 500
    posed = [(_Pose(E + f"enclosure-{q[0]}.step", q[3]), q) for q in quads]
    span = max(_fit(q[4], [_box(pose, 10)], (W, H))[1] for pose, q in posed)
    pics, names, rows = [], [], {"On the bed, drawn in orange": [], "Kept clean": [], "Undersides": []}
    for pose, (key, name, pose_name, rot, cam, bed, clean, under) in posed:
        step, body = pose.step, f"enclosure-{key}"
        payload = _scene(f"petgf-design-pose-{key}", [pose])
        target, _ = _fit(cam, [_box(pose, 10)], (W, H))
        pic = b.render(f"petgf-design-pose-{key}.png",
                       dict(step=step, payload=payload, cam=cam, target=target, span=span, size=f"{W * 2}x{H * 2}", edges=True,
                            materials=[{"names": [body], "color": SLATE, "roughness": 0.85}]))
        foot = b.render(f"petgf-design-foot-{key}.png",
                        dict(step=step, payload=payload, cam=[0, 0, 1], up=[0, 1, 0], target=[0, 0, 0], span=150, size="300x300",
                             clip=[{"axis": "z", "lo": -1.0, "hi": 0.9}],
                             materials=[{"names": [body], "color": k.HOT, "unlit": True, "tone_mapped": False}]))
        plate = _plates(projector(cam, target, span, (W, H)), [pose.footprint(10)], W, H)
        pics.append(f'<div style="position:relative; height:{H}px">{plate}'
                    f'<img src="art/{pic}" alt="{name} as it sits on the bed" style="position:absolute; left:0; top:0; width:{W}px; height:{H}px"></div>')
        names.append(f'<div style="display:flex; gap:16px; align-items:center; padding:6px 0 16px"><img src="art/{foot}" alt="" style="flex:0 0 78px; width:78px; height:78px">'
                     f'<div><h2 style="margin:0 0 4px">{name}</h2>'
                     f'<p class="mono" style="margin:0; font-size:26px; font-weight:600; letter-spacing:.09em; text-transform:uppercase; color:var(--hot)">{pose_name}</p></div></div>')
        for label, text in (("On the bed, drawn in orange", bed), ("Kept clean", clean), ("Undersides", under)):
            rows[label].append(f'<div style="border-top:2px solid var(--line); padding:14px 0 16px"><span class="lab" style="color:var(--muted)">{label}</span>'
                               f'<p class="tiny" style="margin:0; font-size:31px; color:var(--text)">{text}</p></div>')
    grid = (f'<div style="display:grid; grid-template-columns:repeat(4, {W}px); column-gap:34px; margin-top:20px">'
            + "".join(pics) + "".join(names) + "".join("".join(v) for v in rows.values()) + "</div>")

    # the two ways back-top has been stood on a plate
    step = E + "enclosure-back-top.step"
    down = _Pose(step, _rx(180), at=(0.0, -170.0))
    tilt = _Pose(step, _rx(-107), at=(0.0, 170.0))
    payload = _scene("petgf-design-back-top-two-poses", [down, tilt])
    b.source("tilt", ENC + "support-removal-review/height-reading.json", revision="642e1aaa3")
    travel = float(b.value("tilt", "/printer_printable_height_mm"))
    TW, TH = 1000, 600
    cam = [1.0, -0.3, 0.24]
    tx0, ty0, tx1, ty1 = tilt.footprint(10)
    target, tspan = _fit(cam, [_box(down, 10), (tx0, ty0, 0.0, tx1, ty1, travel)], (TW, TH - 90))
    tspan *= TH / (TH - 90)
    target[2] -= 14
    two = b.render("petgf-design-back-top-two-poses.png",
                   dict(step=step, payload=payload, cam=cam, target=target, span=tspan, size=f"{TW * 2}x{TH * 2}", edges=True,
                        materials=[{"names": ["enclosure-back-top"], "color": SLATE, "roughness": 0.85}]))
    pt = projector(cam, target, tspan, (TW, TH))
    lid = [pt([x, y, travel]) for x, y in ((tx0, ty0), (tx1, ty0), (tx1, ty1), (tx0, ty1))]
    la, lb = pt([110.0, -170.0, 0.0]), pt([110.0, 170.0, 0.0])
    under = _plates(pt, [down.footprint(10), tilt.footprint(10)], TW, TH)
    over = k.svg(TW, TH,
                 '<path d="M' + " L".join(f"{k.n(x)} {k.n(y)}" for x, y in lid) + f' Z" fill="none" stroke="{k.BAD}" stroke-width="4" stroke-dasharray="12 9"/>'
                 + k.label(lid[0][0] - 16, lid[0][1] + 8, "TOP OF THE", 25, anchor="end", fill=k.BAD, weight=600)
                 + k.label(lid[0][0] - 16, lid[0][1] + 40, "MACHINE&rsquo;S TRAVEL", 25, anchor="end", fill=k.BAD, weight=600)
                 + k.label(la[0], TH - 8, "CEILING DOWN", 27, anchor="middle", fill=k.INK, weight=600)
                 + k.label(lb[0], TH - 8, "ON ITS REAR WALL, TILTED", 27, anchor="middle", fill=k.BAD, weight=600),
                 "Back-top stood on the bed two ways",
                 "On the left the part lies on its roof and stands low. On the right it stands on its rear wall, leaning, and "
                 "reaches almost to the top of the printer's travel.", style="position:absolute; left:0; top:0")
    b.source("fits", "tools/hsm/shared-data/catalog/scalars.json")
    blurb = lambda t, x: f'<p class="tiny" style="margin:0; font-size:31px; color:var(--text)"><b>{t}</b> {x}</p>'
    body = (
        b.head("Orientation", "Orientation comes first.",
               "Before a part has a hole in it, it has a face that will lie on the bed. That choice fixes which surface comes out flat, "
               "which way grooves and bores run, and where the undersides fall.", lede_size=50)
        + b.scope("PET-GF · the four enclosure quadrants as prepared in November 2026 · textured PEI · left 0.4 mm")
        + grid
        + b.rulebar(20, 28)
        + b.row(
            ("0 0 1000px", f'<div style="position:relative; width:{TW}px; height:{TH}px">{under}<img src="art/{two}" alt="" style="position:absolute; left:0; top:0; width:{TW}px; height:{TH}px">{over}</div>'),
            '<h2>The day the pose was traded away</h2>'
            '<p class="small" style="margin-bottom:16px; font-size:35px">On 6 November 2026 a back-top came off Mark2 with supports no tool could reach. That afternoon the next plate was '
            'prepared with the part stood on its rear wall and tilted, so its catches and rails would grow as plain walls. That solved the supports. '
            f'It also laid the flutes on their sides, hung the rear show face over trees in fine layers, and stood the part {b.setting("tilt", "/highest_layer_mm")} mm tall '
            f'in {b.setting("tilt", "/printer_printable_height_mm")} mm of travel. The slicer&rsquo;s estimate went from 27 hours to 82. It was never sent.</p>'
            + b.quote("Please fix it. Please fix the enclosure. Restore our correct print orientation and fix the support problems the right way.", "DEREK · 7 NOVEMBER 2026", size=40)
            + '<p class="small" style="margin:16px 0 0; font-size:35px">The right way was in the part: a full landing under each end of each bridged catch, pointed roofs on the sideways bores, and every remaining support named. That is the next page.</p>',
            gap=50)
        + b.row(
            blurb("One face is free.", "The face on the plate comes out flat with nothing under it. The last face printed can close however it likes. Every other face is a wall, or it overhangs."),
            blurb("Grooves and holes pick a side.", "Along the build they print as drawn. Across it, a groove is a row of ledges and a round hole needs a pointed roof."),
            blurb("Fits follow.", f"Each supported face in a joint adds {b.setting('fits', '/fits/supported_surface')} mm to its gap. The same rail is drawn looser in the back column, where two of its faces print on support, than in the front, where one does."),
            gap=46, style="margin-top:26px")
        + '<div style="margin-top:22px">' + b.record(
            b.link("How each piece is laid down", ENC + "README.md", anchor="print-orientation--corner-relief"),
            b.link("The tilted plate, prepared and not sent", ENC + "support-removal-review/native-print.json", "642e1aaa3"),
            b.link("The restored pose", "changes/2026-11-07-1859-pisco-bridge-anchor/entry.md"),
            b.link("Back-top first printed on its ceiling", ENC + "print-log.md", anchor="2026-09-22--back-top-v2-on-h2c")) + "</div>"
    )
    return Page("orientation-comes-first", "PET-GF: orientation comes first", "petgf", body, right="Orientation")


# ----------------------------------------------------------------------------- back-top
def back_top():
    step = E + "enclosure-back-top.step"
    pose = _Pose(step, _rx(180))
    payload = _scene("petgf-design-back-top", [pose])
    mat = [{"names": ["enclosure-back-top"], "color": SLATE, "roughness": 0.85}]
    cam, target, span, size = [-0.62, 0.62, 0.7], [18.0, -6.0, 98.0], 166, (1500, 950)
    main = b.render("petgf-design-back-top-on-the-bed.png",
                    dict(step=step, payload=payload, cam=cam, target=target, span=span, size="1500x950", edges=True, materials=mat,
                         section={"at": [-62, 0, 0], "normal": [-1, 0, 0]}))
    pm = projector(cam, target, span, size)
    marks = [("1", pose([24, 322, 346]), ""), ("2", pose([76.5, 469.3, 294.2]), ""), ("2", pose([28.8, 469.3, 264.0]), ""),
             ("3", pose([28.8, 417, 334]), ""), ("4", pose([64.4, 441, 340.6]), ""), ("5", pose([101.1, 300, 168.5]), "hot"),
             ("6", pose([88, 259.5, 346]), "hot"), ("6", pose([99, 210, 322]), "hot")]

    # the Pisco receiver cut open along its length
    rcam, rtarget, rspan = [-0.8, 0.35, 0.5], pose([64.6, 442.5, 345.0]), 18.5
    sec = b.render("petgf-design-back-top-catch-section.png",
                   dict(step=step, payload=payload, cam=rcam, target=rtarget, span=rspan, size="1280x840", edges=True, materials=mat,
                        section={"at": [64.6, 0, 0], "normal": [-1, 0, 0]}))
    pr = projector(rcam, rtarget, rspan, (640, 420))
    fore = pr(pose([64.6, 420.1, 343.3]))     # where the bar leaves its fore landing
    aft = pr(pose([64.6, 462.3, 343.3]))      # where it reaches the rear one
    air = pr(pose([64.6, 441.2, 347.6]))
    roof = pr(pose([64.6, 441.2, 353.4]))
    lf, la = pr(pose([64.6, 418.6, 349.0])), pr(pose([64.6, 463.8, 349.0]))
    over = k.svg(640, 420,
                 k.line(fore[0], fore[1], aft[0], aft[1], k.HOT, 9)
                 + k.label(air[0], air[1] + 9, "AIR", 25, anchor="middle", fill="#c9d2da")
                 + k.label(roof[0] - 40, roof[1] + 9, "ROOF", 23, anchor="middle", fill="white")
                 + f'<rect x="14" y="14" width="398" height="44" fill="white"/>'
                 + k.label(26, 46, "FIRST COURSE OF THE BAR", 25, fill=k.HOT, weight=600)
                 + k.line(210, 58, (fore[0] + aft[0]) / 2 - 40, (fore[1] + aft[1]) / 2 + 2, k.HOT, 3)
                 + f'<rect x="{k.n(lf[0] - 70)}" y="366" width="140" height="40" fill="white"/>'
                 + k.label(lf[0], 396, "LANDING", 25, anchor="middle", fill=k.INK, weight=600)
                 + k.arrow(lf[0], 366, lf[0], lf[1] + 8, k.INK, 3)
                 + f'<rect x="{k.n(la[0] - 70)}" y="366" width="140" height="40" fill="white"/>'
                 + k.label(la[0], 396, "LANDING", 25, anchor="middle", fill=k.INK, weight=600)
                 + k.arrow(la[0], 366, la[0], la[1] + 8, k.INK, 3),
                 "The Pisco receiver cut open along its length, as it prints",
                 "The roof lies on the bed. Above it is the pocket a cap's wing snaps into, and over the pocket a bar. The first "
                 "course of the bar is pulled across the pocket and rests on full stock at both ends.",
                 style="position:absolute; left:0; top:0")

    b.source("backtop", PRINTS + "2026-11-11-back-top-support-D-mark2/project-check.json")
    b.source("fits", "tools/hsm/shared-data/catalog/scalars.json")
    items = [
        ("1", "", "Roof", "On the bed", "The outer roof is the first layer, so it takes the plate&rsquo;s texture and needs nothing under it. Its side edges leave the bed as a chamfer, "
         f"{b.setting('fits', '/overhang_round/OUTWARD_PER_HEIGHT')} mm out per millimetre up, not a round."),
        ("2", "", "Fitting bores", "Lean", "Six holes cross the rear wall sideways. Each keeps its round seat and gains a pointed roof. Coloured plates cover the points."),
        ("3", "", "Receivers", "Straight up", "The cradles for the regulators stand on the slab like furniture on a floor. Under a ceiling, each one was an overhang."),
        ("4", "", "Catches", "Bridge", "The bar a cap snaps under is pulled along its pocket between two full shoulders. Nothing is printed beneath it, so there is nothing to dig out."),
        ("5", "hot", "Rails", "Support", "The face that holds this piece down is flat because it bears. It prints on strips that stand on the rail&rsquo;s own floor and leave through the open lane."),
        ("6", "hot", "Ledges", "Support", "Small undersides at the open end, where a screwdriver does reach. Each one is named for the slicer by hand. One left off the list prints over air."),
    ]
    loops = b.asset("petgf-design-back-top-loops.jpg", PRINTS + "2026-11-10-back-top-D-mark1/physical-observation/photo-1.jpg")
    roof = b.asset("petgf-design-back-top-roof-first.jpg", PRINTS + "2026-11-10-back-top-D-mark1/physical-observation/photo-2.jpg")
    side = (
        '<div style="display:grid; grid-template-columns:1fr 1fr; gap:30px">'
        + b.stat(b.setting("backtop", "/objects/0/parts/support_blocker"), "places the slicer is forbidden to support")
        + b.stat(b.setting("backtop", "/objects/0/parts/support_enforcer"), "undersides it is told to support")
        + "</div>"
        + f'<div style="position:relative; width:640px; height:420px; margin-top:50px; background:var(--wash)"><img src="art/{sec}" alt="" style="position:absolute; left:0; top:0; width:640px; height:420px">{over}</div>'
        '<p class="cap"><span class="lab">Section through a receiver</span>The bar a cap snaps under, bridged over its pocket. On 7 November 2026 a service opening '
        'beside it was shortened so the fore end lands on full stock too.</p>'
    )
    body = (
        b.head("Part study · Enclosure back-top", "The roof is the first layer.",
               "Back-top is the lid over the plumbing and electronics. It prints upside down. Its outer roof lies on the plate, and "
               "what will hang from the ceiling grows up from it.", size=150, lede_size=52, top=60)
        + b.scope("PET-GF · back-top as prepared for Mark2 on 11 November 2026 · textured PEI · left 0.4 mm")
        + '<div style="display:flex; gap:30px; margin-top:10px">'
        + f'<figure style="position:relative; flex:0 0 1500px; height:950px"><img src="art/{main}" alt="Enclosure back-top as it sits on the bed, roof down, with its west side cut away" '
          f'style="position:absolute; left:0; top:0; width:1500px; height:950px">{_discs(marks, pm)}'
          + _note("AS IT SITS ON THE BED<br>WEST SIDE CUT AWAY<br>BUILD DIRECTION ↑", "left:0; bottom:20px") + "</figure>"
        + f'<div style="flex:0 0 640px; padding-top:30px">{side}</div></div>'
        + b.rulebar(10, 30)
        + f'<div style="columns:3; column-gap:46px">{_legend(items, gap=22)}</div>'
        + b.row(
            ("0 0 520px", b.fig(roof, "A print head over the first few millimetres of back-top: a flat black slab with low walls on the textured plate",
                                "10 November 2026 · Mark 1", "A few millimetres up. The slab is the roof.", h=330, pos="88% 42%", zoom=150)),
            ("0 0 520px", b.fig(loops, "Loops of black plastic hanging under a small ledge between two hollow support trunks",
                                "The same print", "A ledge nobody had named, laid over air.", h=330, pos="38% 50%", zoom=150)),
            '<p class="tiny" style="margin:0 0 20px; font-size:32px; color:var(--text)"><b>No tool, no support.</b> The back-top that finished on Mark2 on 6 November 2026 had '
            'slicer supports inside its receivers. On a coupon they had come out with a small screwdriver. In the full part the walls were in the way.</p>'
            + b.quote("I can&rsquo;t reach in that far to remove those tiny little supports.", "DEREK · 6 NOVEMBER 2026", size=40)
            + '<p class="tiny" style="margin:22px 0 0; font-size:32px; color:var(--text)">So those interiors print with none, and every other support is chosen by hand. '
              'The first print prepared that way was stopped on 10 November with loops hanging under three ledges.</p>',
            gap=44, style="margin-top:14px")
        + b.still_open("No back-top has come off the bed since the missing undersides were named. The preparation of 11 November has been sliced and read, not printed.")
        + '<div style="margin-top:20px">' + b.record(
            b.link("What gets support and what must not", ENC + "enclosure-back-top.print-features.json"),
            b.link("The print of 5 November and what came back", PRINTS + "2026-11-05-back-top-smooth-corners-mark2/physical-result.json"),
            b.link("The loops, 10 November", PRINTS + "2026-11-10-back-top-D-mark1/physical-observation/physical-observation.json"),
            b.link("The bar&rsquo;s fore landing", "changes/2026-11-07-1859-pisco-bridge-anchor/entry.md"),
            b.model_link("A receiver on the live model", "feature: enclosure-back-top::pisco-receiver")) + "</div>"
    )
    return Page("the-roof-is-the-first-layer", "Back-top: the roof is the first layer", "petgf", body, right="Part study")


# ----------------------------------------------------------------------------- the skin
def skin():
    step = E + "enclosure-front-bottom.step"
    mat = [{"names": ["enclosure-front-bottom"], "color": SLATE, "roughness": 0.85}]
    MW, MH = 1440, 960
    cam = [1.0, -0.5, 0.34]
    target, span = _fit(cam, [(104.0, 2.0, -6.0, 110.5, 217.8, 174.8)], (MW, MH), pad=3)
    main = b.render("petgf-design-skin-flank.png", dict(step=step, cam=cam, target=target, span=span, size=f"{MW}x{MH}", materials=mat))
    pm = projector(cam, target, span, (MW, MH))
    marks = [("1", [110.5, 176, 118], ""), ("2", [110.5, 112, -1.5], ""), ("2", [110.5, 188, 44], ""), ("3", [109.8, 96, 100], ""),
             ("4", [109.8, 54, 139], ""), ("5", [110.0, 128, 86], ""), ("6", [110.5, 199.5, 128], "")]

    CW, CH = 690, 420
    ccam, ctarget, cspan = [1.0, -0.5, 0.3], [108.0, 60.0, 57.5], 13.0
    close = b.render("petgf-design-skin-slot-ends.png", dict(step=step, cam=ccam, target=ctarget, span=cspan, size=f"{CW * 2}x{CH * 2}", materials=mat))
    scam, starget, sspan = [0.25, -0.2, 1.0], [105.5, 60.0, 70.0], 10.5
    cut = b.render("petgf-design-skin-section.png", dict(step=step, cam=scam, target=starget, span=sspan, size=f"{CW * 2}x{CH * 2}", edges=True, materials=mat,
                                                           section={"at": [0, 0, 70], "normal": [0, 0, 1]}))

    b.source("skin", "tools/hsm/shared-data/catalog/scalars.json")
    items = [
        ("1", "", "Flutes", "Straight up", f"Half-round grooves every {b.setting('skin', '/reeding/flute_pitch')} mm, running the way the part grows. Each layer&rsquo;s outline simply has the grooves in it. Nothing overhangs and nothing steps."),
        ("2", "", "Fades", "Straight up", "Every groove shallows to nothing before the bed, the seam above, an opening or a rounded corner. The first layer is a plain outline, and no groove meets an edge as a row of teeth."),
        ("3", "", "Vent slots", "Lean", f"A slot {b.setting('skin', '/reeding/pierce_width')} mm wide is cut through the floor of each groove in front of the condenser&rsquo;s fan. Seen from the side, the wall still reads as flutes."),
        ("4", "", "Pointed ends", "Lean", "Each slot closes at the top and opens at the bottom on a 45° point, inside the groove&rsquo;s own shadow. Nothing bridges."),
        ("5", "", "Transoms", "Straight up", "Three bands are left unpierced. Every bar between two slots is tied to its neighbours instead of standing free for the height of the fan."),
        ("6", "", "The seam", "Straight up", "The joint between the front and back pieces runs the full height of the wall. It lands in a groove, off its centre, in a shadow that is already there."),
    ]
    photo = b.asset("petgf-design-skin-front-top-printed.jpg", "web/public/update-images/2026-09-25-front-top.png", kind="Photograph from the site's update of 25 September 2026")
    side = (
        f'<figure><img src="art/{close}" alt="Vent slots ending in points at an unpierced band" style="display:block; width:{CW}px; height:{CH}px; background:var(--wash)">'
        '<figcaption class="cap"><span class="lab">At a transom</span>Slots end in a point and begin on one. The grooves run on through the band unbroken.</figcaption></figure>'
        f'<figure style="margin-top:30px"><img src="art/{cut}" alt="The wall cut level through the vent: bars between slots, each slot in the floor of a groove" style="display:block; width:{CW}px; height:{CH}px; background:var(--wash)">'
        '<figcaption class="cap"><span class="lab">Cut level through the vent</span>Each slot goes through the floor of a groove. What is left between two slots is a bar.</figcaption></figure>'
    )
    body = (
        b.head("The skin", "The skin is a printing decision.",
               "The outside of the box is fluted from floor to roof. A printer draws each layer&rsquo;s outline in one pass, so a groove that "
               "runs straight up is simply part of that outline, layer after layer. Turned sideways, the same groove is a row of ledges.", size=150, lede_size=52, top=60)
        + b.scope("PET-GF · every quadrant printed since September 2026 · Mark 1 and Mark2 · left 0.4 mm", not_tried="the coupons that chose the groove were drawn for PETG")
        + '<div style="display:flex; gap:40px; margin-top:14px">'
        + f'<figure style="position:relative; flex:0 0 {MW}px; height:{MH}px"><img src="art/{main}" alt="The east wall of enclosure front-bottom: flutes, with a grille of slots in four courses" '
          f'style="position:absolute; left:0; top:0; width:{MW}px; height:{MH}px">{_discs(marks, pm)}'
          + _note("FRONT-BOTTOM, EAST WALL<br>BUILD DIRECTION ↑", "left:0; bottom:0; background:white; padding:10px 18px 0 0") + "</figure>"
        + f'<div style="flex:0 0 {CW}px">{side}</div></div>'
        + b.rulebar(22, 28)
        + f'<div style="columns:3; column-gap:46px">{_legend(items, gap=20)}</div>'
        + b.row(
            ("0 0 760px", b.fig(photo, "A printed black front-top: flutes along the lower edge fading out below a smooth band and the display",
                                "24 September 2026 · PET-GF", "A printed front-top. The flutes fade out below the display surround.", h=400, pos="50% 100%")),
            '<h2 style="font-size:44px">Four walls behind every groove</h2>'
            f'<p class="tiny" style="margin:0 0 16px; font-size:32px; color:var(--text)">The slicer lays this wall as two loops inside and two outside, {b.setting("skin", "/reeding/pierce_shell")} mm in all. '
            'A groove may take only what leaves all four. Whatever disturbs those loops from behind shows on the outside. On 11 October 2026 a back-top came off Mark 1 with '
            'lengths of flute missing, each opposite a screw pad that the slicer had been told to reinforce with extra walls.</p>'
            + b.quote("&hellip;a bunch of features from the interior side have resulted in parts of the flutes cut off, like different lengths of vertical lines removed from the exterior surface&hellip;", "DEREK · 11 OCTOBER 2026", size=37)
            + '<p class="tiny" style="margin:16px 0 0; font-size:32px; color:var(--text)">Reinforcement now changes infill only, and nothing inside the box is cut into the back of a fluted wall.</p>',
            gap=50, style="margin-top:8px")
        + b.still_open("The bars between slots and the wall under a groove are the thinnest sections on the box. Both were approved as drawn on 21 October 2026. "
                       "No one has yet written down how the vent printed, or whether the missing flutes came back.")
        + '<div style="margin-top:18px">' + b.record(
            b.link("The reeded skin and the vents", ENC + "README.md", anchor="the-reeded-skin"),
            b.link("The flutes cut off, 11 October", "hardware/printed-parts/drain-readiness/prints/2026-10-10-current-back-top-bridge50-mark1/physical-result.json"),
            b.link("The texture coupons, August", "hardware/printed-parts/enclosure/texture-coupons/README.md", "c14bb2fff"),
            b.model_link("The vents on the live model", "feature: enclosure-front-bottom::condenser-vents")) + "</div>"
    )
    return Page("the-skin-is-a-printing-decision", "PET-GF: the skin is a printing decision", "petgf", body, right="The skin")


# ----------------------------------------------------------------------------- the chapter
def pages():
    made = [_mine.anatomy(), orientation(), back_top(), skin()]
    only = os.environ.get("PETGF_DESIGN_ONLY")
    return [made[int(i)] for i in only.split(",")] if only else made
