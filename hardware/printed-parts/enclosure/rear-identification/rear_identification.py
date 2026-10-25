"""Flush identification chips for the selected six-port rear grid.

The rear flange and nut seating planes stay fixed. Each 2 mm chip replaces
2 mm of the 6 mm clamping section; its face is the existing flange plane.
"""

import functools
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
HW = next(p for p in HERE.parents if p.name == 'hardware')
sys.path[:0] = [str(HW / 'scripts'), str(HW / 'manifold-layout'),
               str(HW / 'printed-parts/cadlib'),
               str(HERE.parent / 'bulkhead-ring'),
               str(HERE.parent / 'enclosure'),
               str(HERE.parent / 'nameplate'),
               str(HERE.parent / 'y-wall-of-back-top')]

import above_core
import bulkhead_ring as original
import port_chip
import fits
import _y_wall_dimensions as colours
import nameplate
from _cadq_export import export_assembly, import_step
from _materials import step_safe
from print_mesh import write_print_stl

WIDTH = port_chip.WIDTH
THICK = original.THICK
WORD_SIZE = 4.6
WORD_DEPTH = original.WORD_DEPTH
WORD_RAISE = original.WORD_RAISE

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
    """World stations and exact clamping planes, from the shared rear datum."""
    plan = above_core.specification()['rear_wall']
    relief = plan['interior_panel_relief']
    return tuple({**port, 'which': STATIONS[port['name']],
                  'face_y_mm': relief['flange_seat_y_mm'],
                  'floor_y_mm': relief['flange_seat_y_mm'] - THICK,
                  'nut_y_mm': relief['nut_seat_y_mm']}
                 for port in plan['wet_ports'])


@functools.cache
def word(which):
    flat = cq.Workplane('XY').text(
        original.STATIONS[which].word, WORD_SIZE, WORD_DEPTH + WORD_RAISE,
        font=original.WORD_FONT, kind=original.WORD_KIND,
        halign='center', valign='center')
    letters = (flat.rotate((0, 0, 0), (1, 0, 0), 90.)
               .rotate((0, 0, 0), (0, 0, 1), 180.).val())
    b = letters.BoundingBox()
    bottom = original.bottom(original.family(which))
    return letters.translate((-(b.xmin+b.xmax)/2,
                              THICK-WORD_DEPTH-b.ymin,
                              (bottom+rise())/2-(b.zmin+b.zmax)/2))


@functools.cache
def chip(which):
    family = original.family(which)
    blank = port_chip.outline(WIDTH, rise(), original.bottom(family), THICK)
    bore = cq.Solid.makeCylinder(original.bore_d(family)/2, THICK,
                                 cq.Vector(), cq.Vector(0, 1, 0))
    return blank.cut(bore, word(which)).clean()


def _colour(rgb):
    return step_safe(cq.Color(*(c/255. for c in rgb)))


def parts():
    """Installed `(name, solid, colour)` rows in enclosure world coordinates."""
    rows = []
    for station in stations():
        which = station['which']
        shift = (station['center_x_mm'], station['floor_y_mm'],
                 station['center_z_mm'])
        fluid = original.FLUIDS[which]
        rows.extend(((f'bulkhead-ring-{which}', chip(which).translate(shift),
                      _colour(colours.chip_color(fluid))),
                     (f'bulkhead-ring-{which}-word', word(which).translate(shift),
                      _colour(colours.word_color(fluid)))))
    plan = nameplate_plan()
    body, ink = nameplate.split(import_step(str(nameplate.step_path(1))).val())
    shift = (plan['center_x_mm'], plan['face_y_mm']-nameplate.THICK,
             plan['center_z_mm'])
    rows.extend((('nameplate', body.translate(shift),
                  _colour(colours.chip_color('flavor'))),
                 ('nameplate-ink', ink.translate(shift),
                  _colour(colours.word_color('flavor')))))
    return tuple(rows)


def _nameplate_receiver(piece):
    receiver = nameplate.wing_interface.apply(
        piece, nameplate_station(), nameplate_plan()['face_y_mm'],
        up=-1, wall_face=above_core.specification()['rear_wall']['rear_wall']['ymin'],
        runout_lead=nameplate.wing_interface.RUNOUT_LEAD)
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


def apply(piece):
    """Cut the flush chips and carry the accepted nameplate on its plain field."""
    for station in stations():
        bottom = original.bottom(original.family(station['which']))
        cutter = port_chip.outline(
            WIDTH+2*fits.slip, rise()+fits.slip, bottom+fits.slip,
            THICK+1., station['floor_y_mm'],
            radius=port_chip.LOWER_CORNER_RADIUS+fits.slip)
        piece = piece.cut(cutter.translate((station['center_x_mm'], 0,
                                            station['center_z_mm'])))
    piece = _nameplate_receiver(piece)
    return piece.clean()


def plain_lands():
    """Keep the complete accepted retaining lips in the exterior print mesh."""
    return nameplate.wing_interface.plain_lips(
        nameplate_station(), nameplate_plan()['face_y_mm'])


def main():
    for which in STATIONS.values():
        fluid = original.FLUIDS[which]
        name = f'rear-label-{which}'
        assembly = cq.Assembly(name=name)
        assembly.add(chip(which), name=f'bulkhead-ring-{which}',
                     color=_colour(colours.chip_color(fluid)))
        assembly.add(word(which), name=f'bulkhead-ring-{which}-word',
                     color=_colour(colours.word_color(fluid)))
        step, stl = HERE / f'{name}.step', HERE / f'{name}.stl'
        export_assembly(assembly, str(step))
        native = chip(which).fuse(word(which)).clean()
        write_print_stl(native, stl, tol=.02, angle=.08)


if __name__ == '__main__':
    main()
