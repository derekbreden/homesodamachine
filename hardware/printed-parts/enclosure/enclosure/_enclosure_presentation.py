"""Dispatch the enclosure's printed viewer surfaces to its Rust writer."""


def print_payload(step, *, check_print=False):
    """Keep the caller's print-check policy and return the Rust writer's readings."""
    from _rust_enclosure_presentation import print_payload as write
    return write(step, check_print=check_print)
