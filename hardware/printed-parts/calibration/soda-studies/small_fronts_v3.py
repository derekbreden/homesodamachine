"""Native DATA, bulkhead-label and machine-display bundles for the section.

All geometry is assembled in its producer's mating frame.  Layout belongs to
the cabinet caller.  No production exporter, document synchronizer or main()
is called.  The printed nominal display backer and M3 bulkhead clamp options
are explicitly identified proxies for purchased hardware, not source hardware
or pressure/fit gauges.
"""
from __future__ import annotations

from dataclasses import replace
from functools import lru_cache
import json
import math
from pathlib import Path
import sys

import cadquery as cq

import enclosure_features as f

ROOT, ENC, PP = f.ROOT, f.ENC, f.PP


@lru_cache(None)
def modules():
    e, b = f.source()
    sys.path[:0] = [str(ENC), str(PP / 'enclosure/bulkhead-ring')]
    import _data_wing_interface as data_fit
    import _display_wing_interface as display_fit
    import _y_wall_dimensions as colors
    import bulkhead_ring as ports
    data = f._load(PP / 'enclosure/data-ring/data_ring.py',
                   'pour_section_native_data_ring')
    display = f._load(PP / 'enclosure/display-cover/display_cover.py',
                      'pour_section_native_display_cover')
    gasket = f._load(PP / 'enclosure/display-gasket/display_gasket.py',
                     'pour_section_native_display_gasket')
    return e, b, data_fit, display_fit, colors, ports, data, display, gasket


def _cylinder_y(diameter, y0, y1):
    return cq.Solid.makeCylinder(diameter / 2, y1-y0,
                                 cq.Vector(0, y0, 0), cq.Vector(0, 1, 0))


def data():
    """Whole DATA plate/word plus real two-catch RJ11 receptacle.

    Local origin is the purchased jack axis at the outer wall plane. +Y faces
    the customer. The plate back is Y -3.36; its face is intentionally recessed
    to Y -1.68. Both broad wings and both receiver lips remain full span.
    """
    e, b, fit, _, colors, _, native, _, _ = modules()
    add, cut = f._derive(
        lambda host: fit.apply(host, fit.Station(0, 0), 0, up=-1),
        (-27, 27, -16, 2, -19, 29))
    receptacle = f.keystone_receptacle()
    add.update({'RJ11_'+n: s for n, s in receptacle.add.items()})
    cut.update({'RJ11_'+n: s for n, s in receptacle.cut.items()})
    source_paths = (PP / 'enclosure/data-ring/data_ring.py',
                    ENC / '_data_wing_interface.py',
                    ENC / '_nameplate_wing_interface.py')
    return f.Feature(
        'DATA_and_RJ11', ('E14', 'E25', 'E28', 'E29', 'E34', 'E48'),
        add=add, cut=cut, post_add=receptacle.post_add,
        parts={'DATA_body': native.build_ring().translate((0, -fit.POCKET_DEPTH, 0)),
               'DATA_word': native.build_word().translate((0, -fit.POCKET_DEPTH, 0))},
        source_print_up=(0, 0, -1),
        part_print_up={'DATA_body': (0, 1, 0), 'DATA_word': (0, 1, 0)},
        backing={'plate_back_local_y_mm': -fit.POCKET_DEPTH,
                 'plate_face_local_y_mm': -fit.POCKET_DEPTH+fit.THICK,
                 'plate_body_mm': [fit.WIDTH, fit.HEIGHT, fit.THICK],
                 'wings_mm': [fit.PROJECTION, fit.WING_SPAN, fit.WING_THICK],
                 'floor_stock_mm': fit.FLOOR_STOCK,
                 'body_x_air_per_side_mm': fit.FACE_AIR,
                 'tip_air_mm': fit.TIP_AIR,
                 'retaining_air_mm': fit.THICKNESS_AIR,
                 'supported_end_air_mm': fit.SUPPORTED_AIR,
                 'font': 'Helvetica bold', 'word_embed_mm': fit.INK_DEPTH,
                 'word_raise_mm': .48,
                 'materials': {'DATA_body': colors.chip_filaments['flavor'],
                               'DATA_word': colors.word_color('flavor')},
                 'capture': 'Complete native RJ11 tang/latch catches and 50-degree swing ease; no proxy jack included.'},
        mates=('RiteAV RJ11 keystone tang and latch',
               'source DATA flat wings and matching receiving slots'),
        group='rear DATA service wall',
        notes=('Cut the wall rooms before restoring the two native jack catches.',
               'The continuous plate, broad wings and Helvetica word are current producer geometry.',
               'Current recomposed wall and DATA assembly are unprinted; source acceptance scopes remain separate.'),
        sources=tuple(f.provenance(p) for p in source_paths)+receptacle.sources)


