# Reproduce the native Mark2 sources

Run the commands from the checkout root. Each slicer uses a separate directory
under the same scratch run. [The native-source receipt](../native-sources.json)
records input identities, tool versions and the actual slice hashes.

```sh
faucet='hardware/printed-parts/faucet'
sculpted="$faucet/sculpted"
trial="$PWD/$sculpted/prints/2026-11-13-shaft-tilted-mark2"
stage="$trial/stage"
mkdir -p "$PWD/.cache/runs"
run="$(mktemp -d "$PWD/.cache/runs/faucet-native-repro.XXXXXX")"
base="$PWD/$faucet/faucet-shell/faucet-shell-base.stl"
cover="$PWD/$faucet/faucet-display-cover/faucet-display-cover.stl"
cad_py="$PWD/tools/cad-venv/bin/python"
socket=b6f0e6063170eeeb88f62527a1adeae12be4a3f6
head=c6cecb9b0acfdb41efaf5bbf9d7ee2777fda6d54
socket_dir="$sculpted/prints/2026-11-13-sloped-foot-socket-plugs-mark2"
head_dir="$sculpted/prints/2026-11-13-dispense-face-sloped-foot-mark2"
rustup_bin="$(command -v rustup || printf %s /opt/homebrew/bin/rustup)"
cargo_bin="$("$rustup_bin" which cargo)"
export RUSTC="$("$rustup_bin" which rustc)"
mkdir -p "$run"/shape "$run"/full "$run"/flat

# Restore missing CAD exports before running the trial, with publication disabled.
# tools/run -- hsm-print-build --no-publish -- //:faucet-assembly //:faucet-shell \
#   //:faucet-display-cover //:above-counter-plate //:lever-replica
git show "$socket:$socket_dir/stage/make_union.py" > "$run/make_union.py"
"$cad_py" "$run/make_union.py" "$base" "$run/shape/filled-base.stl" "$run/base-fill.json"

example="faucet-native-repro-$(basename "$run" | cut -d. -f2)"
example_path="tools/hsm/sandbox/examples/$example.rs"
git show "$head:$head_dir/head/faucet-dispense-corner.rs" > "$example_path"
tools/run -- "$cargo_bin" run --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-sandbox --example "$example" -- "$run/shape"
rm "$example_path"
shasum -a 256 "$base" "$cover" "$run/shape/filled-base.stl" "$run/shape/tip-trial.stl"

git show "$socket:$sculpted/prepare_print_project.rs" > "$run/full/prepare_print_project.rs"
git show "$socket:$sculpted/rim_supports.rs" > "$run/full/rim_supports.rs"
git show "$head:$head_dir/stage/trial-inputs.patch" > "$run/trial-inputs.patch"
git show "$head:$head_dir/stage/finish-selection.json" > "$run/finish-selection.json"
patch -d "$run/full" -p1 < "$run/trial-inputs.patch"
python3 - "$run/full/prepare_print_project.rs" "$run/finish-selection.json" <<'PY'
import json, sys
from pathlib import Path
source = Path(sys.argv[1])
old = '"hardware/printed-parts/faucet/sculpted/finish-selection.json"'
content = source.read_text()
assert content.count(old) == 1
source.write_text(content.replace(old, json.dumps(sys.argv[2])))
PY
cp "$run/full/"*.rs "$run/flat/"
patch -d "$run/flat" -p1 < "$stage/flat-donor.patch"
patch -d "$run/flat" -p1 < "$stage/early-support.patch"

for source in full flat; do
  mkdir "$run/$source-ordinary"
  cp "$run/$source/"*.rs "$run/$source-ordinary/"
  patch -d "$run/$source-ordinary" -p1 < "$stage/no-scarf.patch"
done
tools/run -- "$cargo_bin" build --offline --locked --release -j 2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-print-prep --lib --bin petgf-cooling --message-format=json > "$run/cargo-artifacts.jsonl"
for variant in full flat-ordinary full-ordinary; do
  tools/run -- python3 "$stage/link-preparer.py" "$run/cargo-artifacts.jsonl" \
    "$run/$variant/prepare_print_project.rs" "$run/$variant/prepare"
done
for variant in full full-ordinary; do
  tools/run -- "$run/$variant/prepare" "$run/$variant/native.3mf" \
    --printer Mark2 --filament-colour '#161616' \
    --filled-base "$run/shape/filled-base.stl" --tip-mesh "$run/shape/tip-trial.stl" \
    --cover-mesh "$cover" --slice-output "$run/$variant/slice"
done
tools/run -- "$run/flat-ordinary/prepare" "$run/flat-ordinary/donor.3mf" \
  --printer Mark2 --filament-colour '#161616' --base-only --slice-output "$run/flat-ordinary/slice"
```

The tested print-prep library revision is `8806ec4f275235102b167a864af19fc05ca3ef61`.
It retains the socket-plug preparer's native contact and cooling behavior and permits the
empty contact scope the flat donor needs. The linker reads Cargo's artifact stream so
the scratch preparer and libraries use the same compiler and dependency variants.
Use the versions and hashes in the receipt to check the original inputs. The slicer
writes the mapped result first, then restores the physical frame and applies the tip
cooling. Use `slice/plate_1.gcode` and `slice/native.gcode.3mf` under `full`,
after restoration and cooling. The flat donor is a motion source for the transition.

