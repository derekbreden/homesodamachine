# Camera acquisition

The ELP USB camera was opened by its unique device identifier through CoreMediaIO. The Swift helper selects the full-field native video format and reads the camera presentation time and host callback time for each frame. The Python reader rotates the native luma upright, keeps a recent frame ring, and writes timestamped column-band profiles. The named endpoint service averages the requested source frames and records every contributing presentation timestamp. A nearby color sample has its own timestamp.

The camera began delivering native frames before any optical control was set. The fixed focus approach, white-balance experiment, early settled reference, and final restoration use the repository’s panelcam UVC control interface. The acquisition programs use NumPy and Pillow. The Swift source builds against macOS CoreMediaIO and AVFoundation.

The reader and acquisition scripts ran in the camera directory of the experiment’s temporary run. To reproduce the same camera interface there, build the helper beside the reader and run the reader with that output directory empty.

```sh
swiftc -O camera.swift -o nativecamera
python3 feed.py
```

The endpoint service prints the destination of a named exposure window.

```sh
python3 endpoint.py example --seconds 1 --samples 7
```

The live preview and native luma files use the same upright coordinate system. The upper-rim and dry-tube watchers consume this preview from the maintained camera stream. The native gate extracts use the original frame timestamps and independently recorded electrical command receipts.
