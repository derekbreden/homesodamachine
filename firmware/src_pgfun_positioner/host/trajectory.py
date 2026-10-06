#!/usr/bin/env python3
"""Learn a periodic correction from dry rotations and replay it from the pedal."""
import argparse
import hashlib
import json
import math
import time
from pathlib import Path
import numpy as np
from kinematics import GEOMETRY_SHA, COUNTS_PER_REV, SOFT_LIMIT, WORKING_LEVER
from servo import observation

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def period_for_speed(speed):
    if not 5<=speed<=15:raise ValueError('Existing rotator accepts 5..15mm/s')
    # Matches the existing controller's rounded half-period and 14,400 pulses/rev.
    half=math.floor(500000*math.pi*123.698/(speed*14400)+.5)
    return 2*half*14400

def controls(knots):
    p=np.asarray(knots,dtype=np.int64)
    return np.stack((6*p,6*p+np.roll(p,-1,axis=0)-np.roll(p,1,axis=0),
                     6*np.roll(p,-1,axis=0)-np.roll(p,-2,axis=0)+p,6*np.roll(p,-1,axis=0)),axis=1)

def check(profile):
    if profile.get('geometry_sha256')!=GEOMETRY_SHA:raise ValueError('Trajectory geometry mismatch')
    p=np.asarray(profile['knots'])
    if p.shape[1:]!=(2,) or not 16<=len(p)<=256 or p.dtype.kind not in 'iu':raise ValueError('16..256 integer two-axis knots required')
    period=profile['period_us']
    if isinstance(period,bool) or not isinstance(period,int) or not 8_000_000<=period<=120_000_000:raise ValueError('Trajectory period must be 8..120s')
    b=controls(p);dt=period//len(p)
    if np.max(abs(b))>6*SOFT_LIMIT:raise ValueError('Cubic control envelope exceeds joint travel')
    if np.max(abs(np.diff(b,axis=1)))*len(p)*1_000_000>2*1000*period:raise ValueError('Trajectory rate exceeds 1000 counts/s')
    if np.max(abs(np.diff(b,n=2,axis=1)))*1_000_000_000_000>4000*dt*dt:raise ValueError('Trajectory acceleration exceeds 4000 counts/s²')
    return profile

def evaluate(profile,phase):
    p=np.asarray(profile['knots'],float);f=(np.asarray(phase)%1)*len(p);i=np.floor(f).astype(int);u=f-i
    h00=2*u**3-3*u**2+1;h10=u**3-2*u**2+u;h01=-2*u**3+3*u**2;h11=u**3-u**2
    return (p[i]*h00[...,None]+(p[(i+1)%len(p)]-p[(i-1)%len(p)])*h10[...,None]/2+
            p[(i+1)%len(p)]*h01[...,None]+(p[(i+2)%len(p)]-p[i])*h11[...,None]/2)

def rows_for_fit(record):
    rows=record['rows']
    if not record.get('physical') or len(rows)<512:raise ValueError('At least 512 physical observations from two dry revolutions required')
    if max(r['elapsed_s'] for r in rows)<2*record['profile']['period_us']/1e6:raise ValueError('Capture at least two complete revolutions')
    for r in rows:
        if not r.get('valid') or max(r['sigma_mm'])>.0025 or r['clock_uncertainty_ms']>5:raise ValueError('Invalid or uncertain dry-run observation')
        if r.get('optics_config_sha256')!=record.get('optics_config_sha256'):raise ValueError('Dry capture optical configuration changed')
    bins=np.bincount((np.asarray([r['phase'] for r in rows])*64).astype(int)%64,minlength=64)
    if min(bins)<3:raise ValueError('Every phase bin needs three independent observations')
    return rows

