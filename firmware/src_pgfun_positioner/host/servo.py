"""Learn two motor responses from one camera's dot, wire and seam observations.

The response maps emitted count changes to four observed projected-mm values.
It cannot infer unobserved depth. Each approach-direction pair is learned
separately. Models contain evidence identifiers and never qualify themselves.
"""
import argparse
import hashlib
import json
import math
import time
from pathlib import Path
import numpy as np
from kinematics import GEOMETRY_SHA, COUNTS_PER_REV, SOFT_LIMIT, WORKING_LEVER

def fit(rows):
    if len(rows)<12:raise ValueError('At least 12 measured response pairs required')
    optics={r.get('optics_config_sha256') for r in rows}
    if len(optics)!=1 or None in optics:raise ValueError('One fixed optical configuration is required')
    models={}
    for branch in ((1,1),(1,-1),(-1,1),(-1,-1)):
        batch=[r for r in rows if tuple(r['direction'])==branch]
        if len(batch)<3:raise ValueError(f'Insufficient responses for {branch}')
        x=np.asarray([r['delta'] for r in batch],float)
        y=np.asarray([r['change_mm'] for r in batch],float)
        if x.shape[1:]!=(2,) or y.shape[1:]!=(4,) or not np.isfinite(x).all() or not np.isfinite(y).all():
            raise ValueError('Finite 2-count / 4-observation pairs required')
        # Each probe returns to its origin from the opposite direction.
        # Fit the per-axis lost count interval as well as the loaded slope.
        best=None
        for by in range(33):
            for bp in range(33):
                effective=np.sign(x)*np.maximum(abs(x)-[by,bp],0)
                if np.linalg.matrix_rank(effective)<2:continue
                j=np.linalg.lstsq(effective,y,rcond=None)[0].T
                residual=y-effective@j.T;score=float(np.mean(residual**2))
                if best is None or score<best[0]-1e-18:best=(score,j,residual,[by,bp])
        if best is None:raise ValueError('Response probes do not span both joints')
        _,j,residual,deadband=best
        if 32 in deadband:raise ValueError('Reversal deadband reaches the search boundary; inspect preload and routing')
        if np.linalg.matrix_rank(x)<2 or np.linalg.matrix_rank(j)<2 or np.linalg.cond(j)>30:
            raise ValueError('The view cannot separate the two joints')
        models[','.join(map(str,branch))]={'jacobian':j.tolist(),
            'reversal_deadband_counts':deadband,
            'fit_rms_mm':float(np.sqrt(np.mean(residual**2))),
            'sample_count':len(batch),'counts_tested':sorted(set(int(abs(v))for v in x.flat if v))}
    return {'geometry_sha256':GEOMETRY_SHA,'branches':models,'qualified':False,
            'optics_config_sha256':next(iter(optics)),
            'source_sha256':hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest(),
            'physical':all(r.get('physical') is True for r in rows),
            'training_sample_ids':sorted(str(r.get('after_ns')) for r in rows)}

def correction(model,error,direction,trust_mm=.010):
    if model.get('geometry_sha256')!=GEOMETRY_SHA:raise ValueError('Geometry/model mismatch')
    if not .0<trust_mm<=.010:raise ValueError('Trust must be >0 and <=0.010mm')
    error=np.asarray(error,float)
    if error.shape!=(4,) or not np.isfinite(error).all():raise ValueError('Four finite errors required')
    key=','.join(map(str,direction));j=np.asarray(model['branches'][key]['jacobian'],float)
    if j.shape!=(4,2) or not np.isfinite(j).all() or np.linalg.matrix_rank(j)!=2 or np.linalg.cond(j)>30:
        raise ValueError('Unobservable response')
    d=np.linalg.lstsq(j,error,rcond=None)[0]
    residual=error-j@d
    # Two motors cannot remove this component; it calls for a static print change.
    if np.linalg.norm(residual,np.inf)>.010:raise ValueError('Error outside the two-motor span; revise cradle pose')
    nominal_per_count=WORKING_LEVER*2*math.pi/COUNTS_PER_REV
    predicted=float(np.max(np.abs(j@d)))
    factor=min(1.,trust_mm/max(predicted,1e-15),trust_mm/max(np.linalg.norm(d)*nominal_per_count,1e-15))
    d=np.rint(d*factor).astype(int)
    while np.max(abs(j@d))>trust_mm or np.linalg.norm(d)*nominal_per_count>trust_mm:
        d[np.argmax(abs(d))]-=int(np.sign(d[np.argmax(abs(d))]))
    return d.tolist(),residual.tolist()

def qualified(model,holdout):
    if not model.get('physical') or len(holdout)<20 or not all(r.get('physical') is True for r in holdout):
        raise ValueError('20 independent physical holdouts required')
    if any(str(r.get('after_ns')) in model.get('training_sample_ids',[]) for r in holdout):
        raise ValueError('Training and holdout observations overlap')
    errors=[]
    train_hash=model['source_sha256']
    for branch in ((1,1),(1,-1),(-1,1),(-1,-1)):
        if sum(tuple(r['direction'])==branch for r in holdout)<5:raise ValueError('Five physical holdouts per direction branch required')
    if hashlib.sha256(json.dumps(holdout,sort_keys=True).encode()).hexdigest()==train_hash:
        raise ValueError('Training samples are not independent validation')
    for r in holdout:
        if r.get('optics_config_sha256')!=model['optics_config_sha256']:raise ValueError('Holdout optical configuration changed')
        branch=model['branches'][','.join(map(str,r['direction']))];j=np.asarray(branch['jacobian'])
        if any(v>.0025 for v in r['sigma_mm']):raise ValueError('Observation noise exceeds 0.0025mm')
        delta=np.asarray(r['delta']);effective=np.sign(delta)*np.maximum(abs(delta)-branch['reversal_deadband_counts'],0)
        errors.extend(abs(np.asarray(r['change_mm'])-j@effective))
    if np.quantile(errors,.95)>.005 or max(errors)>.010:raise ValueError('Loaded response error exceeds tolerance')
    out=dict(model);out['qualified']=True
    out['holdout_sha256']=hashlib.sha256(json.dumps(holdout,sort_keys=True).encode()).hexdigest()
    out['holdout_p95_mm']=float(np.quantile(errors,.95));return out