def _nominal_bulkhead_clamp(which):
    """A positive M3 clamp using the reference barrel/flange/nut envelopes.

    The source reference fittings deliberately do not model working threads or
    movable nuts. This explicit option lets the native label remain genuinely
    clamped in a 3 mm wall: a smooth locating stub passes the source bore, an
    exterior flange bears on the chip and a separate inboard nut carries a
    ruthex short M3 insert. It does not reproduce the connector's fluid path.
    """
    e, _, _, _, _, ports, _, _, _ = modules()
    reference = ports.FAMILIES[ports.family(which)]
    flange = reference.flange_footprint()
    nut = reference.panel_footprint()[0]
    stub = _cylinder_y(reference.THREAD_D, -2.75, 2.0)
    front = _cylinder_y(flange, 2.0, 8.5).fuse(stub)
    front = front.cut(_cylinder_y(e.screw_clear_dia, -3, 9))
    front = front.cut(_cylinder_y(e.head_cbore_dia, 5.0, 9.0)).clean()
    rear = _cylinder_y(nut, -11.0, -3.0)
    rear = rear.cut(_cylinder_y(e.heatset_dia, -3.0-e.heatset_depth, -2.99)).clean()
    return {'nominal_'+which+'_flange': front,
            'nominal_'+which+'_nut': rear}, {
        'kind': 'Printed nominal barrel/flange/nut envelope with central M3 draw screw',
        'source_barrel_diameter_mm': reference.THREAD_D,
        'source_flange_envelope_diameter_mm': flange,
        'source_nut_envelope_diameter_mm': nut,
        'wall_bearing_planes_local_y_mm': [-3.0, 2.0],
        'stub_end_gap_from_nut_mm': .25,
        'M3_shank_diameter_mm': e.screw_clear_dia,
        'M3_head_counterbore_diameter_mm': e.head_cbore_dia,
        'M3_head_counterbore_depth_mm': 3.5,
        'insert': 'ruthex RX-M3Sx4.0',
        'insert_pilot_diameter_mm': e.heatset_dia,
        'insert_bore_depth_mm': e.heatset_depth,
        'nominal_screw': 'M3 x 12; under-head plane Y 5.0, insert zone Y -3..-7',
        'reference_scope': 'Native circular envelopes; no working connector thread, fluid path or pressure qualification.',
    }


