"""Compatibility calls into the Rust assembly-document programs."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "hardware/scripts"), str(ROOT / "tools")]
import _rust_part
from _rust_data import request


def _plain(value):
    if isinstance(value, dict):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [_plain(item) for item in value]
    return value


def evaluate(driver, inputs=None, *, write=False, operation="document"):
    result = request("assembly-docs", "assembly-docs", {
        "root": str(ROOT), "driver": driver, "input": _plain(inputs or {}),
        "write": write, "operation": operation,
    })
    if result.get("data_reads"):
        for path in result["data_reads"]:
            source = (ROOT / path).resolve()
            if source.is_relative_to(ROOT):
                _rust_part._READ_TARGETS.add(source.relative_to(ROOT).as_posix())
    if result.get("maintained"):
        from docgen import note_rewritten
        for path in result["maintained"]:
            note_rewritten(ROOT / path)
    return result


def update(driver, inputs=None):
    result = evaluate(driver, inputs, write=True)
    if result.get("stdout"):
        print(result["stdout"], end="")
    return result
