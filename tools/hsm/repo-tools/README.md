# Repository tools

`repo-tools` maintains scratch and answers explicit timing, calibration, discovery and integrity questions. It stays outside the print build. No hook starts its check readings.

Build it when needed:

```sh
tools/run -- cargo build --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml -p hsm-repo-tools
```

Use the installed `repo-tools`, or `tools/hsm/target/release/repo-tools`. `--root PATH` selects the checkout to read.

```sh
repo-tools cache-gc
repo-tools cache-gc --apply
repo-tools time-to-site
repo-tools time-to-site --watch
repo-tools missing-tools
repo-tools missing-tools --show '*.step.mesh'
repo-tools model
repo-tools model --set regulator_psi=72 --set glass_g=268
repo-tools model volumes 21 1.4 --liquid-g 452 --bottle-ml 528 --snift 33 --snift 24
repo-tools checks --list
repo-tools paths selftest
```

`cache-gc` lists expired scratch by default. `--apply` removes it. Each child of `runs`, `prints` and `printer-control` ages independently; a fresh run keeps no older run alive. Shared geometry memo caches, the printer-control environment and installed runtimes remain. `--cache PATH` and `--days DURATION` select the location and age.

`cache-gc` also lists the cargo units in `tools/hsm/target` whose fingerprints no build has read within `UNIT_DAYS` in [cache.rs](src/cache.rs), and `--apply` removes them with their outputs and build-script directories. It holds each profile's cargo locks while it works and passes over a profile a build holds. Top-level binaries and dep-info remain. `--target PATH` selects another target.

`time-to-site` reads the served commit and the current deployment filter. `missing-tools` reads the repository's Claude and Codex transcripts, including iCloud files, and counts scratch code and blocking waits. It uses installed `sqlite3` read-only for the Codex index. `--show` reuses a recent reading in `.cache/missing_tools.json`.

`model` predicts the Lillium-fed prototype from the measured bores, current authored tube lengths, firmware pour policy and the shared acceptance and pressure-vessel inputs in [calibration_inputs.rs](/hardware/assembly/calibration_inputs.rs). `--set` pins an input measured at the sink. `volumes` converts a carbonation-tester reading and its snifts.

`drawing-review` renders selected PDF overviews and named contextual crops with Poppler. It records the source PDF hash and image paths in `review-images.json`. Regions use points from the bottom-left of the displayed CropBox after rotation. Run it through `tools/run`; the [engineering drawing workflow](/tools/engineering-drawings/SKILL.md) describes the visual reviews.

```sh
tools/run -- repo-tools drawing-review part.pdf --output-dir /tmp/drawing-review --page 1
```

The retained checks are an explicit list. Run one by name when its question applies:

```sh
tools/run -- repo-tools check enclosure-mating-clearance
repo-tools check ledger
repo-tools check pinmap
repo-tools check purchase-evidence
repo-tools check step-colours
repo-tools paths
```

The enclosure reading consumes existing fine models and the native `enclosure-mating` program. The purchase reading uses the existing native `purchases --check`. These programs must be installed or explicitly built first; a reading starts no compiler.

`repo-tools checks` runs the listed readings. `--json PATH` writes a verdict with no clock or duration. Red is a reading for the settings gear and holds no build or publish. Pinning is also explicit:

```sh
tools/run -- repo-tools checks-now --check
tools/run -- repo-tools checks-now --session '<current chat title>'
tools/run -- repo-tools checks-now --message-file /path/to/complete-message.txt
```

`--check` keeps the verdict in memory. The write mode requires the current chat title, or a complete caller-authored commit message with its trailer block. It freezes only `web/public/checks.json` through `hsm-land --commit-snapshot`, then invokes the existing post-commit hook. A session title produces the fixed reading subject and a `Session:` trailer. Any `Derek:` quotes belong to the caller-authored message. Concurrent writes coalesce through `.cache/checks-now.lock` and its again marker; these files keep explicit readings from racing.

Focused native fixtures run on request:

```sh
tools/run -- cargo test --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml -p hsm-repo-tools
```
