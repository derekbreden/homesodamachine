#!/usr/bin/env python3
"""Compose the self-contained conversation fragment from saved study packs."""

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def compose(destination: Path):
    provenance = json.loads((HERE/"context-provenance.json").read_text())
    metadata = json.loads((HERE/"study-metadata.json").read_text())
    # Different saved snapshots must never look like one clearance study.
    context_hash = provenance["sources"]["step"]["sha256"]
    if context_hash != metadata["step_sha256"]:
        raise ValueError("Context and proposal capacity use different STEP snapshots")
    for filename, field in (("geometry.py", "geometry_sha256"),
                            ("drawer.py", "drawer_geometry_sha256"),
                            ("context-source.facts.json", "facts_sha256")):
        if hashlib.sha256((HERE/filename).read_bytes()).hexdigest() != metadata[field]:
            raise ValueError(f"{filename} changed after proposal generation; rebuild")
    if provenance["sources"]["facts"]["sha256"] != metadata["facts_sha256"]:
        raise ValueError("Context and proposal use different saved facts")
    fragment = (HERE/"viewer.template.html").read_text()
    fragment = fragment.replace("__CONTEXT_DATA__", (HERE/"context.b64").read_text().strip())
    fragment = fragment.replace("__PROPOSAL_DATA__", (HERE/"proposals.b64").read_text().strip())
    if len(fragment.encode()) >= 1_000_000:
        raise ValueError(f"Inline fragment is {len(fragment.encode())} bytes (limit 1 MB)")
    if any(token in fragment for token in ("__CONTEXT_DATA__", "__PROPOSAL_DATA__")):
        raise ValueError("Unfilled study pack")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(fragment)
    print(f"{destination}: {len(fragment.encode()):,} bytes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    compose(parser.parse_args().destination)
