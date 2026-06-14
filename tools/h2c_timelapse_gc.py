#!/usr/bin/env python3
"""
Garbage-collect the Bambu Lab H2C's USB timelapse drive over the network.

The H2C writes per-print timelapses to the SanDisk Ultra Fit in its front USB
port (folder /timelapse, *.mp4; thumbnails in /thumbnail). Bambu firmware does
NOT loop or auto-overwrite on *external* USB storage -- the "overwrite oldest
when full" feature exists only on the P2S/X2D internal storage -- so when the
drive fills, the printer silently stops recording new timelapses.

This connects to the printer's LAN file service (FTPS, implicit TLS on port 990,
user `bblp`, password = the printer's Access Code) and deletes the OLDEST
timelapse clips so the newest keep rolling in. It can archive each clip to your
Mac before deleting, and prune the matching thumbnail.

Nothing is deleted unless you pass --apply. The default is a dry run.

Finding the credentials (do not hardcode the Access Code -- pass it in):
    On the printer: Settings -> WLAN -> LAN Only Mode shows the IP + Access Code.
    You can read the code without toggling LAN-Only ON, so cloud/Handy stays up.

    --host        / $H2C_HOST          printer IP on your LAN
    --access-code / $H2C_ACCESS_CODE   the 8-char Access Code

Usage:
    # First run: just see what's on the drive (deletes nothing).
    H2C_HOST=192.168.1.50 H2C_ACCESS_CODE=12345678 \
        python3 tools/h2c_timelapse_gc.py --list

    # Dry run: show what a 190 GB keep-budget would prune (oldest first).
    ... python3 tools/h2c_timelapse_gc.py --keep-gb 190

    # Do it for real, archiving clips first and pruning thumbnails.
    ... python3 tools/h2c_timelapse_gc.py --keep-gb 190 \
        --archive-dir ~/H2C-timelapses --prune-thumbnails --apply

Retention is "keep the newest, delete the oldest." A clip is kept only if it
fits within every limit you set (--keep-gb total size, --keep file count) and is
not older than --max-age-days. The currently-recording clip (temp*.mp4) and
anything newer than --min-age-hours are never touched.

GB here means 1000^3 bytes, to match how the drive's capacity is labeled.
Requires only the Python standard library.
"""

import argparse
import datetime
import ftplib
import fnmatch
import os
import posixpath
import ssl
import sys

GB = 1000 ** 3


