# Print projects

The part preparers combine the CAD meshes, the plate layout and Bambu Studio's project and filament settings. The shared [PET-GF recipe](../../../hardware/printed-parts/petgf.profile.json) is also the source of the downloadable editable project. [Project downloads](https://github.com/derekbreden/homesodamachine/releases/tag/print-projects)

`plate-recipe` saves the native settings and layout of a Bambu Studio project as text. It also rebuilds and slices that project, and draws a plate's picture for the Parts page. Geometry, triangle paint and previews from a saved project stay together in a ZIP named by its SHA-256. The editable and sliced 3MF files are local outputs.

Build the tool from the checkout root.

```sh
tools/run -- "$(rustup which cargo)" build --release --locked --offline -j 2 \
  --manifest-path tools/hsm/Cargo.toml -p hsm-print-prep --bin plate-recipe
```

Use `plate-recipe profile PROJECT.3mf PROFILE.json` for a settings donor. Use `plate-recipe capture PROJECT.3mf RECIPE.json output/print-assets` for a manually laid-out plate. Keep the recipe in Git and upload its geometry ZIP to the `print-projects` release with `gh release upload`. The website can link directly to the editable project or a named print archive on that release.

Rebuild the shared example with the tools below. The final command uses Bambu Studio and writes the sliced archive and cooling record to a new directory.

```sh
recipe=hardware/printed-parts/petgf.profile.json
asset=$(jq -r .geometry_asset_sha256 "$recipe")
mkdir -p output/print-assets output/print-build
gh release download print-projects --pattern "$asset.zip" --dir output/print-assets --skip-existing
tools/hsm/target/release/plate-recipe build "$recipe" output/print-build/petgf.3mf output/print-assets
tools/run -- tools/hsm/target/release/plate-recipe slice output/print-build/petgf.3mf output/print-build/petgf-slice
```

Restore a saved print or bench-trial input with `node tools/print-archive.mjs REPO_PATH`. An older record's archive link contains the blob ID for that version. Restore it with `node tools/print-archive.mjs BLOB_ID OUTPUT`. The restore downloads the file's byte range from the release and checks its SHA-256. Use `plate-recipe capture` to save a recipe from a restored editable project.

## Plate previews

The website's [plate list](../../../hardware/printed-parts/plates.json) links each layout to its
material's Print view. Update its WebP from the editable project when publishing a new
[playback](../../../print-playbacks/README.md). The picture reads the printable objects, their
transforms and filament assignments from the Bambu project.

```sh
tools/run -- tools/hsm/target/release/plate-recipe picture small-petg=PROJECT.3mf
```

The name before `=` is the plate ID in the list. Append `:PLATE` to select a plate in a
multi-plate project. `hsm render` draws the plate, and the Parts tiles' fitter in
`tools/render` crops and pads it. WebPs go to `web/public/parts/plates/`.
