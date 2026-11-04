import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest


class CacheGcRunsTest(unittest.TestCase):
    def test_new_run_does_not_retain_old_run_or_expire_shared_memos(self):
        with tempfile.TemporaryDirectory() as folder:
            cache = Path(folder) / "cache"
            old = cache / "runs" / "finished-comparison" / "model.npz"
            current = cache / "runs" / "current-publication" / "model.npz"
            for path in [old, current, *(cache / name / "model" for name in
                                        ["realized", "meshes", "boxes", "printer-control/venv"])]:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"model")
                stamp = time.time() if path == current else time.time() - 5 * 86400
                os.utime(path, (stamp, stamp))
            subprocess.run([sys.executable, str(Path(__file__).with_name("cache_gc.py")),
                            "--cache", str(cache), "--days", "3", "--apply"],
                           check=True, capture_output=True, text=True)
            self.assertFalse(old.parent.exists())
            self.assertTrue(current.is_file())
            for name in ["realized", "meshes", "boxes", "printer-control/venv"]:
                self.assertTrue((cache / name / "model").is_file())

    def test_expired_run_symlink_does_not_delete_its_target(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            deliverable = root / "finished-print.3mf"
            deliverable.write_bytes(b"ready print")
            runs = root / "cache" / "runs"
            runs.mkdir(parents=True)
            link = runs / "comparison-input"
            link.symlink_to(deliverable)
            stamp = time.time() - 5 * 86400
            os.utime(link, (stamp, stamp), follow_symlinks=False)
            subprocess.run([sys.executable, str(Path(__file__).with_name("cache_gc.py")),
                            "--cache", str(root / "cache"), "--days", "3", "--apply"],
                           check=True, capture_output=True, text=True)
            self.assertFalse(link.is_symlink())
            self.assertEqual(deliverable.read_bytes(), b"ready print")


if __name__ == "__main__":
    unittest.main()
