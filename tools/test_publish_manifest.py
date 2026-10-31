"""Publication manifest and digest regressions. Run explicitly with unittest."""
import json
import os
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS / "bazel"))
import affected
from _artifact_digest import Digests, hashes
import publish_now


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def reach(self, build, paths):
        (self.root / "BUILD.bazel").write_text(build)
        with patch.object(affected, "_ROOT", self.root):
            return affected.manifest_targets(paths)

    def test_generated_outputs_and_filegroups_carry_transitive_reach(self):
        build = '''
genrule(name="source", srcs=["hardware/part.py"], outs=["pysrc/hardware/part.py"])
genrule(name="part", srcs=["pysrc/hardware/part.py"], outs=["out/part/part.step"])
filegroup(name="pieces", srcs=[":out/part/part.step"])
genrule(name="assembly", srcs=[":pieces"], outs=["out/assembly/a.step.mesh"])
genrule(name="notes", srcs=["hardware/part.py"], outs=["out/notes.md"])
'''
        self.assertEqual(self.reach(build, ["hardware/part.py"])[0], ["//:assembly", "//:part"])

    def test_globs_handle_zero_or_many_directories_and_exclusions(self):
        build = '''
filegroup(name="web", srcs=[] + glob(["web/**"], exclude=["web/**/ignored.js"], allow_empty=True))
genrule(name="part", srcs=[":web"], outs=["out/part.step"])
'''
        for path in ["web/a.js", "web/a/b/c.js"]:
            self.assertEqual(self.reach(build, [path]), (["//:part"], [path]))
        self.assertEqual(self.reach(build, ["web/ignored.js", "web/a/ignored.js"]), ([], []))

    def test_unreadable_dependency_expression_is_not_an_empty_slice(self):
        with self.assertRaises(ValueError):
            self.reach('genrule(name="a", srcs=select({"//conditions:default": []}), outs=["a.step"])', ["a.py"])

    def test_real_manifest_names_the_same_artifact_producers_as_the_inventory(self):
        tree = affected.ast.parse((TOOLS.parent / "BUILD.bazel").read_text())
        names = []
        for statement in tree.body:
            call = statement.value
            fields = {kw.arg: affected.ast.literal_eval(kw.value) for kw in call.keywords if kw.arg in {"name", "outs"}}
            if any(p.endswith(affected._CAD_OUTPUTS) for p in fields.get("outs", [])):
                names.append("//:" + fields["name"])
        self.assertEqual(set(names), affected.artifact_targets())


class DigestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.part = self.root / "part.step"
        self.part.write_bytes(b"original")
        self.addCleanup(self.temp.cleanup)

    def test_unchanged_files_are_not_read_again(self):
        wanted = hashes(self.root, ["part.step"])
        cache = Digests(self.root)
        with patch.object(Path, "open", side_effect=AssertionError("unchanged bytes were read")):
            self.assertEqual(cache.digest(self.part), wanted["part.step"])

    def test_same_size_edit_with_restored_mtime_invalidates_the_cache(self):
        before = self.part.stat()
        original = hashes(self.root, ["part.step"])
        self.part.write_bytes(b"modified")
        os.utime(self.part, ns=(before.st_atime_ns, before.st_mtime_ns))
        self.assertNotEqual(hashes(self.root, ["part.step"]), original)

    def test_replacement_and_a_broken_cache_are_cold(self):
        original = hashes(self.root, ["part.step"])
        replacement = self.root / "new.step"
        replacement.write_bytes(b"new")
        replacement.replace(self.part)
        self.assertNotEqual(hashes(self.root, ["part.step"]), original)
        (self.root / ".cache/cad-artifact-digests.json").write_text("[")
        self.assertEqual(hashes(self.root, ["part.step"])["part.step"], publish_now._sha256(self.part))


