"""Verify or replay the retained, bounded G Ganen installation probes.

The executed probe sources are preserved byte-for-byte in scripts/*.py.txt.
Replay changes only their filesystem bootstrap, uses the frozen foam datum,
and writes to an explicit private output directory. It never runs a producer.
"""
from argparse import ArgumentParser
import gzip
import hashlib
import json
from pathlib import Path
import sys
import types
from urllib.request import urlopen


HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "NAMES.md").is_file())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify():
    manifest = json.loads((HERE / "manifest.json").read_text())
    for name, row in manifest["files"].items():
        path = HERE / name
        assert digest(path) == row["sha256"], name
        if "uncompressed_sha256" in row:
            raw = gzip.decompress(path.read_bytes())
            assert hashlib.sha256(raw).hexdigest() == row["uncompressed_sha256"], name
    for name in ("neighbor-check.json", "installed-mount-check.json"):
        report = json.loads((HERE / "reports" / name).read_text())
        assert report["all_pass"], name
    print(f"PASS: {len(manifest['files'])} retained files and both passing reports")


def materialize(name, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    source = HERE / name
    target.write_bytes(gzip.decompress(source.read_bytes()) if source.suffix == ".gz" else source.read_bytes())
    return target


def source_guard():
    record = json.loads((HERE / "validation.json").read_text())
    for name, expected in record["frozen_geometry_inputs_sha256"].items():
        assert digest(ROOT / name) == expected, f"Geometry input changed: {name}"


def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def baseline_step(args, work):
    record = json.loads((HERE / "fixtures/baseline-assembly.json").read_text())
    source = args.baseline_step or ROOT / record["path"]
    if not source.exists() or digest(source) != record["sha256"]:
        assert args.fetch_baseline, "Supply the exact --baseline-step or explicitly use --fetch-baseline."
        source = work / "baseline-assembly.step"
        with urlopen(record["object_url"], timeout=60) as response:
            source.write_bytes(gzip.decompress(response.read()))
    assert digest(source) == record["sha256"], "Wrong baseline assembly bytes"
    dest = work / "before/hardware/manifold-layout/enclosure-assembly.step"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.symlink_to(source.resolve())


def replay_neighbors(args, work):
    source_guard()
    baseline_step(args, work)
    materialize("fixtures/baseline-facts.json", work / "before/hardware/manifold-layout/enclosure-assembly.facts.json")
    foam = materialize("fixtures/baseline-foam.step.gz", work / "baseline-foam.step")
    cache = work / "vf-cache"
    materialize("fixtures/retained-frames.json", cache / "frames.json")
    materialize("fixtures/valve-v-f.brep.gz", cache / "valve-v-f.brep")
    original = HERE / "scripts/verify_final_neighbors.py.txt"
    code = original.read_text()
    code = replace_once(code, "R=Path('/Users/derekbredensteiner/Developer/homesodamachine');O=Path('/tmp/scanner-review/g-ganen-feet-correction')", f"R=Path({str(ROOT)!r});O=Path({str(work)!r})")
    code = replace_once(code, "import enclosure_assembly as ea\n", f"import enclosure_assembly as ea\nea.FOAM_STEP=Path({str(foam)!r})\n")
    code = replace_once(code, "cache=Path('/tmp/scanner-review/integration-correction/route-pack')", f"cache=Path({str(cache)!r})")
    exec(compile(code, str(original), "exec"), {"__name__": "__main__", "__file__": str(original)})


def replay_washer(work):
    foot = materialize("fixtures/common-foot.step.gz", work / "common-foot.step")
    native = json.loads((HERE / "fixtures/prior-native-index.json").read_text())
    for name, filename in (("cold-core/foam-cap-top", "prior-cap-top.brep"), ("cold-core/foam-cap-lid-top", "prior-cap-lid-top.brep")):
        path = materialize("fixtures/" + filename + ".gz", work / filename)
        assert digest(path) == native["bodies"][name]["sha256"]
        native["bodies"][name]["path"] = str(path)
    (work / "current-native.json").write_text(json.dumps(native, indent=2) + "\n")
    materialize("fixtures/prior-stations.json", work / "observed-envelope-probe.json")
    helper = HERE / "scripts/check_common_positions.py.txt"
    module = types.ModuleType("check_common_positions")
    module.__file__ = str(helper)
    exec(compile(helper.read_text(), str(helper), "exec"), module.__dict__)
    sys.modules[module.__name__] = module
    original = HERE / "scripts/check_washer_15.py.txt"
    code = replace_once(original.read_text(), "O=Path('/tmp/scanner-review/g-ganen-feet-correction')", f"O=Path({str(work)!r})")
    code = replace_once(code, "P=Path('/Users/derekbredensteiner/Developer/homesodamachine/.cache/g-ganen-common-foot/common-foot-candidate.step')", f"P=Path({str(foot)!r})")
    exec(compile(code, str(original), "exec"), {"__name__": "__main__", "__file__": str(original)})


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("verify", "neighbors", "washer"), nargs="?", default="verify")
    parser.add_argument("--output", type=Path, help="New empty private directory; required for a native replay")
    parser.add_argument("--baseline-step", type=Path)
    parser.add_argument("--fetch-baseline", action="store_true", help="Explicitly fetch the hash-named published baseline")
    args = parser.parse_args()
    verify()
    if args.mode != "verify":
        assert args.output, "Native replay requires --output"
        work = args.output.resolve()
        assert HERE not in (work, *work.parents), "Outputs must remain outside the evidence package"
        assert not work.exists(), "Use a new output directory"
        work.mkdir(parents=True)
        if args.mode == "neighbors":
            replay_neighbors(args, work)
        else:
            replay_washer(work)
