"""Summarise the no-pump readings taken before any pump ran: the noise floor and the resting level against Codex's park."""
import json
import statistics as st
import sys
from pathlib import Path

RECORD = Path(__file__).resolve().parents[1]
CODEX_PARK = {'x990': 237.041657089836, 'x1986': 237.49516675550103, 'utc': '2026-11-22T11:01:07.862+00:00'}


def images(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines() if '"event":"image"' in s]


def main(logs):
    rows = images(Path(logs) / 'noise1.jsonl')
    first = [r for r in rows if r['label'].endswith('-0')]
    out = {'codex_park': CODEX_PARK, 'streams': len(first), 'photographs': len(rows)}
    for k in ('x990', 'x1986'):
        across = [r['readings'][k]['ml'] for r in first]
        within = {}
        for r in rows:
            within.setdefault(r['stream'], []).append(r['readings'][k]['ml'])
        out[k] = {
            'mean_ml': st.mean(across),
            'sd_across_reopened_streams_ml': st.stdev(across),
            'range_across_reopened_streams_ml': max(across) - min(across),
            'pooled_sd_within_stream_ml': (sum(st.pvariance(v) * len(v) for v in within.values()) /
                                           sum(len(v) - 1 for v in within.values())) ** .5,
            'mean_minus_codex_park_ml': st.mean(across) - CODEX_PARK[k],
        }
    out['first_utc'], out['last_utc'] = rows[0]['utc'], rows[-1]['utc']
    later = []
    for name in sys.argv[2:]:
        later += images(Path(logs) / name)
    out['later_rest_readings'] = [{'utc': r['utc'], 'x990': r['readings']['x990']['ml'], 'x1986': r['readings']['x1986']['ml']}
                                  for r in later]
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main(sys.argv[1])
