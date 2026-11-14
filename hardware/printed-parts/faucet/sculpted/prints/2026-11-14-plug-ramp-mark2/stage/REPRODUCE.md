# Reproduce the Mark2 plug ramp

Run from the checkout root. The saved native slices reproduce the exact commands
accepted by the printer.

```sh
sculpted='hardware/printed-parts/faucet/sculpted'
trial="$PWD/$sculpted/prints/2026-11-14-plug-ramp-mark2"
stage="$trial/stage"
flat='f5dee32108832f6d0e1f5c50dbb8f7fd5c30576e'
previous="$sculpted/prints/2026-11-14-tip-shoulder-mark2"
shaft_store='ddd391f3d32bd8397f08b517ee58614fcd3e93ba:hardware/printed-parts/faucet/sculpted/prints/2026-11-13-shaft-tilted-mark2/stage'
cad_py="$PWD/tools/cad-venv/bin/python"
mkdir -p "$PWD/.cache/runs"
run="$(mktemp -d "$PWD/.cache/runs/faucet-plug-ramp-repro.XXXXXX")"
unzip -q "$trial/run-inputs.zip" -d "$run"
git show "$flat:$previous/stage/tip_geometry.py" > "$run/tip_geometry.py"
git show "$flat:$previous/stage/sequence.py" > "$run/archived_sequence.py"
git show "$shaft_store/map_base.py" > "$run/map_base.py"
git show "$shaft_store/package.py" > "$run/package.py"
cp "$stage/merge.py" "$run/merge.py"
export PYTHONPATH="$run${PYTHONPATH:+:$PYTHONPATH}"

git show "$flat:$previous/sculpted-faucet-flat-face-black-mark2-review.gcode.3mf" > "$run/previous.gcode.3mf"
unzip -p "$run/previous.gcode.3mf" Metadata/plate_1.gcode > "$run/previous.gcode"
unzip -p "$run/donor/ramp.gcode.3mf" Metadata/plate_1.gcode > "$run/donor/plate_1.gcode"

tools/run -- "$cad_py" "$stage/tip_tape.py" "$run/donor/plate_1.gcode" \
  "$run/donor/ramp.print.json" "$run/donor/tip-warped.json" "$run/mapped-tip.gcode" --band-step 0 --native-nose
cmp "$run/mapped-tip.gcode" "$run/motion/mapped-tip.gcode"
tools/run -- python3 "$run/merge.py" "$run/previous.gcode" --candidate "$run/mapped-tip.gcode" "$run/uncapped.gcode"
tools/run -- python3 "$stage/cap-feed.py" "$run/uncapped.gcode" "$run/capped.gcode"
cmp "$run/capped.gcode" "$run/motion/plate.gcode"
python3 "$stage/bind_capped.py" "$run/uncapped.gcode" "$run/capped.gcode" "$run/plate.gcode" \
  --clamp-receipt "$run/capped.json"

motion="$(python3 -c 'import json,sys;x=json.load(open(sys.argv[1]));print(x["complete_motion_time_seconds"])' "$trial/plate.json")"
first="$(python3 -c 'import json,sys;x=json.load(open(sys.argv[1]));print(x["first_bed_course_deposition_span_seconds"])' "$trial/plate.json")"
tools/run -- python3 "$run/package.py" "$run/native/complete.gcode.3mf" "$run/plate.gcode" \
  "$run/reproduced.gcode.3mf" --motion-seconds "$motion" --first-course-seconds "$first"
unzip -p "$run/reproduced.gcode.3mf" Metadata/plate_1.gcode > "$run/reproduced.gcode"
unzip -p "$trial/sculpted-faucet-plug-ramp-black-mark2-review.gcode.3mf" Metadata/plate_1.gcode > "$run/submitted.gcode"
cmp "$run/reproduced.gcode" "$run/submitted.gcode"
```

To build the donor again, use the standing Sculpted preparer. The selected
physical tip and its editable plate supply the warp. The support recipe describes
the mating annulus, outside access slits and plug keepout in donor coordinates.
A fresh native slice can choose different paths. The saved slice remains the
source for reproducing the launched motion.

```sh
rustup_bin="$(command -v rustup || printf %s /opt/homebrew/bin/rustup)"
cargo_bin="$("$rustup_bin" which cargo)"
tools/run -- "$cargo_bin" build --release --locked --offline -j 2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-print-prep --bin sculpted-faucet-print-project
mkdir "$run/rebuilt"
tools/run -- "$cad_py" "$stage/tip_warp.py" "$run/donor/tip.stl" "$run/native/editable.3mf" "$run/rebuilt/tip-warped.stl"
"$cad_py" "$stage/shoulder_support.py" "$run/rebuilt/tip-warped.json" "$run/rebuilt/warp-settings.json"
tools/run -- tools/hsm/target/release/sculpted-faucet-print-project "$run/rebuilt/ramp.3mf" --printer Mark2 \
  --filament-colour '#161616' --warp-donor --tip-mesh "$run/rebuilt/tip-warped.stl" \
  --warp-settings "$run/rebuilt/warp-settings.json" --finish "$run/native/finish-selection.json"
cmp "$run/rebuilt/ramp.3mf" "$run/donor/ramp.3mf"
```
