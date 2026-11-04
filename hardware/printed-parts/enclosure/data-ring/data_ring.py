"""Black DATA trim, white raised lettering, continuous nameplate wings."""
import json
import sys
from pathlib import Path

_hw=next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
sys.path[:0]=[str(Path(__file__).resolve().parent),str(_hw/'scripts'),
             str(_hw/'printed-parts/enclosure/enclosure'),
             str(_hw/'printed-parts/enclosure/bulkhead-ring'),
             str(_hw/'printed-parts/enclosure/y-wall-of-back-top')]
if __name__=='__main__':
    import _rust_part
    _rust_part.start()

import cadquery as cq
import _data_wing_interface as interface
import bulkhead_ring as ring
import _y_wall_dimensions as rear
from _cadq_export import export_assembly
from _materials import linear,step_safe

STEP=_hw/'printed-parts/enclosure/data-ring/data-ring.step'


def build_word():
    text=(cq.Workplane('XY').text('DATA',ring.WORD_SIZE,interface.INK_DEPTH+ring.WORD_RAISE,
                                font=ring.WORD_FONT,kind=ring.WORD_KIND,
                                halign='center',valign='center').val()
          .rotate((0,0,0),(1,0,0),90).rotate((0,0,0),(0,0,1),180))
    bb=text.BoundingBox()
    return text.translate((-(bb.xmin+bb.xmax)/2,
                           interface.THICK-interface.INK_DEPTH-bb.ymin,
                           (11.0+interface.TOP)/2-(bb.zmin+bb.zmax)/2))


def build_ring():
    return interface.blank().cut(build_word())


def build_part():
    assembly=cq.Assembly()
    for name,solid,color in [('data-ring',build_ring(),rear.chip_color('flavor')),
                             ('data-ring-word',build_word(),rear.word_color('flavor'))]:
        assembly.add(solid,name=name,color=step_safe(cq.Color(*(c/255 for c in color))))
    return assembly


def split(shape):
    return ring.split(shape)


def numbers():
    """The shared DATA trim datums, original glyph controls and filament colours."""
    from _cadq_export import note_read
    from _enclosure_data import dimensions, read
    artwork = STEP.parent/'data-word.json'
    note_read(artwork)
    def color(rgb):
        return linear(step_safe(cq.Color(*(c/255. for c in rgb))))
    values = dimensions()
    return read('data-recipe', data=values['data'], nameplate=values['nameplate'],
                bulkhead=values['bulkhead'], artwork_path=str(artwork),
                chip_color=color(rear.chip_color('flavor')),
                word_color=color(rear.word_color('flavor')))


def main():
    import _rust_part
    _rust_part.cut('enclosure-components','data-ring',numbers(),STEP.parent)


if __name__=='__main__':
    main()
