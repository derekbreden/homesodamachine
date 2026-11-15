# Prepare the short-foundation Mark2 plate

The saved native slice carries the wall and scarf settings of the [sloped
underside print](https://github.com/derekbreden/homesodamachine/tree/c8667107f964589be7dc69f8fb924f69a12729b3/hardware/printed-parts/faucet/sculpted/prints/2026-11-13-sloped-underside-complete-mark2).
The retained donor tape supplies the tip's interface and first shell courses.

```sh
trial="$PWD/hardware/printed-parts/faucet/sculpted/prints/2026-11-14-seven-courses-mark2"
mkdir -p "$PWD/.cache/runs"
run="$(mktemp -d "$PWD/.cache/runs/sculpted-seven-courses-repro.XXXXXX")"
unzip -q "$trial/run-inputs.zip" -d "$run"
unzip -p "$run/native.gcode.3mf" Metadata/plate_1.gcode > "$run/native.gcode"

rustup_bin="$(command -v rustup || printf %s /opt/homebrew/bin/rustup)"
cargo_bin="$("$rustup_bin" which cargo)"
tools/run -- "$cargo_bin" build --release --locked --offline -j 2 \
  --manifest-path tools/hsm/Cargo.toml -p hsm-print-prep --bin sculpted-trial
stages="$PWD/tools/hsm/target/release/sculpted-trial"
courses="$(jq -r .laid.sloped_courses "$trial/foundation.json")"
tools/run -- "$stages" foundation "$run/native.gcode.3mf" "$run/native.print.json" \
  "$run/base.stl" "$PWD/tools/hsm/print-prep/faucet-underside/left-active-height.npz" \
  "$run/base" --part-courses "$courses"
"$stages" rings "$run/rings.gcode"
tools/run -- "$stages" sequence-foundations "$run/base/plate_1.gcode" "$run/native.gcode" \
  "$run/tip.gcode" "$run/tip-warped.json" "$run/rings.gcode" "$run/open.gcode"
tools/run -- "$stages" cap-feed "$run/open.gcode" "$run/capped.gcode"
tools/run -- "$stages" bind-capped "$run/open.gcode" "$run/capped.gcode" "$run/plate.gcode" \
  --clamp-receipt "$run/capped.json"
motion="$(jq -r .complete_motion_time_seconds "$trial/chronology.json")"
first="$(jq -r .first_bed_course_deposition_span_seconds "$trial/chronology.json")"
tools/run -- "$stages" package "$run/native.gcode.3mf" "$run/plate.gcode" \
  "$run/review.gcode.3mf" --motion-seconds "$motion" --first-course-seconds "$first"
hsm-gcode compare "$trial/sculpted-faucet-seven-courses-black-mark2.gcode.3mf" "$run/review.gcode.3mf"
```
