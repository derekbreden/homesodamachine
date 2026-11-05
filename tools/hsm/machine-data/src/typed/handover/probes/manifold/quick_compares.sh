#!/bin/zsh
# usage: quick_compares.sh <binary> <out.jsonl> [targets...]
R=/Users/derekbredensteiner/Developer/homesodamachine/.cache/runs/machine-typed-202611041700
PY=/Users/derekbredensteiner/Developer/homesodamachine/tools/cad-venv/bin/python
BIN=$1; OUT=$2; shift 2
TS=(${@:-acceptance-and-burn-in-sync firmware-and-commissioning-sync fluid-topology-sync internal-plumbing-sync manifold-layout bom-masses})
cd $R || exit 1
for t in $TS; do
  echo "== $t $(date +%T)"
  BINDIR=$R/bin-all $PY compare.py steps $t base0-manifold=$R/bin-base0/machine-data manifold=$BIN | tee -a $OUT | cut -c1-600
done
echo "done $(date +%T)"
