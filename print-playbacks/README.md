# Print playback archive

This archive supplies the material viewer's Print tab with saved H2C toolpaths.
Current product previews use the complete shipped parts and their selected print recipes.
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
path, and `plate`. For an archive retained in Git history, also include its `source_commit`.
For a saved local printer archive, record its filename, `archive_sha256`, and committed `launch`
receipt. The receipt identifies the source of the toolpaths.
For a freshly prepared product plate, record its recipe and revision, the model and project
digests, and the archive and plate G-code digests. Label it as a print plan and record the
effective settings for the selected part in `process`.
Commit and push the catalog and the matching compressed replay together. Use the part's
material link to check the toolpaths and timeline, then remove the scratch directory.
Dense plates draw surface and support paths and retain the complete motion timeline.
