"""Publication manifest and digest regressions. Run explicitly with unittest."""
import json
import hashlib
import os
from contextlib import ExitStack, redirect_stdout
from io import StringIO
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS / "bazel"))
import affected
import _artifact_digest
import _artifact_inputs
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
            self.assertEqual(cache.digest("part.step"), wanted["part.step"])

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


class ListingTests(unittest.TestCase):
    """The walk lists again only a directory whose stat identity moved."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.pack = publish_now._pack()
        self.cap = self.root / "hardware/printed-parts/cap"
        self.cap.mkdir(parents=True)
        (self.cap / "cap.step").write_bytes(b"cap")

    def settled(self):
        return patch.object(_artifact_digest.time, "time_ns",
                            return_value=time.time_ns() + 2 * _artifact_digest.SETTLED_NS)

    def test_a_settled_directory_is_not_listed_again(self):
        with self.settled():
            first = self.pack.solids(self.root)
        with self.settled(), patch.object(_artifact_digest.os, "scandir",
                                          side_effect=AssertionError("listed again")):
            self.assertEqual(self.pack.solids(self.root), first)

    def test_a_member_added_or_removed_is_seen(self):
        with self.settled():
            self.pack.solids(self.root)
            (self.cap / "lid.step").write_bytes(b"lid")
            (self.cap / "cap.step").unlink()
            self.assertEqual(self.pack.solids(self.root), ["hardware/printed-parts/cap/lid.step"])

    def test_a_directory_still_settling_is_listed_again(self):
        self.pack.solids(self.root)
        with patch.object(_artifact_digest.os, "scandir", side_effect=OSError("listed again")):
            self.assertEqual(self.pack.solids(self.root), [])


def git(root, *args, stdin=None):
    return subprocess.run(["git", "-C", str(root), *args], input=stdin, capture_output=True,
                          text=True, check=True).stdout


class IndexTests(unittest.TestCase):
    """`staged` reads the index file itself, and says what `git ls-files --stage` says."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        git(self.root, "init", "-q")
        files = {"a.py": "a", "dir/b.py": "b", "dir/run.sh": "#!/bin/sh\n",
                 "dir/" + "y" * 200 + ".py": "long"}
        for rel, text in files.items():
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.root / rel).write_text(text)
        (self.root / "dir/run.sh").chmod(0o755)
        (self.root / "link").symlink_to("a.py")
        git(self.root, "add", "--", *files, "link")

    def listed(self):
        out = {}
        for row in git(self.root, "ls-files", "--stage", "-z").split("\0"):
            meta, _tab, path = row.partition("\t")
            fields = meta.split()
            if len(fields) == 3 and fields[2] == "0":
                out[path] = fields[1]
        return out

    def test_the_index_file_reads_as_git_lists_it(self):
        self.assertEqual(_artifact_inputs.staged(self.root), self.listed())

    def test_a_conflict_is_not_staged_and_an_intent_to_add_entry_reads_empty(self):
        (self.root / "later.py").write_text("later")
        git(self.root, "add", "-N", "later.py")
        blob = git(self.root, "hash-object", "-w", "a.py").strip()
        git(self.root, "update-index", "--index-info",
            stdin="".join(f"100644 {blob} {stage}\tclash.py\n" for stage in (1, 2, 3)))
        got = _artifact_inputs.staged(self.root)
        self.assertNotIn("clash.py", got)
        self.assertEqual(got["later.py"], git(self.root, "hash-object", "--stdin", stdin="").strip())
        self.assertEqual(got, self.listed())

    def test_a_layout_this_does_not_read_goes_to_git(self):
        for flags in (["--index-version", "4"], ["--split-index"]):
            git(self.root, "update-index", *flags)
            index = (self.root / ".git/index").read_bytes()
            self.assertIsNone(_artifact_inputs._read_index(index))
            self.assertEqual(_artifact_inputs.staged(self.root), self.listed())

    def test_a_blob_id_is_the_one_git_gives_the_bytes(self):
        for rel in ("a.py", "dir/run.sh", "link"):
            self.assertEqual(_artifact_inputs.blob_id(self.root / rel), self.listed()[rel])
        self.assertEqual(_artifact_inputs.blob_id(self.root / "absent.py"), "-")


