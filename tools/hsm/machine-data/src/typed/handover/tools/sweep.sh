#!/bin/zsh
# usage: sweep.sh <out.jsonl> <label=program> [<label=program> ...]
# Runs compare.py for every genrule in genrules.txt, one at a time, appending a JSON line each.
# COVER=1 gives each target its own coverage log under cover-logs/.
R=/Users/derekbredensteiner/Developer/homesodamachine/.cache/runs/machine-typed-202611041700
PY=/Users/derekbredensteiner/Developer/homesodamachine/tools/cad-venv/bin/python
out=$1; shift
mkdir -p $R/cover-logs
for t in $(cat ${TARGETS:-$R/genrules.txt}); do
  if [[ -n $COVER ]]; then export COVER_LOG=$R/cover-logs/$t.log; rm -f $COVER_LOG; fi
  $PY $R/compare.py $R/steps $t "$@" >> $out 2>> $out.err || echo "{\"target\": \"$t\", \"harness_failed\": true}" >> $out
done
echo '{"sweep": "done"}' >> $out
