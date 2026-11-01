"""neoFit ACHV44-E analytic layout reference from the vendor's product media.

The ACHV44-E listing gives nominal connections and product identity. Exterior
scale and socket engagement are inferred from neoFit ATEU44/ATRU444 published
1/4-inch socket dimensions. The vendor GLB supplies the check-specific form.
These are same-family layout estimates, not published ACHV44 dimensions.
See model-dimensions.json for the evidence scope.
Native Y runs with the inferred flow; the origin bisects the two mouth planes.

Geometry is in the frozen STEP and display payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
NAME = 'neofit-achv44-check'
STEP_PATH = HERE / (NAME + '.step')
PAYLOAD_PATH = HERE / (NAME + '.step.mesh')
ASSET_MANIFEST_PATH = HERE / 'frozen-asset.json'
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


def main():
    print(NAME)
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
