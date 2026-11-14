# Prepare the revised Sculpted faucet trial

Run from the checkout root. The prior ready archive supplies the exact base, mounting plate
and lever. The full native slice supplies the revised cover and the tip’s level source.
The editable project contains the flat-faced tip and cover in their print poses.

```sh
sculpted='hardware/printed-parts/faucet/sculpted'
trial="$PWD/$sculpted/prints/2026-11-14-tip-shoulder-mark2"
stage="$trial/stage"
prior="$sculpted/prints/2026-11-13-shaft-tilted-mark2"
legacy="$sculpted/prints/2026-11-13-dispense-face-sloped-foot-mark2"
sockets="$sculpted/prints/2026-11-13-sloped-foot-socket-plugs-mark2"
base="$PWD/hardware/printed-parts/faucet/faucet-shell/faucet-shell-base.stl"
cad_py="$PWD/tools/cad-venv/bin/python"
mkdir -p "$PWD/.cache/runs"
run="$(mktemp -d "$PWD/.cache/runs/faucet-tip-native-repro.XXXXXX")"
mkdir "$run/preparer" "$run/shape" "$run/head"

rustup_bin="$(command -v rustup || printf %s /opt/homebrew/bin/rustup)"
cargo_bin="$("$rustup_bin" which cargo)"
export RUSTC="$("$rustup_bin" which rustc)"
git show "b6f0e6063170eeeb88f62527a1adeae12be4a3f6:$sculpted/prepare_print_project.rs" > "$run/preparer/prepare_print_project.rs"
git show "b6f0e6063170eeeb88f62527a1adeae12be4a3f6:$sculpted/rim_supports.rs" > "$run/preparer/rim_supports.rs"
git show "b6f0e6063170eeeb88f62527a1adeae12be4a3f6:$sockets/stage/make_union.py" > "$run/preparer/make_union.py"
git show "c6cecb9b0acfdb41efaf5bbf9d7ee2777fda6d54:$legacy/stage/finish-selection.json" > "$run/preparer/finish-selection.json"
git show "ddd391f3d32bd8397f08b517ee58614fcd3e93ba:$prior/stage/link-preparer.py" > "$run/preparer/link-preparer.py"
git show "ddd391f3d32bd8397f08b517ee58614fcd3e93ba:$prior/stage/map_base.py" > "$run/preparer/map_base.py"
export PYTHONPATH="$run/preparer${PYTHONPATH:+:$PYTHONPATH}"
patch -d "$run/preparer" -p1 < "$stage/tip-native.patch"
python3 - "$run/preparer/prepare_print_project.rs" "$run/preparer/finish-selection.json" <<'PY'
import json
from pathlib import Path
import sys
source = Path(sys.argv[1])
text = source.read_text()
selection = '".cache/runs/faucet-tip-native-20261114/source/finish-selection.json"'
assert text.count(selection) == 1
source.write_text(text.replace(selection, json.dumps(sys.argv[2])))
PY
tools/run -- "$cargo_bin" build --release --locked --offline -j 2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-print-prep -p hsm-faucet -p hsm-faucet-display-cover-numbers --lib \
  --message-format=json > "$run/preparer/artifacts.jsonl"
tools/run -- python3 "$run/preparer/link-preparer.py" "$run/preparer/artifacts.jsonl" \
  "$run/preparer/prepare_print_project.rs" "$run/preparer/prepare"

"$cad_py" "$run/preparer/make_union.py" "$base" "$run/shape/filled-base.stl" "$run/shape/base-fill.json"
git show "ddd391f3d32bd8397f08b517ee58614fcd3e93ba:$prior/sculpted-faucet-shaft-tilted-black-mark2-ready.gcode.3mf" > "$run/prior.gcode.3mf"
unzip -p "$run/prior.gcode.3mf" Metadata/plate_1.gcode > "$run/prior.gcode"
```

Compile the trial’s Rust geometry example using the same Cargo artifact stream.
The example uses the tip, seated cover and assembled display from the checkout’s
retained print-build exports. The native-source receipt identifies the expected
tip and cover meshes it produces.

```sh
python3 - "$run/preparer/artifacts.jsonl" "$run/preparer/dispense-face.rustc" "$stage/dispense-face.rs" "$run/dispense-face" <<'PY'
import json
from pathlib import Path
import sys
artifacts, args, source, output = map(Path, sys.argv[1:])
names = {"anyhow", "hsm_faucet", "hsm_faucet_display_cover_numbers", "hsm_faucet_numbers", "hsm_kernel", "serde_json"}
libraries = {}
for line in artifacts.read_text().splitlines():
    row = json.loads(line)
    if row.get("reason") != "compiler-artifact" or row["target"]["name"] not in names:
        continue
    paths = [Path(p) for p in row["filenames"]]
    library = next((p.with_suffix(".rlib") for p in paths if p.suffix == ".rmeta"), None)
    if not library or not library.exists():
        library = next((p for p in paths if p.suffix == ".rlib"), None)
    if library:
        libraries[row["target"]["name"]] = library
assert libraries.keys() == names
command = ["--edition=2024", "-C", "opt-level=3"]
for p in sorted({p.parent for p in libraries.values()}):
    command += ["-L", f"dependency={p}"]
for name, p in sorted(libraries.items()):
    command += ["--extern", f"{name}={p}"]
command += [str(source), "-o", str(output)]
args.write_text("\n".join(command) + "\n")
PY
tools/run -- "$RUSTC" "@$run/preparer/dispense-face.rustc"
tools/run -- "$run/dispense-face" "$run/head"
tip="$run/head/tip.stl"
cover="$run/head/cover.stl"
shasum -a 256 "$tip" "$cover"
tools/run -- "$run/preparer/prepare" "$run/editable.3mf" --printer Mark2 \
  --filament-colour '#161616' --physical-base --tip-mesh "$tip" --cover-mesh "$cover"
tools/run -- "$run/preparer/prepare" "$run/native.3mf" --printer Mark2 \
  --filament-colour '#161616' --filled-base "$run/shape/filled-base.stl" \
  --tip-mesh "$tip" --cover-mesh "$cover" --slice-output "$run/native"
```

