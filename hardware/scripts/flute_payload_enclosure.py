"""Rebuild enclosure print surfaces with the native print and graft programs."""
from flute_payload import ENCLOSURE_DIRS, rust_main


if __name__ == "__main__":
    raise SystemExit(rust_main(ENCLOSURE_DIRS))
