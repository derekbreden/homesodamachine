"""Manual source binding of authoritative fine installed wiring.
No mechanical generation or recurring check.
"""
from pathlib import Path
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT),str(ROOT/'hardware/scripts'),str(ROOT/'hardware/manifold-layout')]
OUT=ROOT/'hardware/wiring/installed/above-core-review/installed-wiring-binding.json'
STEP=ROOT/'hardware/wiring/enclosure-wiring.step';MANIFEST=STEP.with_suffix('.json');EA=ROOT/'hardware/manifold-layout/enclosure-assembly.step'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--manifest',type=Path,default=MANIFEST)
parser.add_argument('--aggregate',type=Path,default=EA)
parser.add_argument('--output',type=Path,default=OUT)
parser.add_argument('--source-cache',type=Path,help='Optional explicitly bound native signatures/curves, avoiding unchanged source sweeps.')
parser.add_argument('--update-routing-review',action='store_true',help='Bind existing mesh witnesses and their scoped native resolutions; do not rerun contacts or packing.')
args=parser.parse_args()
MANIFEST,EA,OUT=args.manifest,args.aggregate,args.output
STEP=MANIFEST.with_suffix('.step')
manifest=json.loads(MANIFEST.read_text())
if manifest.get('wiring_fine_model_sha256'):
    if args.source_cache:
        parser.error('--source-cache supplies native shapes; fine sources are regenerated from their bound numeric recipes.')
    from hardware.wiring.installed.review import source_review
    result=source_review(MANIFEST,EA,OUT)
    if args.update_routing_review:
        path=ROOT/'hardware/wiring/installed/routing-review.json'
        review=json.loads(path.read_text())if path.exists()else{}
        review['current_fine_artifact_binding']={
            'scope':'Current graph, numeric recipes and authoritative fine body binding. Existing native/contact/packing receipts retain their own artifact hashes and are not renewed.',
            'record':{'path':str(OUT),'sha256':sha(OUT)},
            'physical_fine_model_sha256':manifest['physical_fine_model_sha256'],
            'wiring_fine_model_sha256':manifest['wiring_fine_model_sha256'],
            'manifest_sha256':sha(MANIFEST),
            'all_source_curves_match':result['all_source_curves_match'],
            'all_fine_shapes_match_regenerated_recipes':result['all_fine_shapes_match_regenerated_recipes'],
            'status':'bound'if result['all_bindings_match']else'binding_incomplete'}
        path.write_text(json.dumps(review,indent=2)+'\n')
    raise SystemExit(0 if result['all_bindings_match']else 1)

parser.error("Manifest has no authoritative fine wiring model; regenerate the installed wiring source.")
