"""Print the Sculpted base's foot as sloped courses on a scaffold, ahead of the rest of the plate.

    sloped.py <sliced .gcode.3mf> <print.json> <faucet-shell-base.stl> <headmap.npz> <out dir>

The slicer was given the base with the space under its mounting face filled, so its courses above
the face are ordinary inside courses. This stage puts a scaffold and three roof courses where the
fill was, then lays the foot itself as courses parallel to the mounting face, each cut from the
base's own section at that height, up past the shoulders of the insert sockets. A support plug
stands in each socket under its shoulder, and a deck stands in the bore for the trees inside the
base. All of that prints before the plate's first layer. The plate then prints as sliced: the
base's level courses are laid only over the slab, each one thinning to nothing where the slab
rises to meet it, and every travel the toolhead would carry into the slab is lifted over it.
"""
import hashlib, io, json, math, re, sys, zipfile
import os
import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from courses import edge_pieces, hatch, level_order, narrow_pieces, sections   # noqa: E402

# ---- the stack, normal to the mounting face (mm) -------------------------------------------
COURSE = 0.24                 # every sloped course's thickness
AIR = 0.24                    # asked between the roof and the skin, as Support D asks
ROOF_COURSES = 3
COURSES_OVER_SHOULDER = 1     # sloped courses laid on the sockets' shoulders before the level courses
ROOF_WIDTH = 0.62             # the support line width; roof lines touch
SKIN_WIDTH = 0.42
SKIN_PITCH = 0.40
LIP = 2.0                     # the roof beyond the rim
DECK_KERF = 0.8               # the bore's deck from the slab's edge
PLUG_CLEAR = 0.5              # a socket's plug from the socket's wall
SHOULDER_REACH = 0.3          # the shoulder's bridge onto the socket's rim
OVERLAP = 0.06                # the fill into the ring beside it
OPEN = 1.0                    # half the least width the fill is laid in; narrower strips take rings
RIM = (29.0, 29.5)
# ---- the scaffold ----------------------------------------------------------------------------
FIRST_LAYER = 0.20
LAYER = 0.24
WALL_PITCH = 2.5
TIE_PITCH = 10.0
# ---- motion ----------------------------------------------------------------------------------
FILAMENT_AREA = math.pi * 0.875 ** 2
FLOW = 0.9555
BRIDGE_FLOW = 1.25
Z_PRINT_RATE = 7.5            # mm/s of Z while extruding
Z_TRAVEL_RATE = 15.0          # mm/s of Z while travelling
RETRACT = 0.8
TRAVEL_LIFT = 1.0
PARK_Z = 26.0
BED_MIN_Z = 0.2
# ---- clearance -------------------------------------------------------------------------------
HEAD_TRAVEL_MARGIN = 3.0
NOZZLE_TRAVEL_MARGIN = 0.3
NOZZLE_FLAT_R = 0.6
NOZZLE_OVER_SKIN = 0.06       # the least the nozzle stands over the skin while laying a level course
FEATHER_MIN = 0.3             # a level course ends where less than this much of its height is left over the slab
KEEP_FRACTION = 0.5           # a level course is kept where this much of its height clears the skin, so it presses onto it

TILT = math.radians(15.0)
S, C, T = math.sin(TILT), math.cos(TILT), math.tan(TILT)


def bead(width, height):
    return (width - height) * height + math.pi * (height / 2.0) ** 2


def e_per_mm(width, height, flow=1.0):
    return bead(width, height) / FILAMENT_AREA * FLOW * flow


class Frame:
    def __init__(self, seat):
        self.cx, self.cy, self.cz = seat

    def xyz(self, a, b, n):
        return (self.cx + a, self.cy - b * C + n * S, self.cz + b * S + n * C)

    def face(self, y):
        """The mounting face's height over the plate at y."""
        return self.cz - (y - self.cy) * T

    def b_at_height(self, z, n):
        return (z - self.cz - n * C) / S


def ellipse(ra, rb, count=720):
    t = np.linspace(0.0, 2.0 * math.pi, count, endpoint=False)
    return Polygon(np.c_[ra * np.cos(t), rb * np.sin(t)])


