"""neoFit ACHV44-E analytic layout reference from the vendor's product media.

Only the 6.35 mm tube connection and product identity are published dimensions.
The exterior is scaled from the vendor's arbitrary-unit GLB using the minor
collet opening; socket depths, the open passage and flow orientation are
explicit layout estimates. See model-dimensions.json for the evidence scope.
Native Y runs with the inferred flow; the origin bisects the two mouth planes.
"""
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
NAME = 'neofit-achv44-check'
TUBE_OD = 6.35
LENGTH = 38.868131347763274
SOCKET_INSERTION = 12.7
FLOW_BORE = 4.24
MAX_BODY_RADIUS = 5.912075
VENDOR_SCALE_MM = 5.432124953066388

# (station from inlet mouth, radius), mm. The circular envelope retains the
# vendor body's distinct barrel, taper and socket bands. Sub-0.01 mm duplicate
# rings in its tessellation are represented by the adjacent analytic shoulder.
FIXED_PROFILE = (
    (1.046084, 4.688), (1.483370, 5.451),
    (3.110834, MAX_BODY_RADIUS), (14.159233, MAX_BODY_RADIUS),
    (17.068679, 5.409986), (24.802939, 5.409986),
    (25.510202, 4.699442), (26.138155, 3.921168),
    (27.387001, 4.675945), (27.782459, 5.432128),
    (29.101379, 5.432128), (29.101379, 5.267481),
    (30.165533, 5.267481), (30.165533, 5.432128),
    (35.776375, 5.432128), (35.776375, 5.267481),
    (36.018647, 5.267481), (36.018647, 5.432128),
    (37.784631, 5.432128), (38.251251, 4.675945),
)
COLLET_MAJOR_RADIUS = 5.1465
COLLET_MINOR_RADIUS = 4.10
COLLET_LIP_LENGTH = .55
COLLET_STEM_RADIUS = 3.85
COLLET_REACH = 4.65


def inlet():
    """Inlet mouth and outward axis, in native mm; inferred flow enters here."""
    return (0., -LENGTH / 2., 0.), (0., -1., 0.)


def outlet():
    """Outlet mouth and outward axis, in native mm."""
    return (0., LENGTH / 2., 0.), (0., 1., 0.)


def socket_depth(port=None):
    """Unmeasured receiving depth, a common 12.7 mm layout estimate."""
    return SOCKET_INSERTION


def ports():
    """One interface table shared by the water and gas installations."""
    result = {}
    for name, station in (('inlet', inlet()), ('outlet', outlet())):
        position, outward = station
        result[name] = {'position': position, 'outward': outward,
                        'tube_od_mm': TUBE_OD,
                        'insertion_mm': socket_depth(name),
                        'insertion_status': 'estimated_unmeasured'}
    return result


def bearing_band():
    """Fixed cylindrical barrel: (start, end, radius), measured from inlet."""
    return 3.110834, 14.159233, MAX_BODY_RADIUS


def sections():
    """Conservative radial sections (label, radius, s0, s1) along flow.

    Tapered fixed-body spans use their larger endpoint radius. The two
    moving collets use their oval major radius. These are axial envelopes,
    not a seal, release stroke, retention or load specification.
    """
    rows = [('inlet-release-collet', COLLET_MAJOR_RADIUS, 0., COLLET_REACH)]
    for index, ((s0, r0), (s1, r1)) in enumerate(zip(FIXED_PROFILE, FIXED_PROFILE[1:])):
        if s1 > s0:
            label = 'barrel' if index == 2 else f'fixed-body-{index:02}'
            rows.append((label, max(r0, r1), s0, s1))
    rows.append(('outlet-release-collet', COLLET_MAJOR_RADIUS,
                 LENGTH - COLLET_REACH, LENGTH))
    return tuple(rows)


def specification():
    """Published identity and explicit scope of the estimated layout geometry."""
    return json.loads((HERE / 'model-dimensions.json').read_text())


def _cylinder(radius, s0, s1):
    import cadquery as cq
    return cq.Solid.makeCylinder(radius, s1 - s0,
                                cq.Vector(0., s0 - LENGTH / 2., 0.),
                                cq.Vector(0., 1., 0.))


def build_parts():
    """Separate fixed acetal case and two estimated movable release collets."""
    import cadquery as cq
    # Revolve a station/radius polyline about Y in the native XY plane.
    profile = [(0., FIXED_PROFILE[0][0] - LENGTH / 2.),
               *((r, s - LENGTH / 2.) for s, r in FIXED_PROFILE),
               (0., FIXED_PROFILE[-1][0] - LENGTH / 2.)]
    body = (cq.Workplane('XY').polyline(profile).close()
            .revolve(360., (0., 0.), (0., 1.)).val())
    body = body.cut(_cylinder(FLOW_BORE / 2., -.01, LENGTH + .01))
    for lo, hi in ((-.01, SOCKET_INSERTION),
                   (LENGTH - SOCKET_INSERTION, LENGTH + .01)):
        body = body.cut(_cylinder(TUBE_OD / 2., lo, hi))
    # Clearance around each illustrative moving collet keeps the fixed case
    # separate from its stem. Grab rings, seals and valve internals are absent.
    body = body.cut(_cylinder(3.90, -.01, COLLET_REACH + .05))
    body = body.cut(_cylinder(3.90, LENGTH - COLLET_REACH - .05, LENGTH + .01))

    def collet(s0, sign):
        mouth = s0 - LENGTH / 2.
        plane = cq.Plane(origin=(0., mouth, 0.), xDir=(1., 0., 0.),
                         normal=(0., sign, 0.))
        lip = (cq.Workplane(plane).ellipse(COLLET_MAJOR_RADIUS, COLLET_MINOR_RADIUS)
               .extrude(COLLET_LIP_LENGTH).val())
        if sign > 0:
            stem = _cylinder(COLLET_STEM_RADIUS, s0, s0 + COLLET_REACH)
            hole = _cylinder(TUBE_OD / 2., s0 - .01, s0 + COLLET_REACH + .01)
        else:
            stem = _cylinder(COLLET_STEM_RADIUS, s0 - COLLET_REACH, s0)
            hole = _cylinder(TUBE_OD / 2., s0 - COLLET_REACH - .01, s0 + .01)
        return lip.fuse(stem).cut(hole)

    return {'fixed-body': body, 'inlet-release-collet': collet(0., 1.),
            'outlet-release-collet': collet(LENGTH, -1.)}


def build():
    """Native exterior compound; no valve, seal or gripping mechanism model."""
    import cadquery as cq
    return cq.Compound.makeCompound(list(build_parts().values()))


def export():
    import cadquery as cq
    sys.path.insert(0, str(HERE.parents[1] / 'scripts'))
    from _cadq_export import export_assembly
    from _materials import M_NEOFIT_ACETAL
    assembly = cq.Assembly(name=NAME)
    for name, shape in build_parts().items():
        assembly.add(shape, name=name, color=M_NEOFIT_ACETAL)
    export_assembly(assembly, str(HERE / (NAME + '.step')))


if __name__ == '__main__':
    export()
