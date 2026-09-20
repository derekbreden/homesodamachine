#!/usr/bin/env python3
"""Rigid PP0208E scan registration and independent external-surface readings.

Uses the archived, unscaled five-view PLY. Fits six external root/collar patches
in a common orthogonal frame. An unconstrained branch-axis fit reports how well
that frame agrees with the scan. Internal insertion depth and collet travel are
bench measurements; this script does not estimate them from the scan.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import trimesh
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

DEFAULT_MESH = (Path.home() / 'Documents/3D Scans/2026-09-19-jg-pp0208e-tee/tee-merged5.ply')
EXPECTED_SHA256 = 'c25584adca577ac559a11117579a8c65f0340413d2ddfa3e05e9e4555790942e'
# A coarse rigid alignment identifies the six fitting patches. Refined by the
# numerical fit below; never used to change scale or reshape the scan.
SEED_ORIGIN = np.array([20.335706707395413, -12.622325870675082, 232.23972763161285])
SEED_BASIS = np.array([
    [-.13521516574835776, .9113373376405451, -.38882015890882926],
    [-.881395345937467, -.28989690922950134, -.3729638403102301],
    [-.4526136355783118, .2922739109832164, .8424469466068222],
])
# name, axis index, outward sign, patch near/far, approximate radius
PATCHES = (
    ('run_plus_root', 2, 1, 6.9, 9.8, 6.9),
    ('run_minus_root', 2, -1, 6.9, 9.8, 6.9),
    ('branch_root', 1, 1, 8.7, 11.7, 6.9),
    ('run_plus_collar', 2, 1, 12.0, 15.1, 8.15),
    ('run_minus_collar', 2, -1, 12.0, 15.1, 8.15),
    ('branch_collar', 1, 1, 13.8, 16.6, 8.15),
)


def readings(values):
    values = np.asarray(values)
    return {
        'count': int(len(values)),
        'signed_median_mm': float(np.median(values)),
        'rms_mm': float(np.sqrt(np.mean(values ** 2))),
        'absolute_p95_mm': float(np.quantile(abs(values), .95)),
        'absolute_max_mm': float(np.max(abs(values))),
    }


def fit(mesh_path):
    sha = hashlib.sha256(mesh_path.read_bytes()).hexdigest()
    if sha != EXPECTED_SHA256:
        raise ValueError('This registration names the archived five-view PLY; input digest differs.')
    mesh = trimesh.load(mesh_path, process=False)
    centers = np.asarray(mesh.triangles_center)
    normals = np.asarray(mesh.face_normals)
    areas = np.asarray(mesh.area_faces)
    initial = (centers - SEED_ORIGIN) @ SEED_BASIS
    initial_normals = normals @ SEED_BASIS
    data = []
    for name, axis, sign, near, far, radius in PATCHES:
        t = sign * initial[:, axis]
        radial = np.linalg.norm(np.delete(initial, axis, 1), axis=1)
        mask = ((t > near) & (t < far) & (abs(radial - radius) < .3)
                & (abs(initial_normals[:, axis]) < .35))
        ids = np.flatnonzero(mask)
        weights = np.sqrt(areas[ids] / np.mean(areas[ids]))
        data.append((initial[ids], weights))

    def residuals(parameters, weighted=False):
        matrix = Rotation.from_rotvec(parameters[3:6]).as_matrix()
        values = []
        for i, ((_, axis, sign, near, far, _), (points, weights)) in enumerate(zip(PATCHES, data)):
            q = (points - parameters[:3]) @ matrix
            radius = np.linalg.norm(np.delete(q, axis, 1), axis=1)
            predicted = parameters[6 + 2*i] + parameters[7 + 2*i] * (sign*q[:, axis] - (near+far)/2)
            values.append((radius-predicted) * weights if weighted else radius-predicted)
        return values

    parameters = np.r_[np.zeros(6), np.array([(p[-1], 0.) for p in PATCHES]).ravel()]
    # Alternate triangles are reserved for a validation reading.
    selected = [np.arange(len(points)) % 2 == 0 for points, _ in data]
    for _ in range(3):
        parameters = least_squares(
            lambda p: np.concatenate([r[s] for r, s in zip(residuals(p, True), selected)]),
            parameters, loss='soft_l1', f_scale=.05, xtol=1e-11, ftol=1e-11, gtol=1e-11).x
        selected = [(np.arange(len(r)) % 2 == 0) & (abs(r) < .22) for r in residuals(parameters)]
    basis = SEED_BASIS @ Rotation.from_rotvec(parameters[3:6]).as_matrix()
    origin = SEED_ORIGIN + SEED_BASIS @ parameters[:3]
    transform = np.eye(4)
    transform[:3, :3] = basis.T
    transform[:3, 3] = -basis.T @ origin
    q = (centers-origin) @ basis
    n = normals @ basis
    patch_reports = []
    for i, ((name, axis, sign, near, far, _), (points, _), r) in enumerate(zip(PATCHES, data, residuals(parameters))):
        holdout = np.arange(len(r)) % 2 == 1
        qp = (points-parameters[:3]) @ Rotation.from_rotvec(parameters[3:6]).as_matrix()
        radial = np.delete(qp, axis, 1)
        angle = np.arctan2(radial[:, 1], radial[:, 0])
        counts = np.histogram(angle, bins=36, range=(-np.pi, np.pi))[0]
        patch_reports.append({
            'name': name, 'axis': 'xyz'[axis], 'outward_sign': sign,
            'axial_band_mm': [near, far], 'mid_station_mm': (near+far)/2,
            'diameter_at_mid_station_mm': float(2*parameters[6+2*i]),
            'radius_taper_per_axial_mm': float(parameters[7+2*i]),
            'angular_bins_10_degrees_present': int(np.count_nonzero(counts)),
            'all_selected_surface_residual': readings(r),
            'held_out_surface_residual': readings(r[holdout]),
            'training_points_excluded_over_0_22_mm': int(np.sum((~holdout)&(abs(r)>=.22))),
        })

    # Independently free branch direction and lateral location. The run axis
    # remains the registration's Z; no right-angle constraint enters this fit.
    branch_data=[]
    branch_specs=((8.7,11.7,6.9),(13.8,16.6,8.15))
    radial=np.linalg.norm(q[:,[0,2]],axis=1)
    for near,far,radius in branch_specs:
        mask=(q[:,1]>near)&(q[:,1]<far)&(abs(radial-radius)<.3)&(abs(n[:,1])<.35)
        branch_data.append(q[mask][::3])
    def branch_residual(p):
        matrix=Rotation.from_rotvec([p[2],0.,p[3]]).as_matrix()
        values=[]
        for i, ((near,far,_), points) in enumerate(zip(branch_specs,branch_data)):
            b=(points-np.array([p[0],0.,p[1]]))@matrix
            values.append(np.linalg.norm(b[:,[0,2]],axis=1)-p[4+2*i]-p[5+2*i]*(b[:,1]-(near+far)/2))
        return np.concatenate(values)
    bfit=least_squares(branch_residual,[0.,0.,0.,0.,6.9,0.,8.15,0.],
                       loss='soft_l1',f_scale=.05,xtol=1e-11,ftol=1e-11,gtol=1e-11).x
    branch_direction=Rotation.from_rotvec([bfit[2],0.,bfit[3]]).as_matrix()[:,1]
    # Closest distance between the fitted branch line and the reference run line.
    cross=np.cross(branch_direction,[0.,0.,1.]);cross/=np.linalg.norm(cross)
    line_distance=abs(np.dot([bfit[0],0.,bfit[1]],cross))
    report={
        'part':'John Guest PP0208E', 'mesh_sha256':sha,
        'mesh_archive_path':str(mesh_path), 'vertices':int(len(mesh.vertices)),
        'faces':int(len(mesh.faces)), 'watertight':bool(mesh.is_watertight),
        'frame':{'run_axis':'+/-Z','branch_axis':'+Y','units':'mm','scale':1.0,
                 'origin_in_scan_mm':origin.tolist(),'reference_axes_in_scan_columns':basis.tolist(),
                 'scan_to_reference_column_vector_4x4':transform.tolist(),
                 'rotation_determinant':float(np.linalg.det(basis))},
        'method':{
            'surfaces':'Six root/collar outer-wall patches; radius selection +/-0.3 mm, normal axial component below 0.35.',
            'fit':'Rigid common orthogonal frame; independent linear radial taper for each patch; area-weighted soft-L1 residuals.',
            'validation':'Every other selected triangle held out. Training outliers over 0.22 mm excluded after first robust fit. Reported holdout residuals are untrimmed.',
            'not_measured':['Internal tube stop','Teeth or O-ring geometry','Collet free/pressed state during scan','Manufacturing tolerance','Print fit'],
        },
        'patches':patch_reports,
        'independent_branch_axis':{
            'direction_in_reference':branch_direction.tolist(),
            'offset_at_y_zero_mm':[float(bfit[0]),0.,float(bfit[1])],
            'angle_to_run_degrees':float(np.degrees(np.arccos(branch_direction[2]))),
            'closest_axis_separation_mm':float(line_distance),
            'residual':readings(branch_residual(bfit)),
        },
        'current_journal':{
            'diameter_mm':14.216,'nominal_production_collar_diameter_mm':16.3,
            'radial_interference_before_clearance_mm':(16.3-14.216)/2,
            'scan_sample_outer_envelope_diameter_mm':16.5,
            'note':'The fitted collar is slightly tapered. 16.3 is the documented nominal; 16.5 is a rounded sampled outer envelope, not a production tolerance bound.',
        },
        'bench_authority':{
            'run_span_extended_mm':42.5,'run_span_pressed_mm':39.2,
            'one_sleeve_stroke_mm':1.65,'carrier_nose_gap_mm':.5,
            'tube_insertion_from_pressed_sleeve_face_mm':10.,
        },
        'open_interfaces':['Absolute fully extended branch sleeve face station pending caliper width.',
                           'Release sleeve/collar edge details must remain explicit when constructing the moving sleeve.'],
    }
    return mesh, q, n, report


def render_profiles(points, report, output):
    """Show the fitted patches beside the registered surface and unresolved noses."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True, sharey=True)
    rows = ((2, 1, '+Z run', 'run_plus'),
            (2, -1, '−Z run', 'run_minus'),
            (1, 1, '+Y branch', 'branch'))
    for ax, (axis, sign, label, prefix) in zip(axes, rows):
        station = sign * points[:, axis]
        radius = np.linalg.norm(np.delete(points, axis, 1), axis=1)
        selected = ((station > 0) & (station < 23) & (radius > 3) & (radius < 9))
        selected &= points[:, 1] < -1 if axis == 2 else abs(points[:, 2]) < 5
        ax.scatter(station[selected][::5], radius[selected][::5], s=1.1,
                   c='#74868c', alpha=.45, rasterized=True)
        for patch in (p for p in report['patches'] if p['name'].startswith(prefix)):
            near, far = patch['axial_band_mm']
            stations = np.array([near, far])
            radii = (patch['diameter_at_mid_station_mm'] / 2
                     + (stations - patch['mid_station_mm'])
                     * patch['radius_taper_per_axial_mm'])
            ax.axvspan(near, far, color='#1696b0', alpha=.08)
            ax.plot(stations, radii, color='#056d84', lw=2.5)
            ax.text((near + far) / 2, radii.mean() + .37,
                    f"Ø{patch['diameter_at_mid_station_mm']:.2f} at midpoint",
                    ha='center', fontsize=10, color='#00586d')
        nose = 17.8 if axis == 2 else 19.3
        ax.axvspan(nose, 23, color='#bf7d27', alpha=.08)
        ax.text(21.7 if axis == 2 else 21.1, 8.5,
                'small barrel + collet\nstate / seam unqualified',
                ha='center', va='top', fontsize=9, color='#785017')
        ax.set_ylabel(label + '\nradius [mm]', fontsize=11)
        ax.grid(alpha=.18)
        ax.set_xlim(0, 23)
        ax.set_ylim(3, 9)
    axes[-1].set_xlabel(
        'Outward station from registered run/branch axis intersection [mm]', fontsize=11)
    fig.suptitle('PP0208E — scan registered without scaling', fontsize=17,
                 fontweight='bold', y=.993)
    fig.text(.5, .01,
             'Blue lines fit six fixed outer-wall patches. Grey points include molded '
             'transitions, thin rims and reconstruction artifacts.\n'
             'Residuals are agreement with this scan; they are not manufacturing or print tolerances.',
             ha='center', fontsize=10, color='#40545e')
    fig.tight_layout(rect=[0, .055, 1, .97])
    fig.savefig(output)
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mesh',type=Path,default=DEFAULT_MESH)
    parser.add_argument('--output',type=Path,default=Path(__file__).with_name('scan-registration.json'))
    args=parser.parse_args()
    _,points,_,report=fit(args.mesh)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    render_profiles(points, report, args.output.with_name('scan-profiles.svg'))
    print(f'Wrote {args.output}')
    for patch in report['patches']:
        print(f"{patch['name']}: diameter {patch['diameter_at_mid_station_mm']:.3f} mm; "
              f"held-out absolute p95 {patch['held_out_surface_residual']['absolute_p95_mm']:.3f} mm")
    print('Independent branch angle:',report['independent_branch_axis']['angle_to_run_degrees'])

if __name__=='__main__':
    main()