class Writer:
    """Relative-extrusion G-code with a tracked nozzle, for the courses this stage adds."""

    def __init__(self):
        self.out = []
        self.pos = None
        self.retracted = True
        self.feed = None
        self.time = 0.0
        self.filament = 0.0
        self.lengths = {}
        self.feature = None
        self.moves = []           # (kind, feature, x0, y0, z0, x1, y1, z1, width, height)

    def raw(self, text):
        self.out.append(text)

    def comment_feature(self, name, width):
        self.feature = name
        self.out.append(f"; FEATURE: {name}")
        self.out.append(f"; LINE_WIDTH: {width:.2f}")

    def _f(self, feed):
        return f" F{feed * 60.0:.0f}"

    def _line(self, target, e=None, feed=None, kind="travel", width=0.0, height=0.0):
        x, y, z = target
        words = []
        if self.pos is None or abs(x - self.pos[0]) > 5e-4:
            words.append(f"X{x:.3f}")
        if self.pos is None or abs(y - self.pos[1]) > 5e-4:
            words.append(f"Y{y:.3f}")
        if self.pos is None or abs(z - self.pos[2]) > 5e-4:
            words.append(f"Z{z:.3f}")
        if not words and e is None:
            return
        text = "G1 " + " ".join(words)
        if e is not None:
            text += f" E{e:.5f}"
        text += self._f(feed)
        self.out.append(text)
        if self.pos is not None:
            d = math.dist(self.pos, target)
            self.time += d / max(feed, 1e-6)
            self.moves.append((kind, self.feature, *self.pos, x, y, z, width, height))
            if e:
                self.lengths[self.feature] = self.lengths.get(self.feature, 0.0) + d
        if e:
            self.filament += e
        self.pos = (x, y, z)

    def retract(self):
        if not self.retracted:
            self.out.append(f"G1 E-{RETRACT:.1f} F1800")
            self.time += RETRACT / 30.0
            self.retracted = True

    def unretract(self):
        if self.retracted:
            self.out.append(f"G1 E{RETRACT:.1f} F1800")
            self.time += RETRACT / 30.0
            self.retracted = False

    def travel(self, target, lift=TRAVEL_LIFT, speed=150.0, hop=1.5):
        """Lift, cross and lower. Both ends stand `lift` over the course in hand, so the
        straight crossing does too. A crossing shorter than `hop` runs along the course."""
        if self.pos is None:
            self.out.append(f"G1 Z{target[2] + lift + 4.0:.3f} F1800")
            self.out.append(f"G1 X{target[0]:.3f} Y{target[1]:.3f} F{speed * 60:.0f}")
            self.pos = (target[0], target[1], target[2] + lift + 4.0)
            self._line(target, feed=20.0)
            return
        x0, y0, z0 = self.pos
        flat = math.hypot(target[0] - x0, target[1] - y0)
        if flat < hop and abs(target[2] - z0) < 0.5 and not self.retracted:
            self._line(target, feed=min(speed, 60.0))
            return
        self.retract()
        self._line((x0, y0, z0 + lift), feed=20.0)
        dz = abs(target[2] + lift - (z0 + lift))
        d = math.hypot(flat, dz)
        feed = speed if dz < 1e-9 else min(speed, Z_TRAVEL_RATE * d / dz)
        self._line((target[0], target[1], target[2] + lift), feed=feed)
        self._line(target, feed=20.0)

    def extrude(self, path, width, height, speed, flow=1.0, heights=None, flows=None):
        """Lay a bead along `path` (xyz points). `heights` gives each segment its own height and
        `flows` its own share of the flow."""
        self.unretract()
        for i in range(1, len(path)):
            a, b = path[i - 1], path[i]
            d = math.dist(a, b)
            if d < 1e-6:
                continue
            h = height if heights is None else heights[i - 1]
            share = 1.0 if flows is None else max(0.0, float(flows[i - 1]))
            dz = abs(b[2] - a[2])
            feed = speed if dz < 1e-9 else min(speed, Z_PRINT_RATE * d / dz)
            self._line(b, e=e_per_mm(width, h, flow * share) * d, feed=feed, kind="extrude", width=width, height=h)


