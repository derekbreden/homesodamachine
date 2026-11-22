# Camera acquisition

The native helper selects the ELP USB camera by unique identifier using CoreMediaIO. Each image carries its native presentation timestamp and host callback time. The Python reader rotates luma and chroma upright, keeps a short frame ring, and records row profiles of adjacent column bands. A named window carries the sequence and presentation time of every luma frame in its average. Its full-field color sample has a separate timestamp.

The macOS Swift compiler builds the camera helper beside the Python reader. The reader uses NumPy and Pillow. To start a new run, place the acquisition source in its own empty output directory and run the following commands there.

```sh
swiftc -O camera.swift -o nativecamera
python3 feed.py
```

From a second terminal in the same directory, request a named endpoint with the persistent capture service.

```sh
python3 endpoint.py example --seconds .6 --samples 9
```

The bench used the project's UVC interface to read the initial hardware state and apply the fixed focus, shutter, gain and white balance in the acquisition record. The settings stayed fixed through the wet runs. The closing readbacks distinguish the end of the measurements from restoration and camera shutdown. The native replay operates entirely on the recorded images, clocks and command receipts.