class ImplicitFTP_TLS(ftplib.FTP_TLS):
    """ftplib over implicit TLS (port 990) with data-channel session reuse.

    Bambu printers wrap the control socket in TLS the moment you connect
    (implicit FTPS), and require each data connection to reuse the control
    connection's TLS session. Stock ftplib does neither, so we override the
    socket setter (wrap on assignment) and ntransfercmd (resume the session).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sock = None

    @property
    def sock(self):
        return self._sock

    @sock.setter
    def sock(self, value):
        if value is not None and not isinstance(value, ssl.SSLSocket):
            value = self.context.wrap_socket(value)
        self._sock = value

    def ntransfercmd(self, cmd, rest=None):
        conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            conn = self.context.wrap_socket(conn, session=self.sock.session)
        return conn, size


class Clip:
    __slots__ = ("name", "path", "size", "mtime")

    def __init__(self, name, path, size, mtime):
        self.name = name
        self.path = path
        self.size = size
        self.mtime = mtime  # aware UTC datetime, or None if unknown

    def age_days(self, now):
        if self.mtime is None:
            return None
        return (now - self.mtime).total_seconds() / 86400.0


def human(nbytes):
    n = float(nbytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1000 or unit == "TB":
            return f"{n:.1f} {unit}"
        n /= 1000


def parse_ftp_time(s):
    """Parse an MLSD/MDTM timestamp 'YYYYMMDDHHMMSS[.fff]' as UTC."""
    if not s:
        return None
    s = s.strip().split(".")[0]
    try:
        dt = datetime.datetime.strptime(s, "%Y%m%d%H%M%S")
    except ValueError:
        return None
    return dt.replace(tzinfo=datetime.timezone.utc)


def connect(host, port, user, access_code, timeout):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE  # printer uses a self-signed cert
    ftp = ImplicitFTP_TLS(context=ctx)
    ftp.encoding = "utf-8"
    try:
        ftp.connect(host=host, port=port, timeout=timeout)
        ftp.login(user=user, passwd=access_code)
        ftp.prot_p()
        ftp.voidcmd("TYPE I")
    except ftplib.all_errors as e:
        raise SystemExit(
            f"Could not connect or log in to the H2C at {host}:{port} as {user}.\n"
            f"  {type(e).__name__}: {e}\n"
            "Check: printer is on and on the LAN, the IP is current, the Access\n"
            "Code is right, and nothing firewalls TCP 990. If it still refuses,\n"
            "toggle Settings -> WLAN -> LAN Only Mode ON and retry."
        )
    return ftp


def list_clips(ftp, folder, pattern):
    """Return Clips in `folder` whose names match `pattern`."""
    folder = "/" + folder.strip("/")
    out = []

    def add(name, size, mtime):
        if pattern and not fnmatch.fnmatch(name, pattern):
            return
        out.append(Clip(name, posixpath.join(folder, name), size, mtime))

    try:
        for name, facts in ftp.mlsd(folder, facts=["type", "size", "modify"]):
            if facts.get("type") != "file" or name in (".", ".."):
                continue
            add(name, int(facts.get("size", 0) or 0), parse_ftp_time(facts.get("modify")))
        return out
    except ftplib.all_errors:
        out.clear()  # server has no MLSD; fall back to NLST + SIZE + MDTM

    for entry in ftp.nlst(folder):
        name = posixpath.basename(entry)
        if not name or name in (".", ".."):
            continue
        full = entry if entry.startswith("/") else posixpath.join(folder, name)
        try:
            size = ftp.size(full) or 0
        except ftplib.all_errors:
            size = 0
        try:
            mtime = parse_ftp_time(ftp.sendcmd("MDTM " + full).split(maxsplit=1)[-1])
        except ftplib.all_errors:
            mtime = None
        add(name, size, mtime)
    return out


def plan_deletions(clips, now, keep_gb, keep_count, max_age_days, min_age_hours):
    """Decide which clips to delete. Newest are kept; oldest are dropped.

    A clip is protected (never deleted) if it is the in-progress recording
    (temp*) or younger than min_age_hours. Of the rest, anything older than
    max_age_days is dropped; then, walking newest-first, clips are kept while
    they fit under both keep_gb and keep_count, and the older remainder dropped.
    """
    protected, candidates = [], []
    for c in clips:
        age_h = None if c.mtime is None else (now - c.mtime).total_seconds() / 3600.0
        too_new = age_h is not None and age_h < min_age_hours
        if c.name.lower().startswith("temp") or too_new:
            protected.append(c)
        else:
            candidates.append(c)

    # Unknown mtimes sort as oldest so they fall out first under a tight budget.
    epoch = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
    candidates.sort(key=lambda c: c.mtime or epoch, reverse=True)  # newest first

    delete, keep = [], list(protected)
    kept_bytes = sum(c.size for c in protected)
    kept_count = 0
    budget = None if keep_gb is None else keep_gb * GB
    for c in candidates:
        age_d = c.age_days(now)
        too_old = max_age_days is not None and age_d is not None and age_d > max_age_days
        over_size = budget is not None and kept_bytes + c.size > budget
        over_count = keep_count is not None and kept_count >= keep_count
        if too_old or over_size or over_count:
            delete.append(c)
        else:
            keep.append(c)
            kept_bytes += c.size
            kept_count += 1

    delete.sort(key=lambda c: c.mtime or epoch)  # oldest first, for execution
    return delete, keep


def main():
    p = argparse.ArgumentParser(
        description="Delete the oldest H2C timelapses over FTPS so the drive keeps recording.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--host", default=os.environ.get("H2C_HOST"),
                   help="printer IP (or set H2C_HOST)")
    p.add_argument("--access-code", default=os.environ.get("H2C_ACCESS_CODE"),
                   help="printer Access Code (or set H2C_ACCESS_CODE)")
    p.add_argument("--user", default="bblp", help="FTP user (default: bblp)")
    p.add_argument("--port", type=int, default=990, help="FTPS port (default: 990)")
    p.add_argument("--timeout", type=float, default=30.0, help="socket timeout seconds")
    p.add_argument("--folder", default="timelapse", help="timelapse folder (default: timelapse)")
    p.add_argument("--thumb-folder", default="thumbnail", help="thumbnail folder (default: thumbnail)")
    p.add_argument("--pattern", default="*.mp4", help="filename glob to manage (default: *.mp4)")
    p.add_argument("--keep-gb", type=float, default=190.0,
                   help="keep at most this many GB of newest clips (default: 190; 0 disables)")
    p.add_argument("--keep", type=int, default=None,
                   help="also cap to this many newest clips")
    p.add_argument("--max-age-days", type=float, default=None,
                   help="also delete clips older than this many days")
    p.add_argument("--min-age-hours", type=float, default=2.0,
                   help="never delete clips younger than this (default: 2)")
    p.add_argument("--archive-dir", default=None,
                   help="download each clip here before deleting it")
    p.add_argument("--prune-thumbnails", action="store_true",
                   help="also delete the matching .jpg in the thumbnail folder")
    p.add_argument("--list", action="store_true",
                   help="just list the timelapse folder and exit")
    p.add_argument("--apply", action="store_true",
                   help="actually delete (default is a dry run)")
    args = p.parse_args()

    if not args.host or not args.access_code:
        p.error("need --host/$H2C_HOST and --access-code/$H2C_ACCESS_CODE")
    keep_gb = None if not args.keep_gb else args.keep_gb

    now = datetime.datetime.now(datetime.timezone.utc)
    ftp = connect(args.host, args.port, args.user, args.access_code, args.timeout)
    try:
        clips = list_clips(ftp, args.folder, args.pattern)
        total = sum(c.size for c in clips)
        print(f"H2C {args.host}  /{args.folder.strip('/')}: "
              f"{len(clips)} clip(s), {human(total)} total")

        if args.list or not clips:
            for c in sorted(clips, key=lambda c: c.mtime or now):
                when = c.mtime.strftime("%Y-%m-%d %H:%M") if c.mtime else "????-??-?? ??:??"
                print(f"  {when}  {human(c.size):>9}  {c.name}")
            return

        delete, keep = plan_deletions(
            clips, now, keep_gb, args.keep, args.max_age_days, args.min_age_hours)
        freed = sum(c.size for c in delete)
        verb = "Deleting" if args.apply else "Would delete"
        print(f"Keeping {len(keep)} clip(s) ({human(sum(c.size for c in keep))}); "
              f"{verb.lower()} {len(delete)} ({human(freed)}).")
        if not delete:
            return

        for c in delete:
            when = c.mtime.strftime("%Y-%m-%d %H:%M") if c.mtime else "unknown date"
            if not args.apply:
                print(f"  would delete  {when}  {human(c.size):>9}  {c.name}")
                continue
            if args.archive_dir:
                dest_dir = os.path.expanduser(args.archive_dir)
                os.makedirs(dest_dir, exist_ok=True)
                dest = os.path.join(dest_dir, c.name)
                if not os.path.exists(dest):
                    tmp = dest + ".part"
                    with open(tmp, "wb") as fh:
                        ftp.retrbinary("RETR " + c.path, fh.write)
                    os.replace(tmp, dest)
                    print(f"  archived      {c.name} -> {dest}")
            ftp.delete(c.path)
            print(f"  deleted       {when}  {human(c.size):>9}  {c.name}")
            if args.prune_thumbnails:
                stem = os.path.splitext(c.name)[0]
                thumb = "/" + args.thumb_folder.strip("/") + "/" + stem + ".jpg"
                try:
                    ftp.delete(thumb)
                    print(f"  deleted thumb {stem}.jpg")
                except ftplib.all_errors:
                    pass  # no matching thumbnail; fine

        if args.apply:
            print(f"Done. Freed {human(freed)}.")
        else:
            print("Dry run -- re-run with --apply to delete.")
    finally:
        try:
            ftp.quit()
        except ftplib.all_errors:
            ftp.close()


if __name__ == "__main__":
    sys.exit(main())
