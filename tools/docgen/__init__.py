"""Python caller metadata for Rust-managed document substitutions.

``hsm-documents`` maintains [value](NAME) markers in Markdown, Mermaid
comments and Python comments/string literals, together with Sources blocks
and figure sidecars. This module supplies Python caller identities and the
existing build trace registries while generators move to Rust.
"""

import importlib.util
import inspect
import os
import re
import sys
from pathlib import Path


# The manual collision/path readers import the notation's patterns.
_LINK_RE = re.compile(r"\[([^\]]*)\]\(([A-Z_][A-Z0-9_]*)\)")
_SOURCES_HEADER = "## Sources"
_SOURCES_PREAMBLE = "[value](NAME) texts are updated by:"
_SOURCES_SECTION_RE = re.compile(
    re.escape(_SOURCES_HEADER) + r"\n"
    + re.escape(_SOURCES_PREAMBLE) + r"\n"
    + r"((?:- `[^`\n]+`(?:\n|\Z))+)"
)
FIGURES_SUFFIX = ".figures.json"
_WRITE_TARGETS = set()


def _request(payload):
    scripts = Path(__file__).resolve().parents[2] / "hardware" / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from _rust_data import request
    return request("documents", "hsm-documents", payload)


def load_module(name, path):
    """Import a remaining Python provider by its explicitly named source."""
    spec = importlib.util.spec_from_file_location(name, Path(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cells(row):
    return _request({"op": "cells", "text": row})


def _find_repo_root(path):
    named = os.environ.get("HSM_REPO_ROOT")
    if named:
        root = Path(named).resolve()
        if path == root or root in path.parents:
            return root
    for parent in [path, *path.parents]:
        if (parent / ".git").exists():
            return parent
    return None


def _note_target(path):
    path = Path(path).resolve()
    root = _find_repo_root(path)
    if root is not None:
        _WRITE_TARGETS.add(path.relative_to(root).as_posix())


def note_rewritten(path):
    """Register a maintained authored file, including an unchanged one."""
    _note_target(path)


def _caller_file(stack_depth=2):
    try:
        return Path(inspect.stack()[stack_depth].filename).resolve()
    except (IndexError, OSError):
        return None


def _caller_repo_path(stack_depth=2):
    caller = _caller_file(stack_depth + 1)
    root = _find_repo_root(caller) if caller is not None else None
    if root is None:
        return None
    try:
        return "/" + caller.relative_to(root).as_posix()
    except ValueError:
        return None


def _substitute(path, variables, kind, caller=None, figures=False):
    path = Path(path).resolve()
    result = _request({"op": "substitute", "kind": kind, "path": str(path),
                       "variables": {name: f"{value}" for name, value in variables.items()},
                       "caller": caller, "figures": figures})
    from _rust_part import _READ_TARGETS
    root = _find_repo_root(path)
    if root is not None:
        _READ_TARGETS.add(path.relative_to(root).as_posix())
        sidecar = path.with_suffix(FIGURES_SUFFIX)
        if figures and sidecar.is_file():
            _READ_TARGETS.add(sidecar.relative_to(root).as_posix())
    for maintained in result["maintained"]:
        _note_target(maintained)


def substitute_md(md_path, variables):
    caller_path = _caller_repo_path()
    caller = _caller_file()
    hardware = next((p for p in caller.parents if p.name == "hardware"), None) if caller else None
    figures = bool(hardware and (hardware.parent / "tools" / "hsm" / "Cargo.toml").is_file())
    _substitute(md_path, variables, "md", caller_path, figures)


def substitute_mmd(mmd_path, variables):
    _substitute(mmd_path, variables, "mmd")


def substitute_py_comments(py_path, variables):
    _substitute(py_path, variables, "py")
