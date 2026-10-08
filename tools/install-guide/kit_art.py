#!/usr/bin/env python3
"""Draw the supplied kit as consistent, vector hidden-line views.

Mechanical items use the existing component models. The machine uses its current
envelope and display stations with small surface details suppressed. The coiled
cord, bag and booklet are presentation props, not dimensioned manufacturing CAD.
"""
from pathlib import Path
import json
import math
import os
import re
import sys

import cadquery as cq
from cadquery.occ_impl.exporters.svg import getPaths
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
from OCP.HLRAlgo import HLRAlgo_Projector
from OCP.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCP.BRepLib import BRepLib

ROOT = Path(__file__).resolve().parents[2]
HARDWARE = ROOT / 'hardware'
ART = HARDWARE / 'install-guide/assets/kit'
sys.path[:0] = [str(HARDWARE/'install-guide'),
               str(HARDWARE/'printed-parts/enclosure/enclosure')]
import _cad_art
import _install_art as shared
import _swept_top

CAMERA = (.8, -1, .7)


def compound(parts):
    return cq.Compound.makeCompound([p.val() if isinstance(p, cq.Workplane) else p
                                    for p in parts])


def assembly_shape(assembly, include=lambda name: True):
    return compound([child.obj for child in assembly.children if include(child.name)])


def machine():
    facts = json.loads(shared.MACHINE_FACTS.read_text())
    xmin, xmax, ymin, ymax, zmin, zmax = facts['box']['outer']
    profile = _swept_top.profile(facts['box']['outer'])
    side = [(ymin, zmin), (ymax, zmin), (ymax, zmax),
            (profile['roof'][0], zmax), profile['end'], profile['start']]
    shell = (cq.Workplane('YZ').polyline(side).close().extrude(xmax-xmin)
             .translate((xmin, 0, 0)))
    # The real enclosure seam separates its upper and lower printed shells.
    lower = shell.intersect(cq.Workplane('XY').box(1000, 1000, 200,
                                                  centered=(True, True, False)))
    upper = shell.intersect(cq.Workplane('XY').box(1000, 1000, 500,
                                                  centered=(True, True, False))
                            .translate((0, 0, 200.1)))
    plane = cq.Plane(origin=profile['origin'], xDir=(1, 0, 0), normal=profile['normal'])
    frame = cq.Workplane(plane).rect(132.7, 83.3).extrude(.8)
    screen = cq.Workplane(plane).rect(103.5, 62.1).extrude(1)
    a,b,c,d,e,f = facts['bodies']['funnel-cover']
    cover = (cq.Workplane('XY').box(d-a, e-b, f-c, centered=(True,True,False))
             .edges('|Z').fillet(5).translate(((a+d)/2, (b+e)/2, c)))
    return compound([lower, upper, frame, screen, cover])


def faucet_and_plate():
    faucet = _cad_art._load_faucet_module()
    parts = _cad_art._children_by_name(faucet.build_assembly())
    rest, _ = _cad_art._physical_levers(faucet)
    selected = []
    names = ['westbrass', 'drain_tube', 'display_signal_ribbon',
             'soda_faucet_tube', 'tpu_o_ring',
             'flavor_tube_pos_x', 'flavor_tube_neg_x', 'lever',
             'above_counter_plate', 'above_counter_gasket', 'shell_base',
             'shell_tip', 'faucet-display-cover-seated', 'faucet_display',
             'faucet_display_screen']
    for name in names:
        obj = rest if name == 'lever' else parts[name].obj
        if name in {'westbrass', 'drain_tube', 'display_signal_ribbon',
                    'flavor_tube_pos_x', 'flavor_tube_neg_x'}:
            obj = _cad_art._clip_z(obj, -110, 260)
        selected.append(obj)
    # Show the supplied slide-on plate beside the faucet, with both channels visible.
    plate = parts['under_counter_plate'].obj
    if isinstance(plate, cq.Workplane):
        plate = plate.val()
    plate = plate.translate((95, 0, -plate.BoundingBox().zmin-70))
    return compound([*selected, plate])


def tees():
    return assembly_shape(shared.s_two_tees())


def regulator():
    # Dial lettering and individual tick marks are too fine for a kit thumbnail.
    shape = assembly_shape(shared.s_regulator(), lambda name:
                           not any(suffix in name for suffix in
                                   ('black-print', 'red-print', 'band-')))
    washer = (cq.Workplane('XZ').center(-108, -62).circle(14).circle(10)
              .extrude(2))
    return compound([shape, washer])


