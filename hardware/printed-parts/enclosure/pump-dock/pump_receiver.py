"""Permanent wall-supported TPU 85A pump-cartridge receiver.

Local +Y enters the enclosure; Y=0 is the PET-GF wall's pump-facing surface.
The closed wall locates X/Z. A flat interior keeper in the rear groove
retains Y. The two tube sockets use radial interference; the cartridge hard
stop sets insertion and leaves its tube tip clear of the annular stop.

The Ø6.10 bore and 2.8 mm minimum radial cuff wall follow the manually fitted
TPU elbow article. Six-millimetre lands, wall confinement, permanent service,
pressure holding and endurance are unqualified on this geometry. Printing
with the bore vertical keeps both sealing lands accessible and support-free;
the rear collar's nonwetted flat underside needs removable external support.
"""
from pathlib import Path
import argparse
import json
import math
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
HARDWARE = next(p for p in HERE.parents if p.name == "hardware")
sys.path.insert(0, str(HARDWARE / "scripts"))

# Shared mechanical contract, all axial stations measured from the wall fore face.
WALL_THICKNESS = 7.0
TUBE_OD = 6.35
TUBE_ID = 4.30
SEAL_BORE_D = 6.10
BODY_OD = 11.70
WALL_BORE_D = 12.00
WALL_RADIAL_CLEARANCE = (WALL_BORE_D - BODY_OD) / 2
FRONT_LIP_OD = 14.0
FRONT_COUNTERBORE_D = 14.3
FRONT_LIP_Y = (0.0, 0.6)
FUNNEL_BORE_D = 9.0
FRONT_SEAL_Y = (1.0, 7.0)
FRONT_RELIEF_D = 6.8
CUSTOMER_TIP_Y = 7.5
CUSTOMER_STOP_Y = 8.0
FACTORY_TIP_Y = 9.0
REAR_END_Y = 15.0
REAR_SEAL_Y = (FACTORY_TIP_Y, REAR_END_Y)
COLLAR_OD = 17.5
COLLAR_RAMP_Y = (4.0, 6.9)
FRONT_COLLAR_Y = (6.9, 7.0)
GROOVE_Y = (7.0, 10.35)
REAR_COLLAR_Y = (10.35, 11.85)
KEEPER_SLOT_D = 12.4
KEEPER_RADIAL_CLEARANCE = (KEEPER_SLOT_D - BODY_OD) / 2
KEEPER_Y = (7.0, 10.0)
KEEPER_THICKNESS = KEEPER_Y[1] - KEEPER_Y[0]
REAR_SUPPORT_Y = (REAR_COLLAR_Y[1], REAR_END_Y)
MATERIAL = "Siraya Tech Flex TPU 85A Clear"
# Clear stock, rather than the black Bambu 90A gasket stock.
COLOR = cq.Color(.92, .92, .90, .60)
_EPS = 0.02


def _cylinder(diameter, y0, y1):
    return cq.Solid.makeCylinder(diameter / 2, y1 - y0,
                                 cq.Vector(0, y0, 0), cq.Vector(0, 1, 0))


def _cone(d0, d1, y0, y1):
    return cq.Solid.makeCone(d0 / 2, d1 / 2, y1 - y0,
                             cq.Vector(0, y0, 0), cq.Vector(0, 1, 0))


def _outside(installed=False):
    # Conserved annular area supplies a conservative occupied envelope only.
    # It is not an elastic-deformation or contact-pressure prediction.
    growth = TUBE_OD ** 2 - SEAL_BORE_D ** 2 if installed else 0.0
    od = lambda diameter: math.sqrt(diameter ** 2 + growth)
    return (_cylinder(od(BODY_OD), FRONT_LIP_Y[0], REAR_END_Y)
            .fuse(_cylinder(od(FRONT_LIP_OD), *FRONT_LIP_Y))
            .fuse(_cone(od(BODY_OD), od(COLLAR_OD), *COLLAR_RAMP_Y))
            .fuse(_cylinder(od(COLLAR_OD), *FRONT_COLLAR_Y))
            .fuse(_cylinder(od(COLLAR_OD), *REAR_COLLAR_Y)).clean())


def _place(shape, wall_fore_y=0.0, x=0.0, z=0.0):
    return shape.translate((x, wall_fore_y, z))


def build_receiver(wall_fore_y=0.0, x=0.0, z=0.0, *, installed=False):
    """One-piece wet solid, relaxed for manufacture or expanded for assembly.

    ``installed`` opens the tight sockets to nominal tube OD and expands the
    outside by conserved annular area, avoiding artificial tube/CAD clashes.
    It supplies occupied geometry and no prediction of seal stress.
    """
    seal_d = TUBE_OD if installed else SEAL_BORE_D
    bores = (_cone(FUNNEL_BORE_D, seal_d, 0.0, FRONT_SEAL_Y[0])
             .fuse(_cylinder(FUNNEL_BORE_D, -_EPS, 0.0))
             .fuse(_cylinder(seal_d, *FRONT_SEAL_Y))
             .fuse(_cylinder(FRONT_RELIEF_D, FRONT_SEAL_Y[1], CUSTOMER_STOP_Y))
             .fuse(_cylinder(TUBE_ID, CUSTOMER_STOP_Y, FACTORY_TIP_Y))
             .fuse(_cylinder(seal_d, *REAR_SEAL_Y))
             .fuse(_cylinder(seal_d, REAR_END_Y, REAR_END_Y + _EPS)))
    return _place(_outside(installed).cut(bores).clean(), wall_fore_y, x, z)


