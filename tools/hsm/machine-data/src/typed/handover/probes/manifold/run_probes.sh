#!/bin/zsh
# usage: run_probes.sh <machine-data binary> <tag>
# Runs ns_dump.py and fn_dump.py with that binary (pinned workers from bin-all, hash seed 0) and
# diffs them against ns_base2.json / fn_base2.json / fn_base2.out.
R=/Users/derekbredensteiner/Developer/homesodamachine/.cache/runs/machine-typed-202611041700
PY=/Users/derekbredensteiner/Developer/homesodamachine/tools/cad-venv/bin/python
P=$R/ws/manifold/probe
BIN=$1
TAG=${2:-mine}
cd $P/work-base || exit 1
PYTHONHASHSEED=0 DUMP_OUT=$P/ns_$TAG.json $PY $R/harness.py $R/bin-all $BIN $P/ns_dump.py > $P/ns_$TAG.out 2>&1
PYTHONHASHSEED=0 DUMP_OUT=$P/fn_$TAG.json $PY $R/harness.py $R/bin-all $BIN $P/fn_dump.py > $P/fn_$TAG.out 2>&1
tail -1 $P/ns_$TAG.out
tail -1 $P/fn_$TAG.out
$PY - $P $TAG <<'EOF'
import json, sys
P, tag = sys.argv[1], sys.argv[2]
a = json.load(open(f"{P}/ns_base2.json")); b = json.load(open(f"{P}/ns_{tag}.json"))
an = [r[0] for r in a]; bn = [r[0] for r in b]
print("ns names", len(an), len(bn), "order same" if an == bn else "ORDER DIFFERS")
if an != bn:
    import difflib
    for line in difflib.unified_diff(an, bn, lineterm="", n=1):
        print("  ", line)
bd = dict((r[0], r) for r in b)
nd = 0
for r in a:
    o = bd.get(r[0])
    if o != r:
        nd += 1
        if nd <= 20:
            print("ns DIFF", r[0]); print("   base", str(r[1:])[:400]); print("   mine", str(o and o[1:])[:400])
print("ns differ", nd)
fa = json.load(open(f"{P}/fn_base2.json")); fb = json.load(open(f"{P}/fn_{tag}.json"))
print("fn calls", len(fa), len(fb))
fd = 0
for x, y in zip(fa, fb):
    if x != y:
        fd += 1
        if fd <= 30:
            print("fn DIFF", x[0], "|", y[0]); print("   base", x[1][:500]); print("   mine", y[1][:500])
print("fn differ", fd)
oa = open(f"{P}/fn_base2.out").read().splitlines(); ob = open(f"{P}/fn_{tag}.out").read().splitlines()
import difflib
d = list(difflib.unified_diff(oa, ob, "base", tag, lineterm="", n=0))
print("stdout diff lines", len(d))
for line in d[:40]:
    print("  ", line[:300])
EOF
