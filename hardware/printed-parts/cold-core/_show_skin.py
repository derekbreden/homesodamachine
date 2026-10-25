"""Smooth cold-core casing surfaces, shared by shell, cups and lids."""

from print_mesh import print_mesh as piece_mesh, write_print_stl


def write_bed_file(solid, path):
    """Write the smooth B-rep surface at the shared absolute print tolerance."""
    mesh = write_print_stl(solid, path)
    print(f'-> {path.name} ({len(mesh.faces)} facets, watertight)')
    return mesh
