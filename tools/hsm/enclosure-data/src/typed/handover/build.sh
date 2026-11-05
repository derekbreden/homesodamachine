#!/bin/zsh
# usage: build.sh <name>   — builds aws/<name> (through tools/run.py) and prints errors only.
# The binary is aws/<name>/target/release/enclosure-data.
R=/Users/derekbredensteiner/Developer/homesodamachine/.cache/runs/typed-enclosure-202611041700
W=$R/aws/$1
cd $W || exit 1
PATH=/opt/homebrew/opt/rustup/bin:$PATH CARGO_TARGET_DIR=$W/target python3 /Users/derekbredensteiner/Developer/homesodamachine/tools/run.py -- \
  cargo build -j2 --release --locked --manifest-path enclosure-data/Cargo.toml --message-format short 2>&1 \
  | grep -E '^(enclosure-data/src/typed/|error)|Finished' | grep -v 'warning: unused\|is never used\|never read\|never constructed\|warning: function\|warning: constant\|warning: struct\|warning: field\|warning: method\|warning: variant\|warning: associated\|warning: type alias\|warning: static' | head -${LINES_MAX:-80}
ls -la $W/target/release/enclosure-data 2>/dev/null | awk '{print $6, $7, $8, $9}'
