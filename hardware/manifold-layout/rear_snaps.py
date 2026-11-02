"""The seats on back-top that the ASSE chain, the Pisco and the flow meter slide into, and the snap
caps that hold each in its seat.

Back-top is inverted on the bench. Each part drops into its seat SLIDE ahead of its station and
slides aft until its nose is through the rear wall; the meter slides aft onto the soda union's
stub. A seat is one block, the part's upper side cut into it, swept forward by SLIDE so the part
passes every station on its way. A snap cap then holds the part's other side at its station: one
half pipe under the part, its two side walls rising past the part's axis as the springs, each
hooking over a ledge in a pocket in the seat's flank. Each pocket's ends are the cap's end
shoulders. The ASSE's seat stands down to the body's axis, through its wrenches' side corners, and
its cap is the lower half of a hex pipe about them, so the two hold the wrenches' flats. The ASSE's
and the Pisco's caps go on from below. The meter's is the same snap turned a quarter about Y and
goes on from the west.

World frame: -Y fore, +Z up, +X east.
"""
import json
import math
from pathlib import Path

import numpy as np
import cadquery as cq

import fits

SLIDE = 16.0        # the aft travel that puts the PP010822E's and the Pisco's noses through the wall
THREAD = 1.5        # how far a taped joint may leave the ASSE body from its drawn station, either way
WALL = 3.0
SPLIT = 335.0       # the Pisco's seat, and lines.py's regulator seat, stand down to here
INTO = 0.5          # how far each seat runs into the walls it joins
WING = 2.0          # intermediate section from the physical bending trial
REACH = 2.6         # flat horizontal bearing beyond the receiver edge
SIDE = 0.5         # relaxed spring face off the receiver edge
FREE_LENGTH = 22.25 # root to hook underside; retains the tested receiver bearing plane
ROOT_RADIUS = 1.5  # broad inside transition into each spring wall
PRY_WIDTH = 5.0    # centered flathead access across the hook's underside
PRY_HEIGHT = 1.0
REAR_ROOT_DROP = 10.0
PISCO_RADIAL_RELIEF = 0.25  # receiver running air plus this radial relief
PISCO_CAP_AIR = 0.4
METER_AIR = 0.75    # drop-in hardware clearance on the square housing and flange
METER_BACK = 9.0    # solid spine between the complete upper and lower leaves
METER_CAP_AIR = 0.25
METER_BEARING_DEPTH = 4.0
LEDGE = 3.0         # the ledge's height off the split
HOOK = 2.6          # leading ramp above the complete flat retaining face
NOSE_LAND = 0.6     # solid inner edge below the insertion ramp
CATCH = fits.clearance(supported=True)
VAR = 0.5           # how far the stub's seat in the soda union may leave the meter aft of its station

CHAIN = ('jg-pp010822e', 'gagira-coupling', 'multiplex-asse1022', 'jg-pi4512f6s', 'jg-pp061208w')
SOLIDS = ('asse-seat', 'asse-snap-cap', 'pisco-seat', 'pisco-snap-cap', 'meter-seat', 'meter-snap-cap')
SEATS = SOLIDS[0::2]
CAPS = SOLIDS[1::2]
# The way each cap goes on, as a unit vector in the world: up from below, or east from the west.
ON = {'asse-snap-cap': (0., 0., 1.), 'pisco-snap-cap': (0., 0., 1.), 'meter-snap-cap': (1., 0., 0.)}


# --- swept cavities -------------------------------------------------------------------------------

def surface_points(shape, step=0.2):
    vs, ts = shape.tessellate(0.02, 0.1)
    vs = np.array([(q.x, q.y, q.z) for q in vs])
    tri = vs[np.array(ts)]
    a, b, c = tri[:, 0], tri[:, 1], tri[:, 2]
    n = np.ceil(0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1) / step ** 2).astype(int)
    i = np.repeat(np.arange(len(tri)), n)
    rng = np.random.default_rng(1)
    r1, r2 = np.sqrt(rng.random(len(i)))[:, None], rng.random(len(i))[:, None]
    return np.concatenate([(1 - r1) * a[i] + r1 * (1 - r2) * b[i] + r1 * r2 * c[i], vs])


