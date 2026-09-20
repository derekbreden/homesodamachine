"""A standalone, screwless tee-carrier lap study; never a production part.

Two headed keys carry separation and shear. The existing final 3.25 mm outward
assembly movement engages them. A removable snap keeper blocks disengagement.
The keeper does not substitute for the keys' broad bearing surfaces.

The coupon copies the current carrier's stack, root overlap and key spacing. Its
extra side wings are grips for a bench comparison. It intentionally does not
import tee_carrier: the production source and generated carrier stay unchanged.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import cadquery as cq


HERE = Path(__file__).resolve().parent
TRAVEL = 3.25
STATIC_AIR = 0.15
SUPPORTED_AIR = 0.40
HEIGHT = 52.82
LEFT_SPLIT_X = -6.40
RIGHT_EDGE_X = -2.65
LAP_X = (-10.57, 9.462)
KEY_X = 1.0
KEY_ZS = (9.0, 37.93)
STEM_X = (-0.5, 2.5)
STEM_Z_HALF = 4.0
HEAD_X = (-1.8, 3.8)
HEAD_Z_HALF = 7.0
STEM_Y = (0.0, 2.0)
HEAD_Y = (2.0, 4.0)
ENTRY_X = (HEAD_X[0] + TRAVEL - STATIC_AIR,
           HEAD_X[1] + TRAVEL + STATIC_AIR)
KEEPER_X = (HEAD_X[1] + STATIC_AIR, ENTRY_X[1] - STATIC_AIR)
BEAM_ROOT_Z = KEY_ZS[1] - HEAD_Z_HALF + STATIC_AIR
BEAM_TIP_Z = 18.9
BEAM_T = 0.8
HOOK_DEFLECTION = 0.45
VOLUME_TOL = 1e-5


def box(xs, ys, zs):
    return cq.Solid.makeBox(xs[1] - xs[0], ys[1] - ys[0], zs[1] - zs[0],
                            cq.Vector(xs[0], ys[0], zs[0]))


def union(shapes):
    body, *others = shapes
    return body.fuse(*others).clean() if others else body


def left_half():
    body = union([
        box((-25.0, LEFT_SPLIT_X), (0.0, 6.0), (0.0, HEIGHT)),
        box(LAP_X, (-6.0, 0.0), (0.0, HEIGHT)),
    ])
    keys = []
    for z in KEY_ZS:
        keys.extend((box(STEM_X, STEM_Y, (z - STEM_Z_HALF, z + STEM_Z_HALF)),
                     box(HEAD_X, HEAD_Y, (z - HEAD_Z_HALF, z + HEAD_Z_HALF))))
    return union([body, *keys])


def keeper_rigid():
    # The two blocks occupy the unused entry windows beside the engaged key heads.
    blocks = [box(KEEPER_X, (0.15, 6.0),
                  (z - HEAD_Z_HALF + 0.15, z + HEAD_Z_HALF - 0.15))
              for z in KEY_ZS]
    spine = box((5.4, KEEPER_X[1]), (4.85, 6.0),
                (KEY_ZS[0] - HEAD_Z_HALF + 0.15,
                 KEY_ZS[1] + HEAD_Z_HALF - 0.15))
    return union([*blocks, spine])


def keeper_beam():
    beam = box((3.95, 4.75), (4.85, 6.0), (17.4, BEAM_ROOT_Z + 1.0))
    # The root enters the upper rigid block. The gap to the spine admits +X flex.
    root = box((3.95, 5.55), (4.85, 6.0), (BEAM_ROOT_Z, BEAM_ROOT_Z + 1.0))
    return union([beam, root])


def keeper_hook():
    # A leading cam deflects the beam +X. The square aft face retains the keeper.
    return (cq.Workplane('XY').workplane(offset=17.4)
            .polyline(((3.95, 2.5), (4.75, 2.5), (4.75, 5.0),
                       (3.95, 5.0), (3.95, 4.5), (3.5, 4.5), (3.5, 3.5)))
            .close().extrude(3.0).val())


def keeper():
    return union([keeper_rigid(), keeper_beam(), keeper_hook()])


def right_half():
    body = box((RIGHT_EDGE_X, 25.0), (0.0, 6.0), (0.0, HEIGHT))
    cuts = []
    for z in KEY_ZS:
        # The entry window takes the head while the right half is 3.25 mm inboard.
        cuts.append(box(ENTRY_X, (-0.1, 6.1),
                        (z - HEAD_Z_HALF - SUPPORTED_AIR,
                         z + HEAD_Z_HALF + SUPPORTED_AIR)))
        # These rectangular prisms are the complete relative seating sweeps.
        # Keep the fore load shoulder and open the pocket to the rear. Supports
        # below its crown then leave directly aft before the keeper goes in.
        cuts.append(box((HEAD_X[0] - STATIC_AIR, ENTRY_X[1]),
                        (HEAD_Y[0] - STATIC_AIR, 6.1),
                        (z - HEAD_Z_HALF - SUPPORTED_AIR,
                         z + HEAD_Z_HALF + SUPPORTED_AIR)))
        cuts.append(box((STEM_X[0] - STATIC_AIR,
                         STEM_X[1] + TRAVEL + STATIC_AIR),
                        (-0.1, STEM_Y[1] + STATIC_AIR),
                        (z - STEM_Z_HALF - SUPPORTED_AIR,
                         z + STEM_Z_HALF + SUPPORTED_AIR)))
    # The keeper's spine seats flush in the rear. Stock remains in front of it.
    cuts.append(box((KEEPER_X[0] - STATIC_AIR, KEEPER_X[1] + STATIC_AIR),
                    (4.85, 6.1), (2.0, 44.93)))
    # The beam's travel channel and the recess behind its retaining lip.
    cuts.append(box((3.8, 5.25), (2.3, 6.1), (17.25, BEAM_ROOT_Z + 0.15)))
    cuts.append(box((3.35, 3.8), (2.3, 4.65), (17.25, 20.55)))
    return body.cut(*cuts).clean()


def _overlap(a, b):
    return a.intersect(b).Volume()


def check():
    left, right, clip = left_half(), right_half(), keeper()
    errors = []
    readings = {}

    def clear(name, a, b):
        volume = _overlap(a, b)
        readings[name] = {'overlap_mm3': volume}
        if volume > VOLUME_TOL:
            errors.append(f'{name}: {volume:.6g} mm3 overlap')

    def contact(name, a, b, displacement):
        volume = _overlap(a, b)
        readings[name] = {'overlap_mm3': volume,
                          'displacement_mm': displacement}
        if volume <= VOLUME_TOL:
            errors.append(f'{name}: no positive bearing contact')

    for name, body in (('left', left), ('right', right), ('keeper', clip)):
        bb = body.BoundingBox()
        readings[name] = {'valid': body.isValid(), 'solids': len(body.Solids()),
                          'volume_mm3': body.Volume(),
                          'bounds_mm': [bb.xlen, bb.ylen, bb.zlen]}
        if not body.isValid() or len(body.Solids()) != 1:
            errors.append(f'{name}: must be one valid solid')
    clear('assembled_halves', left, right)
    clear('keeper_to_right', clip, right)
    clear('keeper_to_keys', clip, left)

    # These are exact sweep volumes for the two rectangular keys, not sparse poses.
    for index, z in enumerate(KEY_ZS, 1):
        head_entry = box((HEAD_X[0] + TRAVEL, HEAD_X[1] + TRAVEL),
                         (-8.0, HEAD_Y[1]), (z - HEAD_Z_HALF, z + HEAD_Z_HALF))
        stem_entry = box((STEM_X[0] + TRAVEL, STEM_X[1] + TRAVEL),
                         (-8.0, STEM_Y[1]), (z - STEM_Z_HALF, z + STEM_Z_HALF))
        clear(f'key_{index}_forward_entry', union([head_entry, stem_entry]), right)
        head_slide = box((HEAD_X[0], HEAD_X[1] + TRAVEL), HEAD_Y,
                         (z - HEAD_Z_HALF, z + HEAD_Z_HALF))
        stem_slide = box((STEM_X[0], STEM_X[1] + TRAVEL), STEM_Y,
                         (z - STEM_Z_HALF, z + STEM_Z_HALF))
        clear(f'key_{index}_outward_seating', union([head_slide, stem_slide]), right)
    # Additional complete-body endpoint readings include the lap root and wing.
    clear('forward_entry_end', left, right.translate((-TRAVEL, 0, 0)))
    joined_right = union([right, clip])
    contact('fore_aft_separation_bearing', left,
            joined_right.translate((0, STATIC_AIR + 0.001, 0)), STATIC_AIR + 0.001)
    contact('lap_compression_bearing', left,
            joined_right.translate((0, -0.001, 0)), 0.001)
    contact('outward_shear_bearing', left,
            joined_right.translate((STATIC_AIR + 0.001, 0, 0)), STATIC_AIR + 0.001)
    contact('keeper_blocks_inward_disengagement', left,
            joined_right.translate((-STATIC_AIR - 0.001, 0, 0)), STATIC_AIR + 0.001)
    for sense in (-1, 1):
        contact(f'vertical_shear_{sense:+d}', left,
                joined_right.translate((0, 0, sense * (SUPPORTED_AIR + 0.001))),
                SUPPORTED_AIR + 0.001)
    contact('keeper_snap_retention', clip.translate((0, 0.151, 0)), right, 0.151)

    # With the hook displaced into its provided flex space, its exact Y sweep clears
    # the lip. This establishes room, not a material/fatigue qualification.
    hook = keeper_hook().translate((HOOK_DEFLECTION, 0, 0))
    bb = hook.BoundingBox()
    flexed_hook_sweep = box((bb.xmin, bb.xmax), (bb.ymin, bb.ymax + 8.0),
                           (bb.zmin, bb.zmax))
    clear('flexed_hook_insertion_envelope', flexed_hook_sweep, right)
    flexed_beam_envelope = box((3.95, 4.75 + HOOK_DEFLECTION), (4.85, 6.0),
                               (17.4, BEAM_ROOT_Z))
    clear('beam_deflection_space', flexed_beam_envelope, keeper_rigid())
    length = BEAM_ROOT_Z - BEAM_TIP_Z
    strain = 1.5 * BEAM_T * HOOK_DEFLECTION / length ** 2
    return {
        'status': 'coupon_geometry_pass' if not errors else 'coupon_geometry_fail',
        'production_ready': False,
        'purpose': 'Screwless interlocking joint feasibility coupon, not a carrier revision',
        'dimensions_mm': {
            'lap_stack': 12.0, 'lap_height': HEIGHT, 'final_outward_travel': TRAVEL,
            'key_head': [5.6, 2.0, 14.0], 'key_stem': [3.0, 2.0, 8.0],
            'key_separation_z': KEY_ZS[1] - KEY_ZS[0],
            'nominal_joint_air_y': STATIC_AIR,
            'nominal_joint_air_z_supported': SUPPORTED_AIR,
            'keeper_block_width_x': KEEPER_X[1] - KEEPER_X[0],
            'keeper_beam_thickness': BEAM_T, 'keeper_beam_effective_length': length,
            'keeper_hook_deflection': HOOK_DEFLECTION,
        },
        'nominal_small_deflection_beam_surface_strain': strain,
        'strain_scope': 'Elastic beam estimate 3*t*deflection/(2*length^2); printed material, '
                        'root concentration, required force and durability are not qualified.',
        'readings': readings, 'errors': errors,
        'release_conditions': [
            'Print in the actual production material and establish sliding fit and latch survival.',
            'Measure joint play; nominal air is not clamping or a stiffness result.',
            'Use the final production tee stations to verify all key and keeper ligaments.',
            'Prove complete-half assembly and keeper access against the actual enclosure and valves.',
            'Compare full-width joined carriers under equal centre and asymmetric hand loads.',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', action='store_true', help='write standalone coupon STEP/STL')
    args = parser.parse_args()
    result = check()
    result['generator_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if result['errors']:
        (HERE / 'checks.json').write_text(json.dumps(result, indent=2) + '\n')
        print('\n'.join(result['errors']))
        return 1
    if args.export:
        import trimesh
        result['printed_meshes'] = {}
        for name, body in (('left', left_half()), ('right', right_half()), ('keeper', keeper())):
            cq.exporters.export(body, str(HERE / f'coupon-only-{name}.step'))
            # Give the keeper its flat rear face as the print bed; bending stays in XY.
            printed = body if name != 'keeper' else body.rotate((0, 0, 0), (1, 0, 0), -90)
            bb = printed.BoundingBox()
            printed = printed.translate((-bb.xmin, -bb.ymin, -bb.zmin))
            path = HERE / f'coupon-only-{name}.stl'
            cq.exporters.export(printed, str(path),
                                tolerance=0.03, angularTolerance=0.10)
            mesh = trimesh.load_mesh(path)
            mesh_ok = bool(mesh.is_watertight and mesh.is_winding_consistent
                           and mesh.volume > 0 and abs(mesh.bounds[0][2]) < 1e-6
                           and abs(mesh.volume - body.Volume()) < 0.01)
            result['printed_meshes'][name] = {
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'watertight': bool(mesh.is_watertight),
                'winding_consistent': bool(mesh.is_winding_consistent),
                'volume_mm3': float(mesh.volume),
                'native_volume_difference_mm3': float(mesh.volume - body.Volume()),
                'bounds_mm': mesh.bounds.tolist(), 'pass': mesh_ok,
            }
            if not mesh_ok:
                result['errors'].append(f'{name}: printed mesh does not match its valid native solid')
        exploded = cq.Compound.makeCompound([
            left_half(), right_half().translate((12, 8, 0)), keeper().translate((37, 24, 0))])
        cq.exporters.export(exploded, str(HERE / 'geometry.svg'),
                            opt={'width': 960, 'height': 680, 'projectionDir': (-1, 2, 0.8),
                                 'showHidden': False, 'showAxes': False, 'strokeWidth': 0.13})
        drawing = ET.parse(HERE / 'geometry.svg')
        drawing.getroot().insert(0, ET.Element('{http://www.w3.org/2000/svg}rect',
                                               width='100%', height='100%', fill='white'))
        drawing.write(HERE / 'geometry.svg', encoding='unicode', xml_declaration=True)
    if result['errors']:
        result['status'] = 'coupon_geometry_fail'
    (HERE / 'checks.json').write_text(json.dumps(result, indent=2) + '\n')
    if result['errors']:
        print('\n'.join(result['errors']))
        return 1
    print('ok: isolated joint coupon geometry; production carrier unchanged and not qualified')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