def port(which='water', *, nominal_clamp=False, contrast_black_white=False):
    """One complete source port-chip family in a real 5 mm wall stack.

    Origin is the chip's inboard face, +Y outward. The full source chip occupies
    Y 0..2. The underlying wall is Y -3..0. The producer's exact supported
    pocket and 36-degree teardrop bore pass through the whole stack. A real
    fitting or the explicitly named nominal M3 clamp retains the chip.
    """
    e, _, _, _, colors, native, _, _, _ = modules()
    if which not in ('water', 'co2', 'drain'):
        raise ValueError('Use one water/union, CO2/neoFit or drain family.')
    family = native.family(which)
    bore = native.bore_d(family)
    height = native.rise(which)
    bottom = native.bottom(family)
    width = 32+2*.15
    field = e.PortField(native.THICK, 0, ((0, 0, width, height+.15, bottom+.15),))
    station = (('round', 0, 0, bore),)
    blank = f.box((-19, 19, -3, native.THICK, -bottom-3, height+3))
    _, cut = f._derive(
        lambda host: e._port_field(host, field, station, native.THICK,
                                   wall_at=lambda x, z: 3, up=-1),
        (-21, 21, -4, 4, -bottom-4, height+4))
    fluid = native.FLUIDS[which]
    parts = {'port_'+which+'_body': native.build_ring(which),
             'port_'+which+'_word': native.build_word(which)}
    source_rgb = {'body': colors.chip_color(fluid), 'word': colors.word_color(fluid)}
    pair_rgb = ({'body': colors.chip_color('flavor'), 'word': colors.word_color('flavor')}
                if contrast_black_white else source_rgb)
    metadata = {'chip_mm': [32, native.tall(which), native.THICK],
                'chip_floor_local_y_mm': 0,
                'outward_face_local_y_mm': native.THICK,
                'wall_thickness_mm': 3, 'clamp_stack_mm': 5,
                'barrel_bore_diameter_mm': bore,
                'source_barrel_diameter_mm': native.FAMILIES[family].THREAD_D,
                'barrel_radial_air_mm': .15,
                'pocket_slip_per_side_mm': .15,
                'print_up': 'Native back-top -Z; supported pocket edge follows this direction.',
                'font': native.WORD_FONT+' '+native.WORD_KIND,
                'word': native.STATIONS[which].word,
                'word_embed_mm': native.WORD_DEPTH,
                'word_raise_mm': native.WORD_RAISE,
                'source_colors_rgb': source_rgb,
                'chosen_colors_rgb': pair_rgb,
                'contrast_option': contrast_black_white,
                'source_flange_to_word_clearance_mm': native.flange_clearance(which),
                'nut_access': 'Keep the inboard Y -3 bearing face and whole nut envelope accessible.'}
    if nominal_clamp:
        clamp, metadata['nominal_clamp'] = _nominal_bulkhead_clamp(which)
        parts.update(clamp)
    part_up = {n: (0, 1, 0) for n in parts}
    return f.Feature('port_'+which, ('E14', 'E17', 'E24', 'E29', 'E31'),
                     add={'native_wall_stack': blank}, cut=cut, parts=parts,
                     source_print_up=(0, 0, -1), part_print_up=part_up,
                     backing=metadata,
                     mates=(family+' fitting barrel, flange and movable panel nut',),
                     group='rear plumbing wall',
                     notes=('The native label is retained by a clamped stack, not a press fit.',
                            'The full source body and registered Helvetica word remain separate material volumes.',
                            'Current source CO2 chip is red/white; black/white is an explicit contrast option only.',
                            'Actual clamp force, bore fit and recomposed print remain unmeasured.'),
                     sources=(f.provenance(PP/'enclosure/bulkhead-ring/bulkhead_ring.py'),
                              f.provenance(ENC/'enclosure.py', '_port_field'),
                              f.provenance(ENC/'enclosure.py', '_port_cuts'),
                              f.provenance(Path(native.FAMILIES[family].__file__))))


def display(*, nominal_backer=True, full_facet_stock=True):
    """The whole 30-degree display assembly in its native face-local frame.

    X is across, Y up the display and Z out of the visible face. Visible face
    Z 0; cover back -3.84; 90A gasket -4.84..-3.84; glass-space backer
    -5.84..-4.84. The receiver cuts retain both wing pockets, 1.8 mm lips and
    native support exits down the 30-degree facet. The optional broad stock
    is the native 19 mm facet thickness and must unite with cabinet stock.
    """
    e, _, _, fit, _, _, _, native, gasket = modules()
    parts = {'display_cover': native.build_display_cover().val(),
             'display_gasket_90A': gasket.build_display_gasket().val()}
    if nominal_backer:
        parts['display_nominal_backer'] = gasket._rounded_prism(
            gasket.outer_x, gasket.outer_slope, gasket.corner_r,
            fit.GLASS_SEAT, gasket.z_bottom).val()
    add = ({'native_19mm_facet_stock': f.box((-73, 73, -51.5, 51.5,
                                                   -e.display_facet_thickness, 0))}
           if full_facet_stock else {})
    return f.Feature(
        'machine_display', ('E8', 'E34', 'E35', 'E36', 'E37'),
        add=add, cut={'native_wing_glass_PCB_and_exit_rooms': fit.cuts(
            e.display_facet_thickness+e.display_pcb_cut_through, 12)}, parts=parts,
        source_print_up=(0, .5, math.cos(math.radians(30))),
        part_print_up={n: (0, 0, 1) for n in parts},
        backing={'cover_mm': [fit.COVER_X, fit.COVER_Y, fit.THICK],
                 'window_mm': [fit.WINDOW_X, fit.WINDOW_Y],
                 'wings_mm': [fit.WING_REACH, fit.WING_SPAN, fit.WING_THICK],
                 'body_air_x_per_side_mm': fit.BODY_X_AIR,
                 'body_air_y_per_side_mm': fit.BODY_Y_AIR,
                 'wing_tip_air_mm': fit.TIP_AIR,
                 'wing_end_air_mm': fit.END_AIR,
                 'bearing_air_mm': fit.BEARING_AIR,
                 'lip_stock_mm': fit.LIP_THICK,
                 'facet_thickness_mm': e.display_facet_thickness,
                 'support_exit_depth_mm': 12,
                 'gasket_material': 'Bambu TPU 90A, distinct from the two 85A faucet parts',
                 'gasket_mm': [gasket.outer_x, gasket.outer_slope, gasket.thickness],
                 'cover_back_local_z_mm': fit.BACK,
                 'gasket_z_mm': [gasket.z_bottom, gasket.z_top],
                 'nominal_backer_z_mm': [fit.GLASS_SEAT, gasket.z_bottom],
                 'nominal_backer_scope': 'Printed 1 mm glass-space geometry; not glass or a working screen.',
                 'orientation': 'Use display_datum(outer); receiver world print-up +Z, cover/backer face-up +localZ.'},
        mates=('native display cover wings and both complete receiving lips',
               '1 mm TPU 90A gasket over the actual glass seat'),
        group='front 30-degree service/display facet',
        notes=('Apply the complete cutter after fusing all surrounding facet stock.',
               'Preserve support exits down into the empty display storey; do not refill these lanes.',
               'The source cover has face-up physical fit/shake evidence; current sectional integration, gasket compression and nominal backer remain unprinted.'),
        sources=tuple(f.provenance(p) for p in (
            PP/'enclosure/display-cover/display_cover.py', ENC/'_display_wing_interface.py',
            PP/'enclosure/display-gasket/display_gasket.py'))+
                (f.provenance(ENC/'enclosure.py', '_display_cuts'),))


