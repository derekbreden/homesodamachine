# Prepare the matched shoulder plate

Run from the checkout root. The rear-seam archive supplies the rest of the
plate's deposition. The native donor and full rotated template supply the tip
roads and archive metadata.

```sh
sculpted="$PWD/hardware/printed-parts/faucet/sculpted"
trial="$sculpted/prints/2026-11-14-matched-shoulder-mark2"
prior="$sculpted/prints/2026-11-14-rear-seam-mark2"
mkdir -p "$PWD/.cache/runs"
run="$(mktemp -d "$PWD/.cache/runs/faucet-matched-repro.XXXXXX")"
unzip -q "$trial/run-inputs.zip" -d "$run"
unzip -p "$prior/sculpted-faucet-rear-seam-black-mark2-review.gcode.3mf" Metadata/plate_1.gcode > "$run/rear.gcode"
unzip -p "$run/donor/matched-donor.gcode.3mf" Metadata/plate_1.gcode > "$run/donor/plate_1.gcode"

rustup_bin="$(command -v rustup || printf %s /opt/homebrew/bin/rustup)"
cargo_bin="$("$rustup_bin" which cargo)"
tools/run -- "$cargo_bin" build --release --locked --offline -j 2 \
  --manifest-path tools/hsm/Cargo.toml -p hsm-print-prep --bin sculpted-trial --bin sculpted-faucet-print-project
stages="$PWD/tools/hsm/target/release/sculpted-trial"
prep="$PWD/tools/hsm/target/release/sculpted-faucet-print-project"

tools/run -- "$stages" tape "$run/donor/plate_1.gcode" "$run/donor/matched-donor.print.json" \
  "$run/donor/tip-warped.json" "$run/tip.gcode" --band-step 0 --native-nose
tools/run -- "$stages" merge "$run/rear.gcode" --candidate "$run/tip.gcode" "$run/uncapped.gcode"
tools/run -- "$stages" cap-feed "$run/uncapped.gcode" "$run/capped.gcode"
tools/run -- "$stages" bind-capped "$run/uncapped.gcode" "$run/capped.gcode" "$run/plate.gcode" \
  --clamp-receipt "$run/capped.json"
motion="$(jq -r .complete_motion_time_seconds "$trial/chronology.json")"
first="$(jq -r .first_bed_course_deposition_span_seconds "$trial/chronology.json")"
tools/run -- "$stages" package "$run/template/matched-native.gcode.3mf" "$run/plate.gcode" \
  "$run/review.gcode.3mf" --motion-seconds "$motion" --first-course-seconds "$first"
tools/run -- hsm-gcode compare "$run/motion/plate.gcode" "$run/plate.gcode"
```

To regenerate the editable and donor projects from the saved tip, cover and
finish, use the physical pose in the [warp receipt](tip-warp.json). The
donor's course bands follow the bearing layer and the end of the taper.

```sh
mkdir "$run/regenerated"
rotation="$(jq -r .orientation_degrees "$trial/tip-warp.json")"
tools/run -- "$prep" "$run/regenerated/editable.3mf" --printer Mark2 \
  --filament-colour '#161616' --physical-base --tip-rotation "$rotation" \
  --tip-mesh "$run/model/tip.stl" --cover-mesh "$run/model/cover.stl" --finish "$run/model/finish-selection.json"
tools/run -- "$stages" warp matched-shoulder "$run/model/tip.stl" \
  "$run/regenerated/editable.3mf" "$run/regenerated/tip-warped.stl"
tools/run -- "$stages" supports "$run/regenerated/tip-warped.json" "$run/regenerated/warp-settings.json"
tools/run -- "$prep" "$run/regenerated/matched-donor.3mf" --printer Mark2 \
  --filament-colour '#161616' --warp-donor --tip-rotation "$rotation" \
  --tip-mesh "$run/regenerated/tip-warped.stl" --warp-settings "$run/regenerated/warp-settings.json" \
  --finish "$run/model/finish-selection.json" --slice-output "$run/regenerated/donor"
```
