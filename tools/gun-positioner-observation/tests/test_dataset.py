"""Append-only session directories, schema validation and integrity checks."""

import json
import unittest

from support import tmpdir

from gpobs import schema
from gpobs.clock import FakeClock
from gpobs.dataset import SessionClosed, SessionReader, SessionWriter

HERE = __import__("pathlib").Path(__file__).resolve().parent


class AppendOnly(unittest.TestCase):
    def test_layout_and_exclusive_creation(self):
        clock = FakeClock()
        w = SessionWriter(tmpdir("ds"), "dry learning / day 1", clock, config={"cameras": 2})
        self.assertTrue(w.session_id.split("-", 1)[1].startswith("dry-learning-day-1"))
        w.append("session_note", text="hello", author="test")
        rel = w.store_frame("cam_a", 0, b"\x00\x01", "pgm")
        with self.assertRaises(FileExistsError):
            w.store_frame("cam_a", 0, b"\x02", "pgm")
        with self.assertRaises(ValueError):
            w.store_frame("../escape", 1, b"", "pgm")
        with self.assertRaises(ValueError):
            w.append("frame", camera_id="cam_a")            # missing required fields
        with self.assertRaises(ValueError):
            w.append("no_such_kind")
        w.append("trial_start", trial_id="t1", purpose="probe", plan={}, direction_state=[0] * 6)
        w.append("trial_end", trial_id="t1", outcome="failed", reason="measurement refused")
        w.close("closed", {"note": "kept failed trial"})
        with self.assertRaises(SessionClosed):
            w.append("session_note", text="late", author="test")
        with self.assertRaises(SessionClosed):
            w.close()
        manifest = json.loads((w.path / "manifest.json").read_text())
        self.assertEqual(manifest["schema"], "gpobs/1")
        self.assertEqual(manifest["config"], {"cameras": 2})
        self.assertEqual((w.path / rel).read_bytes(), b"\x00\x01")
        r = SessionReader(w.path)
        self.assertEqual([x["rec"] for x in r.records()], [0, 1, 2])
        report = r.integrity()
        self.assertTrue(report.ok, report.problems)
        self.assertEqual(report.stats["trial_outcomes"], {"failed": 1})

    def test_integrity_detects_damage_and_interruption(self):
        clock = FakeClock()
        w = SessionWriter(tmpdir("ds2"), "damage", clock)
        frame = dict(camera_id="cam_a", source_seq=None, recv_wall_ns=1, device_pts_ns=None, source_host_ns=None,
                     codec="gray8", width=2, height=1, bytes=2, dims_verified=True, native_4k=False,
                     measurement=False, window_id=None, optics_id=None, excluded_reasons=[])
        rel = w.store_frame("cam_a", 0, b"P5\n2 1\n255\n\x00\x01", "pgm")
        w.append("frame", seq=0, recv_mono_ns=10, stored=True, file=rel, **frame)
        w.append("frame", seq=2, recv_mono_ns=5, stored=False, file=None, **frame)
        w.append("trial_start", trial_id="t9", purpose="probe", plan={}, direction_state=[0] * 6)
        w.append("move_command", cmd_id="m1", counts=[1, 0, 0, 0, 0, 0], duration_us=100000, purpose="probe_jog",
                 trial_id="t9", backend="simulator", issued_mono_ns=1, issued_wall_ns=1)
        w._events.flush()
        (w.path / rel).unlink()
        with open(w.path / "events.jsonl", "a") as fh:
            fh.write('{"kind": "fram')                     # an interrupted final write
        r = SessionReader(w.path)
        report = r.integrity()
        self.assertFalse(report.ok)
        text = "\n".join(report.problems)
        self.assertIn("partial record", text)
        self.assertIn("frame seq 0 -> 2", text)
        self.assertIn("receipt time went backwards", text)
        self.assertIn("is missing", text)
        self.assertIn("no closing.json", text)
        self.assertEqual(report.stats["moves_without_completion"], ["m1"])
        self.assertEqual(report.stats["trials_unterminated"], ["t9"])
        w._events.close()


class SchemaFile(unittest.TestCase):
    def test_exported_schema_matches_code(self):
        on_disk = json.loads((HERE.parent / "observation-schema.json").read_text())
        self.assertEqual(on_disk, json.loads(json.dumps(schema.json_schema())),
                         "observation-schema.json is stale: run observe.py schema --write")

    def test_optional_fields_and_enums_validated(self):
        base = {"kind": "move_complete", "rec": 0, "mono_ns": 1, "wall_ns": 1, "cmd_id": "m", "status": "done",
                "complete_mono_ns": 2, "controller_time_us": None, "reported_counts": None, "driver_state": None,
                "fault": None}
        self.assertEqual(schema.validate(base), [])
        self.assertTrue(schema.validate({**base, "status": "maybe"}))
        self.assertTrue(schema.validate({**base, "completion_mapping_uncertainty_ns": "x"}))
        enc = {"kind": "table_encoder", "rec": 0, "mono_ns": 1, "wall_ns": 1, "counts": 5, "counts_per_rev": 100,
               "sample_mono_ns": 1, "source": "usb_arrival"}
        self.assertTrue(schema.validate(enc))
        self.assertEqual(schema.validate({**enc, "source": "camera_fiducial"}), [])


if __name__ == "__main__":
    unittest.main()
