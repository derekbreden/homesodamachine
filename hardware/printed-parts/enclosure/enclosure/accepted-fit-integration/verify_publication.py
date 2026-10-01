"""Check that the live CAD URLs serve the current local integration artifacts."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools').is_dir())


def check(row):
    path = ROOT / row['local_path']
    expected = hashlib.sha256(path.read_bytes()).hexdigest()
    url = row['url'].split('?')[0] + '?v=' + expected[:16]
    with urlopen(url, timeout=60) as response:
        payload = response.read()
    served = hashlib.sha256(payload).hexdigest()
    return dict(url=url, local_path=row['local_path'], expected_sha256=expected,
                served_sha256=served, bytes=len(payload), **{'pass': served == expected})


if __name__ == '__main__':
    report_path = HERE / 'published-artifacts.json'
    previous = json.loads(report_path.read_text())
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(check, previous['artifacts']))
    report = {'pass': all(row['pass'] for row in rows),
              'observed_at_utc': datetime.now(timezone.utc).isoformat(), 'artifacts': rows}
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    assert report['pass'], report
    print(f'Live bytes match all {len(rows)} local artifacts.')
