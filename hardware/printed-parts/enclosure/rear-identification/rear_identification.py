"""Identification chips for the selected six-port rear grid.

The rear flange and nut seating planes stay fixed. Each 1.8 mm tile slides in a
continuous 2 mm rear channel, 0.2 mm inside the outer wall face, with its bore
on the corresponding fitting.
"""

import functools
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HW = next(p for p in HERE.parents if p.name == 'hardware')
sys.path[:0] = [str(HW / 'scripts'), str(HW / 'manifold-layout'),
               str(HW / 'printed-parts/cadlib'),
               str(HERE.parent / 'bulkhead-ring'),
               str(HERE.parent / 'enclosure'),
               str(HERE.parent / 'nameplate'),
               str(HERE.parent / 'y-wall-of-back-top')]

if __name__ == '__main__':
    import _rust_part
    _rust_part.start()

import cadquery as cq

import above_core
import bulkhead_ring as original
import port_chip
import fits
import _y_wall_dimensions as colours
import nameplate
from _cadq_export import export_assembly, import_step
from _materials import step_safe

WIDTH = port_chip.WIDTH
THICK = 1.8
WORD_SIZE = 4.6
WORD_EM = 5.0
WORD_DEPTH = original.WORD_DEPTH
WORD_RAISE = original.WORD_RAISE
# Keep the short upper-row words above the water and soda fitting flanges
# with at least the 1 mm assembly air gap. Chip outlines and clamp planes stay fixed.
WORD_LIFT = {'water': .25, 'carb': .25}

STATIONS = {
    'bulkhead-water': 'water', 'co2-inlet': 'co2',
    'bulkhead-drain': 'drain', 'bulkhead-carb': 'carb',
    'bulkhead-flavor-a': 'flavor-a', 'bulkhead-flavor-b': 'flavor-b',
}


def nameplate_plan():
    """Accepted flat-wing interface on a plain field clearing the core."""
    return {'center_x_mm': -38., 'center_z_mm': 228.,
            'face_y_mm': 473.5, 'field_proud_mm': 2.2,
            'plate_thickness_mm': nameplate.THICK,
            'backing_mm': nameplate.wing_interface.FLOOR_STOCK}


def nameplate_station():
    plan = nameplate_plan()
    return nameplate.interface.station(plan['center_x_mm'],
                                        plan['center_z_mm'])._replace(
                                            thick=nameplate.THICK)


def rise():
    """Common chip top: the upper row finishes at the enclosure roof."""
    spec = above_core.specification()
    return spec['enclosure']['roof_z_mm'] - max(
        spec['rear_wall']['grid']['rows_z_mm'])


def stations():
    """Tiles slide in two continuous channels, with their bores on the fittings."""
    spec = above_core.specification()
    ports = {p['name']:p for p in spec['rear_wall']['wet_ports']}
    rows = []
    for z,names in zip(spec['fluid_grid']['rows_z_mm'],spec['fluid_grid']['assignment']):
        for x,name in zip(spec['fluid_grid']['columns_x_mm'],names):
            rows.append({**ports[name],'which':STATIONS[name],
                'bore_x_mm':ports[name]['center_x_mm'],'bore_z_mm':ports[name]['center_z_mm'],
                'center_x_mm':x,'center_z_mm':z,'face_y_mm':471.1,'floor_y_mm':469.3,'nut_y_mm':465.3})
    return tuple(rows)


def _station(which):
    return next(row for row in stations() if row['which']==which)


def _top(which):
    row = _station(which)
    return 355.-row['center_z_mm'] if row['center_z_mm']==328. else 19.8


@functools.cache
def word(which):
    flat = cq.Workplane('XY').text(original.STATIONS[which].word,WORD_EM,
        WORD_DEPTH+WORD_RAISE,font=original.WORD_FONT,kind=original.WORD_KIND,
        halign='center',valign='center')
    letters = flat.rotate((0,0,0),(1,0,0),90.).rotate((0,0,0),(0,0,1),180.).val()
    b = letters.BoundingBox()
    return letters.translate((-(b.xmin+b.xmax)/2.,THICK-WORD_DEPTH-b.ymin,
                               (12.+_top(which))/2.-(b.zmin+b.zmax)/2.))


@functools.cache
def chip(which):
    row = _station(which)
    blank = cq.Solid.makeBox(WIDTH,THICK,_top(which)+12.,cq.Vector(-WIDTH/2.,0.,-12.))
    diameter = (above_core.specification()['rear_plumbing']['tap_tile_bore_mm']
                if which=='water' else row['bore_diameter_mm'])
    bore = cq.Solid.makeCylinder(diameter/2.,THICK+.2,
        cq.Vector(row['bore_x_mm']-row['center_x_mm'],-.1,row['bore_z_mm']-row['center_z_mm']),cq.Vector(0,1,0))
    return blank.cut(bore,word(which)).clean()


def _colour(rgb):
    return step_safe(cq.Color(*(c/255. for c in rgb)))


def parts():
    """Installed `(name, solid, colour)` rows in enclosure world coordinates."""
    rows = []
    for station in stations():
        which = station['which']
        if getattr(cq, 'MESH', False):
            body, letters = original.split(import_step(str(HERE / f'rear-label-{which}.step')).val())
        else:
            body, letters = chip(which), word(which)
        shift = (station['center_x_mm'], station['floor_y_mm'],
                 station['center_z_mm'])
        fluid = original.FLUIDS[which]
        rows.extend(((f'bulkhead-ring-{which}', body.translate(shift),
                      _colour(colours.chip_color(fluid))),
                     (f'bulkhead-ring-{which}-word', letters.translate(shift),
                      _colour(colours.word_color(fluid)))))
    plan = nameplate_plan()
    if getattr(cq, 'MESH', False):
        body, ink = nameplate.split(import_step(str(nameplate.step_path(1))).val())
    else:
        body, ink = nameplate.build_plate(1), nameplate.build_ink(1)
    shift = (plan['center_x_mm'], plan['face_y_mm']-nameplate.THICK,
             plan['center_z_mm'])
    rows.extend((('nameplate', body.translate(shift),
                  _colour(colours.chip_color('flavor'))),
                 ('nameplate-ink', ink.translate(shift),
                  _colour(colours.word_color('flavor')))))
    return tuple(rows)