def display_datum(outer, *, centre_x=None):
    """Current source 30-degree face datum for a caller-owned outer envelope."""
    e, *_ = modules()
    plane = e.display_plane(outer)
    if centre_x is None:
        return cq.Location(plane)
    origin = plane.origin
    return cq.Location(cq.Plane(origin=(centre_x, origin.y, origin.z),
                                xDir=plane.xDir, normal=plane.zDir))


def moved(feature, location):
    """Apply the mating-frame transform to geometry and native build axes."""
    zero = cq.Vertex.makeVertex(0, 0, 0).moved(location).Center()
    def axis(direction):
        point = cq.Vertex.makeVertex(*direction).moved(location).Center()
        return (point-zero).toTuple()
    return replace(feature, source_print_up=axis(feature.source_print_up),
                   part_print_up={name: axis(direction) for name, direction
                                  in feature.part_print_up.items()}, **{
        key: {name: shape.moved(location) for name, shape in getattr(feature, key).items()}
        for key in ('add', 'cut', 'post_add', 'parts')})


def export_cache(directory=None):
    """Requested one-time native bundle export and exact mating inspection."""
    directory = Path(directory or Path(__file__).parent/'small-fronts')
    directory.mkdir(parents=True, exist_ok=True)
    features = (data(), *(port(k, nominal_clamp=True) for k in ('water', 'co2', 'drain')),
                display())
    records = []
    for feature in features:
        record = feature.report()
        remote = f.box((1000, 1001, 1000, 1001, 1000, 1001))
        host = feature.apply(remote).cut(remote).clean()
        record['standalone_native_host'] = {
            'bounds_mm': f.bounds(host), 'solids': len(host.Solids()),
            'valid': host.isValid(), 'volume_mm3': host.Volume()}
        cq.exporters.export(host, str(directory/(feature.name+'-host.step')))
        record['host_moving_intersections_mm3'] = {}
        for name, shape in feature.parts.items():
            cq.exporters.export(shape, str(directory/(name+'.step')))
            record['host_moving_intersections_mm3'][name] = host.intersect(shape).Volume()
        record['part_pair_intersections_mm3'] = {}
        names = list(feature.parts)
        for i, first in enumerate(names):
            for second in names[i+1:]:
                record['part_pair_intersections_mm3'][first+' / '+second] = (
                    feature.parts[first].intersect(feature.parts[second]).Volume())
        records.append(record)
    (directory/'metadata.json').write_text(json.dumps(records, indent=2)+'\n')
    return records


if __name__ == '__main__':
    for row in export_cache():
        print(row['name'], row['standalone_native_host'],
              row['host_moving_intersections_mm3'])
