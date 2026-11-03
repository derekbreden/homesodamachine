# Gun-positioner observation toolkit

The camera helper and the frame and feature code that the PGFUN positioner's
host reads. [`observe.py`](../../firmware/src_pgfun_positioner/host/observe.py)
streams one camera through the helper and finds the wire tip, aiming dot and
seam in each frame; the workflow is in
[hardware/gun-positioner/observation.md](../../hardware/gun-positioner/observation.md).
Nothing here can command motion or laser emission.

## Layout

| Path | Contents |
|---|---|
| `helper/` | `GPOCapture`, the AVFoundation capture helper. `build.sh` builds `helper/build/GPOCapture.app` from `main.swift` |
| `gpobs/helper_stream.py` | The helper's stream protocol, its launch, camera enumeration and clock check |
| `gpobs/capture.py` | The frames, drop notices and events a source delivers |
| `gpobs/imageio.py` | Camera JPEG (with the standard Huffman tables a Motion-JPEG frame omits), PGM, PNG and NV12 frames |
| `gpobs/features.py` | The aiming-dot, wire-tip and seam-line extractors |
| `tests/` | Unit tests on rendered images and the helper's synthetic mode |

## Requirements

`requirements.txt`: numpy and Pillow (JPEG and PNG frames).
`tools/cad-venv/bin/python` provides both; with a Python that lacks Pillow, the
one test that needs it is skipped.

The app needs no rebuild while `main.swift` and `Info.plist` are unchanged.
`helper/build.sh` rebuilds it from source and needs `swiftc`. An ad-hoc rebuild
changes the signature, so macOS asks for camera access again.

## Tests

```sh
tools/cad-venv/bin/python -m unittest discover -s tools/gun-positioner-observation/tests
```

The helper tests run when `helper/build/GPOCapture.app` exists
(`helper/build.sh --adhoc` builds it without using the keychain); they use the
helper's synthetic mode and open no camera.
