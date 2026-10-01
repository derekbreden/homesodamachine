"""Coated-scan exterior reference of the PP0308E elbow; dimensions in mm.

The +Y socket is observed; the +Z collet is completed by symmetry. Internal
retention, sealing, insertion depth and operating travel are unmeasured.
"""
from pathlib import Path
import json
import cadquery as cq

HERE = Path(__file__).resolve().parent
STEP = HERE / 'jg-pp0308e-elbow.step'
TUBE_OD = 6.35
COLLET_FACE = 20.56239
FIXED_FACE = 18.84
INSERTION = None
RELEASE_TRAVEL = None


def _turned(profile):
    points = [(0, profile[0][0]), *((r, t) for t, r in profile), (0, profile[-1][0])]
    return cq.Workplane('XZ').polyline(points).close().revolve(360, (0, 0), (0, 1))


def _leg(part, leg):
    return part if leg == 'z' else part.rotate((0, 0, 0), (1, 0, 0), -90)


def port(leg):
    """Observed/resting release face, not an insertion stop or travel endpoint."""
    axis = {'y': (0., 1., 0.), 'z': (0., 0., 1.)}[leg]
    return tuple(COLLET_FACE * a for a in axis), axis


def stations():
    return {leg: port(leg) for leg in ('y', 'z')}


def build():
    """Return named fixed body and two collets in their captured resting state."""
    data = json.loads((HERE / 'scan-measurements.json').read_text())
    # The bend has a round core with a thin, wider web at its outer corner.
    # These measured features remain distinct instead of filling the side recess.
    core = cq.Workplane('XY').sphere(4.05)
    for leg in ('y', 'z'):
        core = core.union(_leg(cq.Workplane('XY').circle(4.05).extrude(3.5), leg))
    web = (cq.Workplane('XY').box(5.16, 7.57, 7.57)
           .edges('|X').fillet(1.25).edges('not |X').fillet(.18)
           .translate((0, -.285, -.285)))
    core = core.union(web)
    parts = []
    for leg in ('y', 'z'):
        body = _leg(_turned(data['profiles'][leg]['fixed_body']), leg)
        core = core.union(body)
        collet = _leg(_turned(data['profiles'][leg]['collet']), leg)
        bore = _leg(cq.Workplane('XY').circle(TUBE_OD / 2).extrude(24), leg)
        # Nominal tube corridors keep the layout model from inventing a stop.
        parts.append((leg + '_collet', collet.cut(bore)))
    for leg in ('y', 'z'):
        core = core.cut(_leg(cq.Workplane('XY').circle(TUBE_OD / 2).extrude(24), leg))
    return [('fixed_body', core), *parts]


def build_elbow_connector():
    """Assembly-compatible compound; the three component solids stay separate."""
    return cq.Workplane(obj=cq.Compound.makeCompound([p.val() for _,p in build()]))


def export():
    shapes = build()
    assembly = cq.Assembly(name='PP0308E_scan_exterior')
    for name, shape in shapes:
        assembly.add(shape, name=name, color=cq.Color(.20, .24, .28) if name == 'fixed_body' else cq.Color(.50, .56, .59))
    assembly.export(str(STEP))
    compound = cq.Compound.makeCompound([p.val() for _, p in shapes])
    cq.exporters.export(compound, str(HERE / 'jg-pp0308e-elbow.stl'), tolerance=.025, angularTolerance=.1)
    print(STEP)
    return shapes


if __name__ == '__main__':
    export()
