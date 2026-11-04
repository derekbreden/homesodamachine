"""Scan-fitted neoFit ACVUS44 1/4-inch stem check, HSM-000383.

+X runs from the free stem tip at X0 to the socket mouth. The frozen model
retains the measured turned exterior; its bore and socket are display closures.
The native archive and physical selections are recorded in scan-evidence.json.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
STEP_PATH = HERE / 'neofit-acvus44-check.step'
PAYLOAD_PATH = HERE / 'neofit-acvus44-check.step.mesh'
ASSET_MANIFEST_PATH = HERE / 'frozen-asset.json'

STEM_D = 6.35
PROFILE = ((0.0, 2.83062),
 (0.27949, 3.15484),
 (0.40449, 3.175),
 (0.90449, 3.175),
 (7.77949, 3.175),
 (8.15449, 3.16232),
 (8.52949, 3.00886),
 (8.77949, 2.99506),
 (10.02949, 3.175),
 (17.0, 3.175),
 (17.65449, 3.23247),
 (17.90449, 3.38674),
 (18.02949, 3.56799),
 (18.15449, 6.16171),
 (18.40449, 6.54923),
 (18.52949, 7.69027),
 (18.65449, 7.85511),
 (19.02949, 7.96635),
 (24.40449, 7.95844),
 (24.77949, 7.88006),
 (24.90449, 7.80932),
 (25.02949, 7.64961),
 (25.15449, 7.38235),
 (25.27949, 5.12092),
 (25.65449, 4.88934),
 (31.52949, 4.87047),
 (33.52949, 4.9357),
 (35.02949, 4.90125),
 (35.27949, 5.0098),
 (35.52949, 5.24616),
 (35.65449, 5.53062),
 (35.77949, 5.95805),
 (35.90449, 6.14981),
 (36.40449, 6.67839),
 (36.65449, 6.87179),
 (37.15449, 6.9992),
 (39.77949, 7.05706),
 (40.02949, 7.16171),
 (40.40449, 7.46785),
 (40.77949, 7.5948),
 (41.15449, 7.63918),
 (44.77949, 7.71604),
 (45.27949, 7.58796),
 (45.77949, 7.22239),
 (46.90449, 7.24716),
 (47.40449, 7.20526),
 (47.65449, 7.1137),
 (47.77949, 7.0014),
 (47.90449, 6.85042),
 (48.15449, 6.31601),
 (48.52949, 6.2125),
 (48.90449, 6.27323),
 (49.02949, 5.16382),
 (49.15449, 5.16382),
 (49.27949, 5.29114),
 (49.40449, 6.46237),
 (49.52949, 6.55167),
 (50.02949, 6.79878),
 (50.40449, 6.79541),
 (50.65449, 6.73775),
 (50.90449, 6.53016),
 (51.091994723978004, 6.45353))
LENGTH = PROFILE[-1][0]
SHOULDER = 18.20643880297786
INSERTION = 16.891
SOCKET_D = 6.50
BORE_D = 4.30


def stem_tip():
    return (0., 0., 0.), (-1., 0., 0.)


def tube_port():
    return (LENGTH, 0., 0.), (1., 0., 0.)


def main():
    import json
    sys.path.insert(0, str(HERE.parents[1] / 'scripts'))
    import _rust_part
    _rust_part.start()
    from _materials import M_NEOFIT_WHITE_ACETAL, linear
    parameters = json.loads((HERE / 'reference-parameters.json').read_text())
    _rust_part.cut('tooling', 'stem-check-reference',
                   {**parameters, 'color': linear(M_NEOFIT_WHITE_ACETAL)}, HERE)


if __name__ == '__main__':
    main()
