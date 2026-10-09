"""Accepted face-up display bezel with coplanar horizontal retaining wings.

The visible face is local Z=0. The back and both wings share one flat bed plane.
The TPU ring separates the bezel from the glass.
"""
import sys
from pathlib import Path
import cadquery as cq

_here=Path(__file__).resolve()
_hw=next(p for p in _here.parents if p.name=='hardware')
for directory in (_hw/'scripts',_hw/'printed-parts/enclosure/enclosure',_hw.parent/'tools'):
    sys.path.insert(0,str(directory))
from _cadq_export import export_assembly
from _materials import M_PETGF_BLACK,one_body
from docgen import substitute_md
import _enclosure_interface as dims
import _display_wing_interface as wings
# Retained for the separately archived vertical-leaf trial generators.
import _display_retention as retention
from _swept_top import rounded_prism

cover_x,cover_slope,cover_corner_r=wings.COVER_X,wings.COVER_Y,wings.CORNER_R
cover_slip=wings.BODY_X_AIR
window_x,window_slope,window_corner_r=wings.WINDOW_X,wings.WINDOW_Y,wings.WINDOW_R


def build_display_cover():
    return cq.Workplane(obj=wings.cover())


def selftest():
    body=build_display_cover().val()
    assert body.isValid() and len(body.Solids())==1
    print('Display cover: one valid solid.')
    return 0


def main():
    selftest()
    out=_here.parent/'display-cover.step'
    body=build_display_cover()
    export_assembly(one_body(body,'display-cover',M_PETGF_BLACK),str(out))
    body.val().copy(mesh=False).exportStl(str(out.with_suffix('.stl')),
        tolerance=.005,angularTolerance=.05,relative=False)
    from flute_payload import cut
    cut(out,out.with_suffix('.stl'))
    substitute_md(_here.parent/'README.md',variables={
        'COVER_X':f'{cover_x:g} mm','COVER_SLOPE':f'{cover_slope:g} mm',
        'COVER_CORNER_R':f'{cover_corner_r:g} mm','COVER_T':f'{wings.THICK:g} mm',
        'WINDOW_X':f'{window_x:g} mm','WINDOW_SLOPE':f'{window_slope:g} mm',
        'WINDOW_CORNER_R':f'{window_corner_r:g} mm'})
    print('-> display-cover.step, display-cover.stl, README.md')


if __name__=='__main__':
    sys.exit(selftest() if len(sys.argv)>1 and sys.argv[1]=='selftest' else main())