def fit(record,model,target,harmonics=3):
    check(record['profile']);rows=rows_for_fit(record)
    if not model.get('qualified') or not model.get('physical') or model['geometry_sha256']!=GEOMETRY_SHA:raise ValueError('Qualified physical motor-response model required')
    if not target.get('physical') or len(target['values_mm'])!=4:raise ValueError('A measured four-value working target is required')
    if record.get('optics_config_sha256')!=model.get('optics_config_sha256') or target.get('optics_config_sha256')!=model.get('optics_config_sha256'):
        raise ValueError('Response, target and dry capture must use the same fixed optics')
    phase=np.asarray([r['phase'] for r in rows]);y=np.asarray([r['values_mm'] for r in rows]);goal=np.asarray(target['values_mm'],float)
    def basis(x):
        return np.stack([np.ones_like(x)]+[f(2*math.pi*k*x) for k in range(1,harmonics+1) for f in (np.cos,np.sin)],axis=-1)
    if not 1<=harmonics<=6:raise ValueError('1..6 spatial harmonics required')
    coef=np.linalg.lstsq(basis(phase),y,rcond=None)[0]
    smooth_residual=y-basis(phase)@coef
    if np.quantile(abs(smooth_residual),.95)>.005:raise ValueError('Runout is not repeatable within 0.005mm; inspect indexing, support and vision')
    q=np.arange(256)/256;values=basis(q)@coef;old=evaluate(record['profile'],q);new=old.copy()
    old_derivative=np.roll(old,-1,axis=0)-np.roll(old,1,axis=0)
    for _ in range(4):
        derivative=np.roll(new,-1,axis=0)-np.roll(new,1,axis=0)
        for i in range(256):
            signs=np.array([1 if v>=0 else -1 for v in derivative[i]])
            key=','.join(map(str,signs));branch=model['branches'][key];j=np.asarray(branch['jacobian'])
            delta=np.linalg.lstsq(j,goal-values[i],rcond=None)[0]
            if max(abs(goal-values[i]-j@delta))>.010:raise ValueError('Dot/wire error lies outside the two-axis span; change static cradle pose')
            if np.linalg.norm(delta)*WORKING_LEVER*2*math.pi/COUNTS_PER_REV>.250:raise ValueError('Correction exceeds the learned local neighborhood; align the cradle or reduce runout')
            old_signs=np.array([1 if v>=0 else -1 for v in old_derivative[i]])
            old_key=','.join(map(str,old_signs));old_band=np.asarray(model['branches'][old_key]['reversal_deadband_counts'])
            new_band=np.asarray(branch['reversal_deadband_counts'])
            # Invert the steady-direction lost-motion branches around reversal.
            # The interpolated take-up is accepted only by real replay holdouts.
            new[i]=old[i]+delta+(signs*new_band-old_signs*old_band)/2
    out={'geometry_sha256':GEOMETRY_SHA,'period_us':record['profile']['period_us'],'knots':np.rint(new).astype(int).tolist(),
         'qualified':False,'physical':True,'model_sha256':digest(model),'target_sha256':digest(target),
         'target_values_mm':goal.tolist(),'training_capture_sha256':digest(record),
         'optics_config_sha256':model['optics_config_sha256'],
         'training_sample_ids':[r['sample_ns'] for r in rows],'speed_mm_s':record['speed_mm_s'],
         'direction':record['direction'],'index_label':record['index_label'],'harmonics':harmonics,
         'training_fit_p95_mm':float(np.quantile(abs(smooth_residual),.95))}
    return check(out)

def qualify(profile,captures):
    check(profile)
    if len(captures)<2:raise ValueError('Two independent physical dry-run captures required')
    training=set(profile['training_sample_ids']);errors=[];ids=set()
    for capture in captures:
        rows=rows_for_fit(capture);check(capture['profile'])
        if digest(capture['profile'])!=digest(profile):raise ValueError('Validation must replay this exact candidate profile')
        if capture['index_label']!=profile['index_label'] or capture['direction']!=profile['direction'] or capture['speed_mm_s']!=profile['speed_mm_s']:raise ValueError('Index/direction/speed mismatch')
        if capture.get('optics_config_sha256')!=profile.get('optics_config_sha256'):raise ValueError('Validation optical configuration changed')
        new={r['sample_ns'] for r in rows}
        if new&training or new&ids:raise ValueError('Training and dry-run holdouts must be independent')
        ids|=new
        for r in rows:errors.extend(abs(np.asarray(r['values_mm'])-profile['target_values_mm']))
    if np.quantile(errors,.95)>.005 or max(errors)>.010:raise ValueError('Both dot and actual wire endpoint must meet 0.005mm p95 / 0.010mm maximum')
    out=dict(profile);out.update(qualified=True,holdout_sha256=[digest(x) for x in captures],
                               holdout_p95_mm=float(np.quantile(errors,.95)),holdout_max_mm=float(max(errors)))
    return out

