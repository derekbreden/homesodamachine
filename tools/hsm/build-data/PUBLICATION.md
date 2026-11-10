# Artifact publication

`publication.rs` selects catalog models, their companions and print files,
walks the stored build outputs, and applies the directory membership rules.
`publication_state.rs` supplies producer provenance, release retention, pointer
projection and publication plans. Native ordered JSON preserves authored and
retained map order through pointer merges.

`publication_archive.rs` writes GNU tar members with fixed metadata and record
padding, deterministic gzip objects, and verified content-addressed adoptions.
`publication_zlib.rs` binds the system zlib primitive so an unchanged member set
reproduces the existing bundle bytes. `HSM_ZLIB_LIBRARY` selects an explicit
library; the defaults are `/usr/lib/libz.1.dylib` on macOS and `libz.so.1` on Linux.
`publication-zlib-info` reports the selected library and its version.

`hsm-publish --root ROOT` advances completed members without building their producers.
It refreshes retained scene references, sends shared mesh objects before manifests,
commits changed pointers with their sidecars, and asks the site to adopt them after
the commit lands. Concurrent requests coalesce while a publisher is running.

`hsm-pack --root ROOT` inspects the stored members. `--write --publish-held` publishes
completed bytes; `--viewer-only` and `--members-json` select a partial update.
`--write` explicitly reconciles producer output and the full download bundle.
`--check`, `--sidecar-debt`, `--room`, `--retire` and `--prune` retain the separate
inspection and maintenance actions. The authored membership and transport policy
is in [`../publication/config.json`](../publication/config.json).

`hsm-merge-pointers` is Git's member-wise pointer merge driver.
`hsm-cut-vs-pointers` compares a requested Bazel slice with the pointer and working
tree. `hsm-build-times` carries recorded full-build timings without starting a build.
The on-demand `hsm-pack selftest` uses local fixtures and a fake transport; it
uploads and deletes no remote objects.
