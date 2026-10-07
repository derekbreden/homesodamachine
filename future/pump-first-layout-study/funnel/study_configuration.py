"""Selected aft-growth datum shared by the native interface producers."""
from pathlib import Path
import argparse,json
HERE=Path(__file__).resolve().parent

def configuration():
 parser=argparse.ArgumentParser()
 parser.add_argument('--aft',type=float)
 parser.add_argument('--preview-only',action='store_true')
 args=parser.parse_args()
 selected=json.loads((HERE/'candidate.json').read_text())
 extra=args.aft if args.aft is not None else selected['aft_extension_mm']
 manifest=selected if args.aft is None else json.loads((HERE/f'candidate-aft-{extra:g}.json').read_text())
 return extra,args.preview_only,manifest

def save_record(name,extra,preview,value):
 text=json.dumps(value,indent=2)+'\n'
 (HERE/f'{name}-aft-{extra:g}.json').write_text(text)
 if not preview:(HERE/f'{name}.json').write_text(text)
