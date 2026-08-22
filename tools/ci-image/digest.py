#!/usr/bin/env python3
"""Print the content tag for every repository input copied into the CAD image."""

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FILES = (
    ".bazelversion",
    ".dockerignore",
    "tools/cad-requirements.txt",
    "tools/ci-image/Dockerfile",
    "tools/ci-image/digest.py",
    "tools/render/package.json",
    "tools/render/package-lock.json",
    "web/package.json",
    "web/package-lock.json",
)
TREES = ("tools/cad-venv-site",)


def inputs() -> list[Path]:
    paths = [ROOT / rel for rel in FILES]
    for rel in TREES:
        paths.extend(p for p in (ROOT / rel).rglob("*")
                     if p.is_file() and "__pycache__" not in p.parts)
    missing = [p for p in paths if not p.is_file()]
    if missing:
        raise SystemExit(f"CAD image input is absent: {missing[0].relative_to(ROOT)}")
    return sorted(set(paths), key=lambda p: p.relative_to(ROOT).as_posix())


def digest() -> str:
    answer = hashlib.sha256()
    for path in inputs():
        rel = path.relative_to(ROOT).as_posix().encode()
        data = path.read_bytes()
        answer.update(len(rel).to_bytes(4, "big"))
        answer.update(rel)
        answer.update(len(data).to_bytes(8, "big"))
        answer.update(data)
    return answer.hexdigest()[:16]


if __name__ == "__main__":
    print(digest())
