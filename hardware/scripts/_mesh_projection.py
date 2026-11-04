"""Python array/path compatibility for Rust's fine-model visible outlines."""
from _build_data import read, request


def visible_edges(vertices, triangles, normal, right, *, sharp_degrees=30.0, join_planes=()):
    return request("visible-edges", vertices=vertices.tolist() if hasattr(vertices, "tolist") else vertices,
                   triangles=triangles.tolist() if hasattr(triangles, "tolist") else triangles,
                   normal=list(normal), right=list(right), sharp_degrees=sharp_degrees,
                   join_planes=join_planes)


def _paths(edges, simplify):
    return request("paths", edges=edges, simplify=simplify)


def model_outlines(path, normal, right, *, simplify=0.0025, join_planes=()):
    return read("model-outlines", path, normal=list(normal), right=list(right),
                simplify=simplify, join_planes=join_planes)
