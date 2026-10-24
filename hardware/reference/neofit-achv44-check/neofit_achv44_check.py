"""neoFit ACHV44-E analytic layout reference from the vendor's product media.

The ACHV44-E listing gives nominal connections and product identity. Exterior
scale and socket engagement are inferred from neoFit ATEU44/ATRU444 published
1/4-inch socket dimensions. The vendor GLB supplies the check-specific form.
These are same-family layout estimates, not published ACHV44 dimensions.
See model-dimensions.json for the evidence scope.
Native Y runs with the inferred flow; the origin bisects the two mouth planes.
"""
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
NAME = 'neofit-achv44-check'
TUBE_OD = 6.35
LENGTH = 55.43160662774284
FAMILY_SOCKET_COLLAR_OD = .610 * 25.4
SOCKET_INSERTION = .665 * 25.4
FLOW_BORE = 4.24
MAX_BODY_RADIUS = 8.431478550423588
VENDOR_SCALE_MM = FAMILY_SOCKET_COLLAR_OD / 2.
# Vendor node0 outlet socket collar has radius1.0. It corresponds to the
# sibling sheets' maximum female collar diameter, not the larger check barrel.

# (station from inlet mouth, radius), mm. The circular envelope retains the
# vendor body's distinct barrel, taper and socket bands. Sub-0.01 mm duplicate
# rings in its tessellation are represented by the adjacent analytic shoulder.
FIXED_PROFILE = (
    (1.4918678819097033, 6.685769623082552),
    (2.1155012981638155, 7.773918561310365),
    (4.43650159122278, 8.431478550423588),
    (20.1931249738797, 8.431478550423588),
    (24.342417995807825, 7.715426633980778),
    (35.372597297220466, 7.715426633980778),
    (36.381257169432544, 6.7020875787197784),
    (37.27680945017563, 5.592155695691845),
    (39.05784542515604, 6.668577440316712),
    (39.62182603172706, 7.747),
    (41.50279771928595, 7.747),
    (41.50279771928595, 7.512193784122122),
    (43.02043604852694, 7.512193784122122),
    (43.02043604852694, 7.747),
    (51.022312542450955, 7.747),
    (51.022312542450955, 7.512193784122122),
    (51.36782764017353, 7.512193784122122),
    (51.36782764017353, 7.747),
    (53.88637759368245, 7.747),
    (54.55184555902435, 6.668577440316712),
)
COLLET_MAJOR_RADIUS = 7.339657287797431
COLLET_MINOR_RADIUS = 5.847196129402403
COLLET_LIP_LENGTH = 0.7843799685783712
COLLET_STEM_RADIUS = 5.490659780048598
COLLET_REACH = 6.6315760979807745


def inlet():
    """Inlet mouth and outward axis, in native mm; inferred flow enters here."""
    return (0., -LENGTH / 2., 0.), (0., -1., 0.)


def outlet():
    """Outlet mouth and outward axis, in native mm."""
    return (0., LENGTH / 2., 0.), (0., 1., 0.)


def socket_depth(port=None):
    """16.891 mm sibling neoFit socket depth, inferred for this unmeasured check."""
    return SOCKET_INSERTION


def ports():
    """One interface table shared by the water and gas installations."""
    result = {}
    for name, station in (('inlet', inlet()), ('outlet', outlet())):
        position, outward = station
        result[name] = {'position': position, 'outward': outward,
                        'tube_od_mm': TUBE_OD,
                        'insertion_mm': socket_depth(name),
                        'insertion_status': 'same_family_inference_unmeasured_check'}
    return result


def bearing_band():
    """Fixed cylindrical barrel: (start, end, radius), measured from inlet."""
    return 4.43650159122278, 20.1931249738797, MAX_BODY_RADIUS


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
    body = body.cut(_cylinder(COLLET_STEM_RADIUS + .05, -.01, COLLET_REACH + .05))
    body = body.cut(_cylinder(COLLET_STEM_RADIUS + .05, LENGTH - COLLET_REACH - .05, LENGTH + .01))

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
