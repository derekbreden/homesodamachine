# Print-process recordings

`hsm-printer recordings` keeps compact, elapsed-time camera playback in iCloud
Drive while the printer retains its native chamber recordings.

## Recording

The H2C's automatic print-process recording saves the live-view camera to the
printer's USB storage during prints. It operates independently of layer-triggered
timelapse photography. The printer controls its recording resolution and native
video segmentation. The camera command reads the setting or explicitly changes
it and verifies a fresh report from the printer:

```sh
hsm-printer camera all
hsm-printer camera H2C on
hsm-printer camera Mark2 on
```

The connection key `H2C` names Mark1. Credentials come from the existing private
printer configuration. Camera settings output excludes stream URLs and access
codes. [Bambu's H2C manual](https://csm.bblcdn.com/hub/eff78da43720461787dc8bbe5fa0372d.pdf)
also describes the touchscreen and Bambu Studio Auto-record Monitoring controls.

## Compact archive

```sh
hsm-printer recordings all
hsm-printer recordings H2C --archive-dir ~/Bambu-recordings
```

The default destination is
`~/Library/Mobile Documents/com~apple~CloudDocs/Bambu-recordings`, with separate
Mark1 and Mark2 folders. This is an ordinary iCloud Drive folder; macOS manages
uploading and local storage optimization. The archive does not require a
separate cloud account or upload service.

The command downloads closed `/ipcam` video segments, samples them at a fixed
cadence, and encodes accelerated playback. Sampling, playback, and image-size
defaults are constants in
[`recordings.rs`](hsm/printer-tools/src/recordings.rs). Each frame labels its
elapsed position in the original recording segment. The original filename is
preserved in the playback name. Printer filenames use the printer's clock;
the receipt separately retains the file service's modification timestamp.

A JSON sidecar records the source checksum, source duration, sampling cadence,
decoded frame count, playback checksum, and the printer state observed when the
segment was archived. That state is an archive-time observation, not an assertion
that the whole segment belongs to that job. The command verifies the downloaded
bytes, decodes the sampled playback to check its duration and coverage, and
verifies the copy written into the archive. Temporary native video is removed
after processing. Native recordings on the printer are untouched.

The newest segment is protected while a print is active. Recent, empty, temporary,
and undated files are also protected. A changing remote file is retried on a
later run. Local receipts under `~/.config/h2c-recordings` prevent archived videos
from being downloaded again after iCloud offloads them. A lock prevents
overlapping archive runs. An unavailable printer is reported without stopping
archiving for the other printer.
Directory durability checks open metadata only, so flushing an iCloud folder does
not recall its offloaded videos.

## Installed schedule

The private runner `~/.config/h2c-recordings/run.sh` invokes the installed
`hsm-printer recordings all`. Its macOS LaunchAgent is
`~/Library/LaunchAgents/com.homesodamachine.h2c-recordings.plist`; its interval is
stored in that plist. The log is `~/.config/h2c-recordings/recordings.log`.
The runner supplies the Homebrew and local executable paths for FFmpeg and the
printer command. Encoding uses `tools/run` and stays outside the normal print build.

Layer-triggered timelapses have their own
[verified retention and archiving](h2c-timelapse-gc.md). Their existing
`~/Bambu-timelapses` path links to the corresponding iCloud Drive folder.
