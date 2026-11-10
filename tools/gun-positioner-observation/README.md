# Gun-positioner observation toolkit

The camera helper and the frame and feature code that the PGFUN positioner's
host reads. [`pgfun-host observe`](../../firmware/src_pgfun_positioner/host/main.rs)
streams one camera through the helper and finds the wire tip, aiming dot and
seam in each frame; the workflow is in
[hardware/gun-positioner/observation.md](../../hardware/gun-positioner/observation.md).
Nothing here can command motion or laser emission.

## Layout

| Path | Contents |
|---|---|
| `helper/` | `GPOCapture`, the AVFoundation capture helper. `build.sh` builds `helper/build/GPOCapture.app` from `main.swift` |
| `src/helper_stream.rs` | The helper's stream protocol, its launch, camera enumeration and clock check |
| `src/capture.rs` | The frames, drop notices and events a source delivers |
| `src/imageio.rs` | Camera JPEG (with the standard Huffman tables a Motion-JPEG frame omits), PGM, PNG and NV12 frames |
| `src/features.rs` | The aiming-dot, wire-tip and seam-line extractors |
| `src/` test modules | Image-codec, feature and framed-stream examples |

## Requirements

The `hsm-pgfun-observation` crate supplies native image readers, feature
extractors and helper transport to `hsm-pgfun-host`. Build the host as described
in its [README](../../firmware/src_pgfun_positioner/README.md).

The app needs no rebuild while `main.swift` and `Info.plist` are unchanged.
`helper/build.sh` rebuilds it from source and needs `swiftc`. An ad-hoc rebuild
changes the signature, so macOS asks for camera access again.

## Tests

```sh
tools/run -- cargo test --manifest-path tools/hsm/Cargo.toml --release --locked -j 2 \
  -p hsm-pgfun-observation -p hsm-pgfun-host -- --test-threads=2
```

The tests exercise image readers, feature extraction and framed stream bytes,
and use fixture controller transports. They start no helper process and open
no camera or serial device.
