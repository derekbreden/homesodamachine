#!/usr/bin/env python3
"""Materialize native comment-free build sources using the standard parser backend."""
import ast
import sys
from _support_data import request


def stripped(raw: bytes) -> bytes:
    return bytes(request("stripped-source", bytes=list(raw)))


def same_code(before: bytes, after: bytes) -> bool:
    return request("same-source-code", before=list(before), after=list(after))


def main(argv: list) -> int:
    result = request("strip-source-files", root=argv[0], files=argv[1:])
    if result.get("error"):
        print(result["error"], file=sys.stderr)
    return result["status"]


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
