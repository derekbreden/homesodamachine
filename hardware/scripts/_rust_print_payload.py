"""Command adapters for Rust's print surfaces and surface-graft input plans."""
import json
import tempfile
from pathlib import Path


def cut(step, stl, *, verbose=True, preserve_print_triangles=False, identity=None):
    """Cut `step`'s viewer payload from the print triangles in `stl`, beside the STEP."""
    import _rust_part
    from _payload_rules import CREASE_DEG, LINEAR_DEFLECTION_RATIO
    if identity is None:
        import flute_payload
        identity = flute_payload.solid_identity(step)
    step = Path(step).resolve()
    numbers = dict(step_name=step.name, model=str(step.with_name(step.name + ".npz")),
                   stl=str(Path(stl).resolve()), check_print=False,
                   preserve_print_triangles=preserve_print_triangles,
                   crease_deg=CREASE_DEG, deflection_ratio=LINEAR_DEFLECTION_RATIO,
                   source=str(step))
    if identity is not None:
        numbers["identity"] = identity
    with tempfile.TemporaryDirectory(prefix="hsm-print-payload-") as directory:
        source = Path(directory) / "print-payload.numbers.json"
        source.write_text(json.dumps(numbers, sort_keys=True) + "\n")
        result = json.loads(_rust_part.run("print-payload", "print-payload", source, step.parent))
    target = step.with_name(step.name + ".mesh")
    _rust_part._WRITE_TARGETS.add(_rust_part._relative(target))
    if verbose:
        print(f"-> {target.name}  {result['printed_triangles']} -> {result['drawing_triangles']} "
              f"facets, {result['deviation']:.3f} mm inside a {result['bound']:.3f} mm budget")
    return result


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
        plan = _rust_part.check("print-payload", "print-payload", item["numbers"])
        for row in plan.get("moved", ()):
            print(f"   {path.name}: {row['name']} keeps its host surface; no placement "
                  f"recovered across {row['drift_mm']:.1f} mm")
        if plan["skins"]:
            result = _machine_export.graft(path, plan["skins"])
            if result["grafted"]:
                print(f"-> {path}  {result['grafted']} piece(s) grafted, "
                      f"{path.stat().st_size/1e6:.2f} MB")
    return 0
