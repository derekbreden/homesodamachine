#!/usr/bin/env bash
# Run the engine without taking the keyboard.
#
# The bare `godot` binary opens a window and brings it to the front, so every render steals focus
# from whoever is typing. Neither job needs the foreground:
#
#   hardware/godot/run.sh settle --scene x.glb --free 'wago-*' --out settled.json
#   hardware/godot/run.sh look   --scene x.glb --view front --ortho --shot out.png
#
# `settle` is physics and JSON and touches no viewport, so it runs headless. `look` reads a frame
# back off a real GL context — headless gives the dummy driver and no image — so it goes through
# `open -g -j`, which launches the bundle hidden and off the front. `open` reports ITS OWN exit
# code and swallows stdout, so the run's account is the log.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
job="${1:?usage: run.sh settle|look [engine args]}"
shift

case "$job" in
  settle)
    exec godot --headless --path "$here" res://settle.tscn --quit-after 60000 -- "$@"
    ;;
  look)
    log="$(mktemp -t godot-look)"
    open -g -j -W -a /Applications/Godot.app --args \
      --path "$here" res://machine.tscn --quit-after 900 --log-file "$log" -- "$@"
    grep -vE '^(Godot Engine v|Metal |$)' "$log" || true
    if grep -qE '^(ERROR|SCRIPT ERROR|USER ERROR)' "$log"; then exit 1; fi
    ;;
  *)
    echo "run.sh: no job named '$job' — settle or look" >&2
    exit 2
    ;;
esac
