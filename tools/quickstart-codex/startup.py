#!/usr/bin/env python3
"""Draw the cylinder handwheel, regulator controls and pressurised upper gauge."""
import json
import math

import cadquery as cq

import scenes


OUT = scenes.HARDWARE / 'quickstart-codex/out/startup'
ART = scenes.HARDWARE / 'quickstart-codex/art'
CAM = (.08, 1, .12)
TARGET = (-35, 0, -4.5)
SPAN = 103.5
SIZE = (1800, 1200)
OUTLET_PSI = 80
CYLINDER_PSI = 800
reg = scenes.reg


def dial_print(child, centre, pressure, full):
    """The dial's scale and a needle at the illustrated pressure."""
    face_y = reg.GAUGE_FACE_Y + reg.PRINT_T
    marks = [solid for solid in child.obj.Solids()
             if solid.BoundingBox().ymin < face_y - 1e-5]
    plane = (cq.Workplane(reg._dial_plane).workplane(offset=face_y)
             .center(-centre[0], centre[2]))
    marks.append(reg._needle(reg._scale_deg(pressure, full), plane))
    return cq.Compound.makeCompound(marks)


def assembly():
    """The fitted regulator and top of the customer's cylinder."""
    result = cq.Assembly(name='startup-gas')
    for child in scenes.cylinder().children:
        if child.name == 'outlet-black-print':
            obj = dial_print(child, reg.outlet_dial()[0], OUTLET_PSI, reg.OUTLET_FULL_PSI)
            result.add(obj, name=child.name, color=child.color)
        elif child.name == 'tank-black-print':
            obj = dial_print(child, reg.tank_dial()[0], CYLINDER_PSI, reg.TANK_FULL_PSI)
            result.add(obj, name=child.name, color=child.color)
        else:
            result.add(child)
    return result


def points():
    angle = math.radians(reg._scale_deg(OUTLET_PSI, reg.OUTLET_FULL_PSI))
    return {
        'upper-gauge': reg.outlet_dial()[0],
        'upper-needle-tip': (-reg.NEEDLE_R * math.cos(angle),
                             reg.GAUGE_FACE_Y + reg.PRINT_T + .8,
                             reg.GAUGE_REACH + reg.NEEDLE_R * math.sin(angle)),
        'big-pressure-knob': reg.adjustment()[0],
        'small-gas-knob': reg.shutoff()[0],
        'cylinder-handwheel': (-115, 0, 33),
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ART.mkdir(exist_ok=True)
    scenes.OUT, scenes.ART, scenes.jobs = OUT, ART, []
    scenes.stage('startup-gas', assembly(), CAM, TARGET, SPAN,
                 size=f'{SIZE[0]}x{SIZE[1]}')
    scenes.render()
    metadata = dict(cam=CAM, target=TARGET, span=SPAN, size=SIZE,
                    outlet_psi=OUTLET_PSI, cylinder_psi=CYLINDER_PSI,
                    points=points())
    (OUT / 'points.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps(metadata, indent=2))


if __name__ == '__main__':
    main()
