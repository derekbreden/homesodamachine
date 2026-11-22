# Camera evidence for the top-off and sitting tests

The cup photographs come from the same USB camera and sightlines as Codex's record, through a different capture path. From a Claude shell only `tools/panelcam-shot/PanelCamShot.app`, launched with `open -W`, holds the macOS camera grant. [`cam.py`](cam.py) starts it at the native `2320x1744` `420v` mode with raw luma dumps, waits for the stream's first frame, then writes Codex's frozen controls through `tools/panelcam-uvc/uvc.js` once the lens has parked: fixed exposure, gain and white balance, the lens stepped up to its working focus, and a readback that must match before any photograph. As each dumped frame lands it keeps the 45 native columns Codex's endpoints keep, rows across the cup's working band, and deletes the frame.

A photograph is the rounded mean of the next nine kept frames, read by Codex's frozen clear-glass reader and calibration ([`../optics`](../optics)). SciPy is not installed in this Mac's Python, so the reader runs on [NumPy stand-ins](../optics/shim/scipy/ndimage.py) for the four 1-D filters it calls. Run against Codex's archived endpoint pixels, the stand-ins return his journaled edge rows exactly ([`../optics/replay_endpoints.py`](../optics/replay_endpoints.py)).

Each measured pour has one stream holding its starting and finishing photographs. Positioning photographs each open their own short stream. The no-pump validation photographed the resting cup through ten separately opened streams, three photographs each, before any pump ran; its summary is [`../results/reader-validation.json`](../results/reader-validation.json). A full-field frame taken then registers against Codex's last archived average with no vertical shift in the printed marks below the liquid.

[`endpoints/`](endpoints) holds the sightline pixels of every photograph named in the journals: `native_luma` indexed by frame, sensor column and sensor row, with the frame counters and file times. From the record directory:

```sh
python3 optics/replay_endpoints.py .
```

The controls were restored after the last stream to the values found at the start ([`../logs/uvc-as-found.txt`](../logs/uvc-as-found.txt), [`../logs/uvc-restored.txt`](../logs/uvc-restored.txt)).
