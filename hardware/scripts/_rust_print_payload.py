"""Command adapters for Rust's print surfaces and surface-graft input plans."""
from pathlib import Path


def _presentation():
    import sys
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root / "hardware/printed-parts/enclosure/enclosure"))
    import _rust_enclosure_presentation
    return _rust_enclosure_presentation


def cut(step, stl, *, verbose=True, preserve_print_triangles=False, identity=None):
    if identity is None:
        import flute_payload
        identity = flute_payload.solid_identity(step)
    return _presentation().print_payload(Path(step), stl=Path(stl), source=Path(step),
        identity=identity, verbose=verbose, preserve_print_triangles=preserve_print_triangles)


def _header(path):
    import _mesh_payload
    return _mesh_payload.read_header(path)


def main(directories, *, preserve_print_triangles=None):
    import flute_payload
    import _rust_part
    import _machine_export
    from _build_data import request

    directories = list(map(str, directories))
    found = request("print-inputs", directories=directories,
                    faucet_directories=list(map(str, flute_payload.FAUCET_DIRS)),
                    preserve=preserve_print_triangles)
    if not found:
        raise SystemExit("no printed meshes beside the solids in " + ", ".join(directories))
    for item in found:
        cut(item["step"], item["stl"], preserve_print_triangles=item["preserve"])
    pending = request("graft-inputs", directories=directories)
    for source in pending["reads"]:
        _rust_part._READ_TARGETS.add(_rust_part._relative(Path(source)))
    for item in pending["requests"]:
        path = Path(item["path"])
        plan = _rust_part.check("enclosure-shell", "enclosure-presentation", item["numbers"])
        for row in plan.get("moved", ()):
            print(f"   {path.name}: {row['name']} keeps its host surface; no placement "
                  f"recovered across {row['drift_mm']:.1f} mm")
        if plan["skins"]:
            result = _machine_export.graft(path, plan["skins"])
            if result["grafted"]:
                print(f"-> {path}  {result['grafted']} piece(s) grafted, "
                      f"{path.stat().st_size/1e6:.2f} MB")
    return 0
