"""Fit the visible ring-down after actual pulse sequences at the independent upper-rim sightlines."""
import argparse,csv
from pathlib import Path
import numpy as np
from read_rewired import read
def fit(t,z):
    trend=np.column_stack((np.ones(len(t)),t))
    resid=z-trend@np.linalg.lstsq(trend,z,rcond=None)[0]
    costs=[]
    for f in np.arange(1.5,5.101,.025):
        basis=np.column_stack((trend,np.sin(2*np.pi*f*t),np.cos(2*np.pi*f*t)))
        coeff=np.linalg.lstsq(basis,z,rcond=None)[0]
        sse=float(np.sum((z-basis@coeff)**2))
        costs.append((sse,f,float(np.hypot(*coeff[-2:]))))
    sse,f,amp=min(costs)
    return float(f),amp,1-sse/max(.000001,float(np.sum(resid**2)))
if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('files',nargs='+',type=Path);a.add_argument('--out',required=True,type=Path);args=a.parse_args()
    with args.out.open('w',newline='') as fh:
        w=csv.writer(fh);w.writerow(['sequence','head','condition','accepted_operational_endpoint','sightline','median_gate_start_spacing_s','median_frame_spacing_ms','post_done_fit_start_s','post_done_fit_end_s','frames','frequency_hz','harmonic_amplitude_px','variance_explained_beyond_linear_trend'])
        for p in args.files:
            meta,sites=read(p);gates=meta['gates']
            if not meta.get('score_accepted'):continue
            spacing=float(np.median(np.diff(np.array(gates)[:,0]))/1e9) if len(gates)>1 else ''
            for label,(summary,z) in sites.items():
                t=z[:,3];v=(t>=.35)&(t<2.15)
                w.writerow([meta['label'],meta['channel'],meta.get('condition'),meta.get('score_accepted'),label,spacing,summary['median_sensor_dt_ms'],.35,2.15,int(v.sum()),*fit(t[v],z[v,5])])
