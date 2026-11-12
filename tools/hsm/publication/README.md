# Publication

`hsm-publish` advances completed geometry and its referenced records on the website.
It starts no producer build. The native print driver requests publication as outputs
finish, and the post-commit hook requests another look after source changes land.
Concurrent requests coalesce while the publisher is running.

From the repository root:

```sh
hsm-publish --root .
hsm-publish --root . --check
```

The publisher hashes completed members, refreshes retained assembly references, and
freezes the changed bytes. An assembly built from a member's current revision publishes
as built. Shared mesh objects upload before manifests that refer to them. Viewer members
advance before manufacturing members; absent retained members keep their pointers and
shared objects. Membership follows the material catalog, native producer graph and
[`config.json`](config.json).

Named assembly views use their shared mesh manifests. The PCB's GLB remains a
viewer member: its component hierarchy and materials serve the board viewer and
the requested harness crops, even when an older mesh payload stands beside it.

Immutable member objects serve live updates. A partial update retains the download
bundle and marks it behind; creating that archive is an explicit reconciliation,
outside the first-view path. The public object store receives member uploads, with
the GitHub release as their fallback. Failed object uploads leave pointers unchanged.

The pointer commit includes the exact sidecar blobs it references. A viewer pass can
keep an earlier scorecard while newer edits remain staged or on disk. Changed
scorecards are frozen before uploads, so a later checkpoint cannot be committed
under an earlier digest. `hsm-land --commit-snapshot` writes the selected blobs
without replacing concurrent files or unrelated staged edits. After its locks are
released, the publisher runs the post-commit hook and verifies that the resulting
commit is on `origin/main`. It then asks the site to adopt the pointer; the site's
poll also recovers a missed notification.

## Explicit packing and maintenance

`hsm-pack` inspects stored publication members and handles requested reconciliation.

```sh
hsm-pack
hsm-pack --check
hsm-pack --sidecar-debt
hsm-pack --room
hsm-pack --retire
hsm-pack --prune
```

`--check` reports byte agreement without building or uploading. `--sidecar-debt`
prints producers for changed scorecards. `--room` inspects release retention;
`--retire` removes eligible release assets using complete Git history. `--prune`
retires outputs removed from the producer graph after checking their source evidence;
`--allow-retired` explicitly permits retirements without that evidence.

```sh
tools/run -- hsm-pack --write
```

`--write` carries owed producer output through the native print driver, leaves
targets reached by uncommitted source edits unbuilt, and reconciles the full
download bundle. Retained members absent locally keep their pointers; an incomplete
local set does not replace the complete bundle.

`--write --publish-held` publishes existing completed bytes. `--viewer-only`,
`--members-json` and repeated `--grafted PATH` select that operation's members and
retained scene references. Normal publication uses `hsm-publish` to share its queue.

## Related native commands

`hsm-merge-pointers BASE OURS THEIRS` is Git's member-wise pointer merge driver. It
writes the merged result to `OURS` and keeps provenance with the winning hashes.

`hsm-cut-vs-pointers` compares retained native producer output with published and local
bytes. `--targets` selects native target or source aliases; the command asks the
print driver only for current cache entries and starts no producer. An explicit
`--receipt FILE --assume-fresh` reads the build that wrote that receipt without
querying current inputs. `--failed` excludes failed target cohorts and `--annotate`
prints CI annotations.

`hsm-build-times` reads completed full native print-build results under `.cache/runs/`
and commits changes to the site's timing list. Existing timing rows remain in that
history. `--check` prints available native records without writing. It starts no build.

## Firmware

`hsm-publish-firmware` packages the images served by `/api/firmware`. Its targets are
`appliance`, `enclosure`, `faucet` and `art`; bench firmware stays outside that set.

```sh
hsm-publish-firmware --no-build
hsm-publish-firmware --check
tools/run -- hsm-publish-firmware --write
```

The default command builds requested images and prints their metadata. `--no-build`
surveys existing images; `--check` compares their hashes without building or writing.
Target names after the flags select a subset. Builds use PlatformIO and
`hsm-marketing make-art`; the publisher freezes completed images, writes a deterministic
bundle, and verifies an existing release asset before skipping its upload. The
pointer moves only after upload succeeds. The command flashes no device.

The firmware pointer carries each image's version, build epoch, size, CRC32 and
SHA256. Art also carries its pixel CRC from the partition header. The web fetcher
reads [`firmware/firmware-images.json`](/firmware/firmware-images.json) at deployment.
Firmware publishing remains an explicit operation outside geometry publication.

## On-demand fixtures

```sh
hsm-pack selftest
tools/run -- cargo test --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml -p hsm-publication --lib
tools/run -- cargo test --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml -p hsm-publication --bin hsm-publish-firmware
```

The fixtures use temporary local inputs and fake transport. They cover progressive
and newly added members, retained absent geometry, partial reference refreshes,
failed uploads, frozen checkpoints and sidecars, caches, merges and timing records.
They upload and delete no remote objects and add no automatic check path.

The firmware bin also has an ignored `existing_display_images_pack_without_build_or_upload`
fixture for a requested comparison of existing local display images. It packs a private
bundle, checks member hashes and CRCs, and removes its temporary files. It starts no
SDK build and writes no firmware pointer.