def observation(path,after_ns=0,timeout=2.0):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        try:
            sample=json.loads(Path(path).read_text())
            stamp=sample['sample_ns'];now=time.monotonic_ns()
            if not sample.get('physical') or not sample.get('valid'):raise ValueError('Features are invalid')
            if not sample.get('noise_qualified'):raise ValueError('Stationary camera noise has not been qualified')
            if stamp<=after_ns or not 0<=now-stamp<=200_000_000:
                time.sleep(.02);continue
            values=np.asarray(sample['values_mm'],float);sigma=np.asarray(sample['sigma_mm'],float)
            if values.shape!=(4,) or sigma.shape!=(4,) or not np.isfinite(values).all() or not np.isfinite(sigma).all() or min(sigma)<0:
                raise ValueError('Malformed observation')
            if np.max(sigma)>.0025:raise ValueError('Feature uncertainty exceeds 0.0025mm')
            return sample
        except (FileNotFoundError,json.JSONDecodeError):pass
        time.sleep(.02)
    raise TimeoutError('No fresh valid camera observation')

def collect(client,latest,levels=(2,4,8,16,32,64)):
    baseline=client.status()
    if baseline['state']!='armed' or not baseline['referenced']:raise RuntimeError('Reference and arm first')
    origin=baseline['count'];rows=[]
    for sy,sp in ((1,1),(1,-1),(-1,1),(-1,-1)):
        for n in levels:
            for d in ([sy*n,sp*2*n],[sy*2*n,sp*n]):
                client.move_to_counts(origin)
                before=observation(latest,after_ns=time.monotonic_ns()+200_000_000)
                client.move(list(d),500_000)
                after=observation(latest,after_ns=time.monotonic_ns()+200_000_000)
                if before['optics_config_sha256']!=after['optics_config_sha256']:raise ValueError('Optics changed during a response probe')
                rows.append({'delta':list(d),'change_mm':(np.asarray(after['values_mm'])-before['values_mm']).tolist(),
                    'direction':[sy,sp],'physical':True,'sigma_mm':np.maximum(after['sigma_mm'],before['sigma_mm']).tolist(),
                    'optics_config_sha256':after['optics_config_sha256'],
                    'before_ns':before['sample_ns'],'after_ns':after['sample_ns']})
    client.move_to_counts(origin)
    return rows

def follow(client,latest,model,target,direction,seconds):
    if not model.get('qualified'):raise ValueError('Independent loaded response qualification required')
    if any(any(b['reversal_deadband_counts']) for b in model['branches'].values()):
        raise ValueError('Measured reversal deadband requires independently validated periodic replay')
    deadline=time.monotonic()+seconds;history=list(direction);stalled=0;last_error=None
    while time.monotonic()<deadline:
        obs=observation(latest)
        error=np.asarray(target)-obs['values_mm']
        magnitude=float(np.max(abs(error)))
        if magnitude<=.005:time.sleep(.05);continue
        d,residual=correction(model,error,history)
        desired=[int(np.sign(v)) if v else history[i] for i,v in enumerate(d)]
        if desired!=history:d,residual=correction(model,error,desired)
        if not any(d):raise RuntimeError('Error persists below the learned useful step')
        client.move(d,150_000)
        settled=observation(latest,after_ns=time.monotonic_ns()+200_000_000)
        new_error=float(np.max(abs(np.asarray(target)-settled['values_mm'])))
        stalled=stalled+1 if new_error>=magnitude-.001 else 0
        if stalled>=5:raise RuntimeError('Five corrections failed to improve observed alignment')
        history=[int(np.sign(v)) if v else history[i] for i,v in enumerate(d)]

if __name__=='__main__':
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='op',required=True)
    f=sub.add_parser('fit');f.add_argument('pairs');f.add_argument('model')
    q=sub.add_parser('qualify');q.add_argument('model');q.add_argument('holdout');q.add_argument('output')
    l=sub.add_parser('learn');l.add_argument('--port',required=True);l.add_argument('--latest',required=True);l.add_argument('--output',required=True);l.add_argument('--reference-central',action='store_true',required=True)
    c=sub.add_parser('follow');c.add_argument('--port',required=True);c.add_argument('--latest',required=True);c.add_argument('--model',required=True);c.add_argument('--target',required=True);c.add_argument('--seconds',type=float,default=60);c.add_argument('--reference-central',action='store_true',required=True)
    args=p.parse_args()
    if args.op=='fit':Path(args.model).write_text(json.dumps(fit(json.loads(Path(args.pairs).read_text())),indent=2)+'\n')
    elif args.op=='qualify':Path(args.output).write_text(json.dumps(qualified(json.loads(Path(args.model).read_text()),json.loads(Path(args.holdout).read_text())),indent=2)+'\n')
    else:
        from positioner import Client
        client=Client(args.port)
        try:
            client.establish()
            if args.op=='learn':Path(args.output).write_text(json.dumps(collect(client,args.latest),indent=2)+'\n')
            else:follow(client,args.latest,json.loads(Path(args.model).read_text()),json.loads(Path(args.target).read_text())['values_mm'],[1,1],args.seconds)
        finally:client.close()
