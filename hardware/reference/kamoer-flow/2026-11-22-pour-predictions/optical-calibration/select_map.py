"""Freeze lowering graduation anchors or explicitly mark a substituted exploratory crossing."""
import argparse
import json
from pathlib import Path

names=('quarter_three_quarters','quarter_one','quarter_one_and_quarter')
sites=('x990','x1986')


def build(folder, permit_fallback):
    preferred=json.loads((folder/'geometry-map-v3.json').read_text())
    assert preferred['clear_lane_reader']=='mark_crossings_v3'
    record={'unit':preferred['unit'], 'clear_lane_reader':preferred['clear_lane_reader'],
            'anchors':{k:[] for k in sites}, 'source_crossings':{},
            'lowering':preferred['lowering'], 'substitutions':[]}
    for name in names:
        chosen=preferred['lowering'].get(name)
        direction='lowering'
        if chosen is None and permit_fallback:
            original=json.loads((folder/'geometry-map.json').read_text())
            rising=original['rising'].get(name)
            eligible=[] if not rising else [r for r in rising['brackets'] if all(x.startswith(('ladder2-up-high-','ladder4-up-high-')) for x in r['labels'])]
            if eligible:
                root=eligible[0]
                chosen={'nominal_ml':rising['nominal_ml'], 'rows':root['interpolated_rows'], 'brackets':[root]}
                direction='exploratory rising, substituted for unresolved lowering'
                if any(y>=1065 for key,y in chosen['rows'].items() if key=='x990'):
                    raise ValueError('Original rising reader cannot substitute below the v3 range split')
                record['substitutions'].append(name)
        if chosen is None:
            raise ValueError(('No photographed anchor meeting the selected graduation rule',name))
        record['source_crossings'][name]={'direction':direction,**chosen}
        for k in sites:record['anchors'][k].append([chosen['rows'][k],chosen['nominal_ml']])
    for pairs in record['anchors'].values():pairs.sort()
    record['calibration_status']='provisional mixed-direction map' if record['substitutions'] else 'lowering-only printed-graduation map'
    return record


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('folder',type=Path);p.add_argument('out',type=Path);p.add_argument('--permit-fallback',action='store_true')
    v=p.parse_args()
    data=build(v.folder,v.permit_fallback)
    with v.out.open('x') as f:json.dump(data,f,indent=2,allow_nan=False);f.write('\n')
    print(data['calibration_status'],data['anchors'])
