"""Exact native rear-corner funnel joint used as a removable plumbing lid.

The whole rear rail, its lead and stop, mating receiver, 30 degree corbel and
concentric rear brim quadrant are retained at 1:1.  The section cuts pass
through the unloaded interior field ahead/inboard of that quadrant.  Broad
3 mm closures make this an actual lid section, not a thin cropped edge.
Production CAD and materials are inputs. Geometry exports use the reference cache.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import enclosure_features as native


def build():
    e,b = native.source()
    ff = e._funnel_frame_part
    f = e._funnel
    centre = tuple(b.pack.funnel)
    seat = e.funnel_seat_z(b.outer)
    floor,plug,rail = ff.datums(seat)
    joint_y = b.y_joint
    # Native back corner is small while containing the complete active joint.
    # The R20/R27 collar/brim turns start beyond these section boundaries.
    x0,y0 = 50.,joint_y
    source_back = centre[1]+ff.depth/2.
    crop_bounds = (x0,b.outer[1]+1.,y0,source_back+1.,floor-1.,seat+f.brim_thickness+1.)
    crop = native.box(crop_bounds)
    frame_path = native.PP/'zone-c/funnel/funnel-frame.step'
    frame_native = cq.importers.importStep(str(frame_path)).val().translate((0,ff.center_y,floor))
    frame = frame_native.intersect(crop)

    # Close only the empty source field.  These end walls do not reach the
    # native curved quadrant or rail's X working section.
    interior_close = native.box((x0,x0+3.,y0,source_back,
                                  floor,seat))
    section_close = native.box((x0,95.25,y0,y0+3.,
                                floor,seat))
    native_blank = ff.body_blank(centre,seat,inner=b.inner,y_joint=joint_y)
    closures = interior_close.fuse(section_close).intersect(native_blank)
    frame = frame.fuse(closures).clean()

    # Same source rear receiver and channel; 3 mm rear/outboard/roof stock
    # is a parent cabinet wall section, not a detachable storage holder.
    receivers = ff.receivers(b.inner,b.outer,joint_y,centre,seat,'back').intersect(crop)
    outer_wall = native.box((b.outer[1]-3.,b.outer[1],y0,source_back,
                             floor,seat+f.brim_thickness))
    rear_wall = native.box((x0,b.outer[1],source_back-3.,source_back,
                            floor,seat+f.brim_thickness))
    roof = native.box((x0,b.outer[1],y0,source_back,
                       seat+f.brim_thickness-3.,seat+f.brim_thickness))
    stock = receivers.fuse(outer_wall).fuse(rear_wall).fuse(roof)
    runs = ff.rail_runs(b.inner,joint_y,'back',centre)
    channel = e._z_rail_channels(b.inner,joint_y,rail,'back',None,runs=runs)
    source_frame_room = ff.shell_clearance(centre,seat,b.inner,joint_y)
    brim_room = f._rounded_box(
        f.collar_w+2*(f.brim_overhang+e.funnel_collar_air),
        f.collar_d+2*(f.brim_overhang+e.funnel_collar_air),
        f.brim_corner_r+e.funnel_collar_air,
        seat,seat+f.brim_thickness+1.,*centre)
    # The source body clearance leaves its supported rail/catch stock; the
    # separately supplied channel opens only the actual rail cross-section.
    for room in (source_frame_room,brim_room,channel):
        stock = stock.cut(room)
    stock = stock.clean()
    origin = (x0,y0,floor)
    return native._feature(
        'complete_rear_funnel_joint',('E20','E21','E25','E29','E50'),origin=origin,
        add={'cabinet_rear_receiver_and_roof':stock},
        cut={'native_body_room':source_frame_room.intersect(crop),
             'native_brim_room':brim_room.intersect(crop),
             'complete_back_rail_channel':channel.intersect(crop)},
        parts={'removable_plumbing_lid':frame},
        source_print_up=(0,0,-1),part_print_up={'removable_plumbing_lid':(0,0,1)},
        functions=('_z_rail_heads','_z_rail_channels'),
        files=(native.PP/'zone-c/funnel/funnel_frame.py',frame_path),
        backing={'section_cut_planes_source_mm':{'X':x0,'Y':y0},
                 'ordinary_closing_stock_mm':3.,
                 'native_bearing_web_mm':ff.web,
                 'native_corbel_angle_degrees':30.,
                 'native_brim_r_mm':f.brim_corner_r,
                 'native_collar_r_mm':f.collar_corner_r,
                 'source_brim_overhang_mm':f.brim_overhang,
                 'source_forming_air_mm':ff.forming_air,
                 'brim_seat_local_z_mm':seat-floor,
                 'native_broad_receiver_height_mm':ff.receiver_height,
                 'rail_mouth_local_z_mm':rail-floor,
                 'running_air_mm':e.slide_slip,
                 'back_catch_air_mm':e.rail_catch_air('back'),
                 'closed_stop_length_mm':e.rail_stop_len-e.slide_slip,
                 'open_lead_length_mm':e.rail_lead,
                 'complete_native_back_run_source_mm':runs[1],
                 'native_outline_source_mm':crop_bounds},
        bearing={'active_section':'whole native rear rail and complete R27 rear-quarter brim turn',
                 'unmodified_active_x_min_source_mm':62.5,
                 'unmodified_active_y_min_source_mm':centre[1]+f.collar_d/2.-f.collar_corner_r,
                 'closures_end_source_mm':{'X':53.,'Y':203.,'rail_side_X':95.25},
                 'removal_route':'remove front-top, withdraw drawer, release grip and Y fasteners, set front-bottom aside; slide local -Y37mm, then lift +Z' ,
                 'rail_disengagement_mm':runs[1][2]-joint_y,
                 'source_frame_clear_slide_mm':36.,
                 'assembly_clear_slide_mm':37.,
                 'review_scope':'zero receiver overlaps at twelve sampled -Y positions from 0 through 45 mm; final cabinet furniture clearance remains parent-owned'},
        mates=('source-profile square rail head and complete slipped receiver',
               'native concentric silicone collar/brim quadrant; full silicone bowl is not recreated'),
        group='back-top plumbing roof; source joint is the removable lid',
        notes=('The full rear rail is retained; no engagement length, open lead, stop or catch is cropped.',
               'The source front pair is repeated hardware and is outside this exact rear-corner section.',
               'Native +Z frame and -Z receiver print directions remain; broad supported catch faces need the source support recipe.',
               'Final cabinet seating/removal clearance is layout-specific. Physical force, retention and cleanup of this section are unprinted.'))


if __name__=='__main__':
    result = build()
    out = native.ROOT/'.cache/the-pour-v3/funnel-joint'
    out.mkdir(parents=True,exist_ok=True)
    assembly = cq.Assembly(name='complete-source-funnel-joint')
    for kind in ('add','parts'):
        for name,shape in getattr(result,kind).items():
            cq.exporters.export(shape,str(out/(name+'.step')))
            cq.exporters.export(shape,str(out/(name+'.stl')),tolerance=.015,angularTolerance=.08)
            assembly.add(shape,name=name,color=cq.Color(.15,.16,.17))
    from _cadq_export import export_assembly
    export_assembly(assembly,str(out/'joint-assembly.step'))
    (out/'metadata.json').write_text(json.dumps(result.report(),indent=2)+'\n')
    print(json.dumps(result.report(),indent=2),flush=True)
