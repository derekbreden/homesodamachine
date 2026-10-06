#!/usr/bin/env python3
"""Qualify stationary image-plane jitter; never commands hardware."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np

def qualify(rows,config):
    good=[r for r in rows if r.get('physical') is True and r.get('valid') is True]
    if len(good)<300 or len(good)<.98*len(rows):raise ValueError('300 valid physical frames and >=98% valid coverage required')
    if (max(r['sample_ns'] for r in good)-min(r['sample_ns'] for r in good))<15_000_000_000:
        raise ValueError('At least 15 seconds of stationary observations required')
    values=np.asarray([r['values_mm'] for r in good],float)
    if values.shape[1:]!=(4,) or not np.isfinite(values).all():raise ValueError('Four finite coordinates required')
    error=values-np.median(values,axis=0)
    std=np.std(values,axis=0,ddof=1)
    if max(std)>.0025 or np.quantile(abs(error),.95)>.005 or np.max(abs(error))>.010:
        raise ValueError('Stationary jitter exceeds 0.0025mm sigma / 0.005mm p95 / 0.010mm max')
    scale=np.asarray(config['mm_per_pixel']*2,float)
    floor=max(.1,float(np.max(std/scale)))
    out=dict(config);out.update(stationary_sigma_px=floor,noise_qualified=True)
    receipt=dict(frame_count=len(good),sigma_mm=std.tolist(),p95_mm=float(np.quantile(abs(error),.95)),
                 maximum_mm=float(np.max(abs(error))),stationary_sigma_px=floor,
                 scope='Stationary projected image-plane jitter; does not certify scale bias or absolute endpoint accuracy')
    return out,receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('log');p.add_argument('config');p.add_argument('output');p.add_argument('--receipt',required=True);a=p.parse_args()
    raw=Path(a.log).read_bytes();cfg=json.loads(Path(a.config).read_text())
    out,receipt=qualify([json.loads(x) for x in raw.splitlines() if x.strip()],cfg)
    receipt['source_sha256']=hashlib.sha256(raw).hexdigest()
    encoded=(json.dumps(receipt,indent=2)+'\n').encode();out['noise_receipt_sha256']=hashlib.sha256(encoded).hexdigest()
    Path(a.receipt).write_bytes(encoded);Path(a.output).write_text(json.dumps(out,indent=2)+'\n')
