"""Require solid deposition through complete fastener hosts and their native roots.

These modifier boxes change infill within existing solids; they add no geometry.
They do not supply a pullout or drop strength allowable.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'tools/docgen').is_dir())
ENC = ROOT / 'hardware/printed-parts/enclosure/enclosure'
sys.path[:0] = [str(ROOT / 'hardware/scripts'), str(ENC)]
import enclosure as e
import _box_spec
from materialize_pump_cartridge import _declared_box


def main():
    box, _bounds, box_path = _declared_box(_box_spec, e)
    pieces = {name: [] for name in e.PIECE_COLORS}
    def region(piece, name, bounds):
        pieces[piece].append(dict(name=name, machine_bounds_mm=bounds,
                                 sparse_infill_density='100%', sparse_infill_pattern='zig-zag'))
    yb = e._y_boss(box.y_joint)
    for xi, xe, sx, z in box.y_bosses:
        _seat, tip, blind, cap = e._boss_x(xe, sx)
        col = 'top' if z > e.z_seam else 'bottom'
        low = z-e.socket_r if col=='top' else e._handhold_levels(box.inner)[1]
        high = box.outer[5] if col=='top' else e.z_seam
        xa, xb = sorted((xe, cap))
        region(f'front-{col}',f'Y seam socket and complete root {sx:+g}/{z:g}',
               [xa,xb,box.y_joint-e.wall,yb+e.socket_r,low,high])
        xa, xb = sorted((xe,tip))
        region(f'back-{col}',f'Y seam shank and fore ligament {sx:+g}/{z:g}',
               [xa,xb,box.y_joint,box.y_joint+e.lip_len+2.0,low,high])
    for col, y0, y1 in (('front',box.outer[2],box.y_joint),('back',box.y_joint,box.outer[3])):
        for sx in (-1,1):
            xa,xb=sorted((sx*90.0,sx*107.5))
            for level in ('top','bottom'):
                region(f'{col}-{level}',f'Z rail, end stop and wall root {sx:+g}',
                       [xa,xb,y0,y1,e.z_seam-e.wall,e.z_seam+e.z_rise+e.wall])
    for y,z,tip,*_ in box.pack.east_bosses:
        name=('front' if y<=box.y_joint else 'back')+('-top' if z>e.z_seam else '-bottom')
        root=e.piece_root_faces(box.inner,*name.split('-'))[1]
        radius=e.mount_boss_dia/2.0
        region(name,f'Electronics host and wall root {y:g}/{z:g}',
               [min(tip,root),box.outer[1],y-radius,y+radius,
                z-radius-abs(root-tip),z+radius])
    for x,y,tip,_dia in box.pack.floor_bosses:
        radius=e.floor_heatset_dia/2.0+2.6
        region('front-bottom' if y<=box.y_joint else 'back-bottom',f'Compressor post and floor {x:g}/{y:g}',
               [x-radius,x+radius,y-radius,y+radius,box.outer[4],tip])
    for x,y,tip in box.pack.cond_mount[-1]:
        region('front-bottom',f'Condenser host and supporting finger {x:g}/{y:g}',
               [x-5,x+5,y-5,y+5,box.outer[4],tip])
    fore=box.outer[3]-e.socket_cap-e.c14_tunnel_len
    for x,z in box.pack.c14:
        region('back-top',f'C14 host and wall {x:g}',
               [x-5,x+5,fore,box.outer[3],z-5,z+5])
    split=e.cap_split_z(box.pack.pump_trays)
    lane = min(abs(cx) for cx, _cy, _cz in box.pack.pump_trays) - e._tray.boss_half - e.cap_boss_air
    for y in e.cap_screw_ys(box.inner,box.pack.collet_plate):
        region('pump-cartridge',f'Clamp insert and complete spine root {y:g}',
               [-lane,lane,y-5,y+5,e.bay_floor_z(box.pack.pump_trays)[1],split])
    x,z=e.pump_contact_station(box)
    for name,face,sgn in (('front-top',e.bay_back_y(box.pack.collet_plate),1),
                          ('pump-cap',e.pump_cartridge_aft_y(box.pack.pump_trays,box.pack.collet_plate),-1)):
        back=face+sgn*(e._pogo.ear_back()+e.pogo_heatset_setback+
                       e.pogo_heatset_len+e.pogo_heatset_relief+e.wall)
        ya,yc=sorted((face,back))
        region(name,'Both pogo insert hosts, entry steps and blind caps',
               [x-15,x+15,ya,yc,z-2.75,z+2.75])
    paths=[Path(__file__),ENC/'enclosure.py',ENC/'_enclosure_interface.py',box_path]
    report=dict(scope='Local 100% infill modifiers in existing native material; complete insert hosts, blind caps, roots and seam load paths. No load capacity or lifetime qualification.',
                source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                native_artifact_sha256={name:{suffix:hashlib.sha256((ENC/f'enclosure-{name}{suffix}').read_bytes()).hexdigest()
                                             for suffix in ('.step','.stl')} for name in pieces},pieces=pieces)
    (Path(__file__).parent/'print-regions.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':
    main()
