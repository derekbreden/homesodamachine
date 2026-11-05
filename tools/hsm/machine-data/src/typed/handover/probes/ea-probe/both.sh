#!/bin/zsh
R=/Users/derekbredensteiner/Developer/homesodamachine/.cache/runs/machine-typed-202611041700
W=$R/ws/assembly/probe
zsh $W/run_probe.sh base $R/bin/machine-data
zsh $W/run_probe.sh assembly $R/ws/assembly/target/release/machine-data