def build_preamble(frame, regions, shoulder, object_label):
    """The scaffold, the roof, and the foot's sloped courses with their plugs and deck, as G-code.

    `regions` holds the base's section for each sloped course, lowest first. `shoulder` is the
    course that first lays the insert sockets' shoulders."""
    w = Writer()
    roof = ellipse(RIM[0] + LIP, RIM[1] + LIP)
    n_roof = [-AIR - COURSE * (ROOF_COURSES - 1 - i) for i in range(ROOF_COURSES)]   # tops, bottom course first
    n_scaffold = -AIR - COURSE * ROOF_COURSES           # the scaffold's ceiling
    face = regions[0]
    openings = sorted((Polygon(h) for h in face.interiors), key=lambda q: -q.area)
    bore, sockets = openings[0], openings[1:]
    deck = bore.buffer(-DECK_KERF)
    plugs = [s.buffer(-PLUG_CLEAR) for s in sockets]
    plug_top = shoulder - 2                              # the last course the plugs rise with
    count = len(regions)
    laid = {"ring_pieces": 0, "narrow_rings": 0, "fill_lines": 0}

    def limited(shape, n_top):
        """`shape` where a bead topped at n_top stands at least a first layer over the bed."""
        return shape.intersection(box(-200.0, frame.b_at_height(BED_MIN_Z, n_top), 200.0, 200.0))

    def to_xyz(points, n):
        return [frame.xyz(a, b, n) for a, b in points]

    w.raw("; ===== sloped underside of faucet-shell-base: scaffold, roof and foot =====")
    w.raw(object_label)
    w.raw("G90")
    w.raw("M83")
    w.raw("M106 S0")

    # ---- the scaffold, level layers under the roof's lowest course ---------------------------
    sx, sy = RIM[0] + LIP, (RIM[1] + LIP) * C
    y_centre = frame.cy + n_scaffold * S
    def span_x(y):
        r = 1.0 - ((y - y_centre) / sy) ** 2
        return None if r <= 0 else (frame.cx - sx * math.sqrt(r), frame.cx + sx * math.sqrt(r))
    def span_y(x):
        r = 1.0 - ((x - frame.cx) / sx) ** 2
        return None if r <= 0 else (y_centre - sy * math.sqrt(r), y_centre + sy * math.sqrt(r))
    layers = []
    z = FIRST_LAYER
    while True:
        nose = frame.cy - (frame.b_at_height(z, n_scaffold)) * C + n_scaffold * S    # the layer reaches back to here
        if nose - ROOF_WIDTH <= y_centre - sy:
            break
        layers.append((z, nose))
        z = round(z + LAYER, 6)
    w.raw("M204 S500")
    for index, (z, nose) in enumerate(layers):
        height = FIRST_LAYER if index == 0 else LAYER
        speed = 40.0 if index == 0 else 80.0
        if index == 1:
            w.raw("M104 S280 ; the plate's own second-layer temperature")
            w.raw("M204 S3000")
        w.comment_feature("Support", ROOF_WIDTH)
        back = min(nose - ROOF_WIDTH / 2.0, y_centre + sy - 0.05)
        paths = []
        # the outline in front of the nose, one arc from side to side
        if back > y_centre - sy + 0.5:
            t0 = math.asin(max(-1.0, min(1.0, (back - y_centre) / sy)))
            ts = np.linspace(math.pi - t0, 2.0 * math.pi + t0, max(8, int((math.pi + 2 * t0) * sx / 1.0)))
            arc = [(frame.cx + sx * math.cos(t), y_centre + sy * math.sin(t), z) for t in ts]
            paths.append(arc)
            # the nose, the chord that carries the roof's edge on this layer
            sp = span_x(back)
            if sp and sp[1] - sp[0] > 1.0:
                paths.append([(sp[1], back, z), (sp[0], back, z)])
        pitch = WALL_PITCH / 2.0 if index == 0 else WALL_PITCH
        walls = []
        for j in range(-int(sx // pitch), int(sx // pitch) + 1):
            x = frame.cx + j * pitch
            sp = span_y(x)
            if not sp:
                continue
            y0, y1 = sp[0] + ROOF_WIDTH / 2.0, min(sp[1] - ROOF_WIDTH / 2.0, back - ROOF_WIDTH / 2.0)
            if y1 - y0 > 1.0:
                walls.append([(x, y0, z), (x, y1, z)])
        for k, wall in enumerate(walls):
            paths.append(wall if k % 2 == 0 else wall[::-1])
        if index == 0 or index % 2 == 1:
            tie = TIE_PITCH / 2.0 if index == 0 else TIE_PITCH
            for k, y in enumerate(np.arange(y_centre - sy + tie / 2.0, back - 2.0, tie)):
                sp = span_x(y)
                if sp and sp[1] - sp[0] > 2.0:
                    line = [(sp[0] + ROOF_WIDTH / 2.0, y, z), (sp[1] - ROOF_WIDTH / 2.0, y, z)]
                    paths.append(line if k % 2 == 0 else line[::-1])
        for path in paths:
            w.travel(path[0], lift=0.6)
            w.extrude(path, ROOF_WIDTH, height, speed)
    scaffold_tops = [z for z, _ in layers]

    def top_below(y):
        """The scaffold's top under the roof at y, or the bed."""
        limit = frame.face(y) + n_scaffold / C
        best = 0.0
        for z in scaffold_tops:
            if z <= limit + 1e-6:
                best = z
        return best

    # ---- roof course 1: level lines across the slope, each on the scaffold under it ----------
    w.raw("M204 S2000")
    w.comment_feature("Support interface", ROOF_WIDTH)
    for a, b in level_order(hatch(limited(roof, n_roof[0]), 0.0, ROOF_WIDTH, shortest=1.0)):
        p0, p1 = frame.xyz(a[0], a[1], n_roof[0]), frame.xyz(b[0], b[1], n_roof[0])
        height = p0[2] - top_below(p0[1])
        assert 0.19 <= height <= COURSE / C + LAYER + 1e-6, height
        w.travel(p0, lift=0.5, hop=4.0)
        w.extrude([p0, p1], ROOF_WIDTH, height, 50.0)
    # ---- roof courses 2 and 3: lines up the slope, then diagonal. Each line climbs: coming
    # down, the nozzle's shoulder would ride on the bead it had just laid.
    for n_top, angle in ((n_roof[1], 90.0), (n_roof[2], 45.0)):
        for pieces in hatch(limited(roof, n_top), angle, ROOF_WIDTH, shortest=1.0):
            for a, b in pieces:
                path = to_xyz([a, b], n_top)
                w.travel(path[0])
                w.extrude(path, ROOF_WIDTH, COURSE, 40.0)

    def lay_pieces(pieces, n_top, width, speed, flow):
        for pts, flows in pieces:
            path = to_xyz(pts, n_top)
            shares = [(flows[i] + flows[i + 1]) / 2.0 for i in range(len(pts) - 1)]
            shares = [0.0 if s < 0.12 else s for s in shares]      # a whisker lays nothing worth having
            w.travel(path[0])
            w.extrude(path, width, COURSE, speed, flow=flow, flows=shares)

    def lay_lines(rows, n_top, angle, width, speed, flow):
        lines = level_order(rows) if angle == 0.0 else [line for pieces in rows for line in pieces]
        for a, b in lines:
            path = to_xyz([a, b], n_top)
            # from one level line to the next the nozzle runs along the course it is laying
            w.travel(path[0], hop=4.0 if angle == 0.0 else 1.5)
            w.extrude(path, width, COURSE, speed, flow=flow)
        return len(lines)

    def lay_course(region, n_top, angle, pitch, ring_speed, fill_speed, flow, ring_feature, fill_feature, lap=1.2):
        """One course of the foot: the rings its stock lies uphill of, the rings of its narrow
        strips, the fill, then the rings its stock lies downhill of."""
        if region.is_empty:
            return
        first, last = edge_pieces(region.buffer(-SKIN_WIDTH / 2.0), taper=lap)
        fill = region.buffer(-(SKIN_WIDTH + pitch / 2.0 - OVERLAP))
        if not fill.is_empty:
            fill = fill.buffer(-OPEN).buffer(OPEN).intersection(fill)
        narrow = narrow_pieces(region, SKIN_WIDTH, pitch, fill)
        w.comment_feature(ring_feature, SKIN_WIDTH)
        lay_pieces(first, n_top, SKIN_WIDTH, ring_speed, flow)
        lay_pieces(narrow, n_top, SKIN_WIDTH, ring_speed, flow)
        w.comment_feature(fill_feature, SKIN_WIDTH)
        laid["fill_lines"] += lay_lines(hatch(fill, angle, pitch, shortest=0.8), n_top, angle, SKIN_WIDTH, fill_speed, flow)
        w.comment_feature(ring_feature, SKIN_WIDTH)
        lay_pieces(last, n_top, SKIN_WIDTH, ring_speed, flow)
        laid["ring_pieces"] += len(first) + len(last)
        laid["narrow_rings"] += len(narrow)

    def lay_support(shape, n_top, angle, pitch):
        """One course of a plug or of the deck: a ring and lines inside it."""
        if shape.is_empty:
            return
        first, last = edge_pieces(shape.buffer(-ROOF_WIDTH / 2.0), taper=0.6)
        lay_pieces(first + last, n_top, ROOF_WIDTH, 30.0, 1.0)
        lay_lines(hatch(shape.buffer(-ROOF_WIDTH * 0.9), angle, pitch, shortest=0.8), n_top, angle, ROOF_WIDTH, 40.0, 1.0)

    # ---- the plugs and the deck start on the roof, level with the mounting face ---------------
    w.comment_feature("Support", ROOF_WIDTH)
    lay_support(limited(deck, 0.0), 0.0, 0.0, ROOF_WIDTH)
    for plug in plugs:
        lay_support(limited(plug, 0.0), 0.0, 0.0, ROOF_WIDTH)

    # ---- the foot, course by course, with the plugs and the deck rising beside it -------------
    w.raw("M204 S1000")
    for k in range(1, count + 1):
        n_top = k * COURSE
        region = regions[k - 1]
        angle = 90.0 if k % 2 == 1 else 0.0
        fill_speed = 40.0 if angle else 50.0
        w.raw(f"; sloped course {k} of {count}")
        if k == 1:
            # the first course crosses the roof's air as a bridge, as Support D lays it
            w.raw("M106 S178 ; the first course over air takes the bridge's fan")
            lay_course(region, n_top, 90.0, SKIN_PITCH, 15.0, 15.0, BRIDGE_FLOW, "Bottom surface", "Bottom surface", lap=0.5)
            w.raw("M106 S0")
        elif k == shoulder:
            # the sockets' shoulders cross the plugs' air the same way, after the rest of the course
            zone = unary_union([s.buffer(SHOULDER_REACH) for s in sockets])
            lay_course(region.difference(zone), n_top, angle, SKIN_WIDTH, 25.0, fill_speed, 1.0, "Outer wall", "Internal solid infill")
            w.raw("M106 S178 ; the shoulders over the plugs take the bridge's fan")
            lay_course(region.intersection(zone), n_top, 90.0, SKIN_PITCH, 15.0, 15.0, BRIDGE_FLOW, "Bridge", "Bridge", lap=0.5)
            w.raw("M106 S0")
        else:
            lay_course(region, n_top, angle, SKIN_WIDTH, 25.0, fill_speed, 1.05 if k == 2 else 1.0, "Outer wall", "Internal solid infill")
        w.comment_feature("Support", ROOF_WIDTH)
        lay_support(deck, n_top, angle, ROOF_WIDTH if k > count - 3 else 3.0 * ROOF_WIDTH)
        if k <= plug_top:
            for plug in plugs:
                lay_support(plug, n_top, angle, ROOF_WIDTH)
    # ---- leave above everything, retracted, as the plate's first layer expects ----------------
    w.retract()
    x, y, z = w.pos
    w._line((x, y, PARK_Z), feed=25.0)
    w.raw("M104 S265 ; the plate's first-layer temperature")
    w.raw("M625")
    w.raw("; ===== end of the sloped underside =====")
    planes = {"scaffold_ceiling": n_scaffold, "roof_tops": n_roof, "slab_top": count * COURSE,
              "shoulder_course": shoulder, "plug_top": plug_top * COURSE, "deck_top": count * COURSE}
    laid.update({"scaffold_layers": len(layers), "scaffold_top_mm": layers[-1][0], "sloped_courses": count})
    return w, planes, laid


# ------------------------------------------------------------------------------------------------
# The toolhead over what stands before the plate starts.

class Clearance:
    """The lowest the active tip may sit at each plate position with the toolhead clear of the
    finished scaffold, roof and skin."""

    def __init__(self, headmap, frame, slab_top, step=0.5):
        h = np.load(headmap)
        self.H, self.N = h["H"], h["N"]
        self.hs, self.hx0, self.hy0 = float(h["step"]), float(h["x0"]), float(h["y0"])
        assert abs(self.hs - step) < 1e-9
        self.step = step
        self.frame = frame
        # the terrain: the slab's top plane wherever the roof reaches. The lip and the bore's
        # deck stand at or under it.
        ra, rb = RIM[0] + LIP, RIM[1] + LIP
        self.tx0 = math.floor((frame.cx - ra - 1.0) / step) * step
        self.ty0 = math.floor((frame.cy - rb * C - 1.5) / step) * step
        nx = int(math.ceil((2 * ra + 2.0) / step)) + 1
        ny = int(math.ceil((2 * rb * C + 3.0) / step)) + 1
        xs = self.tx0 + np.arange(nx) * step
        ys = self.ty0 + np.arange(ny) * step
        X, Y = np.meshgrid(xs, ys)
        A = X - frame.cx
        B = (frame.cy - Y) / C
        inside = (A / ra) ** 2 + (B / rb) ** 2 <= 1.0
        top = frame.cz - (Y - frame.cy) * T + slab_top / C
        self.terrain = np.where(inside, np.maximum(top, 0.0), -np.inf)
        self.terrain_xy = (xs, ys)
        # the lowest tip height, for the head and for the nozzle's own flanks
        self.cx0 = self.tx0 - self.hx0 - (self.H.shape[1] - 1) * step      # nozzle x of the first column
        self.cy0 = self.ty0 - self.hy0 - (self.H.shape[0] - 1) * step
        cols = nx + self.H.shape[1] - 1
        rows = ny + self.H.shape[0] - 1
        self.head = np.full((rows, cols), -np.inf)
        self.nozzle = np.full((rows, cols), -np.inf)
        flank = self.N.copy()
        hy = self.hy0 + np.arange(self.N.shape[0]) * step
        hx = self.hx0 + np.arange(self.N.shape[1]) * step
        flank[np.hypot(hx[None, :], hy[:, None]) < NOZZLE_FLAT_R] = np.inf
        for target, source in ((self.head, self.H), (self.nozzle, flank)):
            iy, ix = np.nonzero(np.isfinite(source))
            for j, i in zip(iy, ix):
                # a head point at offset (dx, dy) over terrain cell (tx, ty) puts the nozzle at (tx - dx, ty - dy)
                r0 = (self.H.shape[0] - 1) - j
                c0 = (self.H.shape[1] - 1) - i
                view = target[r0:r0 + ny, c0:c0 + nx]
                np.maximum(view, self.terrain - source[j, i], out=view)

    def _sample(self, grid, x, y):
        i = np.round((np.asarray(x) - self.cx0) / self.step).astype(int)
        j = np.round((np.asarray(y) - self.cy0) / self.step).astype(int)
        ok = (i >= 0) & (i < grid.shape[1]) & (j >= 0) & (j < grid.shape[0])
        out = np.full(np.shape(x), -np.inf)
        out[ok] = grid[j[ok], i[ok]]
        return out

    def head_floor(self, x, y):
        return self._sample(self.head, x, y)

    def nozzle_floor(self, x, y):
        return self._sample(self.nozzle, x, y)

    def travel_floor(self, x0, y0, x1, y1):
        """The lowest a travel may run from (x0, y0) to (x1, y1)."""
        count = max(2, int(math.hypot(x1 - x0, y1 - y0) / (self.step * 0.8)) + 2)
        xs, ys = np.linspace(x0, x1, count), np.linspace(y0, y1, count)
        return float(np.max(np.maximum(self.head_floor(xs, ys) + HEAD_TRAVEL_MARGIN, self.nozzle_floor(xs, ys) + NOZZLE_TRAVEL_MARGIN)))

    def near(self, x, y):
        return (self.cx0 - 1.0 <= x <= self.cx0 + self.head.shape[1] * self.step + 1.0
                and self.cy0 - 1.0 <= y <= self.cy0 + self.head.shape[0] * self.step + 1.0)

    def crosses(self, x0, y0, x1, y1):
        """Whether a straight run between the two points can pass where the head reaches the scaffold."""
        lo_x, hi_x = self.cx0 - 1.0, self.cx0 + self.head.shape[1] * self.step + 1.0
        lo_y, hi_y = self.cy0 - 1.0, self.cy0 + self.head.shape[0] * self.step + 1.0
        return not (max(x0, x1) < lo_x or min(x0, x1) > hi_x or max(y0, y1) < lo_y or min(y0, y1) > hi_y)


# ------------------------------------------------------------------------------------------------
# The plate's own G-code, with the base kept above the skin.

WORD = re.compile(r"([XYZEFIJP])(-?\d*\.?\d+)")


def fmt(v):
    text = f"{v:.3f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


class Plate:
    def __init__(self, frame, clearance, base_id, slab_top):
        self.frame, self.clear, self.base_id = frame, clearance, base_id
        self.skin = slab_top / C                        # the slab's top over the face, vertical
        self.clip_until = frame.cz + (RIM[1] + LIP) * S + self.skin + 0.6
        self.out = []
        self.real = None            # the nozzle as the printer has it
        self.virtual = None         # the nozzle as the slicer's stream has it
        self.real_retracted = True
        self.virtual_retracted = True
        self.real_feed = None
        self.virtual_feed = None
        self.layer_z = self.layer_h = None
        self.object = None
        self.feature = None
        self.stats = {"kept_mm": 0.0, "dropped_mm": 0.0, "dropped_support_mm": 0.0, "lifted_travels": 0, "highest_lift_mm": 0.0,
                      "clipped_layers": 0, "feathered_mm": 0.0, "least_base_head_clearance_mm": math.inf, "least_other_head_clearance_mm": math.inf,
                      "rewritten_travels": 0}
        self._layer_clipped = False

    # -- emission helpers ----------------------------------------------------------------------
    def emit(self, text):
        self.out.append(text)

    def move(self, x, y, z, feed=None, e=None):
        words = []
        if self.real is None or abs(x - self.real[0]) > 5e-4:
            words.append("X" + fmt(x))
        if self.real is None or abs(y - self.real[1]) > 5e-4:
            words.append("Y" + fmt(y))
        if self.real is None or abs(z - self.real[2]) > 5e-4:
            words.append("Z" + fmt(z))
        if not words and e is None:
            return
        text = "G1 " + " ".join(words)
        if e is not None:
            text += f" E{e:.5f}"
        if feed is not None and feed != self.real_feed:
            text += f" F{feed:.0f}"
            self.real_feed = feed
        self.emit(text)
        self.real = (x, y, z)

    def set_retracted(self, want):
        if want and not self.real_retracted:
            self.emit(f"G1 E-{RETRACT:.1f} F1800")
            self.real_feed = 1800.0
        if not want and self.real_retracted:
            self.emit(f"G1 E{RETRACT:.1f} F1800")
            self.real_feed = 1800.0
        self.real_retracted = want

    def safe_travel(self, x, y, z, retract=True):
        """Carry the real nozzle to (x, y, z), over whatever the toolhead would otherwise meet."""
        x0, y0, z0 = self.real
        flat = math.hypot(x - x0, y - y0)
        if flat < 1e-4 and abs(z - z0) < 1e-4:
            return
        floor = self.clear.travel_floor(x0, y0, x, y) if self.clear.crosses(x0, y0, x, y) else -math.inf
        if flat <= 1.2 and abs(z - z0) < 1e-6 and z >= floor:
            self.move(x, y, z, feed=9000.0)
            return
        if retract:
            self.set_retracted(True)
        high = max(z0, z) + 0.4
        if floor > high:
            self.stats["lifted_travels"] += 1
            self.stats["highest_lift_mm"] = max(self.stats["highest_lift_mm"], floor)
            high = floor
        self.move(x0, y0, high, feed=1800.0)
        self.move(x, y, high, feed=60000.0)
        self.move(x, y, z, feed=1800.0)

    # -- the stream ------------------------------------------------------------------------------
    def clipping(self):
        return (self.object == self.base_id and self.layer_z is not None
                and self.layer_z - KEEP_FRACTION * self.layer_h < self.clip_until)

    def line(self, text):
        if text.startswith(";"):
            if text.startswith("; Z_HEIGHT:"):
                self.layer_z = float(text.split(":")[1])
                self._layer_clipped = False
            elif text.startswith("; LAYER_HEIGHT:"):
                self.layer_h = float(text.split(":")[1])
            elif text.startswith("; start printing object"):
                self.object = int(text.rsplit(":", 1)[1])
            elif text.startswith("; stop printing object"):
                if self.object == self.base_id:
                    self.set_retracted(self.virtual_retracted)
                self.object = None
            elif text.startswith("; FEATURE:"):
                self.feature = text.split(":", 1)[1].strip()
            self.emit(text)
            return
        head = text[:3]
        if head not in ("G1 ", "G0 ", "G2 ", "G3 "):
            self.emit(text)
            return
        w = {k: float(v) for k, v in WORD.findall(text.split(";", 1)[0])}
        vx, vy, vz = self.virtual
        tx, ty, tz = w.get("X", vx), w.get("Y", vy), w.get("Z", vz)
        e = w.get("E")
        moves_xy = abs(tx - vx) > 1e-9 or abs(ty - vy) > 1e-9
        if "F" in w:
            self.virtual_feed = w["F"]
        arc = head in ("G2 ", "G3 ")
        clip = self.clipping()
        if clip and not self._layer_clipped:
            self._layer_clipped = True
            self.stats["clipped_layers"] += 1
        # ---- no position words: the slicer's retract, unretract or a bare feed. A line that names
        # a position is a move even where the stream's nozzle already stands there, because the
        # real nozzle may not.
        if "X" not in w and "Y" not in w and "Z" not in w and not arc:
            if e is not None and abs(e) > 1e-9:
                self.virtual_retracted = e < 0
                if clip:
                    return                                   # this stage retracts for its own travels
                self.real_retracted = self.virtual_retracted
            self.real_feed = self.virtual_feed
            self.emit(text)
            return
        self.virtual = (tx, ty, tz)
        laying = ("X" in w or "Y" in w) and e is not None and e > 0
        if laying and not arc and clip:
            self._clipped_extrusion(vx, vy, vz, tx, ty, tz, e)
            return
        if e is not None and e < 0:
            self.virtual_retracted = True
        if clip:
            if laying:
                raise SystemExit("an arc lays plastic in a course of the base this stage cuts")
            return                                           # travel is made when the next kept bead needs it
        rx, ry, rz = self.real
        target = (w.get("X", rx), w.get("Y", ry), w.get("Z", rz))
        if laying:
            self._pass_extrusion(text, target)
        else:
            self._pass_travel(text, w, arc, target, e)

    def _pass_extrusion(self, text, target):
        self.real = target
        if math.dist(self.real, self.virtual) > 2e-3:
            raise SystemExit(f"the nozzle is not where the plate's course expects it: {self.real} against {self.virtual}")
        self.real_retracted = False
        self.real_feed = self.virtual_feed
        if self.clear.near(target[0], target[1]) and target[2] < PARK_Z:
            gap = target[2] - float(self.clear.head_floor(np.array([target[0]]), np.array([target[1]]))[0])
            key = "least_base_head_clearance_mm" if self.object == self.base_id else "least_other_head_clearance_mm"
            self.stats[key] = min(self.stats[key], gap)
        self.emit(text)

    def _pass_travel(self, text, w, arc, target, e):
        rx, ry, rz = self.real
        tx, ty, tz = target
        def passed():
            self.emit(text)
            self.real = target
            self.real_feed = self.virtual_feed
            if e is not None and e < 0:
                self.real_retracted = True
        if min(rz, tz) >= PARK_Z or not self.clear.crosses(rx, ry, tx, ty):
            passed()
            return
        if arc and "X" not in w and "Y" not in w:
            # a spiral lift: beside the scaffold it becomes a plain lift
            self.move(rx, ry, max(tz, rz), feed=1800.0)
            if self.virtual_feed is not None and self.real_feed != self.virtual_feed:
                self.emit(f"G1 F{self.virtual_feed:.0f}")
                self.real_feed = self.virtual_feed
            return
        floor = self.clear.travel_floor(rx, ry, tx, ty)
        if min(rz, tz) >= floor:
            passed()
            return
        if arc:
            raise SystemExit("an arc travels low beside the scaffold")
        # the travel would run low over the scaffold: rise where it stands, cross, then come down
        end_floor = self.clear.travel_floor(tx, ty, tx, ty)
        if tz < end_floor:
            raise SystemExit(f"a travel ends {end_floor - tz:.2f} mm low at X{tx:.2f} Y{ty:.2f} Z{tz:.2f} (object {self.object})")
        self.stats["rewritten_travels"] += 1
        self.stats["lifted_travels"] += 1
        self.stats["highest_lift_mm"] = max(self.stats["highest_lift_mm"], floor)
        if e is not None and e < 0:
            self.emit(f"G1 E{e:.5f} F1800")
            self.real_retracted = True
        high = max(rz, tz, floor)
        self.move(rx, ry, high, feed=1800.0)
        self.move(tx, ty, high, feed=w.get("F", 60000.0))
        self.move(tx, ty, tz, feed=1800.0)
        if self.virtual_feed is not None and self.real_feed != self.virtual_feed:
            self.emit(f"G1 F{self.virtual_feed:.0f}")
            self.real_feed = self.virtual_feed

    def _clipped_extrusion(self, x0, y0, z0, x1, y1, z1, e):
        length = math.hypot(x1 - x0, y1 - y0)
        f = self.frame
        if self.feature and self.feature.startswith("Support"):
            # the trees inside the base stand on the bore's deck, level with the slab's top
            ym = (y0 + y1) / 2.0
            if z1 - self.layer_h < f.face(ym) + self.skin - 0.05:
                self.stats["dropped_support_mm"] += length
                return
            parts = [(0.0, 1.0, 1.0)]
        else:
            # The bead is laid where it has room over the slab, with as much plastic as the room
            # takes: all of it where the slab is under the course, less and less as the slab
            # rises through the course, none where under FEATHER_MIN of the bead is left.
            under = self.layer_z - self.layer_h
            room0 = z0 - (f.face(y0) + self.skin)
            room1 = z1 - (f.face(y1) + self.skin)
            bead0, bead1 = max(z0 - under, 1e-6), max(z1 - under, 1e-6)
            lo, hi = 0.0, 1.0
            for g0, g1 in ((room0 - FEATHER_MIN * bead0, room1 - FEATHER_MIN * bead1), (room0 - NOZZLE_OVER_SKIN, room1 - NOZZLE_OVER_SKIN)):
                if g0 < 0 and g1 < 0:
                    self.stats["dropped_mm"] += length
                    return
                if g0 < 0:
                    lo = max(lo, g0 / (g0 - g1))
                if g1 < 0:
                    hi = min(hi, g0 / (g0 - g1))
            if (hi - lo) * length < 0.05:
                self.stats["dropped_mm"] += length
                return
            self.stats["dropped_mm"] += (1.0 - (hi - lo)) * length
            full0, full1 = room0 - bead0, room1 - bead1
            if full0 >= 0 and full1 >= 0:
                whole = (lo, hi)
            elif full0 < 0 and full1 < 0:
                whole = None
            else:
                at = full0 / (full0 - full1)
                whole = (max(lo, at), hi) if full0 < 0 else (lo, min(hi, at))
                if whole[1] - whole[0] <= 1e-9:
                    whole = None
            parts = []
            def thin(ta, tb):
                steps = max(1, int(math.ceil((tb - ta) * length / 0.25)))
                for i in range(steps):
                    u0, u1 = ta + (tb - ta) * i / steps, ta + (tb - ta) * (i + 1) / steps
                    um = (u0 + u1) / 2.0
                    share = (room0 + (room1 - room0) * um) / (bead0 + (bead1 - bead0) * um)
                    parts.append((u0, u1, min(1.0, max(0.0, share))))
                self.stats["feathered_mm"] += (tb - ta) * length
            if whole is None:
                thin(lo, hi)
            else:
                if whole[0] - lo > 1e-9:
                    thin(lo, whole[0])
                parts.append((whole[0], whole[1], 1.0))
                if hi - whole[1] > 1e-9:
                    thin(whole[1], hi)
        for u0, u1, share in parts:
            sx, sy, sz = x0 + (x1 - x0) * u0, y0 + (y1 - y0) * u0, z0 + (z1 - z0) * u0
            ex, ey, ez = x0 + (x1 - x0) * u1, y0 + (y1 - y0) * u1, z0 + (z1 - z0) * u1
            if math.hypot(sx - self.real[0], sy - self.real[1]) > 1e-3 or abs(sz - self.real[2]) > 1e-4:
                self.safe_travel(sx, sy, sz)
            self.set_retracted(False)
            gap = ez - float(self.clear.head_floor(np.array([ex]), np.array([ey]))[0])
            self.stats["least_base_head_clearance_mm"] = min(self.stats["least_base_head_clearance_mm"], gap)
            self.stats["kept_mm"] += (u1 - u0) * length
            self.move(ex, ey, ez, feed=self.virtual_feed, e=e * (u1 - u0) * share)


def rewrite(lines, frame, clearance, base_id, slab_top, preamble):
    """The stream with the preamble before its first layer's first object and the base clipped."""
    plate = Plate(frame, clearance, base_id, slab_top)
    first_layer = next(i for i, l in enumerate(lines) if l.startswith("; CHANGE_LAYER"))
    insert = next(i for i in range(first_layer, len(lines)) if lines[i].startswith("; OBJECT_ID:"))
    end = next(i for i, l in enumerate(lines) if l.startswith("; MACHINE_END_GCODE_START"))
    for l in lines[first_layer:insert]:
        if l.startswith("; Z_HEIGHT:"):
            plate.layer_z = float(l.split(":")[1])
        elif l.startswith("; LAYER_HEIGHT:"):
            plate.layer_h = float(l.split(":")[1])
    # where the start sequence leaves the stream's nozzle; the real one leaves the preamble parked
    pos = [None, None, None]
    for l in lines[:insert]:
        if l[:3] in ("G1 ", "G0 "):
            w = {k: float(v) for k, v in WORD.findall(l.split(";", 1)[0])}
            for k, name in enumerate("XYZ"):
                if name in w:
                    pos[k] = w[name]
    out = list(lines[:insert])
    out.extend(preamble.out)
    plate.real = preamble.pos
    plate.virtual = tuple(pos)
    plate.real_retracted = plate.virtual_retracted = True
    plate.out = out
    for l in lines[insert:end]:
        plate.line(l)
    out.extend(lines[end:])
    return out, plate.stats


def main():
    archive, report_path, stl, headmap, out_dir = sys.argv[1:6]
    report = json.load(open(report_path))
    seat = report["base_rim_supports"]["seat_print_world_center_mm"]
    normal = report["base_rim_supports"]["seat_print_world_outward_normal"]
    assert abs(normal[0]) < 1e-9 and abs(normal[1] + S) < 1e-6 and abs(normal[2] + C) < 1e-6, "the seat is not turned 15 degrees about X"
    base_id = next(p["identify_id"] for p in report["parts"] if p["name"] == "faucet-shell-base")
    frame = Frame(seat)
    # the base's sections up past the sockets' shoulders: the shoulder is the first course whose
    # small openings have closed down to the inserts' pilots
    probe = sections(stl, COURSE, 24)
    def small(region):
        return sorted(Polygon(h).area for h in region.interiors)[:-1]
    sockets = small(probe[0])
    assert len(sockets) == 3, "the mounting face does not open on three insert sockets"
    shoulder = next(k for k, region in enumerate(probe, 1) if max(small(region)) < 0.6 * min(sockets))
    regions = probe[:shoulder + COURSES_OVER_SHOULDER]
    slab_top = len(regions) * COURSE
    reach = max(max(abs(r.bounds[0]), abs(r.bounds[2])) for r in regions), max(max(abs(r.bounds[1]), abs(r.bounds[3])) for r in regions)
    assert reach[0] + SKIN_WIDTH < RIM[0] + LIP and reach[1] + SKIN_WIDTH < RIM[1] + LIP, "the foot's courses reach past the roof's lip"
    with zipfile.ZipFile(archive) as z:
        gcode = z.read("Metadata/plate_1.gcode").decode()
    lines = gcode.split("\n")
    start = next(i for i, l in enumerate(lines) if l.startswith(f"; start printing object, unique label id: {base_id}"))
    label = lines[start + 1]
    assert label.startswith("M624 "), label
    preamble, planes, laid = build_preamble(frame, regions, shoulder, label)
    clearance = Clearance(headmap, frame, slab_top)
    out, stats = rewrite(lines, frame, clearance, base_id, slab_top, preamble)
    text = "\n".join(out)
    os.makedirs(out_dir, exist_ok=True)
    name = os.path.basename(archive)
    with open(os.path.join(out_dir, "plate_1.gcode"), "w") as f:
        f.write(text)
    data = text.encode()
    with zipfile.ZipFile(archive) as src, zipfile.ZipFile(os.path.join(out_dir, name), "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            payload = src.read(item.filename)
            if item.filename == "Metadata/plate_1.gcode":
                payload = data
            elif item.filename == "Metadata/plate_1.gcode.md5":
                payload = hashlib.md5(data).hexdigest().encode()
            dst.writestr(item, payload)
    np.savez_compressed(os.path.join(out_dir, "preamble-moves.npz"),
                        moves=np.array([(0 if m[0] == "travel" else 1, *m[2:]) for m in preamble.moves], float),
                        features=np.array([m[1] or "" for m in preamble.moves]))
    record = {
        "purpose": "Binds the Sculpted base's sloped foot to the courses this stage laid and what it kept of the plate.",
        "input_archive": {"path": archive, "sha256": hashlib.sha256(open(archive, "rb").read()).hexdigest()},
        "gcode_sha256": hashlib.sha256(data).hexdigest(),
        "seat_center_mm": seat, "tilt_x_degrees": -15,
        "stack_normal_mm": {"course": COURSE, "air_asked": AIR, "roof_courses": ROOF_COURSES, **planes},
        "roof_lip_mm": LIP, "laid": laid,
        "preamble": {"seconds": round(preamble.time, 1), "filament_mm": round(preamble.filament, 2),
                     "extrusion_mm_by_feature": {k: round(v, 1) for k, v in preamble.lengths.items()}},
        "plate": {k: (round(v, 3) if isinstance(v, float) and math.isfinite(v) else (None if isinstance(v, float) else v)) for k, v in stats.items()},
        "limits": {"z_while_printing_mm_s": Z_PRINT_RATE, "z_while_travelling_mm_s": Z_TRAVEL_RATE,
                   "head_travel_margin_mm": HEAD_TRAVEL_MARGIN, "nozzle_travel_margin_mm": NOZZLE_TRAVEL_MARGIN,
                   "least_share_of_a_level_course_laid": FEATHER_MIN, "nozzle_over_slab_mm": NOZZLE_OVER_SKIN},
    }
    json.dump(record, open(os.path.join(out_dir, "sloped-underside.json"), "w"), indent=2)
    print(json.dumps({k: record[k] for k in ("stack_normal_mm", "laid", "preamble", "plate")}, indent=1))


if __name__ == "__main__":
    main()
