# Prepare the steady base wall plate

`sculpted-trial finish-base-wall` sets the finish speed on the Sculpted
base's ordinary outer-wall moves in the assembled plate. Run it after the
plate's courses are sequenced and before packaging the print archive.

```sh
source_revision=73ecc32672e0dbd84dcb7761d418fa02c5f2dab9
source_trial=hardware/printed-parts/faucet/sculpted/prints/2026-11-14-matched-shoulder-mark2
mkdir -p "$PWD/.cache/runs"
run="$(mktemp -d "$PWD/.cache/runs/sculpted-base-finish.XXXXXX")"
git show "$source_revision:$source_trial/sculpted-faucet-matched-shoulder-black-mark2-review.gcode.3mf" > "$run/source.gcode.3mf"
git show "$source_revision:$source_trial/run-inputs.zip" > "$run/source-inputs.zip"
unzip -p "$run/source.gcode.3mf" Metadata/plate_1.gcode > "$run/source.gcode"
unzip -p "$run/source-inputs.zip" motion/plate.json > "$run/source.json"

rustup_bin="$(command -v rustup || printf %s /opt/homebrew/bin/rustup)"
cargo_bin="$("$rustup_bin" which cargo)"
RUSTC="$("$rustup_bin" which rustc)" tools/run -- "$cargo_bin" build --release --locked --offline -j 2 \
  --manifest-path tools/hsm/Cargo.toml -p hsm-print-prep --bin sculpted-trial
stages="$PWD/tools/hsm/target/release/sculpted-trial"
"$stages" finish-base-wall "$run/source.gcode" "$run/finished.gcode" > "$run/wall-speed.json"
jq --slurpfile report "$run/wall-speed.json" \
  '.sequenced_gcode_sha256 = $report[0].gcode_sha256' "$run/source.json" > "$run/finished.json"

tools/run -- hsm-gcode view playback "$run/finished.gcode" --layers all --inline --data \
  --title 'Matched shoulder plate with steady base wall speed' --out "$run/timing.json"
motion="$(jq -r .seconds "$run/timing.json")"
first="$(git show "$source_revision:$source_trial/chronology.json" | jq -r .first_bed_course_deposition_span_seconds)"
"$stages" package "$run/source.gcode.3mf" "$run/finished.gcode" \
  "$run/sculpted-faucet-steady-base-wall-black-mark2.gcode.3mf" \
  --motion-seconds "$motion" --first-course-seconds "$first"
```
