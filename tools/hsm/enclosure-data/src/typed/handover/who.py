"""Which genrules exercise a module: steps whose traces show the module's functions running or
the module being imported or read, with the number of its distinct functions seen.

usage: who.py <module>
"""
import collections
import glob
import os
import re
import sys

RUN = os.path.dirname(os.path.abspath(__file__))
module = sys.argv[1]
pat = re.compile(rf'compiled/{re.escape(module)}\.rs:(\d+)')
req = re.compile(rf'^(req|send)\t.*\b{re.escape(module)}\b')
seen = collections.defaultdict(set)
for path in glob.glob(f'{RUN}/trace/*.log') + glob.glob(f'{RUN}/trace-types/*.log'):
    rule = re.sub(r'-\d+\.(py|cb|types)?\.?log$', '', os.path.basename(path))
    rule = re.sub(r'-\d+\.log$', '', rule)
    for line in open(path, errors='replace'):
        m = pat.search(line)
        if m:
            seen[rule].add(m.group(1))
        elif req.search(line):
            seen[rule]
for rule, lines in sorted(seen.items(), key=lambda kv: -len(kv[1])):
    print(rule, len(lines))
