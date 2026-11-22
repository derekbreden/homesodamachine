"""Check the registered rising ticks and quiet holds against the exact map used for the wet forecasts."""
import argparse
import json
from pathlib import Path


def extrapolate_anchor(row, points):
    pairs = list(sorted(points))
    if row <= pairs[0][0]:
        a,b=pairs[:2]
    elif row >= pairs[-1][0]:
        a,b=pairs[-2:]
    else:
        a,b=next((a,b) for a,b in zip(pairs,pairs[1:]) if a[0]<=row<=b[0])
    return a[1]+(row-a[0])*(b[1]-a[1])/(b[0]-a[0])


def measures(frozen,registered,observations):
    names=('quarter_three_quarters','quarter_one','quarter_one_and_quarter')
    result={'calibration_status':frozen['calibration_status'],'substitutions':frozen['substitutions'],
            'reserved_rising':{}, 'interior_stationary_holds':{}, 'middle_error_using_outer_only_ml':{}}
    for site,points in frozen['anchors'].items():
        mark={}
        for name in names:
            v=registered['rising'].get(name)
            if not v:
                mark[name]=None;continue
            converted=extrapolate_anchor(v['rows'][site],points)
            mark[name]={'heldout_row':v['rows'][site],'estimated_ml':converted, 'target_ml':v['nominal_ml'],
                        'error_ml':converted-v['nominal_ml'],'within_1_5_ml':abs(converted-v['nominal_ml'])<=1.5,
                        'fit_direction':frozen['source_crossings'][name]['direction']}
        result['reserved_rising'][site]=mark
        pair=sorted(points);middle=pair[1]
        result['middle_error_using_outer_only_ml'][site]=extrapolate_anchor(middle[0],[pair[0],pair[2]])-middle[1]
    lookup={r['label']:r for r in observations}
    for label in ('ladder2-down-low-inside','ladder4-upper-inside'):
        hold={}
        for site, field in (('x990','clear_row'),('x1986','right_clear_row')):
            p=frozen['anchors'][site]
            held_rows=[lookup[f'{label}-hold{time}'][field] for time in (5,20,40,65)]
            within=all(min(x[0] for x in p)<=row<=max(x[0] for x in p) for row in held_rows)
            ml=[extrapolate_anchor(row,p) for row in held_rows]
            hold[site]={'readings_ml':ml,'delta_ml':ml[-1]-ml[0],'span_ml':max(ml)-min(ml),
                        'within_calibrated_span':within,'within_0_75_ml':within and abs(ml[-1]-ml[0])<=0.75}
        result['interior_stationary_holds'][label]=hold
    return result


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    for k in ('map','registered','observations','out'):a.add_argument(k,type=Path)
    v=a.parse_args();read=lambda path:json.loads(path.read_text())
    v.out.write_text(json.dumps(measures(read(v.map),read(v.registered),read(v.observations)),indent=2)+'\n')
