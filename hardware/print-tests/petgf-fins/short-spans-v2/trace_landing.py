"""Trace the reported F-row landing failure in saved native paths; run manually."""
from pathlib import Path
import hashlib
import json
import sys
import zipfile

import numpy as np
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from review import segments


def local_path(path, part):
    offset = np.asarray(part['plate_translation_mm'])[:2]
    ends = [path[key][:2] - offset for key in ('a', 'b')]
    if part['bridge_axis'] == 'Y':
        ends = [np.array([p[1], -p[0]]) for p in ends]
    return {**path, 'a': ends[0], 'b': ends[1]}


def footprint(paths):
    return unary_union([LineString([p['a'], p['b']]).buffer(p['width'] / 2)
                        for p in paths])


def describe(path):
    return {'gcode_line': path['line'], 'feature': path['feature'],
            'from_local_xy_mm': path['a'].tolist(),
            'to_local_xy_mm': path['b'].tolist(),
            'nominal_width_mm': path['width'], 'nozzle_z_mm': path['z']}


def trace(folder=HERE, stem='2026-10-14-fin-v2-fan0-petgf-left04-z004-mark2'):
    archive = folder / f'{stem}.gcode.3mf'
    spec = json.loads((folder / f'{stem}.print.json').read_text())
    with zipfile.ZipFile(archive) as z:
        raw = z.read('Metadata/plate_1.gcode')
    paths = segments(raw.decode())
    records, example = [], None
    for part in spec['parts']:
        if part['kind'] not in ('fin_landing_bridge', 'solid_anchor_bridge'):
            continue
        own = [local_path(p, part) for p in paths if p['object'] == part['identify_id']]
        width = (part['roof_bounds_local_mm'][1][0] if part['bridge_axis'] == 'X'
                 else part['roof_bounds_local_mm'][1][1])
        lower = [p for p in own if abs(p['z'] - part['roof_bottom_z_mm']) < 1e-4]
        below = footprint(lower)
        roof = [p for p in own if abs(p['z'] - part['first_roof_nozzle_z_mm']) < 1e-4
                and -.01 <= (p['a'][0] + p['b'][0]) / 2 <= width + .01
                and -.01 <= (p['a'][1] + p['b'][1]) / 2 <= 12.01]
        # Include the two shorter edge rasters: they still cross from the model
        # post toward the fin, even when they turn before the clear-span end.
        raster = [p for p in roof if p['feature'] == 'Bridge'
                  and abs(p['a'][1] - p['b'][1]) < .005
                  and min(p['a'][0], p['b'][0]) < 3.01
                  and max(p['a'][0], p['b'][0]) > 3.1]
        ends = [Point(max((p['a'], p['b']), key=lambda v: v[0])) for p in raster]
        distances = [p.distance(below) for p in ends]
        walls = [p for p in roof if p['feature'].endswith('wall')]
        wall_before_fill = [p for p in walls if p['line'] < raster[0]['line']]
        land = [p for p in wall_before_fill
                if abs(p['a'][0] - (width - .593)) < .003
                and abs(p['b'][0] - p['a'][0]) < .005]
        landing_probe = LineString([(width-.593, .593), (width-.593, 11.407)])
        gaps = landing_probe.difference(below)
        gap_lengths = ([gaps.length] if gaps.geom_type == 'LineString'
                       else [g.length for g in gaps.geoms])
        row = {'id': part['id'], 'kind': part['kind'],
               'first_roof_nozzle_z_mm': part['first_roof_nozzle_z_mm'],
               'first_roof_extrusion': describe(roof[0]),
               'first_bridge_extrusion': describe(raster[0]),
               'main_bridge_strokes': len(raster),
               'far_end_centers_on_prior_beads': sum(d < .001 for d in distances),
               'far_end_bead_envelopes_touching_prior_beads': sum(
                   end.buffer(p['width'] / 2).intersection(below).area > 1e-6
                   for p, end in zip(raster, ends)),
               'far_end_center_distance_to_prior_beads_max_mm': max(distances),
               'perimeter_precedes_bridge_raster': bool(wall_before_fill),
               'far_end_center_distance_to_earlier_same_layer_walls_max_mm': max(
                   end.distance(footprint(wall_before_fill)) for end in ends),
               'inner_landing_wall_centerline_length_mm': sum(
                   LineString([p['a'], p['b']]).length for p in land),
               'inner_landing_wall_centerline_without_prior_bead_mm': sum(
                   LineString([p['a'], p['b']]).difference(below).length for p in land),
               'landing_centerline_longest_prior_bead_gap_mm': max(gap_lengths, default=0),
               'raster_far_end_distance_to_prior_beads_mm': distances}
        if part['kind'] == 'fin_landing_bridge':
            middle = raster[len(raster) // 2]
            far_x = max(middle['a'][0], middle['b'][0])
            inner_x, outer_x = width - .593, width - .21
            row['middle_raster_landing'] = {
                'raster': describe(middle), 'inner_wall_center_x_mm': inner_x,
                'outer_wall_center_x_mm': outer_x,
                'nominal_inner_wall_overlap_mm': middle['width'] / 2 + .45 / 2 - (inner_x - far_x),
                'nominal_gap_to_outer_overhang_wall_mm': outer_x - far_x - .45 / 2 - middle['width'] / 2}
        records.append(row)
        if part['id'] in ('F2', 'D2'):
            example = (part['id'], lower, wall_before_fill, raster)
    record = {'archive': archive.name,
              'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
              'gcode_sha256': hashlib.sha256(raw).hexdigest(), 'specimens': records,
              'coordinate_frame': 'Unrotated specimen XY; X crosses the clear span; Y follows the fin.',
              'scope': 'Command order and nominal bead geometry only. Centerline coverage is not whole-bead support. '
                       'The report does not measure sag, bonding or actual bead width. Physical F-row collapse is user reported.'}
    (folder / 'landing-path-review.json').write_text(json.dumps(record, indent=2) + '\n')
    if example:
        render(folder, example)
    print(json.dumps({'archive': archive.name, 'rows': [
        {k: r[k] for k in ('id', 'main_bridge_strokes', 'far_end_centers_on_prior_beads',
                          'far_end_bead_envelopes_touching_prior_beads')} for r in records]}))
    return record


def render(folder, example):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch, PathPatch
    from matplotlib.path import Path as PlotPath
    from shapely.geometry.polygon import orient
    name, *layers = example
    fig, axes = plt.subplots(1, 2, figsize=(11, 7), dpi=160,
                             gridspec_kw={'width_ratios': [1.15, 1]})
    colors = ('#c4cbd2', '#32689b', '#dc791c')
    for ax in axes:
        for paths, color in zip(layers, colors):
            shape = footprint(paths)
            for polygon in ([shape] if shape.geom_type == 'Polygon' else shape.geoms):
                polygon = orient(polygon, sign=1)
                rings = [polygon.exterior, *polygon.interiors]
                vertices = np.concatenate([np.asarray(r.coords) for r in rings])
                codes = np.concatenate([[PlotPath.MOVETO] + [PlotPath.LINETO] * (len(r.coords)-2)
                                        + [PlotPath.CLOSEPOLY] for r in rings])
                ax.add_patch(PathPatch(PlotPath(vertices, codes), facecolor=color,
                                       edgecolor='none', alpha=.70))
        ax.set_aspect('equal')
        ax.set_xlabel('Local X (mm)')
        ax.set_ylabel('Local Y (mm)')
        ax.grid(alpha=.15)
    axes[0].set(xlim=(-.4, 7.8), ylim=(-.4, 12.4), title=f'{name}: perimeter first, bridge fill second')
    axes[1].set(xlim=(4.65, 6.6), ylim=(1.1, 4.7), title='Landing detail (same scale in X and Y)')
    axes[1].annotate('Bridge stops at X5.281', xy=(5.281, 3.556), xytext=(4.71, 4.15),
                     fontsize=9, arrowprops={'arrowstyle': '->'})
    axes[1].annotate('Inner perimeter\nX5.607', xy=(5.607, 2.8), xytext=(5.87, 3.35),
                     fontsize=9, arrowprops={'arrowstyle': '->'})
    axes[1].annotate('Tooth below\nfrom preceding layer', xy=(5.9, 2.0), xytext=(5.8, 1.2),
                     fontsize=9, arrowprops={'arrowstyle': '->'})
    fig.suptitle(f'Mark2 PET-GF {name} · first roof Z18.44 mm (layer 77)\n'
                 'Native roof paths over the preceding tooth layer', fontsize=13)
    fig.legend(handles=[Patch(color=c, label=t, alpha=.7) for c, t in zip(colors, (
        'Previous layer: model post, fin and teeth', 'Roof perimeters printed before fill',
        'Roof bridge fill'))], loc='lower center', ncol=1, frameon=False)
    fig.text(.5, .112, 'Nominal fill / inner-perimeter overlap ≈ 0.11 mm. Physical sag is not shown.',
             ha='center', fontsize=9)
    fig.tight_layout(rect=(0, .15, 1, .91))
    fig.savefig(folder / 'landing-paths.png', bbox_inches='tight')
    plt.close(fig)


if __name__ == '__main__':
    trace()