def receiver_envelope(wall_fore_y=0.0, x=0.0, z=0.0, *, installed=False):
    """Nominal occupied envelope, without its internal fluid bore."""
    return _place(_outside(installed), wall_fore_y, x, z)


def receiver_wall_cut(wall_fore_y=0.0, x=0.0, z=0.0):
    """Closed-bore wall tool including front lip and recessed collar seats.

    This only cuts Y=0..7; keeper guides and rear cuff support belong to the
    enclosure. The collar recess carries the same 0.15 mm normal radial room
    as the supported cylindrical cuff. Its ramp allows the TPU to be pressed
    from the interior while flexing the small front lip through the bore.
    """
    tool = (_cylinder(WALL_BORE_D, -_EPS, WALL_THICKNESS + _EPS)
            .fuse(_cylinder(FRONT_COUNTERBORE_D, -_EPS, FRONT_LIP_Y[1]))
            .fuse(_cone(WALL_BORE_D, COLLAR_OD + 2 * WALL_RADIAL_CLEARANCE,
                        *COLLAR_RAMP_Y))
            .fuse(_cylinder(COLLAR_OD + 2 * WALL_RADIAL_CLEARANCE,
                            FRONT_COLLAR_Y[0], WALL_THICKNESS + _EPS)))
    return _place(tool.clean(), wall_fore_y, x, z)


def rear_support_cut(wall_fore_y=0.0, x=0.0, z=0.0):
    """Circular support cavity around the permanent rear tube cuff."""
    return _place(_cylinder(WALL_BORE_D, REAR_SUPPORT_Y[0] - _EPS,
                            REAR_SUPPORT_Y[1] + _EPS), wall_fore_y, x, z)


def wet_stations(wall_fore_y=0.0, x=0.0, z=0.0):
    def point(y):
        return (float(x), float(wall_fore_y + y), float(z))
    return {
        "axis": (0.0, 1.0, 0.0),
        "customer_tip": point(CUSTOMER_TIP_Y),
        "customer_stop": point(CUSTOMER_STOP_Y),
        "factory_tip": point(FACTORY_TIP_Y),
        "rear_mouth": point(REAR_END_Y),
        "front_seal": tuple(point(y) for y in FRONT_SEAL_Y),
        "rear_seal": tuple(point(y) for y in REAR_SEAL_Y),
    }


def print_solid():
    """Funnel ring on the bed, fluid bore along +Z."""
    return build_receiver().rotate((0, 0, 0), (1, 0, 0), 90)


def engineering_record():
    """Dimensions and geometric load cases; no inferred seal/array ratings."""
    bore_area = math.pi * TUBE_OD ** 2 / 4
    return {
        "material": MATERIAL,
        "wall_thickness_mm": WALL_THICKNESS,
        "front_seal_bore_mm": SEAL_BORE_D,
        "front_seal_land_mm": FRONT_SEAL_Y[1] - FRONT_SEAL_Y[0],
        "rear_seal_land_mm": REAR_SEAL_Y[1] - REAR_SEAL_Y[0],
        "relaxed_cuff_od_mm": BODY_OD,
        "wall_radial_room_mm": WALL_RADIAL_CLEARANCE,
        "keeper_radial_room_mm": KEEPER_RADIAL_CLEARANCE,
        "keeper_thickness_mm": KEEPER_THICKNESS,
        "keeper_axial_station_mm": list(KEEPER_Y),
        "keeper_wall_face_gap_mm": KEEPER_Y[0] - WALL_THICKNESS,
        "keeper_rear_groove_room_mm": GROOVE_Y[1] - KEEPER_Y[1],
        "tube_tip_clearance_to_stop_mm": CUSTOMER_STOP_Y - CUSTOMER_TIP_Y,
        "nominal_annular_area_expanded_od_mm": math.sqrt(
            BODY_OD ** 2 + TUBE_OD ** 2 - SEAL_BORE_D ** 2),
        "local_wet_stations_mm": wet_stations(),
        "projected_od_load_cases": [
            {"pressure_psi": psi, "per_port_n": psi * .006894757293168 * bore_area,
             "two_ports_n": 2 * psi * .006894757293168 * bore_area,
             "four_ports_n": 4 * psi * .006894757293168 * bore_area}
            for psi in (10, 30, 80)],
        "scope": "Nominal geometry and separating-load cases; no physical seal, retention or lifetime rating.",
        "print_orientation": "Funnel ring on bed; bore vertical; no support in fluid passage.",
        "external_support": "Rear collar pump-facing flat underside only; remove before factory assembly.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE.parent / "enclosure")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    from _cadq_export import export_assembly
    from _material_base import one_body
    import flute_payload
    shape = build_receiver()
    stem = args.out / "enclosure-pump-receiver"
    cq.exporters.export(shape, str(stem.with_suffix(".stl")),
                        tolerance=.015, angularTolerance=.06)
    export_assembly(one_body(shape, "enclosure-pump-receiver", COLOR),
                    str(stem.with_suffix(".step")))
    flute_payload.cut(stem.with_suffix(".step"), stem.with_suffix(".stl"),
                       preserve_print_triangles=True)
    (HERE / "pump-receiver.json").write_text(
        json.dumps(engineering_record(), indent=2) + "\n")
    print(f"{stem}: {shape.Volume():.1f} mm³, {len(shape.Solids())} solid")


if __name__ == "__main__":
    main()
