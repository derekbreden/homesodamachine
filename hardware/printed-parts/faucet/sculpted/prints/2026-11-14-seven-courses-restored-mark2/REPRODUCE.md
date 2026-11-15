# Prepare the restored short-foundation Mark2 plate

The [retained inputs](run-inputs.zip) hold the sliced project and its native slice as the slicer
wrote it, the [stopped short-foundation plate's](https://github.com/derekbreden/homesodamachine/tree/9ebc8ac1b152c1845f673ce2613d9cbbb9f3cd66/hardware/printed-parts/faucet/sculpted/prints/2026-11-14-seven-courses-mark2)
sliced project and a slice of it as the slicer wrote it, the plate's print report, the base mesh,
and the tip's inclined donor courses with their warp. The sliced project is the stopped plate's
with [`stage/overhang-scope.py`](stage/overhang-scope.py) applied, which the first step checks.
Slicing either project again lays the same beads apart from the slicer's own tree-support
differences between runs; the retained slices are the ones this plate was built from, and they
lay the same beads at the tip's end.

```sh
trial="$PWD/hardware/printed-parts/faucet/sculpted/prints/2026-11-14-seven-courses-restored-mark2"
mkdir -p "$PWD/.cache/runs"
run="$(mktemp -d "$PWD/.cache/runs/sculpted-seven-courses-restored-repro.XXXXXX")"
unzip -q "$trial/run-inputs.zip" -d "$run"

rustup_bin="$(command -v rustup || printf %s /opt/homebrew/bin/rustup)"
cargo_bin="$("$rustup_bin" which cargo)"
tools/run -- "$cargo_bin" build --release --locked --offline -j 2 \
  --manifest-path tools/hsm/Cargo.toml -p hsm-print-prep --bin sculpted-trial --bin petgf-cooling
stages="$PWD/tools/hsm/target/release/sculpted-trial"
cooling="$PWD/tools/hsm/target/release/petgf-cooling"
headmap="$PWD/tools/hsm/print-prep/faucet-underside/left-active-height.npz"

# the sliced project is the stopped plate's with the overhang scope applied
python3 "$trial/stage/overhang-scope.py" "$run/plain.3mf" "$run/scoped.3mf"
cmp "$run/scoped.3mf" "$run/native.3mf"

# the lowest layer the tip-end cooling stage cools on this plate's slice, after the
# bridge-foundation stage, as the standing slice path runs them
mkdir "$run/level"
cp "$run/native.gcode.3mf" "$run/level/native.gcode.3mf"
unzip -p "$run/native.gcode.3mf" Metadata/plate_1.gcode > "$run/level/plate_1.gcode"
tools/run -- "$cooling" --directory "$run/level" --project "$run/native.3mf" > "$run/level-cooling.json"
tools/run -- "$stages" cool-tip-end "$run/level" "$run/native.3mf" "$run/native.print.json" \
  > "$run/tip-end.json"

# the tip's layers from there up from the stopped plate's slice, then the same stages over the splice
tools/run -- "$stages" splice-tip-end "$run/native.gcode.3mf" "$run/plain.gcode.3mf" \
  "$run/tip-end.json" "$run/slice" native > "$run/tip-end-splice.json"
tools/run -- "$cooling" --directory "$run/slice" --project "$run/native.3mf" > "$run/cooling.json"
tools/run -- "$stages" cool-tip-end "$run/slice" "$run/native.3mf" "$run/native.print.json" \
  > "$run/tip-end-cooling.json"

courses="$(jq -r .laid.sloped_courses "$trial/foundation.json")"
tools/run -- "$stages" foundation "$run/slice/native.gcode.3mf" "$run/native.print.json" \
  "$run/base.stl" "$headmap" "$run/base" --part-courses "$courses"
"$stages" rings "$run/rings.gcode"
tools/run -- "$stages" sequence-foundations "$run/base/plate_1.gcode" "$run/slice/plate_1.gcode" \
  "$run/tip.gcode" "$run/tip-warped.json" "$run/rings.gcode" "$run/open.gcode" --headmap "$headmap"
tools/run -- "$stages" cap-feed "$run/open.gcode" "$run/capped.gcode"
tools/run -- "$stages" bind-capped "$run/open.gcode" "$run/capped.gcode" "$run/plate.gcode" \
  --clamp-receipt "$run/capped.json"
# the printer's percent and time-left, at the points the motion estimate put them
"$stages" progress "$run/plate.gcode" "$trial/progress.json" "$run/progressed.gcode"
motion="$(jq -r .complete_motion_time_seconds "$trial/chronology.json")"
first="$(jq -r .first_bed_course_deposition_span_seconds "$trial/chronology.json")"
tools/run -- "$stages" package "$run/slice/native.gcode.3mf" "$run/progressed.gcode" \
  "$run/review.gcode.3mf" --motion-seconds "$motion" --first-course-seconds "$first"
unzip -p "$trial/sculpted-faucet-seven-courses-restored-black-mark2.gcode.3mf" Metadata/plate_1.gcode \
  | cmp - <(unzip -p "$run/review.gcode.3mf" Metadata/plate_1.gcode)
```

The [progress points](progress.json) came from the motion reader's per-move times on the
bound plate, `sculpted-trial progress PLATE.gcode MOVES.bin OUT.gcode`, the same moves the
[estimate](chronology.json) clocks.

Slicing a retained project again takes the standing slice path: `hsm_print_prep::slice::run`
with Bambu Studio's command line, which leaves the project's cooling hook to its caller, then
the stages above. `hsm-gcode compare` of a fresh slice against the retained one shows only the
slicer's own tree-support differences. The splice takes the tip's end, supports included, from
the second slice.