def power_cord():
    body = cq.Workplane('XY').box(28, 35, 19).edges('|Z').fillet(3)
    nose = (cq.Workplane('XY').box(24, 15, 15).edges('|Z').fillet(2)
            .translate((0, -25, 0)))
    plug = body.union(nose)
    for x,z in [(-6, 0), (6, 0), (0, 4)]:
        plug = plug.cut(cq.Workplane('XY').box(2.4, 10, 4)
                        .translate((x, -31, z)))
    cord = shared._cable([(0,17,0),(0,43,0),(40,62,0),(80,35,0),
                          (40,0,0),(15,35,0),(65,55,0),(100,0,0)],
                         6.5, [(0,1,0),(0,-1,0)])
    mains = (cq.Workplane('XY').box(22, 28, 17).edges('|Z').fillet(3)
             .translate((100, -14, 0)))
    prongs = [cq.Workplane('XY').box(2, 12, 6).translate((100+x, -34, 2))
              for x in (-6, 6)]
    ground = shared._cyl(100, -40, -4, 4.5, 13, axis='Y')
    return compound([plug, cord, mains, *prongs, ground])


def book():
    pages = cq.Workplane('XY').box(90, 70, 4, centered=(True,True,False))
    lower = cq.Workplane('XY').box(92, 72, .6).translate((0,0,-.3))
    upper = cq.Workplane('XY').box(92, 72, .6).translate((0,0,4.3))
    spine = cq.Workplane('XY').box(.8, 72, 4).translate((-46,0,2))
    # A simple cover panel identifies this as the illustrated booklet.
    panel = cq.Workplane('XY').box(66, 45, .1).translate((0,0,4.66))
    return compound([pages, lower, upper, spine, panel])


def cold_kit():
    bag = (cq.Workplane('XY').box(90, 18, 104).edges('|Y').fillet(6)
           .translate((0,0,52)))
    zipper = cq.Workplane('XY').box(83, 20, 2).translate((0,0,93))
    tag = cq.Workplane('XY').box(50, .3, 27).translate((0,-9.3,48))
    return compound([bag, zipper, tag])


def line_svg(shape, camera):
    """Use world Z as up and bake all projection transforms into the SVG paths."""
    axis = gp_Ax2(gp_Pnt(), gp_Dir(*camera), gp_Dir(-camera[1], camera[0], 0))
    hlr = HLRBRep_Algo()
    hlr.Add(shape.wrapped)
    hlr.Projector(HLRAlgo_Projector(axis))
    hlr.Update()
    hlr.Hide()
    edges = HLRBRep_HLRToShape(hlr)
    visible = []
    for wrapped in [edges.VCompound(), edges.OutLineVCompound()]:
        if not wrapped.IsNull():
            BRepLib.BuildCurves3d_s(wrapped, 1e-6)
            visible.append(cq.Shape(wrapped))
    _, paths = getPaths(visible, [])
    points = [[(command, float(x), float(y)) for command, x, y in
               re.findall(r'([ML])([-+\d.eE]+),([-+\d.eE]+)', path)]
              for path in paths]
    flat = [p for edge in points for p in edge]
    left, right = min(p[1] for p in flat), max(p[1] for p in flat)
    bottom, top = min(p[2] for p in flat), max(p[2] for p in flat)
    scale = min(564/(right-left), 414/(top-bottom))
    ox, oy = (600-(right-left)*scale)/2, (450-(top-bottom)*scale)/2
    body = []
    for edge in points:
        path = ' '.join(f'{cmd}{ox+(x-left)*scale:.4f},{oy+(top-y)*scale:.4f}'
                        for cmd, x, y in edge)
        if path:
            body.append(f'<path d="{path}"/>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="600" height="450" '
            'viewBox="0 0 600 450">\n'
            '<g fill="none" stroke="#46515b" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round">\n'
            + '\n'.join(body) + '\n</g>\n</svg>\n')


def main():
    ART.mkdir(parents=True, exist_ok=True)
    objects = [
        ('machine', machine, CAMERA),
        ('faucet-and-plate', faucet_and_plate, (.95,-1,.55)),
        ('filtered-line', lambda: assembly_shape(shared.s_filter_in_cabinet()), CAMERA),
        ('water-tees', tees, (.6,-1,.65)),
        ('regulator-and-tether', regulator, (.15,1,.3)),
        ('collet-press', lambda: cq.importers.importStep(str(shared.COLLET_PRESS)).val(),
         (-.5,-.9,.85)),
        ('power-cord', power_cord, CAMERA),
        ('install-guide', book, CAMERA),
        ('cold-kit', cold_kit, CAMERA),
    ]
    for name, factory, camera in objects:
        print('Drawing', name, flush=True)
        shape = factory()
        svg = line_svg(shape, camera)
        (ART/f'{name}.svg').write_text(svg)
    print(f'{len(objects)} kit drawings written to {ART.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
