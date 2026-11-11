# Print playback archive

This archive enables the material viewer's Print tab for selected, archived H2C slices.
The site reads the catalog during its existing live publication poll and loads the replay
when a visitor selects Print. The print build and site build do no replay generation.

From the repository root, choose the archived `.gcode.3mf`, plate, and display title.

```sh
mkdir -p .cache/runs
replay_dir=$(mktemp -d .cache/runs/print-playback-XXXXXXXX)
hsm-gcode view playback "$slice" --plate "$plate" --layers all --inline --data --title "$title" --out "$replay_dir/replay.json"
replay_hash=$(shasum -a 256 "$replay_dir/replay.json" | cut -d ' ' -f 1)
gzip -n -c "$replay_dir/replay.json" > "print-playbacks/$replay_hash.json.gz"
```

Register the material ID in `catalog.json` with `title`, `sha256`, the repo-relative `slice`
path, and `plate`. Commit and push the catalog and the matching compressed replay together.
Use the part's material link to check the toolpaths and timeline, then remove the scratch
directory. The shared player reads the same sampled format as the inline playback and has
the same size limit.
