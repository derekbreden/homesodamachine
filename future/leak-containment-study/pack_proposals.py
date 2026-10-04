#!/usr/bin/env python3
"""Pack display meshes without changing their saved quantized surfaces.

Positions use signed integer micrometres (source is already rounded to 0.001 mm).
Indices are uint32. Exact duplicate positions are reindexed; no triangle or face
is removed. A gzip-compressed header-plus-binary stream avoids JSON digit overhead.
"""

import base64
import gzip
import json
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent


def encode(data):
    blob, entries = bytearray(), []
    for original in data["meshes"]:
        positions, lookup, remap = [], {}, []
        for index in range(0, len(original["p"]), 3):
            point = tuple(round(v*1000) for v in original["p"][index:index+3])
            if point not in lookup:
                lookup[point] = len(positions)//3
                positions.extend(point)
            remap.append(lookup[point])
        indices = [remap[v] for v in original["i"]]
        offset_p = len(blob)
        blob.extend(struct.pack(f"<{len(positions)}i", *positions))
        offset_i = len(blob)
        blob.extend(struct.pack(f"<{len(indices)}I", *indices))
        entries.append(dict(name=original["name"], category=original["category"],
                            p=[offset_p, len(positions)], i=[offset_i, len(indices)]))
    header = json.dumps(dict(schema=2, position_scale=1000, meshes=entries,
                             metadata=data["metadata"]), separators=(",", ":")).encode()
    prefix = struct.pack("<I", len(header))+header
    prefix += b"\0"*((-len(prefix)) % 4)
    return gzip.compress(prefix+blob, mtime=0)


def write_pack(data):
    packed = encode(data)
    (HERE/"proposals.bin.gz").write_bytes(packed)
    (HERE/"proposals.b64").write_text(base64.b64encode(packed).decode()+"\n")
    return len(packed)


if __name__ == "__main__":
    data = json.loads(gzip.decompress((HERE/"proposals.json.gz").read_bytes()))
    print(f"{write_pack(data):,} gzip bytes")
