#!/bin/zsh
# usage: ws.sh <name> <module> [<module> ...]
# A private hybrid workspace at ws/<name>: the named modules and every converted module
# (TYPED = true) compile from the real tree; every other module is a placeholder, so its
# generated namespace runs. Shared runtime files compile from the real tree too.
R=/Users/derekbredensteiner/Developer/homesodamachine/.cache/runs/machine-typed-202611041700
REAL=/Users/derekbredensteiner/Developer/homesodamachine/tools/hsm/machine-data/src/typed
name=$1; shift
W=$R/ws/$name
mkdir -p $W/machine-data/src/typed
sed 's/^debug = 0$/debug = 0\nincremental = true/' $R/typed/Cargo.toml > $W/Cargo.toml
cp $R/typed/Cargo.lock $W/Cargo.lock
cp $R/typed/machine-data/Cargo.toml $W/machine-data/Cargo.toml
for f in $R/typed/machine-data/src/*; do
  b=${f:t}
  [[ $b == typed ]] && continue
  ln -sfn $f $W/machine-data/src/$b
done
for f in mod.rs num.rs py.rs rt.rs docs.rs; do ln -sfn $REAL/$f $W/machine-data/src/typed/$f; done
for p in $R/placeholders/*.rs; do
  m=${p:t:r}
  ln -sfn $p $W/machine-data/src/typed/$m.rs
done
for f in $REAL/*.rs; do
  m=${f:t:r}
  if grep -q '^pub const TYPED: bool = true;' $f; then ln -sfn $f $W/machine-data/src/typed/$m.rs; fi
done
for m in "$@"; do ln -sfn $REAL/$m.rs $W/machine-data/src/typed/$m.rs; done
echo "workspace $W"
ls -l $W/machine-data/src/typed | awk '{print $9, $11}' | grep -v '^ $' | sed "s#$R/##; s#$REAL/#real:#"
