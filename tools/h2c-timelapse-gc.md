# H2C timelapse drive GC

`h2c_timelapse_gc.py` keeps the SanDisk Ultra Fit in the H2C's front USB port
from filling up, so the printer never stops recording timelapses.

## Why it's needed

The H2C records per-print timelapses to the USB drive (`/timelapse/*.mp4`,
thumbnails in `/thumbnail/*.jpg`). On **external USB storage there is no
loop/auto-overwrite** — when the drive fills, the printer silently stops
recording. The "overwrite oldest when full" behavior exists only on the **P2S
and X2D internal storage**, not the H2C and not the USB drive
([Bambu wiki: Timelapse Internal Storage and Video Management](https://wiki.bambulab.com/en/knowledge-sharing/timelapse-internal-storage-and-video-management)).
So clearing space is a manual step unless you automate it — which is what this
script does.

## What actually fills the drive

Two features write video, and the bigger consumer is usually **not** timelapses:

- **Auto-record chamber video** → `/ipcam/*.mp4`, ~250 MB per print. Controlled
  on the printer by `Settings → Video` (H2 series). If you only want timelapses,
  set it to **Off** — it is independent of timelapse and of AI failure-detection
  (which runs on-device and needs no drive). This tool can clear it with
  `--folder ipcam` (e.g. `--folder ipcam --keep 0 --apply` to wipe it).
- **Timelapse** → `/timelapse/*.mp4` (the default folder this tool rotates).

## How it reaches the printer

Bambu's LAN file service is **FTPS, implicit TLS, port 990**, user `bblp`,
password = the printer's **Access Code**.

Find the IP and Access Code on the printer: **Settings → WLAN → LAN Only Mode**
(the code shows without having to enable LAN-Only). FTP file access works while
the printer stays **cloud-connected** — confirmed against an H2 on stock cloud
mode, no LAN-Only needed. Each printer has its **own** access code.

Pass them in — don't commit the Access Code:

```
export H2C_HOST=192.168.1.50        # the printer's IP
export H2C_ACCESS_CODE=12345678     # the 8-char code from the LAN screen
```

## Use

```
# See what's on the drive (deletes nothing):
python3 tools/h2c_timelapse_gc.py --list

# Dry run — show what a 190 GB keep-budget would prune, oldest first:
python3 tools/h2c_timelapse_gc.py --keep-gb 190

# For real, archiving each clip to your Mac first and pruning thumbnails:
python3 tools/h2c_timelapse_gc.py --keep-gb 190 \
    --archive-dir ~/H2C-timelapses --prune-thumbnails --apply
```

Retention is "keep newest, delete oldest." A clip is kept only if it fits within
every limit you set (`--keep-gb` total size, `--keep` count) and is not older
than `--max-age-days`. The in-progress recording (`temp*.mp4`) and anything
newer than `--min-age-hours` (default 2) are never touched. Nothing is deleted
without `--apply`.

Set `--keep-gb` to ~75–80% of the drive's capacity (≈190 for the 256 GB Ultra
Fit, ≈400 for a 512 GB). Run `--list` first to confirm the folder names on your
drive before pruning.

## Scheduled rotation (macOS launchd)

Installed and running: a user LaunchAgent rotates each printer's `/timelapse`
every 6 hours. The printer must be on and on the LAN at run time; a printer
that's off is logged and skipped until the next run.

- **Runner** — holds the per-printer hosts + access codes, kept **out of git**:
  `~/.config/h2c-gc/run.sh` (mode `700`). Edit the `gc <name> <host> <code>`
  lines and `KEEP_GB` there. A second printer is one more `gc …` line.
- **LaunchAgent** — `~/Library/LaunchAgents/com.homesodamachine.h2c-timelapse-gc.plist`
  (`StartInterval` 21600 s), logging to `~/.config/h2c-gc/gc.log`.

```
sh ~/.config/h2c-gc/run.sh                                                  # run once now
launchctl bootout   gui/$(id -u)/com.homesodamachine.h2c-timelapse-gc       # stop
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.homesodamachine.h2c-timelapse-gc.plist  # (re)start
```

The runner pins `/opt/homebrew/bin/python3` (stable) rather than whatever
`python3` resolves to in an interactive shell.