The original cooled full archive supplies the scaffold-stage input and the companion
parts. The matched modified slices supply the mapped lower and level upper base paths.
The patch leaves the rear seam paint in place.

## Prepare the editable project

The editable project contains the actual base mesh and the ordinary rear seam
setting. The sequenced archive supplies the scaffold, inclined courses and grade.

```sh
mkdir "$run/editable"
cp "$run/full/"*.rs "$run/editable/"
git show "$head:$head_dir/stage/physical-base.patch" > "$run/physical-base.patch"
patch -d "$run/editable" -p1 < "$run/physical-base.patch"
patch -d "$run/editable" -p1 < "$stage/no-scarf.patch"
tools/run -- python3 "$stage/link-preparer.py" "$run/cargo-artifacts.jsonl" \
  "$run/editable/prepare_print_project.rs" "$run/editable/prepare"
tools/run -- "$run/editable/prepare" "$run/editable/faucet.3mf" \
  --printer Mark2 --filament-colour '#161616' --physical-base \
  --tip-mesh "$run/shape/tip-trial.stl" --cover-mesh "$cover"
```

The native archive's `Metadata/slice_info.config` supplies the plate's object names
and IDs. After an object-start comment, a single-object `M624` mask uses the bit
associated with that ID in the native-source receipt. The mask covering all objects
marks plate-global moves. The flat donor has a single object and its native export
suppresses object masks.

Both sources carry the Polymaker PET-GF recipe and Bambu identifies that spool
as PET-CF. Use the flat donor as a local motion input. Repeated runs with the same
slicer may order identical roads differently across the native path files.

## Assemble and replay the plate paths

Run the transition and sequence stages using the original full plate for the scaffold
and companion parts and the matched ordinary rear-seam sources for the continued
base. Pass the actual base mesh when reproducing the bridge stitch at the final
graded course.

```sh
lower_map="$PWD/tools/hsm/print-prep/faucet-underside/left-active-height.npz"
mkdir -p "$run/foot"
for source in sloped.py courses.py; do
  git show "$socket:$socket_dir/stage/$source" > "$run/foot/$source"
done
patch -d "$run/foot" -p1 < "$stage/foot-transition.patch"
tools/run -- "$cad_py" "$run/foot/sloped.py" "$run/full/slice/native.gcode.3mf" \
  "$run/full/native.print.json" "$base" "$lower_map" "$run/foundation" 3.558258
tools/run -- "$cad_py" "$stage/shaft-transition.py" \
  "$run/flat-ordinary/slice/plate_1.gcode" "$run/flat-ordinary/donor.print.json" \
  "$run/full-ordinary/slice/plate_1.gcode" "$run/full-ordinary/native.print.json" \
  "$run/continued-base.gcode" --uphill-wall-runs --stitch-mesh "$base"
tools/run -- python3 "$stage/sequence.py" "$run/foundation/plate_1.gcode" \
  "$run/sequenced.gcode" --donor "$run/continued-base.gcode"
tools/run -- python3 "$stage/cool-shaft-join.py" "$run/sequenced.gcode" \
  "$run/full/native.3mf" "$run/cooled.gcode"
python3 "$stage/compare-companions.py" "$run/foundation/plate_1.gcode" "$run/cooled.gcode"
```

The playback planner estimates the duration of the current motion. Use the
first-bed-course deposition span from the trial receipt to reproduce its
native archive estimate. If the slicer emits different motion, recompute that
span from the first deposit through the last deposit of the first bed course
using the same playback planner.

```sh
tools/run -- hsm-gcode view playback "$run/cooled.gcode" --layers all --inline --data \
  --title 'Sculpted faucet shaft trial' --out "$run/estimate.json"
motion_seconds="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["seconds"])' "$run/estimate.json")"
first_course_seconds="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["first_bed_course_deposition_span_seconds"])' "$trial/plate.json")"
tools/run -- python3 "$stage/package.py" "$run/full/slice/native.gcode.3mf" \
  "$run/cooled.gcode" "$run/plate-ready.gcode.3mf" \
  --motion-seconds "$motion_seconds" --first-course-seconds "$first_course_seconds"
```

Extract the executable G-code and compare its model motion with the cooled
sequence before replaying.

```sh
unzip -p "$run/plate-ready.gcode.3mf" Metadata/plate_1.gcode > "$run/executed.gcode"
python3 - "$run/cooled.gcode" "$run/executed.gcode" <<'PY'
from pathlib import Path
import sys

def body(path):
    data = Path(path).read_bytes()
    first = data.index(b"; MACHINE_START_GCODE_END")
    last = data.index(b"; MACHINE_END_GCODE_START", first)
    return data[first:last]

assert body(sys.argv[1]) == body(sys.argv[2])
PY
tools/run -- "$cargo_bin" run --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-sandbox --example h2c-toolhead -- "$run/head"
tools/run -- "$cad_py" "$stage/expand-headmap.py" "$lower_map" \
  "$run/head/h2c-left-active.step.npz" "$run/full-headmap.txt"
tools/run -- c++ -std=c++20 -O3 -Wall -Wextra "$stage/replay.cpp" -o "$run/replay"
tools/run -- "$run/replay" "$run/executed.gcode" "$run/full-headmap.txt" --base-nozzle > "$run/replay.json"
```

The replay follows commanded print motion through the saved G-code using the
left-active head model and its retained lower envelope.