def envelope(points, axis, lo, hi, step=0.1):
    """The largest radius about `axis` (x, z) in each `step` of Y from lo to hi."""
    ys = np.arange(lo, hi, step)
    r = np.zeros(len(ys))
    k = np.floor((points[:, 1] - lo) / step).astype(int)
    ok = (k >= 0) & (k < len(ys))
    np.maximum.at(r, k[ok], np.hypot(points[ok, 0] - axis[0], points[ok, 2] - axis[1]))
    return ys, r


def swept(r, behind, ahead, step=0.1):
    """Each station's radius covers whatever can pass it: anything from `behind` fore of it to
    `ahead` aft of it."""
    a, b = int(round(behind / step)), int(round(ahead / step))
    return np.array([r[max(0, i - a):min(len(r), i + b + 1)].max() for i in range(len(r))])


def steps(ys, r, tol=0.2, step=0.1, shortest=1.5):
    """Plain cylinders over a swept profile: runs whose radii stay within `tol`, each at its
    largest. A run shorter than `shortest` joins its larger neighbour."""
    out, i = [], 0
    while i < len(r):
        if r[i] <= 0:
            i += 1
            continue
        j, lo, hi = i, r[i], r[i]
        while j + 1 < len(r) and r[j + 1] > 0 and max(hi, r[j + 1]) - min(lo, r[j + 1]) <= tol:
            j += 1
            lo, hi = min(lo, r[j]), max(hi, r[j])
        out.append([ys[i], ys[j] + step, hi])
        i = j + 1
    merged = [out[0]]
    for y0, y1, rr in out[1:]:
        if abs(merged[-1][1] - y0) < 1e-6 and abs(merged[-1][2] - rr) < 1e-6:
            merged[-1][1] = y1
        else:
            merged.append([y0, y1, rr])
    while len(merged) > 1:
        i = min(range(len(merged)), key=lambda k: merged[k][1] - merged[k][0])
        if merged[i][1] - merged[i][0] >= shortest:
            break
        j = (i - 1 if i == len(merged) - 1 or (i > 0 and merged[i - 1][2] >= merged[i + 1][2]) else i + 1)
        lo, hi = min(i, j), max(i, j)
        merged[lo:hi + 1] = [[merged[lo][0], merged[hi][1], max(merged[lo][2], merged[hi][2])]]
        k = 0
        while k + 1 < len(merged):
            if abs(merged[k][2] - merged[k + 1][2]) < 1e-9:
                merged[k:k + 2] = [[merged[k][0], merged[k + 1][1], merged[k][2]]]
            else:
                k += 1
    return [tuple(float(v) for v in m) for m in merged]


def turned(profile, axis):
    """One solid of revolution about the Y line through `axis`, from (y0, y1, r) runs."""
    pts = [(profile[0][0], 0.)]
    for y0, y1, r in profile:
        pts += [(y0, r), (y1, r)]
    pts.append((profile[-1][1], 0.))
    clean = [pts[0]]
    for p in pts[1:]:
        if abs(p[0] - clean[-1][0]) > 1e-9 or abs(p[1] - clean[-1][1]) > 1e-9:
            clean.append(p)
    solid = cq.Workplane('XY').polyline(clean).close().revolve(360, (0, 0, 0), (1, 0, 0)).val()
    return solid.rotate((0, 0, 0), (0, 0, 1), 90).translate((axis[0], 0., axis[1]))


def hex_prism(axis, apothem, clock_deg, y0, y1, corner):
    """A wrench prism along Y with its corners clipped round at `corner`; clock 0 stands a corner
    straight down."""
    rr = apothem / math.cos(math.pi / 6)
    pts = [cq.Vector(axis[0] + rr * math.sin(math.radians(clock_deg + 60 * i)), y0,
                     axis[1] - rr * math.cos(math.radians(clock_deg + 60 * i))) for i in range(6)]
    prism = cq.Solid.extrudeLinear(cq.Wire.makePolygon(pts, close=True), [], cq.Vector(0, y1 - y0, 0))
    return prism.intersect(cq.Solid.makeCylinder(corner, y1 - y0, cq.Vector(axis[0], y0, axis[1]), cq.Vector(0, 1, 0)))


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0))


