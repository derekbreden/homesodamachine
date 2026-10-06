#!/usr/bin/env python3
"""Rotate Bambu timelapses by count over implicit FTPS (port 990).

The default dry run retains the newest 96 clips. Applying a plan requires a
local archive directory: every removed clip is downloaded, checked for stable
remote size/mtime, and verified with SHA-256 before deletion. Active temp
recordings, zero-byte clips, clips newer than two hours, and unknown timestamps are
protected and count toward the retention limit.

Pass credentials with --host/--access-code or H2C_HOST/H2C_ACCESS_CODE; never
commit them. See h2c-timelapse-gc.md for usage and the private launchd runner.
Requires only the Python standard library on macOS or Linux.
"""

import argparse
import contextlib
import datetime
import fcntl
import ftplib
import fnmatch
import hashlib
import os
from pathlib import Path
import posixpath
import ssl
import sys
import tempfile

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

    try:
        entries = ftp.nlst(folder)
    except ftplib.error_perm:
        return []  # folder absent or empty (e.g. a fresh drive with no timelapses yet)
    for entry in entries:
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
    (temp*), is empty, has an unknown timestamp, or is younger than min_age_hours.
    Protected clips count toward both limits. Of the rest, anything older than
    max_age_days is dropped; then, walking newest-first, clips are kept while
    they fit under both keep_gb and keep_count, and the older remainder dropped.
    """
    protected, candidates = [], []
    for c in clips:
        age_h = None if c.mtime is None else (now - c.mtime).total_seconds() / 3600.0
        too_new = age_h is not None and age_h < min_age_hours
        if c.name.lower().startswith("temp") or c.size <= 0 or c.mtime is None or too_new:
            protected.append(c)
        else:
            candidates.append(c)

    epoch = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
    candidates.sort(key=lambda c: c.mtime or epoch, reverse=True)  # newest first

    delete, keep = [], list(protected)
    kept_bytes = sum(c.size for c in protected)
    kept_count = len(protected)
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


def remote_metadata(ftp, path):
    """Require exact remote size and UTC mtime before an archive/delete."""
    size = ftp.size(path)
    mtime = parse_ftp_time(ftp.sendcmd("MDTM " + path).split(maxsplit=1)[-1])
    if size is None or size <= 0 or mtime is None:
        raise RuntimeError(f"Cannot verify remote clip metadata: {path}")
    return size, mtime


def file_digest(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@contextlib.contextmanager
def archive_lock(directory):
    """Serialize scheduled and manual rotations sharing an archive directory."""
    directory = Path(directory).expanduser()
    directory.mkdir(parents=True, exist_ok=True)
    with open(directory / ".rotation.lock", "a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("Another rotation is using this archive directory") from exc
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def archive_clip(ftp, clip, directory):
    """Durably archive a stable clip; reject partial transfers and collisions."""
    if clip.name != posixpath.basename(clip.name) or clip.name in ("", ".", ".."):
        raise RuntimeError("Clip must have a plain filename")
    expected = (clip.size, clip.mtime)
    if remote_metadata(ftp, clip.path) != expected:
        raise RuntimeError(f"Remote clip changed since listing: {clip.name}")
    directory = Path(directory).expanduser()
    directory.mkdir(parents=True, exist_ok=True)
    dest = directory / clip.name
    tmp = None
    checksum_tmp = None
    try:
        with tempfile.NamedTemporaryFile(dir=directory, prefix=".clip-", suffix=".part",
                                         delete=False) as fh:
            tmp = Path(fh.name)
            digest = hashlib.sha256()
            transferred = 0

            def receive(block):
                nonlocal transferred
                fh.write(block)
                digest.update(block)
                transferred += len(block)

            ftp.retrbinary("RETR " + clip.path, receive)
            fh.flush()
            os.fsync(fh.fileno())
        if transferred != clip.size or tmp.stat().st_size != clip.size:
            raise RuntimeError(f"Incomplete archive download: {clip.name}")
        if remote_metadata(ftp, clip.path) != expected:
            raise RuntimeError(f"Remote clip changed during download: {clip.name}")
        sha256 = digest.hexdigest()
        if file_digest(tmp) != sha256:
            raise RuntimeError(f"Archive checksum verification failed: {clip.name}")
        if dest.exists() and (dest.stat().st_size != clip.size or file_digest(dest) != sha256):
            raise RuntimeError(f"Archive filename collision: {clip.name}; remote clip retained")
        os.replace(tmp, dest)
        with tempfile.NamedTemporaryFile(mode="w", dir=directory, prefix=".checksum-",
                                         suffix=".part", delete=False) as fh:
            checksum_tmp = Path(fh.name)
            fh.write(f"{sha256}  {clip.name}\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(checksum_tmp, dest.with_name(dest.name + ".sha256"))
        directory_fd = os.open(directory, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
        return dest, sha256
    finally:
        for path in (tmp, checksum_tmp):
            if path is not None:
                path.unlink(missing_ok=True)


def archive_and_delete(ftp, clip, directory):
    """Delete only after a verified durable archive and a final metadata check."""
    dest, sha256 = archive_clip(ftp, clip, directory)
    if remote_metadata(ftp, clip.path) != (clip.size, clip.mtime):
        raise RuntimeError(f"Remote clip changed before deletion: {clip.name}")
    ftp.delete(clip.path)
    return dest, sha256


def main():
    p = argparse.ArgumentParser(
        description="Archive oldest Bambu timelapses over FTPS; retain the newest 96 clips.",
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
    p.add_argument("--thumb-folder", default=None,
                   help="thumbnail folder (default: <folder>/thumbnail)")
    p.add_argument("--pattern", default="*.mp4", help="filename glob to manage (default: *.mp4)")
    p.add_argument("--keep-gb", type=float, default=0,
                   help="optional GB limit in addition to count (default: 0, disabled)")
    p.add_argument("--keep", type=int, default=96,
                   help="retain this many clips, including protected clips (default: 96)")
    p.add_argument("--max-age-days", type=float, default=None,
                   help="also delete clips older than this many days")
    p.add_argument("--min-age-hours", type=float, default=2.0,
                   help="never delete clips younger than this (default: 2)")
    p.add_argument("--archive-dir", default=None,
                   help="verified local backup destination (required with --apply)")
    p.add_argument("--prune-thumbnails", action="store_true",
                   help="also delete the matching .jpg in the thumbnail folder")
    p.add_argument("--list", action="store_true",
                   help="just list the timelapse folder and exit")
    p.add_argument("--apply", action="store_true",
                   help="actually delete (default is a dry run)")
    args = p.parse_args()

    if not args.host or not args.access_code:
        p.error("need --host/$H2C_HOST and --access-code/$H2C_ACCESS_CODE")
    if args.apply and not args.archive_dir:
        p.error("--apply requires --archive-dir; clips must be backed up before removal")
    if args.keep < 0 or args.keep_gb < 0 or args.min_age_hours < 0:
        p.error("retention count, GB limit, and minimum age must be nonnegative")
    if args.max_age_days is not None and args.max_age_days < 0:
        p.error("--max-age-days must be nonnegative")
    keep_gb = None if not args.keep_gb else args.keep_gb

    now = datetime.datetime.now(datetime.timezone.utc)
    lock = archive_lock(args.archive_dir) if args.apply else contextlib.nullcontext()
    with lock:
        return rotate(args, now, keep_gb)


def rotate(args, now, keep_gb):
    ftp = connect(args.host, args.port, args.user, args.access_code, args.timeout)
    try:
        clips = list_clips(ftp, args.folder, args.pattern)
        total = sum(c.size for c in clips)
        print(f"Bambu /{args.folder.strip('/')}: "
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
            dest, sha256 = archive_and_delete(ftp, c, args.archive_dir)
            print(f"  archived      {c.name} -> {dest}  sha256={sha256}")
            print(f"  deleted       {when}  {human(c.size):>9}  {c.name}")
            if args.prune_thumbnails:
                stem = os.path.splitext(c.name)[0]
                thumb_folder = args.thumb_folder or posixpath.join(args.folder, "thumbnail")
                thumb = "/" + thumb_folder.strip("/") + "/" + stem + ".jpg"
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
