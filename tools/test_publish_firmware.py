"""Release failures must leave the public firmware pointer and upload untouched.

    python3 -m unittest discover -s tools -p test_publish_firmware.py
"""

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import publish_firmware as release


class PublicationFailures(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.pointer = self.root / "firmware-images.json"
        self.pointer.write_text("published release\n")
        self.image = self.root / "firmware.bin"
        self.image.write_bytes(b"an earlier successful build")

    def assert_build_failure_stays_local(self, target):
        failed = subprocess.CompletedProcess([], 1, stdout="compile failed\n", stderr="detail\n")
        with patch.object(release, "POINTERS", self.pointer), \
             patch.object(release, "image_path", return_value=self.image), \
             patch.object(release.subprocess, "run", return_value=failed), \
             patch.object(release, "upload") as upload, \
             patch.object(release, "survey") as survey:
            with self.assertRaisesRegex(SystemExit, "firmware release unchanged"):
                release.main(["--write", target])
            upload.assert_not_called()
            survey.assert_not_called()
        self.assertEqual(self.pointer.read_text(), "published release\n")
        self.assertEqual(self.image.read_bytes(), b"an earlier successful build")

    def test_failed_application_build_cannot_publish_stale_binary(self):
        self.assert_build_failure_stays_local("enclosure")

    def test_failed_art_build_cannot_publish_stale_art(self):
        self.assert_build_failure_stays_local("art")

    def test_successful_command_without_output_cannot_publish(self):
        self.image.unlink()
        success = subprocess.CompletedProcess([], 0, stdout="", stderr="")
        with patch.object(release, "image_path", return_value=self.image), \
             patch.object(release.subprocess, "run", return_value=success):
            with self.assertRaisesRegex(SystemExit, "build produced no image"):
                release.build("enclosure")

    def test_no_build_requires_every_requested_image(self):
        with patch.object(release, "POINTERS", self.pointer), \
             patch.object(release, "survey", return_value={"enclosure": {}}), \
             patch.object(release, "show"), patch.object(release, "upload") as upload:
            with self.assertRaisesRegex(SystemExit, "Missing requested images: art"):
                release.main(["--write", "--no-build", "enclosure", "art"])
            upload.assert_not_called()
        self.assertEqual(self.pointer.read_text(), "published release\n")


if __name__ == "__main__":
    unittest.main()
