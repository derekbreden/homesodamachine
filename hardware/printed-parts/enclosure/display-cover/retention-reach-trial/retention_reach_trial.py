"""Broad-leaf covers with 0.60 and 0.75 mm extra reach for the fixed v2 receiver."""
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent/'retention-trial'))
import retention_trial as base

ROOT = base.ROOT
VARIANTS = {'display-cover-retention-reach-060': .60,
            'display-cover-retention-reach-075': .75}


def shoulder(extra):
    return base.ROOT_DEPTH + base.cover.retention.LIP_START + extra


def tip(extra):
    return shoulder(extra) + base.LIP_LAND + base.NOSE_DEPTH


def skirt(side, extra):
    x = base.SKIRT_OUTER
    profile = [(x-base.WALL, -base.ROOT_DEPTH), (x, -base.ROOT_DEPTH),
               (x, -shoulder(extra)), (x+base.LIP, -shoulder(extra)),
               (x+base.LIP, -shoulder(extra)-base.LIP_LAND), (x, -tip(extra)),
               (x-base.WALL, -tip(extra))]
    wire = cq.Wire.makePolygon([cq.Vector(side*px, -base.SPAN/2, z)
                               for px, z in [*profile, profile[0]]])
    return cq.Solid.extrudeLinear(wire, [], cq.Vector(0, base.SPAN, 0))


def build_cover(extra):
    cover = base.cover
    bezel = cover.rounded_prism(cover.cover_x, cover.cover_slope,
                               cover.cover_corner_r, -base.ROOT_DEPTH, 0)
    window = cover.rounded_prism(cover.window_x, cover.window_slope,
                                cover.window_corner_r, -tip(extra)-1, 1)
    body = bezel.fuse(skirt(-1, extra), skirt(1, extra)).cut(window).clean()
    roots = [e for e in body.Edges() if e.geomType() == 'LINE'
             and abs(e.Length()-base.SPAN) < 1e-6
             and abs(abs(e.Center().x)-(base.SKIRT_OUTER-base.WALL)) < 1e-6
             and abs(e.Center().z+base.ROOT_DEPTH) < 1e-6]
    assert len(roots) == 2
    return body.fillet(base.ROOT_FILLET, roots).clean()


def main():
    for name, extra in VARIANTS.items():
        body = build_cover(extra)
        assert body.isValid() and len(body.Solids()) == 1
        out = HERE/(name+'.step')
        base.export_assembly(base.one_body(cq.Workplane(obj=body), name, base.M_PETGF_BLACK), str(out))
        body.copy(mesh=False).exportStl(str(out.with_suffix('.stl')), tolerance=.005,
                                      angularTolerance=.05, relative=False)
        base.note_write(out.with_suffix('.stl'))
        base.cut(out, out.with_suffix('.stl'))
        print(name, 'shoulder', shoulder(extra), 'tip', tip(extra))


if __name__ == '__main__':
    main()
