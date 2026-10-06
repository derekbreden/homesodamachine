# Bambu timelapse retention

`h2c_timelapse_gc.py` retains the newest **96 timelapse clips per printer**.
Older clips are archived to the Mac and verified before removal from the
printer. Retention is based on file count; a size limit is optional.

[Bambu printers](bambu-printers.md) covers status and print submission.

## Storage limits

[Bambu's H2C user manual, section 7.4.1](https://csm.bblcdn.com/hub/eff78da43720461787dc8bbe5fa0372d.pdf#page=115)
documents a maximum of 500 video files and a video allocation of 65% of USB
capacity. It reserves 15% free space and describes automatic deletion of old
videos at 85% utilization. A firmware limit of 128 timelapses is unconfirmed.
The 96-clip retention policy leaves room below that suspected threshold.
Cleanup does not enable timelapse recording or establish why recording failed.

Timelapses live in `/timelapse/*.mp4`, with thumbnails in
`/timelapse/thumbnail`. Continuous chamber recordings live in `/ipcam`;
they have a separate recording switch and are outside the scheduled rotation.

## Use

Bambu's LAN file service uses implicit FTPS on port 990, user `bblp`, and the
printer's Access Code. Read the address and Access Code from the printer's
network settings. File access works while the printer remains cloud connected.
Supply `H2C_HOST` and `H2C_ACCESS_CODE` privately, or use the corresponding
`--host` and `--access-code` arguments. Each printer has its own credentials;
keep them outside this public repository.

```sh
# Inventory only:
python3 tools/h2c_timelapse_gc.py --list

# Dry run: retain 96 clips, regardless of their total size:
python3 tools/h2c_timelapse_gc.py --keep 96

# Verified archive, then removal of older clips:
python3 tools/h2c_timelapse_gc.py --keep 96 \
    --archive-dir ~/Bambu-timelapses/Mark1 --apply
```

The default is `--keep 96 --keep-gb 0`. `--keep-gb` adds a secondary size limit
in decimal GB; `0` disables that limit. `--max-age-days` adds an age limit.
`--keep 0` removes all eligible clips after archiving.

Active `temp*.mp4` recordings, zero-byte recording placeholders, files younger
than `--min-age-hours` (default 2), and unknown timestamps are protected.
They count toward the 96-clip total. If protected files alone exceed the limit, they all remain.
Every deletion requires `--apply` and `--archive-dir`.

Before removal, the script checks remote size and modification time, downloads
the complete clip, flushes it to disk, verifies its SHA-256 by reading it back,
and writes a `.sha256` sidecar. It checks remote metadata again before deleting.
A changed clip, incomplete transfer, disk error, or mismatching existing backup
stops that printer's rotation. Separate archive directories prevent collisions
between printers. A directory lock prevents overlapping rotations.

`--prune-thumbnails` optionally removes matching thumbnails after the video has
been archived and removed. `--thumb-folder` overrides the default
`<folder>/thumbnail`. Use `--folder ipcam` for a separately requested rotation
of continuous recordings.

## Scheduled rotation

The existing macOS LaunchAgent runs every six hours. Its private runner applies
`--keep 96 --keep-gb 0` and archives clips under
`~/Bambu-timelapses/Mark1` and `~/Bambu-timelapses/Mark2`. An unavailable printer
is logged and skipped until the next run.

- Runner: `~/.config/h2c-gc/run.sh` (mode `700`). It stores printer credentials,
  `KEEP_COUNT`, and `ARCHIVE_ROOT` outside Git.
- LaunchAgent: `~/Library/LaunchAgents/com.homesodamachine.h2c-timelapse-gc.plist`,
  `StartInterval` 21600 seconds.
- Log: `~/.config/h2c-gc/gc.log`.
- Runtime: `/opt/homebrew/bin/python3`.

```sh
sh ~/.config/h2c-gc/run.sh
launchctl bootout gui/$(id -u)/com.homesodamachine.h2c-timelapse-gc
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.homesodamachine.h2c-timelapse-gc.plist
```

Validate without contacting a printer:

```sh
python3 -m unittest discover -s tools -p test_h2c_timelapse_gc.py
```