def capture(client,latest,profile,seconds,speed,direction,index_label):
    check(profile);client.load_trajectory(profile);rows=[];deadline=time.monotonic()+seconds+60;started=False;last_stamp=0
    print('Ready. Rotator must be indexed and released for at least 12s. Hold the existing pedal for the dry run.',flush=True)
    while time.monotonic()<deadline:
        send=time.monotonic_ns();s=client.status();receive=time.monotonic_ns()
        if s['state']=='fault':raise RuntimeError('Controller fault: '+s['fault'])
        if s['playback_active']:
            started=True
            # Midpoint estimate bounded by half of measured round-trip latency.
            host_start=(send+receive)//2+(s['playback_started_us']-s['time_us'])*1000
            obs=observation(latest,after_ns=last_stamp,timeout=.5);last_stamp=obs['sample_ns']
            elapsed=(last_stamp-host_start)/1e9
            if elapsed<0:continue
            period=profile['period_us']/1e6
            rows.append(dict(obs,elapsed_s=elapsed,phase=(elapsed/period)%1,
                             command_counts=evaluate(profile,elapsed/period).tolist(),
                             clock_uncertainty_ms=(receive-send)/2e6))
            if elapsed>=seconds:break
        elif started:break
        else:time.sleep(.03)
    client.stop()
    return {'physical':True,'geometry_sha256':GEOMETRY_SHA,'profile':profile,'rows':rows,
            'optics_config_sha256':rows[0]['optics_config_sha256'] if rows else None,
            'speed_mm_s':speed,'direction':direction,'index_label':index_label}

def replay(client,profile,seconds):
    check(profile)
    if not profile.get('qualified') or not profile.get('physical'):raise ValueError('Independently qualified physical dry trajectory required')
    client.load_trajectory(profile);deadline=time.monotonic()+seconds+60;started=None
    print('Ready. Match the indexed dry-run setup and rotator speed/direction; release for 12s before pressing the pedal.',flush=True)
    while time.monotonic()<deadline:
        s=client.status()
        if s['state']=='fault':raise RuntimeError('Controller fault: '+s['fault'])
        if s['playback_active']:
            if started is None:started=time.monotonic()
            if time.monotonic()-started>seconds:break
        elif started is not None:break
        time.sleep(.03)
    client.stop()

def save(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')
def read(path):return json.loads(Path(path).read_text())

if __name__=='__main__':
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='op',required=True)
    f=sub.add_parser('fit');f.add_argument('capture');f.add_argument('model');f.add_argument('target');f.add_argument('output')
    q=sub.add_parser('qualify');q.add_argument('profile');q.add_argument('captures',nargs=2);q.add_argument('--output',required=True)
    for name in ('capture','replay'):
        c=sub.add_parser(name);c.add_argument('--port',required=True);c.add_argument('--reference-central',action='store_true',required=True);c.add_argument('--profile');c.add_argument('--seconds',type=float,default=110);c.add_argument('--log',required=True)
        if name=='capture':
            c.add_argument('--latest',required=True);c.add_argument('--output',required=True);c.add_argument('--speed',type=float,required=True);c.add_argument('--direction',choices=['cw','ccw'],required=True);c.add_argument('--index',required=True)
    a=p.parse_args()
    if a.op=='fit':save(a.output,fit(read(a.capture),read(a.model),read(a.target)))
    elif a.op=='qualify':save(a.output,qualify(read(a.profile),[read(x) for x in a.captures]))
    else:
        from positioner import Client
        if a.op=='replay' and not a.profile:p.error('--profile required')
        profile=read(a.profile) if a.profile else {'geometry_sha256':GEOMETRY_SHA,'period_us':period_for_speed(a.speed),'knots':[[0,0]]*256,'qualified':False}
        if a.op=='capture' and profile['period_us']!=period_for_speed(a.speed):p.error('Profile does not match this rotator speed')
        client=Client(a.port,a.log)
        try:
            client.establish()
            if a.op=='capture':save(a.output,capture(client,a.latest,profile,a.seconds,a.speed,a.direction,a.index))
            else:replay(client,profile,a.seconds)
        finally:client.close()
