"""Small synthetic checks for feature identity and incomplete-coverage rejection."""
import numpy as np

from analyze_scan import fit_slot, port_profiles


def run():
    # A dense internal bore shares every axial station with the exterior. Its
    # inward normals must keep it out of the outer-barb dimensional fit.
    points, normals = [], []
    for station in np.arange(23.125, 38.0, .25):
        for radius, sign in ((5., 1.), (3., -1.)):
            for angle in np.linspace(0, 2*np.pi, 144, endpoint=False):
                cosine, sine = np.cos(angle), np.sin(angle)
                points.append([-69+radius*cosine, station, 26.9+radius*sine])
                normals.append([sign*cosine, 0., sign*sine])
    ports = port_profiles(np.array(points), np.array(normals))
    assert ports[0]['axis'] is None
    assert ports[1]['axis'] is not None
    assert np.allclose(ports[1]['axis']['outward_direction'], [0, 1, 0], atol=1e-7)
    assert all(abs(row['radius_mm']-5) < 1e-7 for row in ports[1]['profiles'])

    # A complete 4 by 7 obround supports its dimensions. An accurately fitted
    # single flank must still be marked partial rather than promoted to a bore.
    angle = np.linspace(0, 2*np.pi, 720, endpoint=False)
    points = np.column_stack((2*np.cos(angle),
                              2*np.sin(angle)+1.5*np.sign(np.sin(angle))))
    full = fit_slot(points, [0, 0])
    assert full['status'] == 'complete_section_observed'
    assert abs(full['width_mm']-4) < 1e-6
    assert abs(full['total_length_mm']-7) < 1e-6
    partial = fit_slot(points[points[:, 0] > 1.5], [0, 0])
    assert partial['status'] == 'partial_profile_only'
    print('External barb excludes the bore; partial slot wall cannot qualify a full opening.')


if __name__ == '__main__':
    run()
