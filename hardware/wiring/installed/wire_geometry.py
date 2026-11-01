"""Recorded installed routes supplied unchanged to the maintained wire geometry kernel."""
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'hardware/scripts')]
if __name__=='__main__':
    import _rust_part
    _rust_part.start()


def numbers(routes, stock, *, components=()):
    """Ordered recorded segments, insulation diameters, and the source's linear materials."""
    from _occt_color import rgba
    from _payload_rules import LINEAR_DEFLECTION_RATIO
    from _mesh_payload import ANGULAR_DEFLECTION
    result={'name':'installed-wiring','presentation_deflection_ratio':LINEAR_DEFLECTION_RATIO,
            'presentation_angular_deflection_rad':ANGULAR_DEFLECTION,
            'routes':[{'name':'wire-'+r['id'],'diameter_mm':stock[r['stock']]['od_mm'],
                       'linear_rgb':rgba(tuple(stock[r['stock']]['color']),{})[:3],
                       'segments':r['segments']} for r in routes]}
    if components:
        import _rust_part
        from _materials import linear
        result['components']=[]
        for name,recipe,color in components:
            row={**recipe,'name':name,'linear_rgb':linear(color)}
            if row['kind']=='import':row['step']=_rust_part.step(row['step'])
            result['components'].append(row)
    return result


def main():
    import argparse
    import _rust_part
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=ROOT/'hardware/wiring/installed-wire-geometry')
    args=parser.parse_args()
    data=json.loads(args.manifest.read_text())
    return _rust_part.cut('machine','installed-wires',numbers(data['routes'],data['stock']),args.output)


if __name__=='__main__':main()
