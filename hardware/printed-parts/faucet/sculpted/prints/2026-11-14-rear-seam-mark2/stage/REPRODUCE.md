# Prepare the rear seam plate

Run from the repository root. The base uses the flat donor's exterior wall
laps and joins the native upper slice at the shaft. The printed plug-ramp
plate supplies the other four parts' deposition. The complete native archive
supplies the preview and part metadata.

```sh
sculpted="$PWD/hardware/printed-parts/faucet/sculpted"
trial="$sculpted/prints/2026-11-14-rear-seam-mark2"
prior="$sculpted/prints/2026-11-14-plug-ramp-mark2"
run="$(mktemp -d "$PWD/.cache/runs/faucet-rear-seam-repro.XXXXXX")"
mkdir "$run/donors"
unzip -q "$trial/run-inputs.zip" -d "$run"
unzip -q "$prior/run-inputs.zip" native/complete.gcode.3mf \
  motion/plate.gcode motion/mapped-tip.gcode motion/rings.gcode -d "$run/donors"
unzip -p "$run/donors/native/complete.gcode.3mf" Metadata/plate_1.gcode > "$run/native.gcode"

rustup_bin="$(command -v rustup || printf %s /opt/homebrew/bin/rustup)"
cargo_bin="$("$rustup_bin" which cargo)"
export RUSTC="$("$rustup_bin" which rustc)"
targets="$PWD/tools/hsm/target/release"
tools/run -- "$cargo_bin" build --release --locked --offline -j 2 \
  --manifest-path tools/hsm/Cargo.toml -p hsm-print-prep --bin sculpted-trial \
  --message-format=json > "$run/build.jsonl"
lib="$(jq -r 'select(.reason=="compiler-artifact" and .target.name=="hsm_print_prep") | .filenames[] | select(endswith(".rlib"))' "$run/build.jsonl")"
tools/run -- "$RUSTC" --edition=2024 -C opt-level=3 -L "dependency=$targets/deps" \
  --extern "hsm_print_prep=$lib" "$trial/stage/retain-other-parts.rs" -o "$run/retain-other-parts"

tools/run -- "$targets/sculpted-trial" continued-base \
  "$run/base/donor.gcode" "$run/base/donor.print.json" \
  "$run/base/physical.gcode" "$run/base/physical.print.json" \
  "$run/continued-base.gcode" --stitch-mesh "$run/base/base.stl"
tools/run -- "$targets/sculpted-trial" sequence-shaft "$run/base/foundation.gcode" \
  "$run/shaft.gcode" --donor "$run/continued-base.gcode"
tools/run -- "$targets/sculpted-trial" cool-shaft-join "$run/shaft.gcode" \
  "$run/base/cooling.3mf" "$run/cooled.gcode"
tools/run -- "$targets/sculpted-trial" sequence "$run/cooled.gcode" "$run/native.gcode" \
  "$run/uncapped.gcode" --tip-model "$run/donors/motion/mapped-tip.gcode" \
  --entire-tip-custom --plate-rings "$run/donors/motion/rings.gcode"
tools/run -- "$run/retain-other-parts" "$run/donors/motion/plate.gcode" \
  "$run/uncapped.gcode" "$run/plate.gcode"
tools/run -- hsm-gcode view playback "$run/plate.gcode" --layers all --inline --data \
  --title 'Sculpted faucet rear seam' --out "$run/playback.json"
motion="$(jq -r .seconds "$run/playback.json")"
first="$(jq -r .first_bed_course_deposition_span_seconds "$trial/chronology.json")"
tools/run -- "$targets/sculpted-trial" package "$run/donors/native/complete.gcode.3mf" \
  "$run/plate.gcode" "$run/review.gcode.3mf" --motion-seconds "$motion" --first-course-seconds "$first"
```

Use the saved continued base tape in `motion/continued-base.gcode` to inspect
the commands that feed the review archive. Evaluate new preparations by the wall
paths and their deposition in the [seam reading](../seam-evidence.json). The
[retained deposition](../retained-deposition.json) describes the archived review plate.
