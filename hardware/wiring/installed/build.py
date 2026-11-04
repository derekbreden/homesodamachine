"""Materialize installed enclosure wiring through its Rust composer and kernel."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "hardware/scripts"), str(ROOT / "hardware/manifold-layout")]
from hardware.wiring.installed.connections import connections, interfaces, UNUSED, BOUNDARIES
from hardware.wiring.installed.model import STOCK
from hardware.wiring.installed.routes import routed
from hardware.wiring.installed.terminals import Attachments
from hardware.wiring.installed._wiring_data import read as _read

OUT = ROOT / "hardware/wiring/enclosure-wiring"


def routed_inputs(scene, ea):
    at = Attachments(scene, ea)
    at.resolve()
    graph = connections()
    return at, graph, routed(graph, at)


def _manifest(at, graph, routes, terminations, bundles):
    return _read("build_manifest", {"state": at._state, "graph": graph, "routes": routes,
                                    "terminations": terminations, "bundles": bundles})


def numeric_inputs(scene, ea):
    at = Attachments(scene, ea)
    at.resolve()
    return tuple(_read("build_numeric", {"state": at._state}, ea=ea))


def numeric_source_paths(numbers=None):
    return _read("build_sources", {"numbers": numbers})


def export_enclosure(assembly, target, *, physical_export=None):
    import _machine_export
    return _machine_export.export(assembly, Path(target).parent)


def export_from_fine(model, target, ea, *, reading=None, output=OUT):
    return _read("build_export", {"model": str(Path(model).resolve()), "target": str(Path(target).resolve()),
                                  "output": str(Path(output).resolve()), "reading": reading}, ea=ea)


def digest(path):
    return _read("file_digest", {"path": str(Path(path).resolve())})


def write_manifest(manifest, scene_step, *, output=OUT, additional_sources=(), physical_sha256=None):
    updated = _read("build_write_manifest", {"manifest": manifest, "scene_step": str(Path(scene_step).resolve()),
                    "output": str(Path(output).resolve()), "additional_sources": additional_sources,
                    "physical_sha256": physical_sha256})
    manifest.clear()
    manifest.update(updated)


def read_enclosure(target):
    from hardware.wiring.installed._model_input import read
    return read(Path(str(target) + ".npz"))


def _kernel_main(target, output, verify_retained=False):
    import json
    from _machine_reporting import scalar_namespace
    result = _read("build_kernel", {"target": str(Path(target).resolve()), "output": str(Path(output).resolve()),
                                    "verify_retained": verify_retained}, ea=scalar_namespace())
    print(json.dumps(result), flush=True)


def main():
    import argparse
    from _machine_reporting import scalar_namespace
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--kernel", action="store_true", help="Build from the explicit fine enclosure model")
    mode.add_argument("--numbers-output", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--target", type=Path, default=ROOT / "hardware/manifold-layout/enclosure-assembly.step")
    parser.add_argument("--output", type=Path, default=OUT.parent)
    parser.add_argument("--verify-retained", action="store_true")
    args = parser.parse_args()
    if args.numbers_output is not None:
        _read("build_numbers_output", {"target": str(args.target.resolve()), "output": str(args.output.resolve()),
                                       "numbers_output": str(args.numbers_output.resolve())}, ea=scalar_namespace())
        return
    _kernel_main(args.target, args.output, args.verify_retained)


if __name__ == "__main__":
    main()
