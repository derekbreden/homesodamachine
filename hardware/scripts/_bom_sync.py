"""Doc-sync driver for hardware/ledger/bom.md.

Run: tools/cad-venv/bin/python hardware/scripts/_bom_sync.py
Use --only-bom to update the BOM without rewriting the labor ledger.
"""

import argparse
import json
import sys
from decimal import Decimal, ROUND_CEILING, ROUND_HALF_UP
from pathlib import Path

_here = Path(__file__).resolve().parent  # = hardware/scripts/
sys.path.insert(0, str(_here.parent / "printed-parts" / "cadlib"))
sys.path.insert(0, str(_here.parent / "printed-parts" / "cold-core"))
sys.path.insert(0, str(_here.parent / "printed-parts" / "cold-core" / "reservoir"))
sys.path.insert(0, str(_here.parent / "printed-parts" / "faucet"))
sys.path.insert(0, str(_here.parent / "printed-parts" / "faucet" / "faucet-shell"))
sys.path.insert(0, str(_here.parent / "reference" / "beduan-solenoid"))
sys.path.insert(0, str(_here.parent / "manifold-layout"))
sys.path.insert(0, str(_here.parent / "printed-parts" / "enclosure" / "pump-dock"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

from _cold_core_interface import (attachment_xy_positions, cap_anchors,
                                  cap_cradles, deck_mounts,
                                  deck_mount_xy, deck_mount_reach, deck_mount_bore_depth)
from _reed_channels import reeds_per_reservoir
from docgen import load_module, substitute_md
from _funnel_casting import casting_estimate, figures as _casting_figures
from reservoir import insert_positions_for_side_plus_1
from faucet_shell import base_pod_centers

import manifold_layout as ml
import _facts
import enclosure_assembly as _ea  # noqa: F401  — holds the closure these docs watch
import ground_ring_stack as _gnd  # on the path once `enclosure_assembly` is imported
import enclosure as _enc  # likewise
import _box_spec
import _fixed_pump_mount
from materialize_pump_cartridge import _declared_box
import digiten_flow_sensor as _digiten  # likewise — the arm the meter's anchors bore for
import iec_c14_inlet as _c14  # likewise — the inlet whose flange the +Y wall's tunnel bores for
import meanwell_irm90 as _psu  # the west-wall supply and its mounting ears
import teyleten_relay as _relay  # likewise
import pcba_tray as _pcba  # likewise
import _above_core_shell as _selected_shell
import _above_core_mounts as _selected_cap
import _reservoir_a_anchors
import above_core as _above_core
import above_core_wiring as _above_core_wiring
import above_core_bom as _above_core_bom

# The placed pack, for the counts that are the machine's rather than a part's — off the
# artifact the last build wrote, so this driver stands no appliance to count bosses.
_f = _facts.read()
_placed = set(_f.pack["placed"])
_floor_bosses = _f.box["floor_bosses"]
_cond_bosses = _f.box["cond_mount"][3] if _f.box["cond_mount"] else ()


# Fixed solid-copper cuts: AC-1 has three conductors, AC-2 two, AC-3 one,
# DC-1 two, DC-2 one and DC-4 two. Allocate in 0.1 m increments.
_wire_schedule = load_module(
    "bom_wire_schedule", _here.parent / "wiring" / "_ac_wiring_schedule_sync.py")
# AC-1's three conductors and DC-4's two, AC-2's pair, AC-3, DC-1's pair, DC-2, and the
# relay 1 NO and N-block pigtails to AC-4/AC-5's joins under the funnel opening.
solid16_cut_m = Decimal(str(
    5 * _wire_schedule.len_mid_mm + 2 * _wire_schedule.len_short_2_mm
    + _wire_schedule.len_short_mm + 2 * _wire_schedule.len_dc1_mm
    + _wire_schedule.len_dc2_mm + 2 * _wire_schedule.len_opening_join_mm)) / 1000
solid16_allocation_m = (solid16_cut_m * 10).to_integral_value(
    rounding=ROUND_CEILING) / 10


# Evaporator-coil copper consumption (§5 GOORY row) — pitch and wrap arc
# from the coil-mandrel generator, whose printed groove enforces them.
_coil_mandrel_gen = load_module(
    "bom_coil_mandrel_gen",
    _here.parent / "printed-parts" / "cold-core" / "coil-mandrel" / "coil_mandrel.py",
)

# The evaporator wrap AS DRAWN ON THE CARBONATOR (§5) — `coil_mandrel` strikes the helix, and
# `cold-core-layout/_coil` is where it is actually laid: sprung out to the carbonator's own radius
# and lifted again over the reed bridge it crosses. That is the copper a build consumes, so it
# is what the row bills; the mandrel's two shorter figures stay beside it in its own module.
_coil_gen = load_module(
    "bom_coil_gen", _here.parent / "cold-core-layout" / "_coil.py")
_wrap_mm = _coil_gen.wrap_length()
_cut_mm = _coil_gen.cut_length()
_roll_spare_ft = _coil_gen.roll_spare_ft()

# The PRV vent line (§2), read off the run `_internal_routes` draws down the port lane rather
# than restated: the row bills the stock that line is cut from.
_routes_gen = load_module(
    "bom_internal_routes_gen",
    _here.parent / "printed-parts" / "cold-core" / "_internal_routes.py",
)
_prv_vent_mm = _routes_gen.route_wire(
    _routes_gen.routes["prv-vent"], _routes_gen.route_bend_radius).Length()

# The continuous black 4 mm flavor runs and finish-matched 3/8" soda tube (§9). The cut lengths are the ones `faucet-and-umbilical.md` §1 hands the bench.
_faucet_gen = load_module(
    "bom_faucet_assembly_gen", _here.parent / "faucet-layout" / "faucet_assembly.py")
_flavor_4mm_mm = (2 * _faucet_gen.flavor_cut_length
                  + sum(r.length for r in _f.runs if r.id in ("fluid-18", "fluid-28")))


# Pressure vessel geometry: two laser-welded SS endcap plates per
# vessel, four 1/4" NPT ports tapped into the plates (water in, water
# out, CO2 in, PRV).
end_cap_plates_per_carbonator = 2
carbonator_ports = 4

# Flavor reservoirs per appliance.
reservoirs_per_build = 2

# One inserted RC62 per vessel float.
floats_per_build = 1 + reservoirs_per_build
rc62_per_build = floats_per_build

# Carbonator reeds (threshold-only). Per-reservoir count lives in
# `_reed_channels.py`.
reeds_per_carbonator = 2

# Purchased flavor-manifold fittings come from the pack's own declarations: every Y node is
# a purchased PP0208E, the four on the pump ports included.
solenoid_count = sum(1 for n in ml.P if n.startswith("V-"))
tee_count = len(ml.PURCHASED_TEES)

# Cable management, vent-adapter lands and paired stations with tie closures
# use four-inch stock. Each snapped station carries one separate printed cap.
reservoir_a_ties_per_build = sum(row.get('closure', 'tie') == 'tie'
                                for row in _reservoir_a_anchors.datums().values())
reservoir_a_snap_caps_per_build = sum(row.get('closure') == 'snap'
                                     for row in _reservoir_a_anchors.datums().values())
four_inch_ties_per_build = 15 + 2 + reservoir_a_ties_per_build
# One six-inch tie at each selected fluid saddle and explicit cap retaining path.
# This allocates owned stock; installed loop fit/retention remain unqualified.
_cap_retaining_paths = {**_selected_cap.meter_tie_routes(),
                        **{name: route for name, route in _selected_cap.union_tie_routes().items()
                           if _selected_cap.union_support_datums()[name]['support_implemented']},
                        'water-check': _selected_cap.check_tie_route()}
six_inch_ties_per_build = (len(_selected_shell.fluid_supports())
                            + len(_cap_retaining_paths))

# PP1208E bulkheads: soda umbilical and tap-water inlet. The flavor pair uses 4 mm ABU44M-E.
panel_umbilical_bulkheads = 1
panel_water_inlet_bulkheads = 1

# Per-cap insert counts.
# Foam caps: `attachment_xy_positions` is the list of (x, y) pairs for one
# shell face (4 corners, 4 mid-wall and 2 end stations); a cap stack fastens on each
# face (top mouth-up, bottom mouth-down), inserts pressed from each face.
# Reservoir: `insert_positions_for_side_plus_1` is the list of (x, z)
# pairs for one reservoir cap (6 per cap).
foam_cap_faces = 2
inserts_per_foam_cap_face = len(attachment_xy_positions)
inserts_per_reservoir_cap = len(insert_positions_for_side_plus_1)


# ─── Derived totals ────────────────────────────────────────────────────

# Reeds.
reservoir_reeds_total = reeds_per_reservoir * reservoirs_per_build
total_reeds_per_build = reeds_per_carbonator + reservoir_reeds_total

# PP1208E per build: soda umbilical (1) + water inlet (1) = 2.
pp1208e_per_build = panel_umbilical_bulkheads + panel_water_inlet_bulkheads

# Funnel drain and the selected warm/core union turns use PP0308E stock.
pp0308e_per_build = (1 + len(_above_core_bom.union_elbow_names())
                     + len(_above_core_bom.core_union_elbow_names()))
stem_elbows_per_build = (2*len(ml.LOWER_CONNECTIONS)
                        + len(_above_core_bom.stem_elbow_names())
                        + len(_above_core_bom.core_stem_elbow_names()))
stem_elbow_delivered_unit_cost = (
    Decimal('36.18') / Decimal(30) * Decimal('173.54') / Decimal('147.22'))

# Valve sockets belong to the printed parent already billed in §7: V-B to the
# cap lid, V-A/V-K to back-top, and the front manifold
# valves to enclosure-front-top. Both flavour-pump trays also belong to that
# front piece. No separate valve panel or equipment tray is allocated.
_trays = sorted(n for n in _placed if "tray" in n or n.startswith("valve-panel"))
assert not _trays, (
    f"the machine places {len(_trays)} body(ies) under its valves and pumps ({_trays}) — a seat "
    f"is printed into the piece that carries it, and bom.md §7 bills no part standing under one")

# NO ADDED SHEET-METAL COVER SHIPS OVER THE COMPRESSOR, and that too is read off the placed
# machine. The terminal block and clip-on PTC remain under the R-600a donor's own moulded cover,
# which is part of the harvested compressor assembly rather than a separately billed or placed
# body. So §5 buys no cut cover, no pass-through gland and no bond stud for one, and THAT ONE
# ADDED BODY appearing in the placed machine is what fails here.
#
# Named, not matched on a substring. `prv-shroud` (`printed-parts/cold-core/prv-shroud/`) is a
# live printed part with a §7 row and a mass of its own, and the day it joins the pack a
# substring test would fail here holding out §5's compressor rows for a part that is not the
# compressor's.
ADDED_COMPRESSOR_COVER = "compressor-shroud"
_cover = {ADDED_COMPRESSOR_COVER} & _placed
assert not _cover, (
    f"the machine places `{ADDED_COMPRESSOR_COVER}` and bom.md §5 bills no added sheet-metal "
    f"cover over the compressor "
    f"— add the cut-part row, its cable gland and its bond back with it")

# Foam-cap hardware: one clamp insert + one M3 × 25 screw per station per face, both faces, PLUS
# the top cap's pump and PCB columns, each with a full-length M3
# insert. The upright V-B wall takes no separate mount fasteners.
foam_cap_deck_inserts_per_build = sum(len(deck_mount_xy(n)) for n in deck_mounts)
pump_mount_screws_per_build = len(deck_mount_xy("g-ganen-pump"))
foam_cap_clamp_inserts_per_build = inserts_per_foam_cap_face * foam_cap_faces
foam_cap_inserts_per_build = (foam_cap_clamp_inserts_per_build
                              + foam_cap_deck_inserts_per_build)
foam_cap_screws_per_build = foam_cap_clamp_inserts_per_build  # 1:1 clamp only

# Reservoir-cap hardware (12 inserts + 12 M3 × 12 screws).
reservoir_cap_inserts_per_build = inserts_per_reservoir_cap * reservoirs_per_build
reservoir_cap_screws_per_build = reservoir_cap_inserts_per_build  # 1:1

# Touch-flo plate-to-shell hardware: one short insert and M3 × 8 per station.
touchflo_inserts_per_build = len(base_pod_centers)
touchflo_screws_per_build = touchflo_inserts_per_build  # 1:1

# The faucet display cover engages the shell's two printed cantilevers.
faucet_display_cover_stations = ()
faucet_display_cover_inserts_per_build = len(faucet_display_cover_stations)
faucet_display_cover_screws_per_build = faucet_display_cover_inserts_per_build

# Electronics use their native hole patterns and the selected wall fastener plans.
# PCB inserts belong to the cap count; wall relays use short inserts.
psu_fasteners = _selected_shell.psu_fastener_plan()
relay_fasteners = _selected_shell.relay_fastener_plan()
shelf_psu_screws_per_build = psu_fasteners['count']
shelf_ground_screws_per_build = len(_gnd.holes)
ground_fasteners = _above_core_wiring.ground_fastener_datums()
shelf_pcba_screws_per_build = len(deck_mount_xy('pcba'))
shelf_relay_screws_per_build = (sum(1 for name in _placed if name.startswith("relay-"))
                                * relay_fasteners['count'])
shelf_inserts_per_build = shelf_psu_screws_per_build + shelf_ground_screws_per_build
shelf_screws_per_build = (shelf_ground_screws_per_build + shelf_pcba_screws_per_build
                          + shelf_psu_screws_per_build + shelf_relay_screws_per_build)
# The uxcell Ø9 × 0.8 flat washer seats under each pump-foot screw and once on each cap
# ground stack, above its ring tongues: the stack's 0.8 mm washer layer is this washer.
ground_stack_washers_per_build = (shelf_ground_screws_per_build
                                  if ground_fasteners['washer_thickness_mm'] else 0)
flat_washers_9_per_build = pump_mount_screws_per_build + ground_stack_washers_per_build

# Floor-slab hardware (assembly/enclosure-mechanical.md §5). The compressor is the one body in
# the box bolted DOWN to it: `enclosure_assembly.floor_mounts` stands ONE POST PER HOLE in the
# compressor's own plate pattern, each post rising through that hole's rubber grommet to its
# crown and bored there for a ruthex M5. So the count is the pack's the way the shelf's is — a
# body arriving on the floor with a hole pattern brings its posts, inserts and screws with it.
#
# The compressor posts and four Y-seam anchors take M5 inserts. A floor post stands in a
# Ø14 grommet bore and carries the larger insert inside that section.
floor_inserts_per_build = len(_floor_bosses)
# One M5 down into each post's insert, through a fender washer that spans the grommet's bore —
# 1:1 with the posts.
floor_screws_per_build = floor_inserts_per_build
floor_washers_per_build = floor_screws_per_build

# Condenser-block hardware (assembly/enclosure-mechanical.md §3). The block is a donor envelope
# whose two Y faces stand back between folded sheet flanges, and `enclosure._cond_mount` stands
# ONE BORED FINGER PER HOLE in the aft pair — so this count is the pack's the way the shelf's
# and the floor's are. The fore pair takes a groove and no fastener.
cond_inserts_per_build = len(_cond_bosses)
# One M3 × 8 down through each aft flange into its finger's insert — 1:1 with the fingers, and
# the same screw the main board's four are.
cond_screws_per_build = cond_inserts_per_build

# The nameplate's two integral PET-GF tabs engage rigid enclosure shoulders.
nameplate_inserts_per_build = 0
nameplate_wings_per_build = len(_enc._nameplate_fit.wings())
nameplate_screws_per_build = 0

# The machine display cover is retained by its coplanar horizontal wings.
display_cover_stations = ()
display_cover_inserts_per_build = 0
display_cover_screws_per_build = 0
display_cover_wings_per_build = len(_enc._display_wings.support_exits(1.0))

# Three underside M3 x 60 screws close the broad lower retainer against the two
# pump skirts. Their full-length M3 inserts belong to front-top's integral upper mount.
# Read the declared placement and the mount's own fastener plan without drawing solids.
_pump_mount_box, _pump_mount_bounds, _pump_mount_box_path = _declared_box(_box_spec, _enc)
pump_retainer_inserts_per_build = len(_fixed_pump_mount.fasteners(_enc, _pump_mount_box))
pump_retainer_screws_per_build = pump_retainer_inserts_per_build

# Each pump tee stands in its bore through front-top's tee wall and takes no fastener.
dock_tees_per_build = len(_f.box["collet_plate"]["holes"])
dock_fixture_locks_per_build = 0

# Two C14 flange screws use the acquired Ø7×0.5 washers to span the native
# moulding's countersinks. Their short inserts seat on the flange-back plane.
c14_inserts_per_build = len(_c14.panel_screws())
c14_screws_per_build = c14_inserts_per_build
c14_washers_per_build = c14_screws_per_build
c14_fasteners = _selected_shell.c14_fastener_plan()
c14_washer_thickness = c14_fasteners['washer_thickness_mm']
c14_bore = c14_fasteners['pilot_depth_mm']
# The selected fixed-tee dock has no keeper or return-cover locks.
small_washers_per_build = dock_fixture_locks_per_build + c14_washers_per_build

# THE PLATE AND ITS RING ARE PRINTED PARTS AND §7 BILLS BOTH: the plate a row of its own, the
# gasket a line in the soft-seal sentence that carries every TPU seal in the machine. A body
# the machine places and the ledger does not buy is a part nobody prints.
_display_stack = {"display-cover", "display-gasket"} - set(_f.bodies)
assert not _display_stack, (
    f"the machine no longer stands {sorted(_display_stack)} — bom.md §7 bills the display's "
    f"snap-retained cover and its gasket")

# Four M5 seam screws pass through the printed knuckles. Each head bears on its
# printed floor and the thread engages a ruthex M5 insert: the two lower screws enter
# from the handholds into back-bottom's knuckles under the Z seam, the two upper from
# the roof into front-top's. The Z seams retain their sliding hooked rails.
_seam_rods = _enc.y_stack_rods(_f.box["inner"])
enclosure_seam_rods_per_build = 2 * len(_seam_rods)
enclosure_seam_inserts_per_build = enclosure_seam_rods_per_build

# The drop-in funnel frame fastens from above the continuous electronics ceiling.
funnel_frame_screws_per_build = len(_enc._funnel_frame_part.fastener_datums())
roof_closure_screws_per_build = funnel_frame_screws_per_build
roof_closure_inserts_per_build = roof_closure_screws_per_build

# M3×8 screws retain the PCB, relay diagonals, condenser and faucet base, and close the
# cap ground stack.
m3x8_per_build = (shelf_pcba_screws_per_build + cond_screws_per_build + shelf_ground_screws_per_build
                  + shelf_relay_screws_per_build
                  + nameplate_screws_per_build + display_cover_screws_per_build
                  + faucet_display_cover_screws_per_build
                  + touchflo_screws_per_build)

# C14 uses M3×10.
m3x10_per_build = c14_screws_per_build
m3x20_per_build = pump_mount_screws_per_build

# The PCB stack belongs to the cap; PSU and relay stacks belong to the wall.
psu_screw_len = psu_fasteners['screw_length_mm']
pcba_screw_len = deck_mounts['pcba'].screw
relay_screw_len = relay_fasteners['screw_length_mm']
c14_screw_len = c14_fasteners['screw_length_mm']
pcba_insert_recess = 0.0
pcba_bore = deck_mount_bore_depth
psu_bore = psu_fasteners['pilot_depth_mm']
relay_bore = relay_fasteners['pilot_depth_mm']
psu_screw_reach = min(psu_fasteners['receiving_range_mm'])
psu_screw_reach_max = max(psu_fasteners['receiving_range_mm'])
pcba_screw_reach = deck_mount_reach('pcba')
relay_screw_reach = min(relay_fasteners['receiving_range_mm'])
c14_screw_reach = c14_screw_len - _c14.FLANGE_T - c14_washer_thickness

# Every M3 x 60 belongs to the pump retainer's underside screw row.
m3x60_per_build = pump_retainer_screws_per_build

# M3 × 12 retains the funnel frame and the PSU's four wall ears.
m3x12_per_build = (dock_fixture_locks_per_build + roof_closure_screws_per_build
                   + shelf_psu_screws_per_build)

# WHICH M3 BODY EACH STATION TAKES. ruthex's short and full-length M3 are the same insert but
# for the body — same knurl, same recommended hole — so this split is a statement about BORE
# DEPTH and nothing else. A station is on the long list when the bore it already cuts is deeper
# than 5.7 mm of brass plus the relief its own screw needs; it is on the short list when giving
# it that depth would cost geometry the machine is spending elsewhere.
#
# Short insert families and the stock available behind their seats:
#   touch-flo base pods  — the blind pilots receive 4 mm inserts above the locating sockets
#   PSU/relay wall hosts and cap earth boss — their screws use the short family
m3_long_inserts_per_build = (
    foam_cap_inserts_per_build
    + reservoir_cap_inserts_per_build
    + cond_inserts_per_build
    + nameplate_inserts_per_build
    + display_cover_inserts_per_build
    + pump_retainer_inserts_per_build
    + roof_closure_inserts_per_build
)
m3_short_inserts_per_build = (
    touchflo_inserts_per_build
    + shelf_inserts_per_build
    + faucet_display_cover_inserts_per_build
    + c14_inserts_per_build
    + dock_fixture_locks_per_build
    + shelf_relay_screws_per_build
)

# Combined heat-set insert count across the appliance, by thread.
total_m3_inserts_per_build = m3_long_inserts_per_build + m3_short_inserts_per_build
total_m5_inserts_per_build = floor_inserts_per_build + enclosure_seam_inserts_per_build

# And the screws that go into them. `labor.md` §8 prices both passes off these two figures.
total_m3_screws_per_build = (
    foam_cap_screws_per_build
    + pump_mount_screws_per_build
    + reservoir_cap_screws_per_build
    + touchflo_screws_per_build
    + shelf_screws_per_build
    + cond_screws_per_build
    + nameplate_screws_per_build
    + display_cover_screws_per_build
    + faucet_display_cover_screws_per_build
    + pump_retainer_screws_per_build
    + c14_screws_per_build
    + dock_fixture_locks_per_build
    + roof_closure_screws_per_build
)
total_m5_screws_per_build = floor_screws_per_build + enclosure_seam_rods_per_build

# The cap check's complete nominal strip needs the allocated six-inch stock.
# Its installed threading and retention remain unqualified.
chain_tie_loop = _cap_retaining_paths['water-check']['length_mm']


def pack_line_cost(quantity, pack_price, pack_quantity):
    """Allocate the exact paid/list pack price; round only the final line."""
    allocated = Decimal(str(quantity)) * Decimal(pack_price) / Decimal(str(pack_quantity))
    return f"${allocated.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}"


def main(*, only_bom=False):
    casting = casting_estimate()
    variables = {
        **_casting_figures(),
        "FUNNEL_KIT_YIELD": f"{1098.0 / casting['mixed_g']:.2f}",
        "FUNNEL_BATCH_COST": f"${35.16 * casting['mixed_g'] / 1098.0:.2f}",
        # Carbonator.
        "END_CAPS": f"{end_cap_plates_per_carbonator:.4g}",
        "CARBONATOR_PORTS": f"{carbonator_ports:.4g}",
        # Reservoirs.
        "RESERVOIRS": f"{reservoirs_per_build:.4g}",
        "RESERVOIR_CAP_COUNT": f"{reservoirs_per_build:.4g}",
        "AERO_FLOATS": f"{floats_per_build:.4g}",
        "RC62_TOTAL": f"{rc62_per_build:.4g}",
        "RC62_COST": pack_line_cost(rc62_per_build, "88.28", 30),
        # Reeds.
        "REEDS_PER_RES": f"{reeds_per_reservoir:.4g}",
        "CARB_REEDS": f"{reeds_per_carbonator:.4g}",
        "RES_REEDS_TOTAL": f"{reservoir_reeds_total:.4g}",
        "REEDS_TOTAL": f"{total_reeds_per_build:.4g}",
        # Flavor subsystem.
        "SOLENOIDS": f"{solenoid_count:.4g}",
        "TEES": f"{tee_count:.4g}",
        "TEES_COST": pack_line_cost(tee_count, "42.68", 20),
        "FOUR_INCH_TIES": f"{four_inch_ties_per_build:.4g}",
        "FOUR_INCH_TIES_COST": pack_line_cost(four_inch_ties_per_build, "4.28", 200),
        "RESERVOIR_A_TIES": f"{reservoir_a_ties_per_build}",
        "RESERVOIR_A_SNAP_CAPS": f"{reservoir_a_snap_caps_per_build}",
        "SIX_INCH_TIES": f"{six_inch_ties_per_build:.4g}",
        "SIX_INCH_TIES_COST": pack_line_cost(six_inch_ties_per_build, "6.42", 100),
        "SOLID16_CUT_LENGTH": f"{solid16_cut_m:g} m",
        "SOLID16_ALLOCATION": f"{solid16_allocation_m:g} m",
        "SOLID16_COST": pack_line_cost(solid16_allocation_m, "12.86", "7.62"),
        "PP1208E_PANEL": f"{panel_umbilical_bulkheads:.4g}",
        "PP1208E_INLET": f"{panel_water_inlet_bulkheads:.4g}",
        "PP1208E_TOTAL": f"{pp1208e_per_build:.4g}",
        "ANCHOR_LOOP": f"{chain_tie_loop:.3g} mm",
        # Heat-set insert + screw hardware.
        "FOAM_INSERTS": f"{foam_cap_inserts_per_build:.4g}",
        "FOAM_CLAMP_INSERTS": f"{foam_cap_clamp_inserts_per_build:.4g}",
        "FOAM_SCREWS": f"{foam_cap_screws_per_build:.4g}",
        "FOAM_FACE_SCREWS": f"{inserts_per_foam_cap_face:.4g}",
        "RES_INSERTS_PER_CAP": f"{inserts_per_reservoir_cap:.4g}",
        "RES_INSERTS": f"{reservoir_cap_inserts_per_build:.4g}",
        "RES_SCREWS": f"{reservoir_cap_screws_per_build:.4g}",
        "TOUCHFLO_INSERTS": f"{touchflo_inserts_per_build:.4g}",
        "TOUCHFLO_SCREWS": f"{touchflo_screws_per_build:.4g}",
        "FAUCET_DISPLAY_INSERTS": f"{faucet_display_cover_inserts_per_build:.4g}",
        "FAUCET_DISPLAY_SCREWS": f"{faucet_display_cover_screws_per_build:.4g}",
        "SHELF_INSERTS": f"{shelf_inserts_per_build:.4g}",
        "SHELF_SCREWS": f"{shelf_screws_per_build:.4g}",
        "SHELF_SCREWS_PSU": f"{shelf_psu_screws_per_build:.4g}",
        "SHELF_SCREWS_GROUND": f"{shelf_ground_screws_per_build:.4g}",
        "GROUND_STACK_T": f"{ground_fasteners['clamped_thickness_mm']:g}",
        "GROUND_SCREW_REACH": f"{ground_fasteners['screw_projection_mm']:g}",
        "GROUND_BORE": f"{ground_fasteners['pilot_depth_mm']:g}",
        "GROUND_TIP_AIR": f"{ground_fasteners['tip_air_mm']:g}",
        "GROUND_BOSS_D": f"{ground_fasteners['boss_diameter_mm']:g}",
        "SHELF_SCREWS_PCBA": f"{shelf_pcba_screws_per_build:.4g}",
        "SHELF_SCREWS_RELAY": f"{shelf_relay_screws_per_build:.4g}",
        "COND_INSERTS": f"{cond_inserts_per_build:.4g}",
        "COND_SCREWS": f"{cond_screws_per_build:.4g}",
        "SHORT_INSERT_LEN": f"{_enc.heatset_len:g}",
        "PSU_EAR_T": f"{_psu.ledge_h:g}",
        "PSU_BORE": f"{psu_bore:.3g}",
        "PSU_SCREW_REACH": f"{psu_screw_reach:.3g}",
        "PSU_SCREW_REACH_MAX": f"{psu_screw_reach_max:.3g}",
        "PSU_SCREW_TIP": f"{psu_bore - psu_screw_reach_max:.3g}",
        "PCBA_BOARD_T": f"{_pcba._thickness:g}",
        "PCBA_INSERT_RECESS": f"{pcba_insert_recess:.3g}",
        "PCBA_BORE": f"{pcba_bore:.3g}",
        "PCBA_SCREW_REACH": f"{pcba_screw_reach:.3g}",
        "PCBA_SCREW_TIP": f"{pcba_bore - pcba_screw_reach:.3g}",
        "RELAY_BOARD_T": f"{_relay.pcb_t:g}",
        "RELAY_INSERT_LEN": f"{relay_fasteners['insert_length_mm']:g}",
        "RELAY_BEARING_TIP": f"{relay_fasteners['bearing_tip_height_mm']:g}",
        "RELAY_BACKING": f"{relay_fasteners['minimum_blind_backing_mm']:.3g}",
        "RELAY_FLUTED_BACKING": f"{relay_fasteners['minimum_fluted_backing_mm']:.3g}",
        "RELAY_BORE": f"{relay_bore:.3g}",
        "RELAY_SCREW_REACH": f"{relay_screw_reach:.3g}",
        "RELAY_SCREW_TIP": f"{relay_bore - relay_screw_reach:.3g}",
        "C14_FLANGE_T": f"{_c14.FLANGE_T:g}",
        "C14_RIM_PROUD": f"{_c14.RIM_PROUD:g}",
        "C14_BORE": f"{c14_bore:g}",
        "C14_SCREW_REACH": f"{c14_screw_reach:.3g}",
        "C14_SCREW_TIP": f"{c14_bore - c14_screw_reach:.3g}",
        "C14_WASHERS": f"{c14_washers_per_build:g}",
        "C14_WASHER_T": f"{c14_washer_thickness:g}",
        "C14_WASHERS_COST": pack_line_cost(c14_washers_per_build, "7.82", 200),
        "SMALL_WASHERS": f"{small_washers_per_build:g}",
        "SMALL_WASHERS_COST": pack_line_cost(small_washers_per_build, "7.82", 200),
        "M3X8_TOTAL": f"{m3x8_per_build:.4g}",
        "M3X8_COST": pack_line_cost(m3x8_per_build, "7.71", 120),
        "NAMEPLATE_INSERTS": f"{nameplate_inserts_per_build:.4g}",
        "NAMEPLATE_SCREWS": f"{nameplate_screws_per_build:.4g}",
        "NAMEPLATE_MOUNT": (
            f"retained in `enclosure-back-top` by {nameplate_wings_per_build} coplanar "
            "horizontal wings. The plate takes "
            f"{nameplate_screws_per_build} screws and {nameplate_inserts_per_build} inserts."),
        "DISPLAY_COVER_INSERTS": f"{display_cover_inserts_per_build:.4g}",
        "DISPLAY_COVER_SCREWS": f"{display_cover_screws_per_build:.4g}",
        "DISPLAY_COVER_MOUNT": (
            f"retained flush with `enclosure-front-top`'s {_enc._display_wings.ANGLE:g}° "
            f"display plane by {display_cover_wings_per_build} coplanar horizontal wings. "
            "The TPU ring bears between the cover's lap and the glass. "
            f"The cover takes {display_cover_screws_per_build} screws and "
            f"{display_cover_inserts_per_build} inserts."),
        "M3X10_TOTAL": f"{m3x10_per_build:.4g}",
        "M3X10_COST": pack_line_cost(m3x10_per_build, "8.57", 120),
        "M3X20_TOTAL": f"{m3x20_per_build:.4g}",
        "M3X20_COST": pack_line_cost(m3x20_per_build, "8.14", 60),
        "FUNNEL_FRAME_SCREWS": f"{funnel_frame_screws_per_build:.4g}",
        "ROOF_CLOSURE_INSERTS": f"{roof_closure_inserts_per_build:.4g}",
        "ROOF_CLOSURE_SCREWS": f"{roof_closure_screws_per_build:.4g}",
        "M3X60_TOTAL": f"{m3x60_per_build:.4g}",
        "M3X60_COST": pack_line_cost(m3x60_per_build, "10.18", 60),
        "M3X12_TOTAL": f"{m3x12_per_build:.4g}",
        "M3X12_COST": pack_line_cost(m3x12_per_build, "8.57", 120),
        "SEAM_RODS": f"{enclosure_seam_rods_per_build:.4g}",
        "SEAM_SCREW_UNIT_COST": pack_line_cost(1, "7.70", 20),
        "SEAM_SCREWS_COST": pack_line_cost(enclosure_seam_rods_per_build, "7.70", 20),
        "SEAM_INSERTS": f"{enclosure_seam_inserts_per_build:.4g}",
        "DOCK_PUMP_TUBES": f"{len(_f.box['collet_plate']['holes'])}",
        "PUMP_TUBE_CUT": f"{ml.PUMP_TUBE_CUT:.3g} mm",
        "DOCK_TEES": f"{len(ml.PUMP_JUNCTIONS)}",
        "DOCK_RETURNS": f"{len(ml.LOWER_CONNECTIONS)}",
        # The dock subset uses the same delivered receipt allocation as all stems.
        "DOCK_ELBOWS": f"{2 * len(ml.LOWER_CONNECTIONS)}",
        "DOCK_ELBOWS_COST": f"${(Decimal(2*len(ml.LOWER_CONNECTIONS))*stem_elbow_delivered_unit_cost).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)}",
        "STEM_ELBOWS": f"{stem_elbows_per_build:.4g}",
        "STEM_ELBOWS_COST": f"${(Decimal(stem_elbows_per_build)*stem_elbow_delivered_unit_cost).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)}",

        "PP0308E_TOTAL": f"{pp0308e_per_build}",
        "PP0308E_COST": pack_line_cost(pp0308e_per_build, "68.49", 30),
        "DOCK_TEES": f"{dock_tees_per_build:.4g}",
        "DOCK_FIXTURE_LOCKS": f"{dock_fixture_locks_per_build:.4g}",
        "PUMP_RETAINER_INSERTS": f"{pump_retainer_inserts_per_build:.4g}",
        "PUMP_RETAINER_SCREWS": f"{pump_retainer_screws_per_build:.4g}",
        "FLOOR_INSERTS": f"{floor_inserts_per_build:.4g}",
        "FLOOR_SCREWS": f"{floor_screws_per_build:.4g}",
        "FLOOR_WASHERS": f"{floor_washers_per_build:.4g}",
        "COMPRESSOR_LIGAMENT": f"{_ea._comp.MOUNT_LIGAMENT:.4g}",
        "COMPRESSOR_BORE": f"{_ea._comp.MOUNT_D:.4g}",
        # The widest washer the plate's own steel still carries: the bore plus the ligament
        # either side of it.
        "WASHER_MAX_OD":
            f"{_ea._comp.MOUNT_D + 2.0 * _ea._comp.MOUNT_LIGAMENT:.4g}",
        "GROMMET_SQUEEZE": f"{_ea.FLOOR_GROMMET_SQUEEZE:.4g}",
        "DECK_INSERTS": f"{foam_cap_deck_inserts_per_build:.4g}",
        "PUMP_MOUNT_SCREWS": f"{pump_mount_screws_per_build:.4g}",
        "FLAT_WASHERS_9": f"{flat_washers_9_per_build:.4g}",
        "FLAT_WASHERS_9_COST": pack_line_cost(flat_washers_9_per_build, "9.00", 200),
        "RES_SCREWS_COST": pack_line_cost(reservoir_cap_screws_per_build, "8.66", 120),
        "CAP_CRADLES": f"{len(cap_cradles):.4g}",
        "TOTAL_M3_INSERTS": f"{total_m3_inserts_per_build:.4g}",
        "M3_LONG_INSERTS": f"{m3_long_inserts_per_build:.4g}",
        "M3_LONG_INSERTS_COST": pack_line_cost(m3_long_inserts_per_build, "10.71", 100),
        "M3_SHORT_INSERTS": f"{m3_short_inserts_per_build:.4g}",
        "M3_SHORT_INSERTS_COST": pack_line_cost(m3_short_inserts_per_build, "10.71", 100),
        "C14_INSERTS": f"{c14_inserts_per_build:.4g}",
        "C14_SCREWS": f"{c14_screws_per_build:.4g}",
        "TOTAL_M5_INSERTS": f"{total_m5_inserts_per_build:.4g}",
        "M5_INSERTS_COST": pack_line_cost(total_m5_inserts_per_build, "10.71", 50),
        # Evaporator-coil copper (§5 GOORY row). LAID_FT is the copper a build CONSUMES —
        # the finished winding on the vessel, including bridge relief. The
        # mandrel-groove calculations are independent tool references.
        "PITCH": f"{_coil_gen.PITCH:.4g} mm",
        "NET_UNDERSIZE": f"{_coil_mandrel_gen.net_undersize:.4g} mm",
        "LAID_FT": f"{_wrap_mm / 304.8:.4g} ft",
        "MANDREL_FT": f"{_coil_mandrel_gen.mandrel_wrap_length / 304.8:.4g} ft",
        "STUB_INLET": f"{_coil_mandrel_gen.stub_allowance['inlet']:.4g} mm",
        "STUB_OUTLET": f"{_coil_mandrel_gen.stub_allowance['outlet']:.4g} mm",
        "ROLL_SHARE": f"1/{_coil_mandrel_gen.carbonators_per_roll}",
        "CUT_FT": f"{_cut_mm / 304.8:.4g} ft",
        "ROLL_SPARE": f"{_roll_spare_ft:+.2f} ft",
        # The PRV vent line (§2), as `cold-core-layout` draws it inside the core.
        "PRV_VENT_MM": f"{_prv_vent_mm:.0f} mm",
        # A White faucet's flavor runs, unions and soda faucet tube (§9). The cut names are the
        # ones `_faucet_and_umbilical_sync` writes into §1 of the bench, so the two cannot drift.
        "FLAVOR_CUT": f"{_faucet_gen.flavor_cut_length:g}",
        "FLAVOR_4MM_FT": f"{_flavor_4mm_mm / 304.8:.2f}",
        "FLAVOR_4MM_COST": f"${_flavor_4mm_mm / 304.8 * 0.13:.2f}",
        "SODA_FAUCET_CUT": f"{_faucet_gen.soda_faucet_cut_length:g}",
        "SODA_FAUCET_FT": f"{_faucet_gen.soda_faucet_cut_length / 304.8:.2f}",
    }

    substitute_md(
        _here.parent / "ledger" / "bom.md",
        variables=variables,
    )
    print("-> bom.md")
    if only_bom:
        return

    # `labor.md` §8 prices two passes of the same hardware — pressing every insert, then
    # driving every screw — so the counts it quotes are these, not its own.
    substitute_md(
        _here.parent / "ledger" / "labor.md",
        variables={
            # The bench presses a thread it is handed; both passes are counted whole.
            "TOTAL_INSERTS":
                f"{total_m3_inserts_per_build + total_m5_inserts_per_build:.4g}",
            "TOTAL_SCREWS":
                f"{total_m3_screws_per_build + total_m5_screws_per_build:.4g}",
            "TOTAL_M3_INSERTS": f"{total_m3_inserts_per_build:.4g}",
            "TOTAL_M5_INSERTS": f"{total_m5_inserts_per_build:.4g}",
            "SEAM_INSERTS": f"{enclosure_seam_inserts_per_build:.4g}",
            "SEAM_RODS": f"{enclosure_seam_rods_per_build:.4g}",
            "FOAM_CLAMP_INSERTS": f"{foam_cap_clamp_inserts_per_build:.4g}",
            "FOAM_SCREWS": f"{foam_cap_screws_per_build:.4g}",
            "FOAM_FACE_SCREWS": f"{inserts_per_foam_cap_face:.4g}",
            "PUMP_MOUNT_SCREWS": f"{pump_mount_screws_per_build:.4g}",
            "RES_SCREWS": f"{reservoir_cap_screws_per_build:.4g}",
            "TOUCHFLO_SCREWS": f"{touchflo_screws_per_build:.4g}",
            "FAUCET_DISPLAY_INSERTS": f"{faucet_display_cover_inserts_per_build:.4g}",
            "FAUCET_DISPLAY_SCREWS": f"{faucet_display_cover_screws_per_build:.4g}",
            "SHELF_INSERTS": f"{shelf_inserts_per_build:.4g}",
            "SHELF_SCREWS": f"{shelf_screws_per_build:.4g}",
            "COND_SCREWS": f"{cond_screws_per_build:.4g}",
            "DISPLAY_COVER_SCREWS": f"{display_cover_screws_per_build:.4g}",
            "PUMP_RETAINER_SCREWS": f"{pump_retainer_screws_per_build:.4g}",
            "DOCK_LOCKS": f"{dock_fixture_locks_per_build:.4g}",
            "C14_SCREWS": f"{c14_screws_per_build:.4g}",
            "ROOF_CLOSURE_SCREWS": f"{roof_closure_screws_per_build:.4g}",
            "NAMEPLATE_SCREWS": f"{nameplate_screws_per_build:.4g}",
            "FLOOR_SCREWS": f"{floor_screws_per_build:.4g}",
            "SOLENOIDS": f"{solenoid_count:.4g}",
        },
    )
    print("-> labor.md")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only-bom", action="store_true",
                        help="update only bom.md and its figure bindings")
    main(only_bom=parser.parse_args().only_bom)
