# Prepare the extended-cover Mark2 plate

The steady finish is applied to the complete toolpath after the enlarged cover's
native roads are scheduled with the matched tip, base, lever and mounting plate.

```sh
sculpted="$PWD/hardware/printed-parts/faucet/sculpted"
trial="$sculpted/prints/2026-11-14-aft-cover-mark2"
prior="$sculpted/prints/2026-11-14-matched-shoulder-mark2"
mkdir -p "$PWD/.cache/runs"
run="$(mktemp -d "$PWD/.cache/runs/sculpted-aft-cover-repro.XXXXXX")"
unzip -q "$trial/run-inputs.zip" -d "$run"
unzip -q "$prior/run-inputs.zip" motion/tip.gcode -d "$run"
unzip -p "$prior/sculpted-faucet-matched-shoulder-black-mark2-review.gcode.3mf" Metadata/plate_1.gcode > "$run/matched.gcode"
unzip -p "$run/template/slice/full.gcode.3mf" Metadata/plate_1.gcode > "$run/native.gcode"

rustup_bin="$(command -v rustup || printf %s /opt/homebrew/bin/rustup)"
cargo_bin="$("$rustup_bin" which cargo)"
tools/run -- "$cargo_bin" build --release --locked --offline -j 2 \
  --manifest-path tools/hsm/Cargo.toml -p hsm-print-prep --bin sculpted-trial
stages="$PWD/tools/hsm/target/release/sculpted-trial"
tools/run -- "$stages" sequence "$run/matched.gcode" "$run/native.gcode" "$run/uncapped.gcode" \
  --entire-tip-custom --tip-model "$run/motion/tip.gcode"
tools/run -- "$stages" cap-feed "$run/uncapped.gcode" "$run/capped.gcode"
tools/run -- "$stages" bind-capped "$run/uncapped.gcode" "$run/capped.gcode" "$run/pre-finish.gcode" \
  --clamp-receipt "$run/capped.json"
tools/run -- "$stages" finish-base-wall "$run/pre-finish.gcode" "$run/plate.gcode" > "$run/wall-speed.json"
jq --slurpfile finish "$run/wall-speed.json" \
  '.sequenced_gcode_sha256 = $finish[0].gcode_sha256' "$run/pre-finish.json" > "$run/plate.json"
motion="$(jq -r .complete_motion_time_seconds "$trial/chronology.json")"
first="$(jq -r .first_bed_course_deposition_span_seconds "$trial/chronology.json")"
tools/run -- "$stages" package "$run/template/slice/full.gcode.3mf" "$run/plate.gcode" \
  "$run/review.gcode.3mf" --motion-seconds "$motion" --first-course-seconds "$first"
tools/run -- hsm-gcode compare "$trial/sculpted-faucet-aft-cover-black-mark2.gcode.3mf" "$run/review.gcode.3mf"
```

The native input project uses the revised [cover loft](../../../faucet-display-cover/numbers.rs)
with the [flat dispense-face tab](../2026-11-14-tip-shoulder-mark2/stage/dispense-face.rs).
The editable project uses the assembled part geometry. The native input project fills
under the base for the native slice and the sequencer installs the reviewed base paths.
