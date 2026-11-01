"""The viewer payload's format, print shading and stated deflection rule."""

VERSION = 3
LINEAR_DEFLECTION_RATIO = 0.001
CREASE_DEG = 30.0


def print_payload_rules() -> dict:
    """The print surface's rules, written with a Rust part's geometry numbers."""
    return {
        "deflection_ratio": LINEAR_DEFLECTION_RATIO,
        "crease_deg": CREASE_DEG,
    }
