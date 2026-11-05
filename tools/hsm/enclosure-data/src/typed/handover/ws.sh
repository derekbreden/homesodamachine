#!/bin/zsh
# usage: ws.sh <name> [<module> ...]
# A private hybrid workspace at aws/<name>. Your own modules (the ones named here, now or on an
# earlier run, kept in aws/<name>/.own) compile live from the real tree. Every other converted
# module (TYPED = true) is copied as it stands at this run, so another agent's unfinished edits
# never break your build; re-run to take their latest. Every other module is a placeholder, so its
# generated namespace runs. The shared runtime files compile live from the real tree.
# A file in a subdirectory of typed/ is named <dir>/<stem> (for example enclosure/p3).
R=/Users/derekbredensteiner/Developer/homesodamachine/.cache/runs/typed-enclosure-202611041700
REAL=/Users/derekbredensteiner/Developer/homesodamachine/tools/hsm/enclosure-data/src/typed
name=$1; shift
W=$R/aws/$name
D=$W/enclosure-data/src/typed
mkdir -p $D
# The modules this workspace owns: an earlier run's, else the module files it links live.
if [[ ! -f $W/.own ]]; then
  : > $W/.own
  for f in $D/*.rs(N@); do
    m=${f:t:r}
    [[ -f $R/placeholders/$m.rs && $(readlink $f) == $REAL/$m.rs ]] && echo $m >> $W/.own
  done
fi
for m in "$@"; do grep -qxF -- "$m" $W/.own || echo $m >> $W/.own; done
own=(${(f)"$(<$W/.own)"})
cp $R/typed/Cargo.toml $W/Cargo.toml
[[ -f $W/Cargo.lock ]] || cp $R/typed/Cargo.lock $W/Cargo.lock
cp $R/typed/enclosure-data/Cargo.toml $W/enclosure-data/Cargo.toml
# Start from the base workspace's compiled dependencies (an APFS clone costs nothing).
[[ -d $W/target || ! -d $R/aws/base/target || $name == base ]] || cp -cR $R/aws/base/target $W/target
for f in $R/typed/enclosure-data/src/*; do
  b=${f:t}
  [[ $b == typed ]] && continue
  ln -sfn $f $W/enclosure-data/src/$b
done
# put <real file> <workspace file> <name>: live link when owned, else a copy as it stands now.
put() {
  rm -f $2
  if (( ${own[(Ie)$3]} )); then ln -s $1 $2; else cp $1 $2; fi
}
# Shared runtime files: every .rs in the real typed/ that is not a module slot.
for f in $REAL/*.rs; do
  m=${f:t:r}
  [[ -f $R/placeholders/$m.rs ]] && continue
  ln -sfn $f $D/$m.rs
done
for p in $R/placeholders/*.rs; do
  m=${p:t:r}
  rm -f $D/$m.rs; ln -s $p $D/$m.rs
done
for f in $REAL/*.rs; do
  m=${f:t:r}
  [[ -f $R/placeholders/$m.rs ]] || continue
  if (( ${own[(Ie)$m]} )) || grep -q '^pub const TYPED: bool = true;' $f; then put $f $D/$m.rs $m; fi
done
# Subdirectories (a module's own submodules): each file live when owned, else copied.
for d in $REAL/*(N/); do
  dn=${d:t}
  [[ -L $D/$dn ]] && rm $D/$dn
  mkdir -p $D/$dn
  for f in $d/*.rs(N); do put $f $D/$dn/${f:t} $dn/${f:t:r}; done
done
echo "workspace $W (own: ${own[*]})"
for f in $D/*.rs(N) $D/*/*.rs(N); do
  if [[ -L $f ]]; then t=$(readlink $f); [[ $t == $R/placeholders/* ]] && continue; echo "live ${f#$D/}"; else echo "copy ${f#$D/}"; fi
done | grep -v '^live \(mod\|rt\|py\|num\)\.rs$'