def stadium_x(yc, zc, r, fore, aft, x0, x1):
    """A circle in YZ swept fore and aft along Y, extruded along X."""
    a, b = yc - fore, yc + aft
    w = (cq.Workplane('YZ', origin=(x0, 0, 0)).moveTo(a, zc - r).lineTo(b, zc - r)
         .threePointArc((b + r, zc), (b, zc + r)).lineTo(a, zc + r)
         .threePointArc((a - r, zc), (a, zc - r)).close())
    return w.extrude(x1 - x0).val()


def half_width(radius, z, axis_z):
    return math.sqrt(max(radius ** 2 - (z - axis_z) ** 2, 0.))


# --- one snap station -----------------------------------------------------------------------------

def station(axis_x, neck, y0, y1, split=SPLIT, *, wing_root=None, free_length=FREE_LENGTH):
    """A cap station's flank numbers, from the seat's neck half-width and the cap's Y span."""
    ledge = neck + REACH + fits.running
    inner = ledge + SIDE
    root = split if wing_root is None else wing_root
    catch = max(root + free_length, split + LEDGE + CATCH)
    bearing = catch - CATCH
    tip = catch + HOOK
    return dict(axis_x=axis_x, y0=y0, y1=y1, split=split, neck=neck, ledge=ledge, inner=inner,
                outer=inner + WING, hook=ledge - REACH, bearing=bearing, catch=catch, tip=tip,
                ceiling=tip + 2 * fits.running, root=root, nose_land=NOSE_LAND,
                root_radius=ROOT_RADIUS,pry_width=PRY_WIDTH,pry_height=PRY_HEIGHT)


def pry_bounds(s):
    """Two centered blade entries under the hooks; spring walls remain continuous."""
    middle=(s['y0']+s['y1'])/2.
    return [(*sorted((s['axis_x']+side*(s['hook']-.1),
                      s['axis_x']+side*s['inner'])),
             middle-PRY_WIDTH/2.,middle+PRY_WIDTH/2.,
             s['catch']-.1,s['catch']+PRY_HEIGHT) for side in (-1.,1.)]


def pry_cuts(s):
    return [box(*bounds) for bounds in pry_bounds(s)]


def clearance_profile(profile, radial, axial, tolerance=.06):
    """A short outward line profile with the measured shoulders retained.

    The axial window supplies fit air. Chord reduction stays outside that
    envelope and adds no more than `tolerance` radial air; short shoulders
    are not merged into a neighboring large cylinder.
    """
    profile=np.array(profile,float)
    x,r=profile[:,0],profile[:,1]
    stations=np.unique(np.concatenate((x-axial,x+axial)))
    rows=[]
    for t in stations:
        within=r[(x>=t-axial-1.e-8)&(x<=t+axial+1.e-8)]
        end=np.interp((t-axial,t+axial),x,r)
        rows.append((float(t),float(max(*end,*within)+radial)))
    points=np.array(rows)
    kept=[0];i=0
    while i<len(points)-1:
        best=i+1
        for j in range(i+2,len(points)):
            line=np.interp(points[i:j+1,0],points[[i,j],0],points[[i,j],1])
            extra=line-points[i:j+1,1]
            if extra.min()>=-1.e-8 and extra.max()<=tolerance:best=j
        kept.append(best);i=best
    return points[kept].tolist()


def radial_profile(points):
    """A linear radius profile revolved about native +X."""
    path=[(points[0][0],0.),*map(tuple,points),(points[-1][0],0.)]
    return cq.Workplane('XY').polyline(path).close().revolve(360,(0,0,0),(1,0,0)).val()


def pisco_grip_stock(s, axis_z, body_r, neck_r, lip):
    """One broad body saddle and a raised outlet-neck lip between free springs."""
    half=s['inner']-ROOT_RADIUS-.5
    bottom=axis_z-body_r-WALL
    top=axis_z-math.sqrt(max(body_r**2-(half-WALL)**2,0.))
    return [(s['axis_x']-half,s['axis_x']+half,s['y0'],s['y1'],bottom,top),
            (s['axis_x']-half,s['axis_x']+half,s['y0'],lip,bottom,axis_z)]


