"""Native supported roofs as moving drawer crossmembers, plus bare seam controls.

The three roofs are intentionally separate prints because top contact distance
is an object setting.  Their common handhold section is unscaled: R6 inner
returns, R6 exterior roof roll with the production additive transition, 80 mm
opening, 35.25 mm ceiling, 12 mm roof and 3 mm inner wall.  Their feet bolt to
upward pads on the actual moving drawer floor.  No stationary cabinet insert
or sample storage holder is introduced.

The two neck controls retain the frozen complete source STEP/STL.  Actual tube
bundle placement is a caller-owned rigid transform; manufacturing geometry and
every source triangle remain unchanged.  End ties on the bundle retain them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile

import cadquery as cq
import numpy as np
import trimesh

import enclosure_features as f

HERE = Path(__file__).resolve().parent
SNAPSHOTS = f.PP/'calibration/soda-studies/inputs'
ROOF_GAPS = {'R30': .30, 'R45': .45, 'R60': .60}


def _union(shapes):
    result = shapes[0]
    for shape in shapes[1:]:
        result = result.fuse(shape)
    return result.clean()


def _zcylinder(diameter, x, y, z0, z1):
    return cq.Solid.makeCylinder(diameter/2, z1-z0, cq.Vector(x, y, z0))


@lru_cache(None)
def native_roof():
    """Complete native handhold active section, clear of Y-seam furniture.

    Only unloaded end stock is broadened to carry the isolated R12 outside
    returns. The source inner cutter and exact expanding roof rim are retained.
    The original 3 mm inner wall is the crossmember's back; both ends reach the
    moving floor.  Long source Y becomes the new X opening, without scaling.
    """
    e, b = f.source()
    sx = 1.
    x_face = b.inner[0]-e.wall
    cap = e._boss_x(x_face, sx)[3]
    bed, roof, crown = e._handhold_levels(b.inner)
    y0, y1 = e._handhold_y()
    # Native rolling corners need the neighbouring wall's broad stock. That
    # stock is retained beyond the end walls, rather than chopping the R12 rim.
    stock = e._ybox(x_face, cap, y0-9, y1+9, bed, crown)
    before = stock.cut(e._handhold_cutter(b.inner, x_face, sx)).clean()
    rim = []
    for edge in before.Edges():
        bb = edge.BoundingBox()
        if (abs(bb.xmin-x_face) < 1e-6 and abs(bb.xmax-x_face) < 1e-6
                and bb.ymin >= y0-1e-6 and bb.ymax <= y1+1e-6
                and bb.zmin >= bed-1e-6 and bb.zmax <= roof+1e-6
                and bb.zmax > bed+1e-6):
            rim.append(edge)
    rounded = before.fillet(e.handhold_edge_r, rim)
    from overhang_round import roof_rim
    native = roof_rim(before, rounded, x_face, sx, y0, y1, roof,
                      e.handhold_corner_r, e.handhold_edge_r)
    mid_x, mid_y = (x_face+cap)/2, (y0+y1)/2
    result = native.translate((-mid_x, -mid_y, -bed)).rotate(
        (0, 0, 0), (0, 0, 1), -90)
    return result, {
        'opening_length_mm': e.handhold_length,
        'clear_ceiling_from_foot_plane_mm': roof-bed,
        'roof_stock_mm': e.handhold_roof,
        'inner_wall_mm': e.handhold_wall,
        'roof_depth_mm': cap-x_face,
        'inner_return_r_mm': e.handhold_corner_r,
        'exterior_roll_r_mm': e.handhold_edge_r,
        'outside_return_r_mm': e.handhold_corner_r+e.handhold_edge_r,
        'end_stock_outside_opening_mm': 9.,
        'source_frame_rotation_z_deg': -90,
        'source_frame_translation_mm': [-mid_x, -mid_y, -bed],
        'active_ceiling': 'Uncut complete source cutter/roof-rim section; bolt axes and marks are outside it.',
        'sources': [f.provenance(f.ENC/'enclosure.py', '_handhold_cutter'),
                    f.provenance(f.ENC/'enclosure.py', '_handhold_levels'),
                    f.provenance(f.ENC/'enclosure.py', '_handholds'),
                    f.provenance(f.PP/'cadlib/overhang_round.py', 'roof_rim')],
    }


def _roof_code(shape, identifier, y_face, z):
    """Small code on the outside vertical roof stock, clear of its underside."""
    label = cq.Workplane('XY').text(identifier, 4., .72,
        font='Helvetica', kind='bold', halign='center', valign='center').val()
    label = label.rotate((0, 0, 0), (1, 0, 0), 90).rotate(
        (0, 0, 0), (0, 0, 1), 180)
    bb = label.BoundingBox()
    label = label.translate((-(bb.xmin+bb.xmax)/2,
                             y_face-.24-bb.ymin,
                             z-(bb.zmin+bb.zmax)/2))
    return shape.fuse(label).clean()


@dataclass
class Comparisons:
    parts: dict
    bed_parts: dict
    drawer_add: dict
    drawer_cut: dict
    mating_rooms: dict
    metadata: dict = field(default_factory=dict)

    def apply_drawer(self, drawer):
        for stock in self.drawer_add.values():
            drawer = drawer.fuse(stock)
        for room in self.drawer_cut.values():
            drawer = drawer.cut(room)
        return drawer.clean()

    def report(self):
        report = dict(self.metadata)
        for key in ('parts', 'bed_parts', 'drawer_add', 'drawer_cut', 'mating_rooms'):
            report[key] = {name: {'bounds_mm': f.bounds(shape),
                                 'volume_mm3': shape.Volume(),
                                 'valid': shape.isValid(), 'solids': len(shape.Solids())}
                           for name, shape in getattr(self, key).items()}
        return report


def build(*, centre_x=2., stations_y=(20., 48., 76.),
          drawer_floor_bottom_z=6., drawer_floor_thickness=3.,
          upward_pad_height=3.25, foot_height=6., foot_diameter=13.,
          insert_depth=5.7):
    """Three separately printed roofs on the actual moving drawer floor.

    Default seat Z 12.25 gives native ceiling Z 47.50 and top 59.50, below the
    70 mm fascia. Upward pads start at the actual forward floor's Z 9.00 top;
    its underside and the original active cartridge sill datum remain intact.
    Whole roofs move out with the drawer; their individual bolts permit removal
    outside the cabinet for tactile support-surface comparison.
    """
    e, _ = f.source()
    source_shape, source_meta = native_roof()
    opening_half = source_meta['opening_length_mm']/2
    bolt_x = opening_half+foot_diameter/2
    floor_top = drawer_floor_bottom_z+drawer_floor_thickness
    seat_z = floor_top+upward_pad_height
    parts, bed_parts, adds, cuts, mating = {}, {}, {}, {}, {}
    recipes, axes, poses = {}, {}, {}
    for (identifier, gap), y in zip(ROOF_GAPS.items(), stations_y):
        body = source_shape
        for sign in (-1, 1):
            body = body.fuse(_zcylinder(foot_diameter, sign*bolt_x, 0, 0, foot_height))
            shaft = _zcylinder(e.screw_clear_dia, sign*bolt_x, 0, -.1, foot_height+.1)
            head = _zcylinder(e.head_cbore_dia, sign*bolt_x, 0,
                              foot_height-e.head_cbore_depth, foot_height+.1)
            body = body.cut(shaft).cut(head)
            key = identifier+('_left' if sign < 0 else '_right')
            x = centre_x+sign*bolt_x
            adds[key+'_floor_pad'] = _zcylinder(foot_diameter, x, y, floor_top, seat_z)
            cuts[key+'_M3_insert'] = _zcylinder(e.heatset_dia, x, y,
                                               seat_z-insert_depth, seat_z+.01)
            mating[key+'_M3_clear'] = shaft.translate((centre_x, y, seat_z))
            mating[key+'_M3_head'] = head.translate((centre_x, y, seat_z))
            axes[key] = [x, y]
        body = _roof_code(body.clean(), identifier,
                          source_meta['roof_depth_mm']/2,
                          source_meta['clear_ceiling_from_foot_plane_mm']+8.)
        bed_parts[identifier] = body
        parts[identifier] = body.translate((centre_x, y, seat_z))
        recipes[identifier] = {
            'support_top_z_distance': str(gap),
            'supports_enabled': True, 'support_type': 'tree(auto)',
            'first_layer_height': .20, 'layer_height': .24,
            'wall_generator': 'classic',
            'native_expanding_rim_wall_band': {'z_mm': [35., 41.5], 'wall_loops': 6},
            'support_exclusions': 'Expanding exterior R6 strip; retain supports under broad flat ceiling, native 0.8 mm contact-edge inset.',
            'scope': 'Requested gap; actual emitted separation requires the current native slice.',
            'native_contact_probe': {
                'nominal_ceiling_z_mm': source_meta['clear_ceiling_from_foot_plane_mm'],
                'window_xy_mm': [-30., 30., -4., 1.],
                'flat_ceiling_bounds_xy_mm': [-34., 34., -5.5, 2.5],
                'source_contact_edge_inset_mm': .8,
                'lower_support_footprint': 'Open to the bed below this central flat roof; the 3 mm back wall and both end feet lie outside the named probe window.',
                'frame': 'Isolated local +Z manufacturing shape; not world assembly coordinates.',
            },
        }
        poses[identifier] = {'rotation_deg': [0, 0, 0],
                             'translation_from_assembly_mm': [-centre_x, -y, -seat_z],
                             'print_up': [0, 0, 1]}
    meta = {
        'name': 'three_native_roof_drawer_crossmembers',
        'entries': ['E9', 'E11', 'E21', 'E23', 'E27', 'E29', 'E31', 'E32'],
        'source_profile': source_meta, 'ribs': list(ROOF_GAPS),
        'native_roof_setting_convention': 'R30 / R45 / R60 are requested top support distances 0.30 / 0.45 / 0.60 mm.',
        'native_wall_band_convention': 'Local print Z from each crossmember foot plane.',
        'recipes': recipes, 'print_pose': poses, 'bolt_axes_world_xy_mm': axes,
        'drawer_floor_bottom_world_z_mm': drawer_floor_bottom_z,
        'drawer_floor_stock_mm': drawer_floor_thickness,
        'added_upward_floor_pad_mm': upward_pad_height,
        'resulting_insert_stock_mm': drawer_floor_thickness+upward_pad_height,
        'foot_seat_world_z_mm': seat_z,
        'active_ceiling_world_z_mm': seat_z+source_meta['clear_ceiling_from_foot_plane_mm'],
        'roof_top_world_z_mm': seat_z+source_meta['clear_ceiling_from_foot_plane_mm']+source_meta['roof_stock_mm'],
        'foot_diameter_mm': foot_diameter, 'foot_height_mm': foot_height,
        'M3': {'clear_diameter_mm': e.screw_clear_dia,
               'head_counterbore_diameter_mm': e.head_cbore_dia,
               'head_counterbore_depth_mm': e.head_cbore_depth,
               'insert_pilot_diameter_mm': e.heatset_dia,
               'insert_pilot_depth_mm': insert_depth,
               'blind_floor_cap_mm': drawer_floor_thickness+upward_pad_height-insert_depth,
               'nominal_screw': 'M3 x 8: 5.5 mm pilot engagement with the default foot/pad datums; 0.2 mm tip clearance.',
               'scope': 'Geometric fastening option; current root pad and assembled crossmember load/fit remain unprinted.'},
        'support_access': 'Both Y ends of the native lifting opening remain open before bolting to the drawer. Remove support with the crossmember loose.',
        'service': 'Remove front-top, then withdraw whole drawer and all three crossmembers together. Unbolt individual roofs only on the withdrawn drawer.',
        'identity': 'Helvetica bold 4 mm code on exterior vertical roof stock, 0.48 mm relief; active underside is unmarked.',
        'physical_scope': {
            'source_record': 'hardware/printed-parts/enclosure/grip-cover/physical-acceptance.json',
            'accepted': 'Identified native grip receiver coupon support removal and assembled fit.',
            'limits': 'These three full-span roof crossmembers, new floor pads and fasteners are unprinted. Source evidence supplies no lifting-load or repeated-use claim.'},
    }
    return Comparisons(parts, bed_parts, adds, cuts, mating, meta)


@lru_cache(None)
def frozen_neck():
    """The byte-bound source swatch; no public capture/exporter is invoked."""
    step_bytes = gzip.decompress((SNAPSHOTS/'faucet-neck-swatch.step.gz').read_bytes())
    mesh_bytes = gzip.decompress((SNAPSHOTS/'faucet-neck-swatch.stl.gz').read_bytes())
    with tempfile.TemporaryDirectory(prefix='section-neck-source-') as directory:
        step = Path(directory)/'source.step'
        stl = Path(directory)/'source.stl'
        step.write_bytes(step_bytes); stl.write_bytes(mesh_bytes)
        shape = cq.importers.importStep(str(step)).val()
        mesh = trimesh.load_mesh(stl, process=False)
    section = cq.Workplane(obj=shape).section(0).val().Wires()
    exterior = max((cq.Face.makeFromWires(w) for w in section), key=lambda w: w.Area())
    origin = exterior.Center()
    return shape, mesh, step_bytes, mesh_bytes, {
        'frozen_step': str((SNAPSHOTS/'faucet-neck-swatch.step.gz').relative_to(f.ROOT)),
        'frozen_stl': str((SNAPSHOTS/'faucet-neck-swatch.stl.gz').relative_to(f.ROOT)),
        'source_step_sha256': hashlib.sha256(step_bytes).hexdigest(),
        'source_stl_sha256': hashlib.sha256(mesh_bytes).hexdigest(),
        'original_triangle_count': len(mesh.faces),
        'source_axis_origin_print_frame_mm': origin.toTuple(),
        'source_axis_direction_print_frame': [0, math.sin(math.radians(15)), math.cos(math.radians(15))],
        'manufacturing_pose': 'The accepted -15 degree X production pose is already baked into the frozen source mesh.',
    }


def neck_controls():
    """Two unchanged bare controls and their explicit setting/identity scopes."""
    shape, mesh, _, _, provenance = frozen_neck()
    return ({name: shape for name in ('NR00', 'NR05')},
            {name: mesh.copy() for name in ('NR00', 'NR05')}, {
        'source': provenance,
        'recipes': {name: {'wall_generator': 'arachne', 'seam_position': 'aligned',
                          'seam_gap': str(gap)+'%', 'seam_slope_type': 'none',
                          'scarf': 'none', 'first_layer_height': .20, 'layer_height': .24,
                          'fine_band': {'z_mm': [4.04, 16.04], 'layer_height': .12}}
                    for name, gap in (('NR00', 0), ('NR05', 5))},
        'recipe_scope': 'Only regular seam gap varies on unchanged short source necks. Arachne, aligned seam and no scarf match the full neck configuration; NR00 and NR05 select 0% and 5% instead of its 15%. The fine comparison band remains 0.12 mm.',
        'assembly': 'Ride on the actual water/flavor/drain/ribbon bundle through their retained source passage. Align both source passage axes. Retain at the bundle ends with real ties and use the source tube anchor for its stated tube/fitting.',
        'identity': 'Keep source mesh unchanged. NR code belongs on the adjacent anchoring underside or is pen-written on the cut face after printing; no engraved or below-bed relief is added to the source mesh.',
        'limits': 'Short source sections have different thermal conditions from the complete faucet; surfaces, tie handling and fit of this section remain unprinted.'})


def neck_on_bundle(shape, *, axis_origin, direction=(0, 1, 0), roll_deg=0.):
    """Rigidly align the retained axis to a caller-owned real bundle segment.

    axis_origin is the outer shell axis at its lower cut plane, not the water
    tube center. Native water lies N -4.027512922 from that outer axis. The
    three tube/drain/ribbon datums are supplied by faucet_paths.py.
    """
    *_, provenance = frozen_neck()
    origin = provenance['source_axis_origin_print_frame_mm']
    shape = shape.translate(tuple(-v for v in origin)).rotate(
        (0, 0, 0), (1, 0, 0), 15.)
    direction = np.array(direction, dtype=float)
    direction /= np.linalg.norm(direction)
    normal = np.array((0., 0., 1.))
    cross = np.cross(normal, direction)
    angle = math.degrees(math.acos(float(np.clip(np.dot(normal, direction), -1, 1))))
    if np.linalg.norm(cross) > 1e-9:
        shape = shape.rotate((0, 0, 0), tuple(cross), angle)
    elif angle > 1:
        shape = shape.rotate((0, 0, 0), (1, 0, 0), 180.)
    if roll_deg:
        shape = shape.rotate((0, 0, 0), tuple(direction), roll_deg)
    return shape.translate(axis_origin)


def export_cache(directory=None):
    """One requested prototype export; no live/publication or recurring check."""
    directory = Path(directory or HERE/'comparison-additions')
    directory.mkdir(parents=True, exist_ok=True)
    roof = build()
    report = roof.report()
    for name, shape in roof.parts.items():
        cq.exporters.export(shape, str(directory/(name+'-assembly.step')))
    for name, shape in roof.bed_parts.items():
        cq.exporters.export(shape, str(directory/(name+'.step')))
        shape.exportStl(str(directory/(name+'.stl')), tolerance=.012,
                        angularTolerance=.07, relative=False)
    parts, _, neck_meta = neck_controls()
    _, _, step_bytes, mesh_bytes, _ = frozen_neck()
    for name in parts:
        (directory/(name+'.step')).write_bytes(step_bytes)
        (directory/(name+'.stl')).write_bytes(mesh_bytes)
    report['neck_controls'] = neck_meta
    report['mating_review'] = {
        'roof_pair_overlaps_mm3': {a+' / '+b: roof.parts[a].intersect(roof.parts[b]).Volume()
                                  for a, b in (('R30', 'R45'), ('R45', 'R60'), ('R30', 'R60'))},
        'roof_pad_overlaps_mm3': {name: shape.intersect(_union(list(roof.drawer_add.values()))).Volume()
                                 for name, shape in roof.parts.items()},
        'scope': 'Nominal source active section and matching pad/feet geometry only. Parent owns the final moving drawer/fascia/cabinet withdrawal review.'}
    (directory/'metadata.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


if __name__ == '__main__':
    report = export_cache()
    print(json.dumps({k: report[k] for k in ('active_ceiling_world_z_mm',
          'roof_top_world_z_mm', 'foot_seat_world_z_mm', 'parts', 'mating_review')}, indent=2))
