"""Prepare and review the PET-GF sample plates or replacement box cap; never sends a job."""
from pathlib import Path
import argparse
import copy
import importlib.util
import itertools
import json
import re
import sys
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
TRIAL=ROOT/'hardware/printed-parts/enclosure/trial-preparation'
sys.path[:0]=[str(TRIAL),str(ROOT/'tools')]
loader=importlib.util.spec_from_file_location('rear_retention_prepare',TRIAL/'prepare.py')
trial=importlib.util.module_from_spec(loader)
loader.loader.exec_module(trial)
import review
from bambu_print_archive import package


def centered_layout(footprints,low,high,spacing,yaw):
    """Keep this five-piece comparison compact in the middle of its plate."""
    best=None
    for turns in itertools.product((0,90),repeat=len(footprints)):
        sizes=[(a,b) if turn==0 else (b,a) for (a,b),turn in zip(footprints,turns)]
        for order in itertools.permutations(range(len(sizes))):
            for target in range(140,261,10):
                rows=[];row=[];x=0.
                for i in order:
                    w,h=sizes[i]
                    if row and x+w>target:
                        rows.append(row);row=[];x=0.
                    row.append((i,x,w,h));x+=w+spacing
                rows.append(row)
                width=max(row[-1][1]+row[-1][2] for row in rows)
                height=sum(max(p[3] for p in row) for row in rows)+spacing*(len(rows)-1)
                margin=min((high[0]-low[0]-width)/2.,(high[1]-low[1]-height)/2.)
                score=(margin,-width*height)
                if best is None or score>best[0]: best=(score,turns,rows,width,height)
    _,turns,rows,width,height=best
    positions={};y=0.;cx,cy=(low[0]+high[0])/2.,(low[1]+high[1])/2.
    for row in rows:
        depth=max(p[3] for p in row);breadth=row[-1][1]+row[-1][2]
        for i,x,w,h in row:
            positions[i]=(turns[i],cx+x+w/2.-breadth/2.,cy+y+depth/2.-height/2.)
        y+=depth+spacing
    return [positions[i] for i in range(len(sizes))]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plate',choices=('mark1','mark2','box','all'),default='all')
    parser.add_argument('--trial',type=Path,default=HERE/'v4')
    args=parser.parse_args()
    case=args.trial.resolve()
    production=json.loads((TRIAL/'pieces.json').read_text())
    geometry=json.loads((case/'geometry.json').read_text())
    spec={k:production[k] for k in ('schema','profile','filament_mapping','printers')}
    nozzle=production['pieces']['pump-snap-cap']['nozzle']
    groups={'rear-retention-mark1':('Mark1',('pump-seat','asse-seat','asse-cap','pisco-seat','pisco-cap')),
            'rear-retention-mark2':('Mark2',('pump-cap','meter-seat','meter-cap','regulator-seat','regulator-cap'))}
    rows={p['name']:p for p in geometry['parts']}
    spec['pieces']={}
    for plate,(printer,names) in groups.items():
        parts=[]
        for name in names:
            part={'name':name,'stl':rows[name]['stl']}
            if name.endswith('-cap'):
                part['object_settings']={
                    'sparse_infill_density':{'value':'100%','reason':'Solid stock through each retaining cap and spring root.'},
                    'sparse_infill_pattern':{'value':'zig-zag','reason':'Solid cap deposition.'}}
            parts.append(part)
        spec['pieces'][plate]={'printer':printer,'nozzle':nozzle,
          'material':'Polymaker Fiberon PET-GF15, black','parts':parts,
          'spacing_mm':12.,'plate_border_mm':40.,
          'pose_reason':'Each full receiver and cap retains its production print orientation; XY yaw only packs the comparison.',
          'settings':{
            'wall_loops':{'value':'3','reason':'Three Classic walls with solid stock through the 2.0 mm spring leaves.'},
            'wall_generator':{'value':'classic','reason':'Retain the production fixed-width wall recipe.'},
            'sparse_infill_density':{'value':'15%','reason':'Production receiver bulk recipe; caps have a local solid override.'},
            'sparse_infill_pattern':{'value':'gyroid','reason':'Production receiver bulk recipe.'},
            'enable_support':{'value':'1','reason':'Tree(auto)/Default supports the actual retention ceilings in production orientation.'}}}
    if args.plate=='box':
        piece=copy.deepcopy(production['pieces']['pump-snap-cap'])
        piece['parts']=[{'name':'pump-box-cap','stl':rows['pump-cap']['stl']}]
        spec['pieces']={'pump-box-cap':piece}
    trial.SPEC_PATH=case/('pump-box-spec.json' if args.plate=='box' else 'plate-spec.json')
    trial.SPEC_PATH.write_text(json.dumps(spec,indent=2)+'\n')
    if args.plate!='box':trial.layout=centered_layout
    jobs_file=case/('box-cap-print.json' if args.plate=='box' else 'print-jobs.json')
    jobs=json.loads(jobs_file.read_text()).get('jobs',[]) if jobs_file.exists() else []
    for plate in spec['pieces']:
        if args.plate in ('mark1','mark2') and not plate.endswith(args.plate):continue
        folder=trial.prepare(plate,output=case/'prints')
        archive=trial.slice_project(folder)
        checked=review.review(folder,audit=False)
        if not checked['pass']:raise RuntimeError(f'{plate}: native slice review failed')
        prep=json.loads((folder/'preparation.json').read_text())
        printable=folder/archive.name.replace('.gcode.3mf','-print-only.gcode.3mf')
        packaging=package(archive,printable)
        (folder/'packaging.json').write_text(json.dumps(packaging,indent=2)+'\n')
        with zipfile.ZipFile(archive) as z:text=z.read('Metadata/plate_1.gcode').decode()
        jobs=[job for job in jobs if job['plate']!=plate]
        jobs.append({'plate':plate,'printer':prep['printer'],'connection_key':prep['connection_key'],
          'preparation':str(folder.relative_to(ROOT)),'archive':str(archive.relative_to(ROOT)),
          'print_only_archive':str(printable.relative_to(ROOT)),
          'gcode_sha256':prep['gcode_sha256'],'estimated_seconds':prep['estimated_seconds'],
          'filament_g':float(re.search(r'; total filament weight \[g\]\s*:\s*([\d.]+)',text)[1]),
          'minimum_bed_margin_mm':checked['minimum_bed_margin_mm'],
          'requested_z_trim_mm':prep['requested_z_trim_mm'],
          'emitted_trim_mm':prep['emitted_textured_trim_mm'],'native_review_pass':True,'submitted':False})
        jobs_file.write_text(json.dumps({'jobs':jobs},indent=2)+'\n')
        print(json.dumps(jobs[-1]),flush=True)


if __name__=='__main__':main()
