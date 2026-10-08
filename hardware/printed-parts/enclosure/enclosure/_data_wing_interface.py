"""Flush DATA trim with flat-back side snaps; millimetres in the jack frame.

The fixed enclosure receptacle carries the purchased jack. The removable trim
has its own lateral flexures and does not carry the keystone catches or lip.
Y=0 is the trim's flat print-bed back; +Y is the customer-facing direction.
"""
import sys
from pathlib import Path

import cadquery as cq

_hw = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
sys.path[:0] = [str(_hw/'printed-parts/cadlib')]
import fits
import port_chip

WIDTH = 32.0
TOP = 18.789
BOTTOM = 11.0
THICK = 3.36
OPENING_W = 20.8
OPENING_H = 18.3
OPENING_R = .4
WING_THICK = 1.68
PROJECTION = 1.9
STEM_WIDTH = 1.2
STEM_INNER = WIDTH/2-STEM_WIDTH
ROOT_Z = 12.0
ROOT_OVERLAP = 3.0
ROOT_RADIUS = .6
TIP_LOW = -8.4
TIP_HIGH = -6.0
FLEXURE_INNER = 12.0
FLEXURE_BOTTOM = -9.6
FACE_AIR = fits.slip
TIP_AIR = .25
END_AIR = fits.slip
THICKNESS_AIR = .48
SUPPORTED_AIR = fits.supported_surface
FLOOR_STOCK = 3.6
ENTRY_WIDTH = .75
ENTRY_DEPTH = .4
MAX_DEFLECTION = 2.4


def box(x0,x1,y0,y1,z0,z1):
    return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))


def mirrored(shape, side):
    return shape if side>0 else shape.mirror('YZ')


def aperture(y0,y1):
    return (cq.Workplane('XY').rect(OPENING_W,OPENING_H).extrude(y1-y0)
            .edges('|Z').fillet(OPENING_R).val()
            .rotate((0,0,0),(1,0,0),-90).translate((0,y0,0)))


def blank():
    """One flat-back solid with in-plane side flexures and no enclosed bridges."""
    plate = port_chip.outline(WIDTH,TOP,BOTTOM,THICK).cut(aperture(-.01,THICK+.01))
    slot_roof = WING_THICK+THICKNESS_AIR
    for side in (-1,1):
        relief=box(FLEXURE_INNER,WIDTH/2+.01,-.01,THICK+.01,
                   FLEXURE_BOTTOM,ROOT_Z)
        plate=plate.cut(mirrored(relief,side))
        stem=box(STEM_INNER,WIDTH/2,0,THICK,TIP_LOW,ROOT_Z+ROOT_OVERLAP)
        # A tangent R0.6 root joins the in-plane cantilever to the top crossbar.
        root=box(STEM_INNER-ROOT_RADIUS,STEM_INNER,0,THICK,
                 ROOT_Z-ROOT_RADIUS,ROOT_Z)
        round_cut=cq.Solid.makeCylinder(ROOT_RADIUS,THICK+.02,
                     cq.Vector(STEM_INNER-ROOT_RADIUS,-.01,ROOT_Z-ROOT_RADIUS),
                     cq.Vector(0,1,0))
        root=root.cut(round_cut)
        # The nose decreases toward the face; it grows no unsupported print edge.
        barb=(cq.Workplane('XY').workplane(offset=TIP_LOW)
              .polyline([(WIDTH/2-.1,0),(WIDTH/2+PROJECTION,0),
                         (WIDTH/2+PROJECTION,WING_THICK-.4),
                         (WIDTH/2+PROJECTION-.4,WING_THICK),
                         (WIDTH/2-.1,WING_THICK)]).close().extrude(TIP_HIGH-TIP_LOW).val())
        plate=plate.fuse(mirrored(stem.fuse(root).fuse(barb),side))
    return plate


