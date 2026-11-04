# Artifact publication

`publication.rs` selects catalog models, their companions and print files,
walks the stored build outputs, and applies the directory membership rules.
`publication_state.rs` supplies producer provenance, release retention, pointer
projection and publication plans. Ordered-pair transport preserves authored and
retained map order through the Python compatibility modules.

`publication_archive.rs` writes GNU tar members with fixed metadata and record
padding, deterministic gzip objects, and verified content-addressed adoptions.
`publication_zlib.rs` binds the system zlib primitive so an unchanged member set
reproduces the existing bundle bytes. `HSM_ZLIB_LIBRARY` selects an explicit
library; the defaults are `/usr/lib/libz.1.dylib` on macOS and `libz.so.1` on Linux.
`publication-zlib-info` reports the selected library and its version.

The `pack.py` and `publish_now.py` entry points retain their CLI and backend
process/network boundaries. Geometry generation and live publication are
separate operations; fixture comparisons use no uploads or remote deletions.