def pockets(s):
    """Both flank pockets of one station, cut from its seat: beside the ledge from the split to
    the bearing plane, beside the neck above it to the pocket's ceiling. The station's ends are
    the cap's shoulders."""
    out, a = [], fits.running
    for side in (-1., 1.):
        far = s['axis_x'] + side * (s['outer'] + 1.)
        ledge, neck = s['axis_x'] + side * s['ledge'], s['axis_x'] + side * s['neck']
        out.append(box(*sorted((ledge, far)), s['y0'] - a, s['y1'] + a, s['split'] - 1., s['bearing']))
        out.append(box(*sorted((neck, far)), s['y0'] - a, s['y1'] + a, s['bearing'], s['ceiling']))
        radius=s.get('root_radius',ROOT_RADIUS)
        near=s['axis_x']+side*(s['inner']-radius-a)
        out.append(box(*sorted((near,far)),s['y0']-a,s['y1']+a,
                       s['root']-a,s['root']+radius+a))
    return out


def pisco_cap_service_cuts(s):
    """Open the fore flank exits below the retained hook-bearing plane.

    A released cap lowers 3.6 mm and slides forward with its leaves open.
    The complete fore stops above the bearing plane retain the seated cap.
    """
    half=s['outer']+3.2+fits.running
    return [box(s['axis_x']-half,s['axis_x']+half,
        s['y0']-fits.running-WALL-1.,s['y0']+fits.running,
        s['split']-1.,s['bearing'])]


def pisco_station(axis_x, admitted_radius, axis_z, y0, y1):
    """Full 3 mm receiver walls beside the widened hardware passage."""
    web=WALL-REACH-fits.running
    return station(axis_x,half_width(admitted_radius,SPLIT,axis_z)+web,
                   y0,y1,wing_root=axis_z-REAR_ROOT_DROP)


def cap_section(s, base, bottom, axis_z=None, hexed=False):
    """A cap's line/arc section in X/Z, with its Y span, independent of a CAD kernel."""
    c, W, wi, h = s['axis_x'], s['outer'], s['inner'], s['hook']
    catch, tip = s['catch'], s['tip']

    def run(points):
        return [{'line':(p,q)} for p,q in zip(points,points[1:])]

    root = s.get('root', base if axis_z is None else axis_z)
    base = min(base, root)
    radius=s.get('root_radius',ROOT_RADIUS)
    west = [(c - W, root), (c - W, tip), (c - wi, tip),
            (c - h, catch+s['nose_land']),
            (c - h, catch), (c - wi, catch), (c - wi, base+radius)]
    east = [(2 * c - x, z) for x, z in reversed(west)]
    a,b=(c-wi+radius,base),(c+wi-radius,base)
    k=radius/math.sqrt(2.)
    edges=run(west)+[{'arc':(west[-1],(c-wi+radius-k,base+radius-k),a,
                           (c-wi+radius,base+radius)),'ccw':True}]
    edges+=run([a,b])+[{'arc':(b,(c+wi-radius+k,base+radius-k),east[0],
                             (c+wi-radius,base+radius)),'ccw':True}]+run(east)
    if axis_z is None:
        edges += run([east[-1], (c + W, bottom), (c - W, bottom), west[0]])
    elif hexed:
        low = axis_z - W * math.sqrt(3.) / 2.
        edges += run([east[-1], (c + W / 2., low), (c - W / 2., low), west[0]])
    else:
        r = axis_z - bottom
        z = root-axis_z
        distance2 = W*W+z*z
        tangent = r*math.sqrt(max(distance2-r*r, 0.))/distance2
        tx, tz = r*r*W/distance2 + tangent*z, r*r*z/distance2 - tangent*W
        edges += run([east[-1], (c + tx, axis_z + tz)])
        edges.append({'arc':((c + tx, axis_z + tz),(c,bottom),
                             (c - tx, axis_z + tz),(c,axis_z))})
        edges += run([(c - tx, axis_z + tz), west[0]])
    return {'segments':edges, 'span':(s['y0'],s['y1'])}


