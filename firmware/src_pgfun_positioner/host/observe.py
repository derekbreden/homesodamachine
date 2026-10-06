#!/usr/bin/env python3
"""One camera; actual wire endpoint, aiming dot and seam in the same frame."""
import argparse
import hashlib
import json
import math
import os
import queue
import sys
import time
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/gun-positioner-observation'))
from gpobs.helper_stream import HelperSource,list_cameras
from gpobs.capture import RawFrame
from gpobs.features import AimingDot,WireTip,SeamLine,roi_center
from gpobs.imageio import decode_jpeg,nv12_to_rgb,split_nv12

def extract(image,config):
    dot=AimingDot(**config['dot']).run(image)
    wire=WireTip(**config['wire']).run(image)
    seam=SeamLine(**config['seam']).run(image)
    record={'valid':False,'diagnostics':{n:{'valid':r.valid,'reason':r.reason,'confidence':r.confidence,'details':r.diagnostics}
                                       for n,r in [('dot',dot),('wire',wire),('seam',seam)]}}
    record['features']={n:{'values':r.values,'sigma':r.sigma} for n,r in [('dot',dot),('wire',wire),('seam',seam)]}
    if not all(r.valid and r.confidence>=.5 for r in (dot,wire,seam)):return record
    # With significant clipped dots, centroid confidence cannot qualify motion.
    if dot.diagnostics.get('saturated_pixels',0)>0:return record
    theta=math.radians(seam.values['theta_deg']);n=np.array([math.cos(theta),math.sin(theta)]);t=np.array([n[1],-n[0]])
    center=np.asarray(roi_center(config['seam'].get('roi'),image.shape));values=[];sigmas=[]
    scale=np.asarray(config['mm_per_pixel'],float)
    if scale.shape!=(2,) or not np.isfinite(scale).all() or min(scale)<=0:raise ValueError('Calibrated tangent/normal scales required')
    for r in (dot,wire):
        point=np.asarray([r.values['u'],r.values['v']])-center
        values.extend([(point@t)*scale[0],(point@n-seam.values['rho'])*scale[1]])
        # Empirical stationary jitter floor takes precedence over extractor estimates.
        # Seam angle uncertainty grows with distance from the ROI origin.
        su,sv=r.sigma['u'],r.sigma['v'];sth=math.radians(seam.sigma['theta_deg'])
        st=math.sqrt((t[0]*su)**2+(t[1]*sv)**2+((point@n)*sth)**2)
        sn=math.sqrt((n[0]*su)**2+(n[1]*sv)**2+seam.sigma['rho']**2+((point@t)*sth)**2)
        floor=config['stationary_sigma_px']
        sigmas.extend([max(floor,st)*scale[0],max(floor,sn)*scale[1]])
    record.update(valid=True,values_mm=values,sigma_mm=sigmas,
                  noise_qualified=config.get('noise_qualified',False))
    return record

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--list',action='store_true');p.add_argument('--camera-id');p.add_argument('--config');p.add_argument('--latest');p.add_argument('--log');p.add_argument('--seconds',type=float,default=3600);args=p.parse_args()
    if args.list:print(json.dumps(list_cameras(),indent=2));raise SystemExit()
    if not all([args.camera_id,args.config,args.latest,args.log]):p.error('--camera-id --config --latest --log required')
    cfg=json.loads(Path(args.config).read_text())
    config_hash=hashlib.sha256(Path(args.config).read_bytes()).hexdigest()
    if not cfg.get('manual_focus') or not cfg.get('manual_exposure') or cfg.get('auto_tracking',True):raise SystemExit('Lock focus, exposure, pan and tracking before measuring')
    if not all(cfg[n].get('roi') for n in ('dot','wire','seam')):raise SystemExit('Measured ROIs required for the actual dot, wire endpoint and seam')
    source=HelperSource('weld-view',args.camera_id,chroma=True,mode='open');source.start()
    deadline=time.monotonic()+args.seconds;last_seq=None
    try:
        with open(args.log,'a') as log:
            while time.monotonic()<deadline:
                try:item=source.read(.2)
                except queue.Empty:continue
                if item is None:break
                if not isinstance(item,RawFrame):continue
                now=time.monotonic_ns();stamp=item.device_pts_ns or item.source_host_ns
                if (item.width,item.height)!=(3840,2160):record={'valid':False,'reason':'requires_native_3840x2160'}
                elif not stamp or not 0<=now-stamp<=200_000_000:record={'valid':False,'reason':'stale_frame'}
                else:
                    if item.codec=='nv12':stack=np.frombuffer(item.payload,dtype=np.uint8).reshape(item.height*3//2,item.width);y,uv=split_nv12(stack,item.height);image=nv12_to_rgb(y,uv)
                    elif item.codec=='jpeg':image=decode_jpeg(item.payload)
                    elif item.codec=='gray8':image=np.asarray(item.payload)
                    else:record={'valid':False,'reason':'unsupported_codec'};image=None
                    if image is not None:record=extract(image,cfg)
                if last_seq is not None and item.source_seq!=last_seq+1:record.update(valid=False,reason='frame_gap')
                last_seq=item.source_seq;record.update(physical=True,sample_ns=stamp,receive_ns=now,frame_seq=item.source_seq,camera_id=args.camera_id,optics_config_sha256=config_hash)
                log.write(json.dumps(record,separators=(',',':'))+'\n');log.flush()
                path=Path(args.latest);tmp=path.with_suffix('.new');tmp.write_text(json.dumps(record));os.replace(tmp,path)
    finally:source.stop()
