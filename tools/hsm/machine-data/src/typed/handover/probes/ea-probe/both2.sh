#!/bin/zsh
R=/Users/derekbredensteiner/Developer/homesodamachine/.cache/runs/machine-typed-202611041700
W=$R/ws/assembly/probe
zsh $W/run_probe.sh base2 $R/bin/machine-data ea_probe2.py
zsh $W/run_probe.sh assembly2 $R/ws/assembly/target/release/machine-data ea_probe2.py