def section_solid(section):
    """Extrude the shared line/arc cap section without changing its boundaries."""
    def v(p):
        return cq.Vector(p[0],section['span'][0],p[1])
    edges = []
    for segment in section['segments']:
        if 'line' in segment:
            p,q = segment['line']
            edges.append(cq.Edge.makeLine(v(p),v(q)))
        else:
            a,mid,b,_centre = segment['arc']
            edges.append(cq.Edge.makeThreePointArc(v(a),v(mid),v(b)))
    return cq.Solid.extrudeLinear(cq.Wire.assembleEdges(edges), [],
        cq.Vector(0.,section['span'][1]-section['span'][0],0.))


def cap(s, base, bottom, axis_z=None, hexed=False):
    """One cap extruded over its station: two spring walls over a flat, round or hex body."""
    body=section_solid(cap_section(s,base,bottom,axis_z,hexed))
    return body.cut(*pry_cuts(s))


def at_world(location, point):
    return np.array(cq.Vertex.makeVertex(*point).moved(location).Center().toTuple())


# --- the three seats and their caps -----------------------------------------------------------------

def build(parts, asse_axis, asse_at, asse_turn, pisco_axis, mouth_y, ceiling, rear, side, meter, meter_at):
    """The six solids against the placed parts, and the numbers they were built from.

    `parts` maps names to (solid, colour) in appliance coordinates; `asse_at` is the chain's
    location and `asse_turn` the degrees the ASSE body turns about its axis from it, its wrenches'
    clock with it; `meter_at` is the meter's location and `meter` its reference module; `ceiling`,
    `rear` and `side` are the inner faces of the roof, the rear wall's land and the side wall."""
    import multiplex_asse1022 as bfp
    HW = Path(__file__).resolve().parent.parent
    pts = {n: surface_points(parts[n][0]) for n in (*CHAIN, *(n for n in parts if n.startswith('pisco-')), 'co2-check')}
    LO, HI = 370., 482.
    c, s = fits.running, fits.slip
    out, numbers = {}, {}

    # --- ASSE: the GAGIRA stops on the land; the body may sit THREAD either way of it ---------------
    ys, r_g = envelope(np.concatenate([pts['gagira-coupling'], pts['jg-pp010822e']]), asse_axis, LO, HI)

    def wrench(profile, across_flats, clock):
        """A wrench's Y span, apothem, clock and corner radius, as multiplex_asse1022.build() cuts it
        and the assembly turns it."""
        y = sorted(float(at_world(asse_at, (x, 0., bfp.BODY_CENTER_Z))[1]) for x in (profile[0][0], profile[-1][0]))
        return y, across_flats / 2., clock + asse_turn, max(r for _, r in profile)

    wrenches = (wrench(bfp.BODY_PROFILE, bfp.HEX_ACROSS_FLATS, .3), wrench(bfp.CAP_PROFILE, bfp.CAP_ACROSS_FLATS, .9))
    # Use the sampled round cavity's axial stations for the wrench ends as
    # well. Round outward so the fitted clearance never decreases, and the
    # two cuts meet on one end plane rather than leaving a sub-grid step.
    wrench_rooms = [(math.floor((y0-THREAD)*10.)/10.,
                     math.ceil((y1+THREAD)*10.)/10., a, k, r)
                    for (y0,y1),a,k,r in wrenches]
    asse = pts['multiplex-asse1022']
    # The vent hangs from the main wrench's bottom flat: the cap's slot passes it, the seat's sweep
    # leaves it out.
    under = asse_axis[1] - bfp.HEX_ACROSS_FLATS / 2. - .5
    vent, asse = asse[asse[:, 2] < under], asse[asse[:, 2] >= under]
    rr = np.hypot(asse[:, 0] - asse_axis[0], asse[:, 2] - asse_axis[1])
    keep = np.ones(len(asse), bool)
    for (y0, y1), apothem, _, _ in wrenches:      # each wrench is its own prism
        keep &= (asse[:, 1] <= y0) | (asse[:, 1] >= y1) | (rr <= apothem)
    body = np.concatenate([asse[keep], pts['jg-pi4512f6s']])
    _, r_b = envelope(body, asse_axis, LO, HI)
    cav = np.maximum(swept(r_g, 0., SLIDE), swept(r_b, THREAD, SLIDE + THREAD))
    cav = np.where(cav > 0, cav + c, 0.)
    asse_steps = steps(ys, cav)
    # One hex half pipe from the outlet bonnet's full round to the GAGIRA's fore face, which it bears
    # on. The seat stands down to the body's axis.
    bonnet = max(x for x, r in bfp.CAP_PROFILE if r == max(r for _, r in bfp.CAP_PROFILE))
    gag_fore = parts['gagira-coupling'][0].BoundingBox().ymin
    cap_y = (float(at_world(asse_at, (bonnet, 0., bfp.BODY_CENTER_Z))[1]) - s, gag_fore - s)
    split = asse_axis[1] + c
    m = (ys >= cap_y[0] - .25) & (ys <= cap_y[1] + .25)
    widest = max(cav[m].max(), *(corner + c for *_, corner in wrenches))
    st_a = station(asse_axis[0], half_width(widest, split, asse_axis[1]) + WALL,
                   *cap_y, split=split, wing_root=asse_axis[1]-REAR_ROOT_DROP)
    # The cap's room: the body's lower round swept by the thread either way, head on; both wrenches'
    # lower faces; a slot through its bottom flat for the vent.
    _, r_low = envelope(body[body[:, 2] <= asse_axis[1] + .01], asse_axis, LO, HI)
    room = swept(r_low, THREAD, THREAD)
    room = np.where((ys >= cap_y[0] - 1.) & (ys <= cap_y[1] + 1.) & (room > 0), room + s, 0.)
    room_steps = steps(ys, room)
    v_lo, v_hi = vent.min(axis=0), vent.max(axis=0)
    snap = cap(st_a, asse_axis[1], None, asse_axis[1], hexed=True).cut(turned(room_steps, asse_axis))
    for y0, y1, apothem, clock, corner in wrench_rooms:
        snap = snap.cut(hex_prism(asse_axis, apothem + s, clock, y0, y1, corner + s))
    slot = box(v_lo[0] - c, v_hi[0] + c, v_lo[1] - THREAD - c, v_hi[1] + THREAD + c, v_lo[2] - 1., asse_axis[1])
    out['asse-snap-cap'] = snap.cut(slot).clean()
    W = st_a['outer']
    seat = box(asse_axis[0] - W, asse_axis[0] + W, cap_y[0] - c - WALL, rear + INTO, split, ceiling + INTO)
    room = turned(asse_steps, asse_axis)
    for y0, y1, apothem, clock, corner in wrench_rooms:
        room = room.fuse(hex_prism(asse_axis, apothem + c, clock, y0 - SLIDE, y1, corner + c))
    seat = seat.cut(room)
    for p in pockets(st_a):
        seat = seat.cut(p)
    out['asse-seat'] = seat.clean()
    numbers['asse'] = {'station': st_a, 'seat_runs': asse_steps, 'cap_runs': room_steps,
                       'wrenches': [{'y': y, 'apothem': a, 'clock': k, 'corner': r} for y, a, k, r in wrenches],
                       'gagira_fore_y': gag_fore, 'vent': [v_lo.tolist(), v_hi.tolist()]}

    # --- Pisco: one rigid piece; its check rides in its outlet collet ---------------------------
    dims = json.load(open(HW / 'reference/compact-inline-candidates/dimensions.json'))['pisco_rvfup_quarter']
    ranges = dims['fitted_exterior']['component_ranges_mm']
    profile = np.array(dims['fitted_exterior']['profile_z_radius_mm'])
    ys2, r_p = envelope(np.concatenate([pts[n] for n in pts if n.startswith('pisco-')]), pisco_axis, LO, HI)
    _, r_c = envelope(pts['co2-check'], pisco_axis, LO, HI)
    cav2 = np.maximum(swept(r_p, 0., SLIDE), swept(r_c, .5, SLIDE + .5))
    cav2 = np.where(cav2 > 0, cav2 + c + PISCO_RADIAL_RELIEF, 0.)
    # The cap runs from the outlet collet to 2.6 mm short of the outlet fitting's aft end, clear of
    # the ring there, its lip in front of the step down to the outlet's neck.
    fitting, collet = ranges['outlet_fitting'], ranges['outlet_collet']
    neck_z = profile[(profile[:, 0] > fitting[0]) & (profile[:, 1] < 6.5)][0, 0]
    step_face = mouth_y - neck_z
    pcap = (mouth_y - collet[0] + c + .01, mouth_y - fitting[0] - 2.6)
    m = (ys2 >= pcap[0] - .25) & (ys2 <= pcap[1] + .25)
    st_p = pisco_station(pisco_axis[0],cav2[m].max(),pisco_axis[1],*pcap)
    W = st_p['outer']
    front = pcap[0] - c - WALL
    seat = box(pisco_axis[0] - W, pisco_axis[0] + W, front, rear + INTO, SPLIT, ceiling + INTO)
    seat = seat.cut(turned(steps(ys2, np.where(ys2 >= front - 1, cav2, 0.)), pisco_axis))
    for p in pockets(st_p):
        seat = seat.cut(p)
    for opening in pisco_cap_service_cuts(st_p):
        seat = seat.cut(opening)
    out['pisco-seat'] = seat.clean()
    held = profile[(profile[:, 0] >= mouth_y - pcap[1] - 1.) & (profile[:, 0] <= neck_z)]
    r_body = held[:, 1].max() + PISCO_CAP_AIR
    neck=profile[(profile[:,0]>=neck_z)&(profile[:,0]<=collet[0])]
    r_neck = neck[:,1].max() + PISCO_CAP_AIR
    lip = step_face - s
    snap=cap(st_p,st_p['root'],pisco_axis[1]-r_body-WALL)
    snap=snap.fuse(*(box(*b) for b in pisco_grip_stock(st_p,pisco_axis[1],r_body,r_neck,lip)))
    out['pisco-snap-cap'] = (snap
                             .cut(turned([(pcap[0] - 1., lip, r_neck), (lip, pcap[1] + 1., r_body)], pisco_axis))
                             .clean())
    numbers['pisco'] = {'station': st_p, 'step_face_y': step_face, 'body_r': r_body,
        'neck_r': r_neck, 'cap_release_drop_mm':3.6, 'cap_service_fore_slide_mm':45.}

    # --- the meter: its seat on the side wall, its cap from the west -----------------------------
    # The housing's label side stands in a cup on the side wall, swept forward by the slide and aft
    # by VAR. The cap is a block over the housing's west end and rim; its top and bottom walls run
    # east past the housing as the springs, onto ledges on the seat's top and bottom faces.
    centre = at_world(meter_at, (meter.body_center_x, 0., meter.body_center_z))
    MY, MZ = float(centre[1]), float(centre[2])
    port = at_world(meter_at, (0., 0., 0.))
    soda_axis = (float(port[0]), float(port[2]))  # the port axis, on the soda union's

    def wx(y):                                    # the world X of a station along the housing's axis
        return float(at_world(meter_at, (meter.body_center_x, y, meter.body_center_z))[0])

    def wy(x):                                    # the world Y of a station along the port axis
        return float(at_world(meter_at, (x, 0., 0.))[1])

    # The lower housing's cones and the cover flange, as the reference builds them.
    UNDER, CONE, FLANGE, R_CONE, R_HOUSING, R_FLANGE = meter.underside_y, -8.1, 7.3, 15.1, 15.45, 17.5
    MX = wx(FLANGE) - METER_AIR                   # the split: the cap holds what is west of it
    fore, aft = SLIDE + VAR, VAR
    x0 = MX - 1.
    east = wx(meter.screw_head_y_range[1]) + METER_AIR
    cup = stadium_x(MY, MZ, R_FLANGE + METER_AIR, fore, aft, x0, east)
    for dy in (-meter.boss_x, meter.boss_x):
        for dz in (-meter.boss_z, meter.boss_z):
            cup = cup.fuse(stadium_x(MY + dy, MZ + dz, meter.boss_radius + METER_AIR, fore, aft, x0, east))
    r_collar = max(meter.port_collar_radii)
    for sign in (-1., 1.):
        ya, yb = sorted((wy(sign * meter.port_neck_end), wy(sign * meter.port_collar_end)))
        collar = cq.Solid.makeCylinder(r_collar + METER_AIR, (yb + aft + METER_AIR) - (ya - fore - METER_AIR),
                                       cq.Vector(soda_axis[0], ya - fore - METER_AIR, soda_axis[1]), cq.Vector(0, 1, 0))
        cup = cup.fuse(collar.intersect(box(x0, soda_axis[0] + r_collar + 1., ya - fore - 2., yb + aft + 2.,
                                            soda_axis[1] - r_collar - 1., soda_axis[1] + r_collar + 1.)))
    # The fixed lead boss enters a shallow chamber. Flexible leads turn west
    # against the body above the complete lower leaf and its receiving ledge.
    root = at_world(meter_at, meter.wire_root)
    half = meter.wire_root_width / 2.
    wire_room=(x0,wx(meter.wire_root[1]+meter.wire_root_depth/2.)+METER_AIR,
               wy(-half)-fore-METER_AIR,wy(half)+aft+METER_AIR)
    SEAT_Y = (386.0, 446.0)                       # clear of the soda inlet's foam and the carb bulkhead
    CAP_Y = (397.0, 435.0)                        # between the port collars
    core = wx(meter.boss_y_range[0]) - METER_AIR
    west_end = wx(UNDER)
    st_m = station(0., soda_axis[1] + r_collar + METER_AIR - MZ + WALL,
                   *CAP_Y, split=0., wing_root=west_end-METER_AIR-MX)
    W = st_m['outer']
    # Join the lead chamber to the lower spring pocket at one plane. The
    # complete retaining face remains; no thin membrane roofs the pocket.
    cup=cup.fuse(box(*wire_room,min(float(root[2])-3.,MZ-st_m['neck']),
                    float(root[2])+meter.wire_boss_len+METER_AIR)).clean()

    def to_world(shape):
        """The snap's frame (insertion +z, lateral x, length y) to the world's: insertion +X."""
        return shape.rotate((0, 0, 0), (0, 1, 0), 90).translate((MX, 0., MZ))

    seat = box(MX, side + INTO, SEAT_Y[0], SEAT_Y[1], MZ - W, MZ + W).cut(cup)
    for p in pockets(st_m):
        seat = seat.cut(to_world(p))
    out['meter-seat'] = seat.clean()
    hollow = stadium_x(MY, MZ, R_HOUSING + METER_CAP_AIR, 0., METER_CAP_AIR, wx(CONE), core + 1.)
    hollow = hollow.fuse(stadium_x(MY, MZ, R_CONE + METER_CAP_AIR, 0., METER_CAP_AIR, west_end - METER_CAP_AIR, wx(CONE) + .01))
    hollow = hollow.fuse(cq.Solid.makeCylinder(meter.port_neck_radius + METER_CAP_AIR, SEAT_Y[1] - SEAT_Y[0],
                                               cq.Vector(soda_axis[0], SEAT_Y[0], soda_axis[1]), cq.Vector(0, 1, 0)))
    bottom=west_end-METER_AIR-METER_BACK-MX
    half=st_m['inner']-ROOT_RADIUS-.5
    blank=cap(st_m,st_m['root'],bottom).fuse(
        box(-half,half,*CAP_Y,bottom,st_m['root']+METER_BEARING_DEPTH))
    body = to_world(blank).cut(hollow)
    out['meter-snap-cap'] = body.clean()
    numbers['meter'] = {'station': st_m, 'split_x': MX, 'axis': [MY, MZ],
                       'housing_air_mm':METER_AIR,'lower_leaf_span_mm':CAP_Y[1]-CAP_Y[0]}
    return {n: out[n] for n in SOLIDS}, numbers
