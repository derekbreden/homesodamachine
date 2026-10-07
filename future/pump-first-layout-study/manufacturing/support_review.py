"""Read complete support topology from each already reviewed native slice.

Retains short bodies without interface feature labels. The resulting positions,
roots and build-up distances are slice measurements; removal effort and surface
finish require the physical part.
"""
from pathlib import Path
import argparse,hashlib,json,sys,zipfile

HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
CACHE=ROOT/'.cache/pump-first-layout/slices'
sys.path.insert(0,str(ROOT/'hardware/scripts'))
import enclosure_support_audit as support

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main(names):
    for name in names or [p.name[:-11] for p in HERE.glob('*-slice.json')]:
        review=json.loads((HERE/(name+'-slice.json')).read_text())
        dirs=list(CACHE.glob(name+'-'+review['brep_sha256'][:12]+'-'+review['review_source_sha256'][:8]))
        assert len(dirs)==1,(name,dirs)
        directory=dirs[0];mesh=directory/(name+'.stl');project=directory/(name+'-input.3mf')
        archive=directory/'slice'/(name+'.gcode.3mf');gcode=directory/'slice'/(name+'.gcode')
        assert sha(archive)==review['archive_sha256']
        with zipfile.ZipFile(archive) as z:gcode.write_bytes(z.read('Metadata/plate_1.gcode'))
        report=support.audit(gcode,name,model=mesh,profile=project,coordinate_profile=project,
                             profile_label=str(project.relative_to(ROOT)),include_unlabelled_support=True)
        report['inputs'].update({'model':str(mesh.relative_to(ROOT)),'profile':str(project.relative_to(ROOT)),
                                  'brep_sha256':review['brep_sha256'],'archive_sha256':review['archive_sha256'],
                                  'reviewer_sha256':sha(Path(__file__)),'topology_tool_sha256':sha(Path(support.__file__))})
        report['scope']='Complete emitted support topology including unlabelled short bodies. Physical removal effort, trapped branches, contact finish and mechanical qualification remain unverified.'
        (HERE/(name+'-supports.json')).write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({'part':name,**report['summary']}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('names',nargs='*');main(parser.parse_args().names)
