"""Split existing mesh facets for a precise seam-enforcer strip, without moving the surface."""

import numpy as np


def _half(polygon, axis, coordinate, sign):
    result = []
    previous = polygon[-1]
    previous_in = sign * (previous[axis] - coordinate) >= -1e-10
    for current in polygon:
        current_in = sign * (current[axis] - coordinate) >= -1e-10
        if current_in != previous_in:
            fraction = (coordinate - previous[axis]) / (current[axis] - previous[axis])
            point = previous + fraction * (current - previous)
            point[axis] = coordinate
            result.append(point)
        if current_in:
            result.append(current)
        previous, previous_in = current, current_in
    return result


def strip(vertices, faces, declaration):
    """A native-coordinate strip on one exterior plane; return mesh, paint and measurements."""
    original = vertices[faces]
    triangles = original.copy()
    parents = np.arange(len(faces))
    axis = "xyz".index(declaration["axis"])
    center = declaration["center_mm"]
    half_width = declaration["half_width_mm"]
    for coordinate in (center-half_width, center+half_width):
        result, ids = [], []
        for triangle, parent in zip(triangles, parents):
            if triangle[:, axis].min() >= coordinate-1e-10 or triangle[:, axis].max() <= coordinate+1e-10:
                result.append(triangle)
                ids.append(parent)
                continue
            for sign in (-1, 1):
                polygon = _half(triangle, axis, coordinate, sign)
                for i in range(1, len(polygon)-1):
                    child = np.array([polygon[0], polygon[i], polygon[i+1]])
                    if np.linalg.norm(np.cross(child[1]-child[0], child[2]-child[0])) > 1e-10:
                        result.append(child)
                        ids.append(parent)
        triangles, parents = np.array(result), np.array(ids)
    points, inverse = np.unique(np.round(triangles.reshape(-1, 3), 9), axis=0, return_inverse=True)
    split_faces = inverse.reshape(-1, 3)
    triangles = points[split_faces]
    face_axis = "xyz".index(declaration["face_axis"])
    plane = declaration["face_coordinate_mm"]
    normals = np.cross(triangles[:, 1]-triangles[:, 0], triangles[:, 2]-triangles[:, 0])
    norms = np.linalg.norm(normals, axis=1)
    selected = ((np.abs(triangles[:, :, face_axis]-plane).max(axis=1) < .001)
                & (triangles[:, :, axis].min(axis=1) >= center-half_width-1e-8)
                & (triangles[:, :, axis].max(axis=1) <= center+half_width+1e-8)
                & (normals[:, face_axis]*declaration["face_sign"] > .99*norms))
    source_normals = np.cross(original[:, 1]-original[:, 0], original[:, 2]-original[:, 0])
    source_lengths = np.linalg.norm(source_normals, axis=1)
    source_unit = source_normals/source_lengths[:, None]
    errors = np.abs(np.einsum("ijk,ik->ij", triangles-original[parents, :1], source_unit[parents]))
    area = np.zeros(len(original))
    np.add.at(area, parents, norms/2)
    record = {**declaration, "source_facets": len(faces), "project_facets": len(split_faces),
              "painted_facets": int(selected.sum()), "maximum_source_plane_error_mm": float(errors.max()),
              "maximum_source_facet_area_error_mm2": float(np.max(np.abs(area-source_lengths/2)))}
    if not selected.any():
        raise ValueError(f"seam strip misses the declared exterior plane: {declaration}")
    return points, split_faces, [{"paint_seam": "4"} if on else None for on in selected], record