The final native input is `$run/native/plate_1.gcode` after the stored tip contact,
rim and cooling passes, with pose and settings in `$run/native.print.json`. The
full plate contributes the cover. Generate the donor from the actual tip in
that pose, preserving its bed and nose regions. The restored shoulder follows the
plug and its local support. The donor includes finer courses through the entering
and exiting slopes.

```sh
tools/run -- "$cad_py" "$stage/tip_warp.py" "$tip" "$run/editable.3mf" "$run/tip-warped.stl"
tools/run -- "$run/preparer/prepare" "$run/warp.3mf" --printer Mark2 \
  --filament-colour '#161616' --warp-donor --tip-mesh "$run/tip-warped.stl" \
  --slice-output "$run/warp"
tools/run -- "$cad_py" "$stage/tip_tape.py" "$run/warp/plate_1.gcode" \
  "$run/warp.print.json" "$run/tip-warped.json" "$run/tip.gcode" \
  --band-step 1 --uphill-all --native-nose
"$cad_py" "$stage/audit_native_nose.py" "$run/warp/plate_1.gcode" "$run/warp.print.json" \
  "$run/tip-warped.json" "$run/tip.gcode" "$run/native-nose.json"
"$cad_py" "$stage/measure_pitch.py" "$run/warp/plate_1.gcode" "$run/warp.print.json" \
  "$run/tip-warped.json" "$run/tip-pitch.json"
```

The nose comparator reads native donor roads after the grade has returned to
level. It checks emitted deposition, feed, cooling and acceleration in the
physical plate coordinates after applying the donor placement shift.

```sh
python3 "$stage/make-rings.py" "$run/rings.gcode" "$run/ring-supports.json"
tools/run -- python3 "$stage/sequence.py" "$run/prior.gcode" "$run/native/plate_1.gcode" \
  "$run/plate.gcode" --tip-model "$run/tip.gcode" --entire-tip-custom --plate-rings "$run/rings.gcode"
python3 "$stage/audit-retained.py" "$run/prior.gcode" "$run/native/plate_1.gcode" \
  "$run/plate.gcode" > "$run/plate-retention.json"
"$cad_py" "$stage/measure_native_support.py" "$tip" "$run/editable.3mf" "$run/plate.gcode" \
  "$run/shoulder-support.json"
```

The native archive supplies the slice metadata for the sequenced plate. The
playback planner measures the path time. The first-bed-course span comes from
the trial’s plate receipt. If regenerating with different paths, measure that
span through the first course using the same playback planner.

```sh
git show "ddd391f3d32bd8397f08b517ee58614fcd3e93ba:$prior/stage/package.py" > "$run/package.py"
tools/run -- hsm-gcode view playback "$run/plate.gcode" --layers all --inline --data \
  --title 'Sculpted faucet tip shoulder trial' --out "$run/estimate.json"
motion_seconds="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["seconds"])' "$run/estimate.json")"
first_course_seconds="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["first_bed_course_deposition_span_seconds"])' "$trial/plate.json")"
tools/run -- python3 "$run/package.py" "$run/native/native.gcode.3mf" "$run/plate.gcode" \
  "$run/plate-review.gcode.3mf" --motion-seconds "$motion_seconds" --first-course-seconds "$first_course_seconds"
unzip -p "$run/plate-review.gcode.3mf" Metadata/plate_1.gcode > "$run/executed.gcode"
python3 - "$run/plate.gcode" "$run/executed.gcode" <<'PY'
from pathlib import Path
import sys

def body(path):
    data = Path(path).read_bytes()
    first = data.index(b"; MACHINE_START_GCODE_END")
    last = data.index(b"; MACHINE_END_GCODE_START", first)
    return data[first:last]

assert body(sys.argv[1]) == body(sys.argv[2])
PY
```

Replay the extracted commands with the rasterized left-active toolhead. The
nozzle windows cover the base, tip, screw-seat rings and display cover.

```sh
git show "ddd391f3d32bd8397f08b517ee58614fcd3e93ba:$prior/stage/expand-headmap.py" > "$run/expand-headmap.py"
tools/run -- "$cargo_bin" run --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-sandbox --example h2c-toolhead -- "$run/head-model"
tools/run -- "$cad_py" "$run/expand-headmap.py" \
  tools/hsm/print-prep/faucet-underside/left-active-height.npz \
  "$run/head-model/h2c-left-active.step.npz" "$run/full-headmap.txt"
tools/run -- c++ -std=c++20 -O3 -Wall -Wextra "$stage/replay.cpp" -o "$run/replay"
tools/run -- "$run/replay" "$run/executed.gcode" "$run/full-headmap.txt" --base-nozzle \
  --nozzle-box 143 174 225 246 --nozzle-box 180 82 232 110 \
  --nozzle-box 234 202 268 266 > "$run/replay.json"
```

The source code and data here build the offline trial. The prototype’s
production recipes are separate.
