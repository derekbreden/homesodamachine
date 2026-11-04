"""What each material on this machine looks like with the lights on.

A body is coloured by what it is MADE OF, and every part of one material takes one constant here.
Both ends read these: the assembly that places a body, and the generator that cuts the body's own
STEP — so the same part is the same colour in the picture of the machine and in the picture of
itself.

EVERY PICTURE IN THIS REPO IS A PICTURE OF THE THING, not a diagram of it. A colour here is what
the part is, and nothing else may set one: not telling a piece from its neighbour, not seeing
through a wall, not holding a contrast ratio against the viewer's ground. Those are the viewer's
jobs and it has them — x-ray ghosts the whole model and draws every solid's feature edges
(web/public/js/viewer/xray.js), the component picker highlights the one you point at, and the
scorecard's rows select a body by name. A colour spent on any of that is a colour that lies
about the material, and the lie survives into every render the tree ships.

TRANSLUCENCY IS A MATERIAL PROPERTY TOO. The alpha on a constant here is carried because the
stock is see-through — the reservoirs' PETG Translucent Clear, their silicone washers, the
vent telltale's clear PVC, the reed's glass ampoule — and for no other reason.

A COLOUR IS THREE COMPONENTS by the time it is drawn: `_mesh_payload` hands over the RGB a STEP
carries and occt-import-js reads back the same three.
"""

import sys
from pathlib import Path
import cadquery as cq
from _shared_data import call, color_record
from _material_base import one_body, step_safe

_yw = Path(__file__).resolve().parents[1] / 'printed-parts/enclosure/y-wall-of-back-top'
if str(_yw) not in sys.path:
    sys.path.insert(0,str(_yw))
import _y_wall_dimensions as _rear

_CATALOG = call('color.catalog')
for _name,_args in _CATALOG['colors'].items():
    globals()[_name] = cq.Color(*_args)
for _name,_source in _CATALOG['aliases'].items():
    globals()[_name] = globals()[_source]
WALL_COLORS = {name:M_PETGF_BLACK for name in _CATALOG['wall_names']}
PETGF_BLACK_PARTS = set(_CATALOG['petgf_black_parts'])
_METAL, _DIELECTRIC = 1.0,0.0
FINISHES = [(globals()[name],rough,metal) for name,rough,metal in _CATALOG['finishes']]
_palette_args = call('color.palette_constructors',rgbs=[_rear.chip_color(f) for f in _rear.chip_filaments]
                     + [_rear.word_color(f) for f in _rear.chip_word_colors])
FINISHES.extend((cq.Color(*args),.85,0.0) for args in _palette_args)


def linear(color):
    record = color_record(color)
    if isinstance(color,str) and call('color.rgba',args=[color],kwargs={}) is None:
        record = color_record(cq.Color(color))
    return tuple(call('color.linear',color=record))


def petgf_color(name):
    value = call('color.petgf',name=name,
                 chip_colors={f:_rear.chip_color(f) for f in _rear.chip_filaments},
                 word_colors={f:_rear.word_color(f) for f in _rear.chip_word_colors})
    if value is None:
        return None
    return globals()[value['symbol']] if 'symbol' in value else cq.Color(*value['args'])


def _finish_inputs():
    return {'finishes':[[color_record(color),rough,metal] for color,rough,metal in FINISHES],
            'named':{name:color_record(globals()[name]) for name in [*_CATALOG['colors'],*_CATALOG['aliases']]}}


def finish_rows():
    return call('color.finish_rows',**_finish_inputs())
