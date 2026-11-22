"""Score the reserved programs in image pixels without using the graduated volume map."""
import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean,median


def score(journal, forecasts):
    observations = defaultdict(list)
    for line in journal.read_text().splitlines():
        t = json.loads(line)
        if t['event'] != 'trial':
            continue
        head = t['head']
        expected = forecasts[t['scenario']][head]
        before = t['pre_cup']['x990']
        after = t['post_cup']['x990']
        displacement = (after['row']-before['row'])*(1 if head=='A' else -1)
        error = displacement-expected
        good = min(before['contrast'],after['contrast'])>=6 and t['burst_count']==t['expected_bursts']
        key = (t['scenario'],head,t.get('level','central'))
        observations[key].append({'index':t['index'], 'block':t['block'], 'start_row':before['row'],
            'end_row':after['row'], 'forecast_row':before['row']+(expected if head=='A' else -expected),
            'observed_px':displacement,'expected_px':expected,'error_px':error,'readable_and_expected_burst_count':good,
            'in_band':good and abs(error)<=max(2.5,.10*expected)})
    results=[]
    for (name,head,level),obs in sorted(observations.items()):
        expected=obs[0]['expected_px']
        errors=[x['error_px'] for x in obs if x['readable_and_expected_burst_count']]
        inside=sum(o['in_band'] for o in obs)
        bias=mean(errors) if errors else None
        results.append({'scenario':name,'head':head,'level':level,'forecast_px':expected,
                        'median_observed_px':median([x['observed_px'] for x in obs]),'inside':inside,
                        'mean_bias_px':bias,'pass':len(obs)==6 and inside>=5 and bias is not None and abs(bias)<=max(1.5,.05*expected),
                        'trials':obs})
    return results


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    for key in ('frozen','journal','output'):a.add_argument(key,type=Path)
    v=a.parse_args()
    v.output.write_text(json.dumps(score(v.journal,json.loads(v.frozen.read_text())['forecasts_px']),indent=2)+'\n')
