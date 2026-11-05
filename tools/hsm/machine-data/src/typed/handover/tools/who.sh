#!/bin/zsh
# usage: who.sh <module>  — genrules whose coverage log shows a function of <module> running,
# with the number of distinct functions seen. Coverage comes from cover-logs/<genrule>.log.
R=/Users/derekbredensteiner/Developer/homesodamachine/.cache/runs/machine-typed-202611041700
for f in $R/cover-logs/*.log; do
  n=$(grep -E "^$1\|" $f | sort -u | wc -l | tr -d ' ')
  [[ $n -gt 0 ]] && echo "${f:t:r} $n"
done | sort -k2 -n -r
