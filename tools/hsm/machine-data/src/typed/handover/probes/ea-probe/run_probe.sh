#!/bin/zsh
# usage: run_probe.sh <label> <machine-data binary> [probe script]   — one probe run in a clone of the
# enclosure-assembly stage, at one fixed path so absolute paths match between runs.
# Workers come from bin-all; unpinned-<label>.txt names any taken from the live checkout.
R=/Users/derekbredensteiner/Developer/homesodamachine/.cache/runs/machine-typed-202611041700
REPO=/Users/derekbredensteiner/Developer/homesodamachine
PY=$REPO/tools/cad-venv/bin/python
W=$R/ws/assembly/probe
work=$W/tree
rm -rf $work $W/unpinned-$1.txt
cp -c -R $R/steps/enclosure-assembly $work || exit 1
cd $work
HSM_REPO_ROOT=$work HSM_INPUT_DIGEST=probe HSM_WORKSPACE=$REPO UNPINNED_LOG=$W/unpinned-$1.txt /usr/bin/time -l $PY $R/harness.py $R/bin-all $2 $W/${3:-ea_probe.py} $W/out-$1.jsonl > $W/log-$1.txt 2>&1
echo "exit $?" >> $W/log-$1.txt
cd $W
rm -rf $work
