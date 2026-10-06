"""Retention and archive-before-delete checks; no printer connections."""
import datetime
import ftplib
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import h2c_timelapse_gc as gc

UTC = datetime.timezone.utc
NOW = datetime.datetime(2026, 10, 6, 21, tzinfo=UTC)


def clip(name, age_hours, size=5):
    mtime = None if age_hours is None else NOW - datetime.timedelta(hours=age_hours)
    return gc.Clip(name, "/timelapse/" + name, size, mtime)


class Retention(unittest.TestCase):
    def test_protected_clips_count_toward_total_retention(self):
        clips = [clip("temp.mp4", 100), clip("recent.mp4", 1),
                 clip("newest-old.mp4", 3), clip("middle.mp4", 4), clip("oldest.mp4", 5)]
        delete, keep = gc.plan_deletions(clips, NOW, None, 3, None, 2)
        self.assertEqual([c.name for c in delete], ["oldest.mp4", "middle.mp4"])
        self.assertEqual({c.name for c in keep}, {"temp.mp4", "recent.mp4", "newest-old.mp4"})

    def test_small_clips_are_pruned_by_count_without_a_size_budget(self):
        clips = [clip(f"clip-{i}.mp4", 3 + i, 1) for i in range(128)]
        delete, keep = gc.plan_deletions(clips, NOW, None, 96, None, 2)
        self.assertEqual(len(keep), 96)
        self.assertEqual(len(delete), 32)
        self.assertEqual([c.name for c in delete], [f"clip-{i}.mp4" for i in range(127, 95, -1)])

    def test_unknown_or_active_clips_survive_even_when_protected_count_exceeds_limit(self):
        clips = [clip("temp.mp4", 100), clip("unknown.mp4", None), clip("recent.mp4", 1),
                 clip("old.mp4", 4)]
        delete, keep = gc.plan_deletions(clips, NOW, None, 0, 1, 2)
        self.assertEqual([c.name for c in delete], ["old.mp4"])
        self.assertEqual(len(keep), 3)

    def test_size_is_an_optional_additional_limit(self):
        clips = [clip("recent.mp4", 1, 6), clip("old.mp4", 3, 5)]
        delete, keep = gc.plan_deletions(clips, NOW, 10 / gc.GB, 96, None, 2)
        self.assertEqual([c.name for c in delete], ["old.mp4"])
        self.assertEqual([c.name for c in keep], ["recent.mp4"])

    def test_empty_recording_placeholder_survives_a_long_print(self):
        clips = [clip("active-job.mp4", 12, 0), clip("old.mp4", 48)]
        delete, keep = gc.plan_deletions(clips, NOW, None, 1, None, 2)
        self.assertEqual([c.name for c in delete], ["old.mp4"])
        self.assertEqual([c.name for c in keep], ["active-job.mp4"])

    def test_cli_defaults_to_count_only(self):
        with patch("sys.argv", ["gc", "--host", "example", "--access-code", "example"]), \
                patch.object(gc, "rotate") as rotate:
            gc.main()
        args, _, keep_gb = rotate.call_args.args
        self.assertEqual(args.keep, 96)
        self.assertIsNone(keep_gb)

    def test_apply_without_archive_is_rejected_before_connecting(self):
        with patch("sys.argv", ["gc", "--host", "example", "--access-code", "example", "--apply"]), \
                patch.object(gc, "connect") as connect, patch("sys.stderr"):
            with self.assertRaises(SystemExit):
                gc.main()
        connect.assert_not_called()


class FakeFTP:
    def __init__(self):
        self.content = b"video bytes"
        self.mtime = NOW - datetime.timedelta(days=3)
        self.remote_size = len(self.content)
        self.deleted = []
        self.after_download = None
        self.download_error = None
        self.size_calls = 0
        self.change_before_delete = False

    def size(self, path):
        self.size_calls += 1
        if self.change_before_delete and self.size_calls == 3:
            self.remote_size += 1
        return self.remote_size

    def sendcmd(self, command):
        return "213 " + self.mtime.strftime("%Y%m%d%H%M%S")

    def retrbinary(self, command, callback):
        callback(self.content)
        if self.download_error:
            raise self.download_error
        if self.after_download:
            self.after_download(self)

    def delete(self, path):
        self.deleted.append(path)


class VerifiedArchive(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.ftp = FakeFTP()
        self.clip = gc.Clip("old.mp4", "/timelapse/old.mp4", self.ftp.remote_size, self.ftp.mtime)

    def assert_remote_retained(self, message):
        with self.assertRaisesRegex((RuntimeError, ftplib.error_temp, OSError), message):
            gc.archive_and_delete(self.ftp, self.clip, self.directory)
        self.assertEqual(self.ftp.deleted, [])
        self.assertFalse(list(self.directory.glob("*.part")))
        self.assertFalse(list(self.directory.glob(".*.part")))

    def test_success_writes_video_and_checksum_before_remote_delete(self):
        original_delete = self.ftp.delete

        def check_backup_then_delete(path):
            dest = self.directory / "old.mp4"
            self.assertEqual(dest.read_bytes(), self.ftp.content)
            expected = hashlib.sha256(self.ftp.content).hexdigest() + "  old.mp4\n"
            self.assertEqual((self.directory / "old.mp4.sha256").read_text(), expected)
            original_delete(path)

        self.ftp.delete = check_backup_then_delete
        gc.archive_and_delete(self.ftp, self.clip, self.directory)
        self.assertEqual(self.ftp.deleted, [self.clip.path])

    def test_existing_wrong_backup_does_not_authorize_deletion(self):
        dest = self.directory / "old.mp4"
        dest.write_bytes(b"other video")
        self.assert_remote_retained("collision")
        self.assertEqual(dest.read_bytes(), b"other video")

    def test_existing_matching_backup_is_verified_against_remote_content(self):
        (self.directory / "old.mp4").write_bytes(self.ftp.content)
        gc.archive_and_delete(self.ftp, self.clip, self.directory)
        self.assertEqual(self.ftp.deleted, [self.clip.path])

    def test_truncated_successful_download_does_not_authorize_deletion(self):
        self.ftp.content = b"short"
        self.assert_remote_retained("Incomplete")

    def test_transfer_failure_does_not_authorize_deletion(self):
        self.ftp.download_error = ftplib.error_temp("transfer interrupted")
        self.assert_remote_retained("interrupted")

    def test_changed_since_listing_does_not_authorize_deletion(self):
        self.ftp.remote_size += 1
        self.assert_remote_retained("since listing")

    def test_changed_during_download_does_not_authorize_deletion(self):
        self.ftp.after_download = lambda ftp: setattr(ftp, "mtime", NOW)
        self.assert_remote_retained("during download")

    def test_changed_after_archiving_does_not_authorize_deletion(self):
        self.ftp.change_before_delete = True
        self.assert_remote_retained("before deletion")
        self.assertTrue((self.directory / "old.mp4").exists())

    def test_failed_disk_verification_does_not_authorize_deletion(self):
        with patch.object(gc, "file_digest", return_value="wrong"):
            self.assert_remote_retained("checksum")

    def test_failed_backup_flush_does_not_authorize_deletion(self):
        with patch.object(gc.os, "fsync", side_effect=OSError("disk error")):
            self.assert_remote_retained("disk error")

    def test_overlapping_rotation_is_rejected(self):
        with gc.archive_lock(self.directory):
            with self.assertRaisesRegex(RuntimeError, "Another rotation"):
                with gc.archive_lock(self.directory):
                    self.fail("second rotation acquired the lock")


if __name__ == "__main__":
    unittest.main()
