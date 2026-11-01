"""Prepare the base on Mark1 and exact published clip on Mark2; never sends."""
from pathlib import Path
import argparse
import importlib.util
import json
import re
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TRIAL = ROOT/'hardware/printed-parts/enclosure/trial-preparation'
sys.path[:0] = [str(TRIAL),str(ROOT/'tools')]
loader = importlib.util.spec_from_file_location('pump_fit_trial_prepare',TRIAL/'prepare.py')
trial = importlib.util.module_from_spec(loader)
loader.loader.exec_module(trial)
import review
from bambu_print_archive import package


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=HERE/'prints')
    parser.add_argument('--piece',choices=('pump-fit-base','pump-fit-clip','all'),default='all')
    args = parser.parse_args()
    production = json.loads((TRIAL/'pieces.json').read_text())
    geometry = json.loads((HERE/'geometry.json').read_text())
    spec = {k:production[k] for k in ('schema','profile','filament_mapping','printers')}
    base = dict(printer='Mark1',nozzle=production['pieces']['foam-cap-lid-top']['nozzle'],
        material='Polymaker Fiberon PET-GF15, black',plate_border_mm=80,
        parts=[dict(name='pump-mount-base',stl=geometry['base']['stl'])],
        pose_reason='Flat 7.4 mm lid underside on the bed, matching the production lid orientation.',
        settings={
            'wall_loops':dict(value='3',reason='Retain the production lid receiver wall count.'),
            'wall_generator':dict(value='classic',reason='Retain the production fixed-width perimeter recipe.'),
            'sparse_infill_pattern':dict(value='gyroid',reason='Retain the production 15% gyroid bulk recipe.'),
            'enable_support':dict(value='1',reason='Tree(auto)/Default supports the outward-open hook-pocket ceilings with accessible cleanup.')})
    clip = json.loads(json.dumps(production['pieces']['pump-snap-cap']))
    clip['settings']['wall_loops']['reason']='Three Classic perimeters from each face of the 3.1 mm spring arch and 3 mm wings.'
    spec['pieces']={'pump-fit-base':base,'pump-fit-clip':clip}
    path = HERE/'plate-spec.json'
    path.write_text(json.dumps(spec,indent=2)+'\n')
    trial.SPEC_PATH = path
    jobs_file = HERE/'print-jobs.json'
    jobs = json.loads(jobs_file.read_text()).get('jobs',[]) if jobs_file.exists() else []
    for piece in spec['pieces']:
        if args.piece != 'all' and piece != args.piece:
            continue
        folder = trial.prepare(piece,output=args.output)
        archive = trial.slice_project(folder)
        checked = review.review(folder,audit=False)
        if not checked['pass']:
            raise RuntimeError(f'{piece}: native slice review failed')
        prep = json.loads((folder/'preparation.json').read_text())
        printable = folder/archive.name.replace('.gcode.3mf','-print-only.gcode.3mf')
        packaging = package(archive,printable)
        (folder/'packaging.json').write_text(json.dumps(packaging,indent=2)+'\n')
        with zipfile.ZipFile(archive) as z:
            text = z.read('Metadata/plate_1.gcode').decode()
        mass = float(re.search(r'; total filament weight \[g\]\s*:\s*([\d.]+)',text)[1])
        jobs = [job for job in jobs if job['piece'] != piece]
        jobs.append(dict(piece=piece,printer=prep['printer'],connection_key=prep['connection_key'],
            preparation=str(folder.relative_to(ROOT)),archive=str(archive.relative_to(ROOT)),
            print_only_archive=str(printable.relative_to(ROOT)),gcode_sha256=prep['gcode_sha256'],
            estimated_seconds=prep['estimated_seconds'],filament_g=mass,
            minimum_bed_margin_mm=checked['minimum_bed_margin_mm'],
            requested_z_trim_mm=prep['requested_z_trim_mm'],
            emitted_trim_mm=prep['emitted_textured_trim_mm'],
            native_review_pass=True,submitted=False))
    jobs_file.write_text(json.dumps(dict(jobs=jobs),indent=2)+'\n')
    print(json.dumps(jobs,indent=2),flush=True)


if __name__ == '__main__':
    main()
