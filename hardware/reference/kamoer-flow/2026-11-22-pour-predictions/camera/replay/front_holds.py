"""Measure stationary movement at both front liquid contacts from timestamped preview pixels and native endpoint photographs."""
import argparse
import bisect
import json
from pathlib import Path

import numpy as np
from front_wall import COLUMNS, SITES, track


def capture(camera,photo_reports):
    out=camera/'evidence/front-holds';out.mkdir(exist_ok=True)
    clock=json.loads((camera/'evidence/ladder-hold-clock.json').read_text())
    files=sorted((camera/'front-preview').glob('[0-9]*.npz'));times=[]
    for path in files:
        with np.load(path) as z:times.append(int(z['pts_ns'][0]))
    for label,h in clock.items():
        dest=out/(label+'.npz')
        if dest.exists():continue
        begin=h['begin_ns'];end=h['end_ns']
        stamps=[];sequence=[];frames=[]
        for f in files[max(0,bisect.bisect_right(times,begin)-1):bisect.bisect_right(times,end)]:
            with np.load(f) as raw:
                take=(raw['pts_ns']>=begin)&(raw['pts_ns']<=end)
                if not np.any(take):continue
                sel=np.searchsorted(raw['sensor_x'],COLUMNS);all_rows=raw['sensor_y'];rr=(all_rows>=708)&(all_rows<=1200)
                frames.append(raw['luma'][take][:,rr,:][:,:,sel]);stamps.append(raw['pts_ns'][take]);sequence.append(raw['seq'][take])
        photo_names=[h['starting_photograph'],*[r['window'] for r in h['hold_photographs']]]
        snapshots=[]
        for name in photo_names:
            f=photo_reports/name/'cap-reading-v3.json'
            report=json.loads(f.read_text());source=json.loads((camera/'windows'/name/'window.json').read_text())
            snapshots.append({'label':name,'pts_ns':source['mid']['pts_ns'],'x990':report['clear_row'],'x1986':report['right_clear_row'],
                              'x990_contrast':report['clear_contrast'],'x1986_contrast':report['right_clear_contrast']})
        meta={'label':label,'begin_ns':begin,'end_ns':end,'native_photo_observations':snapshots}
        with dest.open('wb') as output:
            np.savez_compressed(output,pts_ns=np.concatenate(stamps),seq=np.concatenate(sequence),luma=np.concatenate(frames),
                                sensor_x=COLUMNS,sensor_y=all_rows[rr],metadata=np.asarray(json.dumps(meta)))
    return out


def read(path):
    with np.load(path) as z:
        t=z['pts_ns'];y=z['sensor_y'];im=z['luma'];meta=json.loads(str(z['metadata']))
    begin=meta['begin_ns'];photos=meta['native_photo_observations'];elapsed=(t-begin)*1e-9
    stats={'preview_frames':len(t),'native_photo_observations':photos,'sites':{}}
    for k,site in enumerate(SITES):
        coords,score=track(im[:,:,3*k:3*k+3],y,photos[0][site],t,begin+700_000_000)
        def center(tick):return float(np.median(coords[abs(elapsed-tick)<=.5]))
        anchors=[(x,center(x)) for x in (2.35,5,20,40,64)]
        pairs=[center(x+3)-center(x) for x in np.arange(2,61,1.)]
        stats['sites'][site]={'positions_by_second_px':anchors,'delta_2_to_64_seconds_px':anchors[-1][1]-anchors[0][1],
           'stationary_three_second_median_difference_abs_95_px':float(np.quantile(np.abs(pairs),.95)),
           'native_first_to_last_photo_delta_px':photos[-1][site]-photos[0][site],
           'native_photo_row_range_px':[min(s[site] for s in photos), max(s[site] for s in photos)],
           'minimum_local_edge_score':float(np.min(score)),'median_local_edge_score':float(np.median(score))}
    return stats


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
    p=sub.add_parser('pack');p.add_argument('camera',type=Path);p.add_argument('photo_reports',type=Path)
    v=sub.add_parser('score');v.add_argument('files',nargs='+',type=Path);v.add_argument('--out',type=Path,required=True)
    a=parser.parse_args()
    if a.action=='pack':capture(a.camera,a.photo_reports)
    else:a.out.write_text(json.dumps({f.stem:read(f) for f in a.files},indent=2,allow_nan=False)+'\n')
