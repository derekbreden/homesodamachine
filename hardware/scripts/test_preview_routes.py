#!/usr/bin/env python3
"""Run on request to check that route previews execute current sources.

    python3 hardware/scripts/test_preview_routes.py

The fixture is a tiny std-only Rust program in a temporary checkout. Its source
and payload change between two complete CLI requests; both must be rebuilt and
executed through the regular Rust part builder. No CadQuery or hsm query runs.
"""
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

PREVIEW = Path(__file__).resolve().with_name("preview_routes.py")


def payload(x):
    blob = bytearray()
    row = {"name": "tube-test", "color": [0.1, 0.2, 0.3]}
    for key, kind, values in (
            ("pos", "f", [x, 0., 0., x + 1., 0., 0., x, 1., 0.]),
            ("nrm", "f", [0., 0., 1.] * 3),
            ("idx", "I", [0, 1, 2]), ("fac", "I", [0, 0])):
        row[key] = [len(blob), len(values)]
        blob.extend(struct.pack("<" + kind * len(values), *values))
    head = json.dumps({"v": 3, "meshes": [row]}).encode()
    head += b" " * ((-(len(head) + 4)) % 4)
    return struct.pack("<I", len(head)) + head + blob


class CurrentSourceExecution(unittest.TestCase):
    def test_source_edit_changes_the_program_executed_by_the_cli(self):
        with tempfile.TemporaryDirectory(prefix="route-preview-source-") as directory:
            root = Path(directory)
            crate = root / "tools/hsm/kernel"
            source = crate / "src"
            source.mkdir(parents=True)
            (crate / "Cargo.toml").write_text(
                '[package]\nname = "hsm-kernel"\nversion = "0.1.0"\nedition = "2021"\n'
                '[[bin]]\nname = "route-preview"\npath = "src/main.rs"\n')
            (crate / "Cargo.lock").write_text(
                'version = 4\n\n[[package]]\nname = "hsm-kernel"\nversion = "0.1.0"\n')
            routes, scene, output = (root / name for name in ("routes.json", "context.mesh", "preview.mesh"))
            routes.write_text(json.dumps({"test": {"od_mm": 6.35, "id_mm": 4.32,
                "segments": [{"kind": "line", "points_mm": [[0, 0, 0], [0, 0, 10]]}]}}))
            scene.write_bytes(payload(0.))
            env = {**os.environ, "HSM_WORKSPACE": str(root), "CARGO_BUILD_JOBS": "2"}
            results = []
            for revision, x in (("first", 1.), ("second", 2.)):
                (source / "tube.mesh").write_bytes(payload(x))
                (source / "main.rs").write_text('''use std::{env, fs};
fn main() {
    let args: Vec<String> = env::args().collect();
    fs::write(&args[2], include_bytes!("tube.mesh")).unwrap();
    println!("{}", r#"{"linear_mm":0.005,"angular_rad":0.05,"revision":"REVISION"}"#);
}
'''.replace("REVISION", revision))
                run = subprocess.run([sys.executable, str(PREVIEW), "--routes", str(routes),
                                      "--scene", str(scene), "--output", str(output)],
                                     env=env, text=True, capture_output=True)
                self.assertEqual(run.returncode, 0, run.stderr)
                report = json.loads(run.stdout)
                self.assertEqual(report["kernel"]["revision"], revision)
                self.assertGreaterEqual(report["build_seconds"], 0.)
                raw = output.read_bytes()
                size = struct.unpack_from("<I", raw)[0]
                header = json.loads(raw[4:4 + size])
                offset = header["meshes"][0]["pos"][0]
                self.assertEqual(struct.unpack_from("<f", raw, 4 + size + offset)[0], x)
                results.append(report["payload_sha256"])
            self.assertNotEqual(*results)


if __name__ == "__main__":
    unittest.main()