def apply(solid,station,y_outer,*,up=-1,supported=SUPPORTED_AIR):
    """Decorative trim pocket and independently backed lateral retaining lips."""
    x,z=station
    floor=y_outer-THICK
    shift=(x,floor,z)
    outer_width=WIDTH+2*(PROJECTION+TIP_AIR+3)
    pad=port_chip.outline(outer_width,TOP+3,BOTTOM+3,THICK+FLOOR_STOCK,
                         y0=-FLOOR_STOCK,radius=port_chip.LOWER_CORNER_RADIUS+3)
    edge=TOP+3 if up<0 else -BOTTOM-3
    ramp=(cq.Workplane('YZ',origin=(-outer_width/2-.01,0,0))
          .polyline([(-FLOOR_STOCK,edge),(-FLOOR_STOCK,edge+up*FLOOR_STOCK),(0,edge)])
          .close().extrude(outer_width+.02).val())
    solid=solid.fuse(pad.cut(ramp).translate(shift))
    mouth=port_chip.outline(WIDTH+2*FACE_AIR,TOP+FACE_AIR,BOTTOM+FACE_AIR,
                           THICK+1,radius=port_chip.LOWER_CORNER_RADIUS+FACE_AIR)
    mouth=mouth.fuse(mouth.translate((0,0,up*supported)))
    solid=solid.cut(mouth.translate(shift))
    z0=TIP_LOW-END_AIR+min(0,up*supported)
    z1=TIP_HIGH+END_AIR+max(0,up*supported)
    for side in (-1,1):
        slot=box(WIDTH/2-.1,WIDTH/2+PROJECTION+TIP_AIR,0,
                 WING_THICK+THICKNESS_AIR,z0,z1)
        lead=(cq.Workplane('XY').workplane(offset=z0)
              .polyline([(WIDTH/2+FACE_AIR,WING_THICK+THICKNESS_AIR),
                         (WIDTH/2+FACE_AIR+ENTRY_WIDTH,WING_THICK+THICKNESS_AIR),
                         (WIDTH/2+FACE_AIR,WING_THICK+THICKNESS_AIR+ENTRY_DEPTH)])
              .close().extrude(z1-z0).val())
        solid=solid.cut(mirrored(slot.fuse(lead),side).translate(shift))
        # A tool reaches the back of each snap from inside the enclosure.
        # Its diamond crown is self-supporting in the back-top print orientation.
        access=(cq.Workplane('XZ').center(side*(STEM_INNER+STEM_WIDTH/2),(TIP_LOW+TIP_HIGH)/2)
                .polyline([(-1.2,0),(0,2.8),(1.2,0),(0,-2.8)])
                .close().extrude(FLOOR_STOCK+.5).val())
        solid=solid.cut(access.translate(shift))
    return solid


def plain_lips(station,y_outer):
    """Keep the complete 1.20 mm retention lip through the decorative flutes."""
    x,z=station
    fields=[]
    for side in (-1,1):
        lo,hi=sorted((side*(WIDTH/2+FACE_AIR),side*(WIDTH/2+PROJECTION+TIP_AIR)))
        fields.append((x+lo-.4,x+hi+.4,y_outer-THICK,y_outer+1,
                       z+TIP_LOW-END_AIR-SUPPORTED_AIR-.4,z+TIP_HIGH+END_AIR+.4))
    return tuple(fields)


def strain_screen():
    """Linear cantilever screening, not an established load or cycle-life result."""
    shortest=ROOT_Z-ROOT_RADIUS-TIP_HIGH
    required=PROJECTION-FACE_AIR+FACE_AIR
    return {'minimum_free_length_mm':shortest,'stem_width_mm':STEM_WIDTH,
            'stem_print_height_mm':THICK,'barb_print_height_mm':WING_THICK,'root_radius_mm':ROOT_RADIUS,
            'maximum_required_deflection_mm':required,
            'screened_deflection_mm':MAX_DEFLECTION,
            'nominal_peak_outer_strain':1.5*STEM_WIDTH*MAX_DEFLECTION/shortest**2,
            'scope':'Small-deflection in-plane cantilever estimate; root concentrations, anisotropy, fit force and endurance are not measured.'}