def _nameplate_receiver(piece):
    wall = above_core.specification()['rear_wall']['rear_wall']
    # One wall of pad stock under the mouth's print-down allowance, and the pad's crown run
    # out to the rear face at 45 degrees: back-top prints ceiling-down.
    receiver = nameplate.wing_interface.apply(
        piece, nameplate_station(), nameplate_plan()['face_y_mm'],
        up=-1, wall_face=wall['ymin'],
        runout_lead=nameplate.wing_interface.RUNOUT_LEAD,
        end_margin=3.+fits.supported_surface, crown_face=wall['ymax'])
    return receiver.cut(nameplate_release_access()).clean()


def nameplate_release_access():
    """Extend the accepted 18 by 20 mm release diamond through the host wall."""
    plan = nameplate_plan()
    x, z = plan['center_x_mm'], plan['center_z_mm']
    outside = plan['face_y_mm'] + 1.
    inside = above_core.specification()['rear_wall']['rear_wall']['ymin'] - 1.
    # This is the same release diamond as wing_interface.apply. Extending its
    # depth removes the host-wall membrane behind the raised receiver's pad.
    return (cq.Workplane('XZ', origin=(0., outside, 0.))
            .polyline(((x-9., z), (x, z+10.), (x+9., z), (x, z-10.)))
            .close().extrude(outside-inside).val())


@functools.cache
def receiver_field():
    """Exact named receiver stock, including its pocket and retaining lips."""
    return _nameplate_receiver(cq.Compound.makeCompound([]))


def rail_bounds():
    west,east = above_core.specification()['fluid_grid']['columns_x_mm']
    return tuple((x0,x1,471.3,474.3,252.,355.) for x0,x1 in (
        (west-19.15,west-14.),(west+14.,east-14.),(east+14.,east+19.15)))


def rail_roots():
    """Full roots outside the sliding tile channels, into the rear corner stock."""
    west,east = above_core.specification()['fluid_grid']['columns_x_mm']
    half = (WIDTH+.3)/2.
    return tuple((x0,x1,469.299,471.31,252.,355.) for x0,x1 in (
        (west-19.15,west-half),(west+half,east-half),(east+half,east+19.15)))


def apply(piece):
    """One open channel per column, with side rails and a flat bottom stop."""
    for x in above_core.specification()['fluid_grid']['columns_x_mm']:
        piece = piece.cut(cq.Solid.makeBox(WIDTH+.3,3.5,105.,cq.Vector(x-WIDTH/2.-.15,469.299,252.)))
    for x0,x1,y0,y1,z0,z1 in (*rail_roots(),*rail_bounds()):
        piece = piece.fuse(cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0)))
    return _nameplate_receiver(piece).clean()


def field_land():
    """The raised nameplate field's whole footprint on the rear face. The flutes leave it flat,
    so the field joins the fluted wall across its whole base (`enclosure._raised_relief`)."""
    face = above_core.specification()['rear_wall']['rear_wall']['ymax']
    proud = receiver_field().intersect(cq.Solid.makeBox(
        400., 20., 400., cq.Vector(-200., face, 0.))).BoundingBox()
    return (proud.xmin, proud.xmax, face - 3., face + 1., proud.zmin, proud.zmax)


def plain_lands():
    """Keep the complete accepted retaining lips, and the raised field's base, in the exterior
    print mesh."""
    return nameplate.wing_interface.plain_lips(
        nameplate_station(), nameplate_plan()['face_y_mm']) + (field_land(),) + rail_bounds()


def numbers():
    """The sliding tiles' native fitting-frame dimensions and filament colours."""
    from _materials import linear
    spec = above_core.specification()
    rows = []
    for which in STATIONS.values():
        row = _station(which)
        fluid = original.FLUIDS[which]
        label = original.STATIONS[which].word
        rows.append({
            'name': f'rear-label-{which}', 'body_name': f'bulkhead-ring-{which}',
            'word_name': f'bulkhead-ring-{which}-word', 'word': label,
            'top': _top(which),
            'bore_x': row['bore_x_mm']-row['center_x_mm'],
            'bore_z': row['bore_z_mm']-row['center_z_mm'],
            'bore_diameter': (spec['rear_plumbing']['tap_tile_bore_mm']
                              if which == 'water' else row['bore_diameter_mm']),
            'chip_color': list(linear(_colour(colours.chip_color(fluid)))),
            'word_color': list(linear(_colour(colours.word_color(fluid)))),
            'word_width': original.WORD_WIDTHS[label]*WORD_EM/original.WORD_SIZE,
        })
    return {'width': WIDTH, 'thick': THICK, 'bottom': 12., 'bore_overrun': .1,
            'word_size': WORD_EM, 'word_font': original.WORD_FONT,
            'word_kind': original.WORD_KIND,
            'word_depth': WORD_DEPTH, 'word_raise': WORD_RAISE,
            'word_band_bottom': 12., 'stations': rows}


def main():
    import _rust_part
    _rust_part.cut('enclosure-components', 'rear-identification', numbers(), HERE)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'selftest':
        import json
        print(json.dumps(_rust_part.check('enclosure-components', 'rear-identification', numbers()), indent=2))
    else:
        main()
