"""Integrity regressions for the exact historical A–F artifact set."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

import cover_retention_trial as trial


class RetainedArtifactsTest(unittest.TestCase):
    def test_clean_restore_needs_no_production_tree(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(trial.restore(directory), 19)
            manifest = trial.read_manifest()
            self.assertEqual(trial.verify_files(directory, manifest["outputs"]), 19)
            self.assertEqual({path.name for path in Path(directory).iterdir()}, trial.OUTPUTS)

    def test_restore_replaces_drift_without_touching_records(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "cover-retention-a.stl").write_bytes(b"different geometry")
            project = root / "faucet-cover-retention-petgf.3mf"
            project.write_bytes(b"retained print project")
            trial.restore(root)
            self.assertEqual(trial.verify_files(root, trial.read_manifest()["outputs"]), 19)
            self.assertEqual(project.read_bytes(), b"retained print project")

    def test_whole_archive_corruption_prevents_all_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = trial.read_manifest()
            (root / manifest["archive"]["file"]).write_bytes(b"corrupted archive")
            manifest_path = root / "retained-artifacts.json"
            manifest_path.write_text(json.dumps(manifest))
            output = root / "outputs"
            with self.assertRaisesRegex(ValueError, "Retained artifact differs"):
                trial.restore(output, manifest_path)
            self.assertFalse(output.exists())

    def test_member_corruption_is_caught_with_a_matching_archive_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, members = trial.snapshot()
            members["cover-retention-f.step.mesh"] = b"wrong viewer geometry"
            archive_path = root / manifest["archive"]["file"]
            with zipfile.ZipFile(archive_path, "w") as archive:
                for name, raw in members.items():
                    archive.writestr(name, raw)
            raw = archive_path.read_bytes()
            manifest["archive"].update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
            manifest_path = root / "retained-artifacts.json"
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "cover-retention-f.step.mesh"):
                trial.restore(root / "outputs", manifest_path)
            self.assertFalse((root / "outputs").exists())

    def test_incomplete_manifest_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = trial.read_manifest()
            del manifest["outputs"]["cover-retention-e.stl"]
            path = Path(directory) / "retained-artifacts.json"
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "complete retained A–F"):
                trial.read_manifest(path)

    def test_changed_report_is_reported_without_rewriting_it(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fit-check.json"
            path.write_bytes(b"current-production reading")
            reading = {path.name: trial.read_manifest()["records"][path.name]}
            with self.assertRaisesRegex(ValueError, "fit-check.json"):
                trial.verify_files(directory, reading)
            self.assertEqual(path.read_bytes(), b"current-production reading")

    def test_held_outputs_project_and_reports_are_exact(self):
        result = trial.verify()
        self.assertEqual((result["outputs"], result["records"]), (19, 14))


if __name__ == "__main__":
    unittest.main()
