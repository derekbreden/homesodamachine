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

## How it reaches the printer

Bambu's LAN file service is **FTPS, implicit TLS, port 990**, user `bblp`,
password = the printer's **Access Code**.

Find the IP and Access Code on the printer: **Settings → WLAN → LAN Only Mode**.
You can read the Access Code without toggling LAN-Only ON, so this does not cut
the printer off from the cloud / Bambu Handy. (If a connection is refused, turn
LAN-Only Mode ON as a fallback.)

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

## Run it on a schedule (macOS)

The printer must be powered on and on the LAN when this runs. A nightly cron
line (note the Access Code sits in plaintext in your crontab):

```
0 3 * * * H2C_HOST=192.168.1.50 H2C_ACCESS_CODE=12345678 \
  /usr/bin/python3 /Users/derekbredensteiner/Developer/homesodamachine/tools/h2c_timelapse_gc.py \
  --keep-gb 190 --archive-dir ~/H2C-timelapses --prune-thumbnails --apply \
  >> ~/h2c-gc.log 2>&1
```

The second H2C uses the same script with its own `--host` / `--access-code`.
