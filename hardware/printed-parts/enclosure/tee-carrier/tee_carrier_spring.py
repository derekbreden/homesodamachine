"""Measured envelope of the delivered carrier springs; no wire or load model.

The direct measurements in spring-measurements.json control this sample's fit.
The displayed cylinder is occupied clearance, not spring material. Its volume
must not be used for mass, stiffness, stored energy or force calculations.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


MEASUREMENT_FILE = Path(__file__).with_name('spring-measurements.json')
_measurement_bytes = MEASUREMENT_FILE.read_bytes()
MEASUREMENTS = json.loads(_measurement_bytes)
OUTSIDE_DIAMETER = float(MEASUREMENTS['outside_diameter_mm'])
FREE_LENGTH = float(MEASUREMENTS['free_length_mm'])
COMPRESSED_LENGTH_UPPER_ESTIMATE = float(
    MEASUREMENTS['compressed_length_upper_estimate_mm'])
if (not all(math.isfinite(value) and value > 0.0 for value in
            (OUTSIDE_DIAMETER, FREE_LENGTH, COMPRESSED_LENGTH_UPPER_ESTIMATE))
        or COMPRESSED_LENGTH_UPPER_ESTIMATE >= FREE_LENGTH):
    raise ValueError('carrier spring measurements do not define a positive working interval')

ENVELOPE_METADATA = {
    'representation': 'measured spring clearance envelope',
    'use': 'fit and collision checks only',
    'material_volume_mm3': None,
    'mass_g': None,
    'force_model': None,
}


def check_length(length: float) -> None:
    """A compressed sample stays above its estimated solid limit and below free length."""
    if (not math.isfinite(length)
            or not COMPRESSED_LENGTH_UPPER_ESTIMATE < length < FREE_LENGTH):
        raise ValueError(
            f'carrier spring length {length:g} mm is outside the measured working '
            f'interval ({COMPRESSED_LENGTH_UPPER_ESTIMATE:g}, {FREE_LENGTH:g}) mm')


def fit_facts(bearing_lengths: dict[str, float], *, bore_diameter: float,
              loading_length: float, required_radial_air: float) -> dict:
    """Sample envelope checks and provenance, with unmeasured forces kept unknown."""
    if not bearing_lengths:
        raise ValueError('carrier spring has no installed bearing lengths')
    for length in (*bearing_lengths.values(), loading_length):
        check_length(length)
    radial_air = (bore_diameter - OUTSIDE_DIAMETER) / 2.0
    if (not math.isfinite(radial_air) or not math.isfinite(required_radial_air)
            or required_radial_air < 0 or radial_air <= 0
            or radial_air < required_radial_air - 1e-9):
        raise ValueError('carrier spring lacks the required radial air in its printed guide')
    return {
        'spring_bearing_lengths': dict(bearing_lengths),
        'spring_pair_forces_n': dict.fromkeys(bearing_lengths),
        'spring_rate_n_per_mm': MEASUREMENTS['rate_n_per_mm'],
        'spring_force_status': MEASUREMENTS['measured_force_note'],
        'spring_sample': MEASUREMENTS['part'],
        'spring_measurement_source': {
            'path': 'hardware/printed-parts/enclosure/tee-carrier/spring-measurements.json',
            'sha256': hashlib.sha256(_measurement_bytes).hexdigest(),
            'authority': MEASUREMENTS['authority'],
            'recorded_date': MEASUREMENTS['recorded_date'],
        },
        'spring_od': OUTSIDE_DIAMETER,
        'spring_free_length': FREE_LENGTH,
        'spring_compressed_length_upper_estimate': COMPRESSED_LENGTH_UPPER_ESTIMATE,
        'spring_wire_diameter': MEASUREMENTS['wire_diameter_mm'],
        'spring_inside_diameter': None,
        'spring_manufacturing_tolerances': MEASUREMENTS['manufacturing_tolerances'],
        'spring_clearance_d': OUTSIDE_DIAMETER,
        'spring_clearance_basis': 'measured sample OD; manufacturing tolerance unmeasured',
        'spring_radial_air_in_bore': round(radial_air, 6),
        'spring_required_radial_air': required_radial_air,
        'spring_compression_from_free': {
            state: round(FREE_LENGTH - length, 6) for state, length in bearing_lengths.items()},
        'spring_clearance_above_compressed_estimate': {
            state: round(length - COMPRESSED_LENGTH_UPPER_ESTIMATE, 6)
            for state, length in bearing_lengths.items()},
        'spring_loading_clearance_above_compressed_estimate': round(
            loading_length - COMPRESSED_LENGTH_UPPER_ESTIMATE, 6),
        'spring_representation': dict(ENVELOPE_METADATA),
    }


def build_envelope(installed_length: float):
    """A clearance-only cylinder from z=0 to the installed bearing separation."""
    import cadquery as cq

    check_length(installed_length)
    return cq.Solid.makeCylinder(OUTSIDE_DIAMETER / 2.0, installed_length)
