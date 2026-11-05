"""Four blind sockets locating a Beduan valve on a printed face.

`build_sockets` supplies the cuts for the enclosure's valve trays. `build_seat`
supplies a raised plinth for the cold-core lid: one rectangular body with rounded
corners, four sockets and an open cylindrical port channel. The valve's round body
lands on the broad top faces beside that channel.

Geometry is in the valve's frame, with its mounting plane at Z0 and port axis on Y.
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hardware = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hardware / 'scripts'))
sys.path.insert(0, str(_hardware / "reference" / "beduan-solenoid"))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

sys.path.insert(0, str(_hardware / "printed-parts" / "cadlib"))
import fits
import beduan_solenoid as valve


from _rust_data import request as _request


def _data(**payload):
    return _request('part-data', 'part-data', {'part': 'valve-seat',
        'corner_inset_x': valve.corner_inset_x, 'corner_inset_y': valve.corner_inset_y,
        'corner_post_radius': valve.corner_boss_radius, 'seat_top_z': valve.boss_z_range[0],
        'port_radius': valve.port_radius, 'port_center_z': valve.port_center_z,
        'slip': fits.slip, **payload})


globals().update(_data()['values'])


def socket_depth():
    return _data(method='socket_depth')


def build_sockets():
    """Four blind socket cuts in the valve frame, opening at its bearing plane."""
    import cadquery as cq
    sockets = None
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            socket = (
                cq.Workplane("XY")
                .workplane(offset=socket_floor_z)
                .center(sx * corner_inset_x, sy * corner_inset_y)
                .circle(socket_radius)
                .extrude(seat_top_z - socket_floor_z + 1.0)
            )
            sockets = socket if sockets is None else sockets.union(socket)
    return sockets


def build_seat(seat):
    """A plinth from Z=-seat to the valve's bearing plane, with four blind sockets."""
    import cadquery as cq
    assert seat >= -socket_floor_z - 1e-9, (
        f"seat {seat:g} leaves the socket floor below the supporting face")
    solid = (cq.Workplane("XY").workplane(offset=-seat)
             .rect(2.0 * seat_half_x, 2.0 * seat_half_y)
             .extrude(seat + seat_top_z)
             .edges("|Z").fillet(seat_corner_radius))
    return solid.cut(build_sockets()).cut(build_port_channel(2.0 * seat_half_y + 2.0))


def build_port_channel(length):
    """The valve barrel's circular clearance, open through both Y faces."""
    import cadquery as cq
    return (cq.Workplane("XZ").center(0.0, valve.port_center_z)
            .circle(valve.port_radius + port_air).extrude(length / 2.0, both=True))


def seat_volume(seat):
    """Rounded stock less sockets and the analytic circular port segment."""
    return _data(method='volume', seat=seat)


def _distance(a, b):
    return a.distance(b)


def port_clearance():
    """The distance from the finished plinth to the valve's port barrel."""
    return _distance(build_seat(-socket_floor_z).val(), valve.build_port().val())


def _port_clearance_from_dimensions():
    return _data(method='port_clearance')


def main():
    result = _data(method='main')
    print(result['report'])


if __name__ == "__main__":
    main()


def __getattr__(name):
    if name == "cq":
        import cadquery
        return cadquery
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