class DebtTests(unittest.TestCase):
    def test_warm_source_debt_skips_the_dependency_process(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = ["hardware/cad-artifacts.json", "BUILD.bazel", "tools/bazel/graph.json",
                     "tools/bazel/affected.py", "tools/bazel/inventory.py", "tools/bazel/gen_build.py"]
            for rel in paths:
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("{}")
            (root / paths[0]).write_text(json.dumps({"source": {"commit": "base"}}))
            calls = []

            def run(args, quiet=False):
                calls.append(args)
                out = "head\n" if args[:2] == ["git", "rev-parse"] else ""
                return subprocess.CompletedProcess(args, 0, out, "")

            with patch.object(publish_now, "ROOT", root), patch.object(publish_now, "run", run):
                self.assertEqual(publish_now.source_owes(), [])
                self.assertTrue(any("--manifest" in c for c in calls))
                calls.clear()
                self.assertEqual(publish_now.source_owes(), [])
                self.assertEqual(calls, [["git", "rev-parse", "HEAD"]])
                (root / "BUILD.bazel").write_text("changed")
                calls.clear()
                publish_now.source_owes()
                self.assertTrue(any("--manifest" in c for c in calls))

    def test_dependency_process_failure_cannot_mean_nothing_is_owed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in ["hardware/cad-artifacts.json", "BUILD.bazel", "tools/bazel/graph.json",
                        "tools/bazel/affected.py", "tools/bazel/inventory.py", "tools/bazel/gen_build.py"]:
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(json.dumps({"source": {"commit": "base"}}))

            def run(args, quiet=False):
                if "--manifest" in args:
                    return subprocess.CompletedProcess(args, 1, "", "manifest failed")
                return subprocess.CompletedProcess(args, 0, "head", "")

            with patch.object(publish_now, "ROOT", root), patch.object(publish_now, "run", run):
                with self.assertRaisesRegex(RuntimeError, "manifest failed"):
                    publish_now.source_owes()


class ByteDriftTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "tools/cad-artifacts").mkdir(parents=True)
        (self.root / "tools/docgen").mkdir()
        (self.root / "tools/bazel").mkdir()
        shutil.copyfile(TOOLS / "cad-artifacts/pack.py", self.root / "tools/cad-artifacts/pack.py")
        self.part = self.root / "hardware/printed-parts/example/part.step"
        self.part.parent.mkdir(parents=True)
        self.part.write_bytes(b"solid")
        self.score = self.part.with_name("part.scorecard.json")
        self.score.write_text('{"score":1}')
        (self.root / "tools/bazel/graph.json").write_text(json.dumps({"part.py": {
            "writes": [self.score.relative_to(self.root).as_posix()]}}))
        self.pointer = {"solids": {self.part.relative_to(self.root).as_posix(): publish_now._sha256(self.part)},
                        "sidecars": {self.score.relative_to(self.root).as_posix(): publish_now._sha256(self.score)}}
        (self.root / "hardware/cad-artifacts.json").write_text(json.dumps(self.pointer))

    def drifted(self):
        with patch.object(publish_now, "ROOT", self.root):
            return publish_now.bytes_drifted()

    def test_source_independent_bytes_additions_deletions_and_sidecars(self):
        self.assertFalse(self.drifted())
        self.part.write_bytes(b"new solid")
        self.assertTrue(self.drifted())
        self.part.write_bytes(b"solid")
        self.assertFalse(self.drifted())
        extra = self.part.with_name("extra.step")
        extra.write_bytes(b"extra")
        self.assertTrue(self.drifted())
        extra.unlink()
        self.assertFalse(self.drifted())
        self.score.write_text('{"score":2}')
        self.assertTrue(self.drifted())
        self.score.write_text('{"score":1}')
        self.assertFalse(self.drifted())
        self.part.unlink()
        self.assertTrue(self.drifted())

    def test_an_unreadable_pointer_cannot_mean_unchanged_bytes(self):
        (self.root / "hardware/cad-artifacts.json").write_text("bad")
        with self.assertRaises(ValueError):
            self.drifted()


if __name__ == "__main__":
    unittest.main()