class OwedTests(unittest.TestCase):
    """What `publish_now.owed` reads off a tree whose one rule writes a part from its source."""

    PART = "hardware/printed-parts/example/part.step"
    SOURCE = "hardware/printed-parts/example/part.py"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "tools/cad-artifacts").mkdir(parents=True)
        (self.root / "tools/docgen").mkdir()
        (self.root / "tools/bazel").mkdir()
        shutil.copyfile(TOOLS / "cad-artifacts/pack.py", self.root / "tools/cad-artifacts/pack.py")
        for rel, text in ((self.SOURCE, "part"), (self.PART, "solid"), ("README.md", "docs")):
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.root / rel).write_text(text)
        (self.root / "tools/bazel/graph.json").write_text(json.dumps(
            {self.SOURCE: {"reads": [self.SOURCE], "writes": [self.PART]}}))
        git(self.root, "init", "-q")
        git(self.root, "add", "--", self.SOURCE, "README.md")
        self.pointer({self.PART: {"inputs": self.tree()[self.PART], "commit": "c"}})

    def patched(self):
        return patch.object(publish_now, "ROOT", self.root)

    def tree(self):
        with self.patched():
            pack = publish_now._pack()
            return pack.tree_digests(self.root, pack.Graph.load(self.root),
                                     {self.PART: publish_now._sha256(self.root / self.PART)})

    def pointer(self, made):
        lines = {self.PART: publish_now._sha256(self.root / self.PART)}
        (self.root / publish_now.POINTERS).write_text(json.dumps({"solids": lines, "made": made}))
        git(self.root, "add", "--", publish_now.POINTERS)

    def owed(self):
        with self.patched():
            return publish_now.owed()

    def commit_to(self, rel, text):
        (self.root / rel).write_text(text)
        git(self.root, "add", "--", rel)

    def test_a_docs_commit_owes_nothing_and_starts_no_process(self):
        self.commit_to("README.md", "docs, edited")
        with patch.object(subprocess, "run", side_effect=AssertionError("a process started")), \
                patch.object(subprocess, "Popen", side_effect=AssertionError("a process started")):
            self.assertEqual(self.owed(), publish_now.Owed("", [], [], []))

    def test_an_edit_to_what_a_member_reads_owes_its_line(self):
        self.commit_to(self.SOURCE, "part, moved")
        self.assertEqual(self.owed().inputs, [self.PART])
        self.commit_to(self.SOURCE, "part")
        self.assertEqual(self.owed().inputs, [])

    def test_bytes_that_moved_with_no_commit_are_owed(self):
        (self.root / self.PART).write_text("recut")
        self.assertEqual(self.owed().moved, [self.PART])

    def test_a_member_with_no_line_owes_one_and_one_with_nothing_to_say_waits(self):
        self.pointer({})
        self.assertEqual(self.owed().inputs, [self.PART])
        self.pointer({self.PART: {"commit": "c", "unproven": True}})
        self.commit_to(self.SOURCE, "part, moved")
        self.assertEqual(self.owed().inputs, [])

    def test_a_pointer_file_the_index_does_not_hold_is_owed_as_it_stands(self):
        path = self.root / publish_now.POINTERS
        path.write_text(path.read_text() + "\n")
        self.assertEqual(self.owed().heal, [publish_now.POINTERS])


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

    def test_source_independent_bytes_additions_and_sidecars(self):
        part = self.part.relative_to(self.root).as_posix()
        self.assertEqual(self.drifted(), [])
        self.part.write_bytes(b"new solid")
        self.assertEqual(self.drifted(), [part])
        self.part.write_bytes(b"solid")
        self.assertEqual(self.drifted(), [])
        extra = self.part.with_name("extra.step")
        extra.write_bytes(b"extra")
        self.assertEqual(self.drifted(), [extra.relative_to(self.root).as_posix()])
        extra.unlink()
        self.assertEqual(self.drifted(), [])
        self.score.write_text('{"score":2}')
        self.assertEqual(self.drifted(), [self.score.relative_to(self.root).as_posix()])
        self.score.write_text('{"score":1}')
        self.assertEqual(self.drifted(), [])

    def test_a_member_this_disk_does_not_hold_keeps_its_line(self):
        self.part.unlink()
        self.assertEqual(self.drifted(), [])

    def test_an_unreadable_pointer_cannot_mean_unchanged_bytes(self):
        (self.root / "hardware/cad-artifacts.json").write_text("bad")
        with self.assertRaises(ValueError):
            self.drifted()


class PublicationSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.pack = publish_now._pack()
        self.relative = "hardware/manifold-layout/enclosure-assembly.step.mesh"
        self.part = self.root / self.relative
        self.part.parent.mkdir(parents=True)
        self.part.write_bytes(b"completed mechanics")
        self.captured = 1_700_000_000.125
        self.final_time = 1_700_000_000.375
        os.utime(self.part, ns=(int((self.captured - 1) * 1e9),) * 2)
        self.clock = self.captured
        self.held = {
            "solids": {self.relative: "preceding scene"},
            "moved": {self.relative: self.captured - 2},
            "sidecars": {},
            "bundle": {"sha256": "preceding bundle", "bytes": 1},
        }

    def run_publication(self, *, bundle=False):
        pointers = []
        fallback = []
        staging = self.root / "staging"
        staging.mkdir()

        def upload(root, rels, hashes, known, sources):
            self.assertEqual(sources[self.relative].read_bytes(), b"completed mechanics")
            self.part.write_bytes(b"completed wiring")
            os.utime(self.part, ns=(int(self.final_time * 1e9),) * 2)
            self.clock = self.captured + 10
            return True

        def mesh_assets(*args, **kwargs):
            if bundle:
                self.clock = self.captured + 10
            return {}

        def cut_bundle(*args, **kwargs):
            fallback.append(kwargs["stamp"])
            return 0

        held = {**self.held, "bundle": {} if bundle else self.held["bundle"]}
        replacements = {
            "_ROOT": self.root,
            "POINTERS": self.root / "hardware/cad-artifacts.json",
            "time": SimpleNamespace(time=lambda: self.clock, monotonic=time.monotonic),
            "read_pointers": lambda: held,
            "staged": lambda _: {},
            "_head": lambda _: "source revision",
            "solids": lambda _: [self.relative],
            "sidecar_lines": lambda *args: {},
            "made_here": lambda *args: {},
            "upload_mesh_assets": mesh_assets,
            "objects_in_store": lambda _: [],
            "upload_objects": upload,
            "_origin_slug": lambda _: "example/machine",
            "_write_pointers": pointers.append,
            "cut_bundle": cut_bundle,
        }
        with ExitStack() as stack:
            for name, value in replacements.items():
                stack.enter_context(patch.object(self.pack, name, value))
            stack.enter_context(patch.object(self.pack.Graph, "load", return_value=None))
            stack.enter_context(redirect_stdout(StringIO()))
            self.assertEqual(self.pack._publish_held(set(), staging, viewer_only=True), 0)
        return pointers, fallback

    def test_later_checkpoint_survives_an_intermediate_upload_in_the_same_second(self):
        pointers, fallback = self.run_publication()
        self.assertEqual(fallback, [])
        published = pointers[0]
        self.assertEqual(published["moved"][self.relative], self.captured)
        now = {self.relative: hashlib.sha256(self.part.read_bytes()).hexdigest()}
        mtimes = self.pack._native("mtimes", root=self.root, rels=[self.relative])
        self.assertGreater(mtimes[self.relative], self.captured)
        self.assertLess(mtimes[self.relative], int(self.captured) + 1)
        built, fresh, stale, absent = self.pack.held_publish_plan(published, [self.relative], now, mtimes)
        self.assertEqual((built, fresh, stale, absent), ([self.relative], [], [], []))
        state = self.pack._native("held-state", held=published, rels=[self.relative], now=now,
                                  sidecar_now={}, mtimes=mtimes)
        self.assertEqual((state["built"], state["stale"]), ([self.relative], []))

    def test_bundle_fallback_keeps_the_original_snapshot_time(self):
        pointers, fallback = self.run_publication(bundle=True)
        self.assertEqual(pointers, [])
        self.assertEqual(fallback, [self.captured])

    def test_genuinely_older_local_bytes_remain_stale(self):
        now = {self.relative: "different older bytes"}
        plan = self.pack.held_publish_plan(self.held, [self.relative], now,
                                           {self.relative: self.captured - 3})
        self.assertEqual(plan, ([], [], [self.relative], []))


if __name__ == "__main__":
    unittest.main()
