# Camera evidence for the unseen programs

Every named exposure comes from one open USB camera stream. Each lossless endpoint recording contains its contributing native luma pixels, frame sequences and presentation timestamps. The two volume sightlines use the original clear-glass reader and geometry map from the archived pour calibration. The primary sightline uses neighboring columns to reject an alternate reflection. The compact record includes every column and row accessed by either reader.

From this directory, run the following with Python, NumPy, SciPy and Pillow. The first command checks all camera and file hashes, original sensor samples, reconstructed volumes, timestamps and the hardware restoration. The second prints the photographed baseline.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 verify_evidence.py .
PYTHONDONTWRITEBYTECODE=1 python3 replay_sights.py endpoints/station-idle.npz
```

The raw pixel array is indexed by frame, original column and original row. The rounded mean along the frame axis gives the exact lossless sensor pixels used by the full-photograph volume reader. Each archived window was compared with its full photograph before the source was reduced to these columns. Its two calibrated readings and exposure times are in `windows.json`. The `photographed-programs` directory shows native before-and-after cup crops from the first completed run of each program.

The camera clock and appliance journal use the same host monotonic timebase. The receipt index preserves motor and meter messages, adjacent camera presentation timestamps, and named photographs referenced by the journal. The trial clock record links every completed dispense to the last source frame before the first meter write and the first settled source frame after the appliance closure. The within-window table compares the early and late subsets of each named exposure. The source revision, previous final photograph, fresh stationary reference, dry-print registration and control readbacks are in `reference/`. All pixel coordinates use the upright native field.
