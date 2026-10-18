"""Doc-sync driver for hardware/ledger/bom.md.

Run: tools/cad-venv/bin/python hardware/scripts/_bom_sync.py
Use --only-bom to update the BOM without rewriting the labor ledger.
"""

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
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

from _cold_core_interface import (attachment_xy_positions, cap_anchor_tie_loop,
                                  cap_cradles, cap_side_anchor_tie_loop, deck_mounts,
                                  deck_mount_xy)
from _reed_channels import reeds_per_reservoir
from docgen import load_module, substitute_md
from _funnel_casting import casting_estimate, figures as _casting_figures
from reservoir import insert_positions_for_side_plus_1
from faucet_shell import base_pod_centers

import manifold_layout as ml
import dock_retention
import _facts
import enclosure_assembly as _ea  # noqa: F401  — holds the closure these docs watch
import ground_ring_stack as _gnd  # on the path once `enclosure_assembly` is imported
import enclosure as _enc  # likewise
import digiten_flow_sensor as _digiten  # likewise — the arm the meter's anchors bore for
import iec_c14_inlet as _c14  # likewise — the inlet whose flange the +Y wall's tunnel bores for
import meanwell_irm90 as _psu  # likewise — the +X wall's bodies, each counting its own screws
import teyleten_relay as _relay  # likewise
import pcba_tray as _pcba  # likewise

# The placed pack, for the counts that are the machine's rather than a part's — off the
# artifact the last build wrote, so this driver stands no appliance to count bosses.
_f = _facts.read()
_placed = set(_f.pack["placed"])
_east_bosses = _f.box["east_bosses"]
_floor_bosses = _f.box["floor_bosses"]
_cond_bosses = _f.box["cond_mount"][3] if _f.box["cond_mount"] else ()


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

# The faucet's finish-bound tubes (§9), off the assembly that routes them: a White faucet's white
# flavor runs and its union on each, and the 3/8" soda faucet tube either finish cuts from its own
# stock. The cut lengths are the ones `faucet-and-umbilical.md` §1 hands the bench.
_faucet_gen = load_module(
    "bom_faucet_assembly_gen", _here.parent / "faucet-layout" / "faucet_assembly.py")
_white_flavor_mm = sum(_faucet_gen.white_cut_length(x) for x in _faucet_gen.flavor_sides)


# Pressure vessel geometry: two laser-welded SS endcap plates per
# vessel, four 1/4" NPT ports tapped into the plates (water in, water
# out, CO2 in, PRV).
end_cap_plates_per_carbonator = 2
carbonator_ports = 4

# Flavor reservoirs per appliance.
reservoirs_per_build = 2

# One inserted RC62 per vessel float. Cartridge retention uses stepped block magnets.
floats_per_build = 1 + reservoirs_per_build
rc62_per_build = floats_per_build
dock_magnets_per_build = 2 * len(dock_retention.stations(_f.box["collet_plate"]["holes"]))

# Carbonator reeds (threshold-only). Per-reservoir count lives in
# `_reed_channels.py`.
reeds_per_carbonator = 2

# The flavor manifold, counted off the pack `manifold_layout` places rather than
# restated here — `P` is every body on the four limbs, and a valve or a junction
# that leaves the pack leaves this count with it. Every junction is a PP0208E Tee
# (in-line run + branch); per-limb grouping is
# `topology/fluid-topology-limbs.mmd`.
solenoid_count = sum(1 for n in ml.P if n.startswith("V-"))
tee_count = sum(1 for n in ml.P if n.startswith("Y-"))

four_inch_ties_per_build = 24
# Two fixed-collar ties on each of the four pump-side tees.
six_inch_ties_per_build = 7 + 2 * len(_f.box["collet_plate"]["holes"])

# PP1208E bulkheads in the +Y wall of back-top. Umbilical port: 3 on that wall
# (1 carbonated water + 2 flavor). Water inlet: 1 more, same SKU and
# panel hole (the customer-facing 1/4" QC potable-water inlet).
panel_umbilical_bulkheads = 3
panel_water_inlet_bulkheads = 1

# Per-cap insert counts.
# Foam caps: `attachment_xy_positions` is the list of (x, y) pairs for one
# shell face (4 corners + 2 mid-long-side = 6); a cap stack fastens on each
# face (top mouth-up, bottom mouth-down), inserts pressed from each face.
# Reservoir: `insert_positions_for_side_plus_1` is the list of (x, z)
# pairs for one reservoir cap (6 per cap).
foam_cap_faces = 2
inserts_per_foam_cap_face = len(attachment_xy_positions)
inserts_per_reservoir_cap = len(insert_positions_for_side_plus_1)

# Reservoir cap vent filter: one ø13 PTFE membrane per cap.
vent_filters_per_reservoir_cap = 1


# ─── Derived totals ────────────────────────────────────────────────────

# Reeds.
reservoir_reeds_total = reeds_per_reservoir * reservoirs_per_build
total_reeds_per_build = reeds_per_carbonator + reservoir_reeds_total

# PP1208E per build: umbilical cluster (3) + water inlet (1) = 4. The
# reservoir-cap outlet uses the PureSec B0968K4JRN single-piece 90° PTC
# bulkhead, not PP1208E.
pp1208e_per_build = panel_umbilical_bulkheads + panel_water_inlet_bulkheads

# The placed pack turns no line on a fitting, so the BOM's one union-elbow row is the
# funnel drain's (§8). `manifold_layout.JOINS` is empty — every valve is butted collet to
# collet down its limb and every junction is a Tee. The four pump paths pass through
# permanent TPU receivers before reaching fixed tee branches.
assert not ml.JOINS, (
    f"the manifold poses {len(ml.JOINS)} elbow(s) ({sorted(ml.JOINS)}) and bom.md §8 buys "
    f"one, for the funnel drain — raise that row's count to cover these too")

# EVERY VALVE IN THIS MACHINE STANDS IN FOUR BOSSES (`valve_seat`) PRINTED INTO A PART §7
# ALREADY BILLS — three on the cold core's cap lid (`_cold_core_interface.cap_cradles`), eight on
# the two valve panels, which are `enclosure-front-top`'s own material
# (`enclosure._valve_trays`) — and both flavour pumps hang in a tray of that same piece's
# material (`enclosure._pump_trays`). So §7 carries no seat row of its own, and a plate appearing
# in the machine as a body rather than as a wall is what fails here.
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
# the top cap's deck-mount columns — each takes a ruthex short in its top bore, and
# each is a bolt station, and the water pump is the one module that uses any: the
# clamp screws are 1:1 with the clamp inserts, and a deck column takes a screw only
# where a module bolts into it — which today is `g-ganen-pump`'s four and nothing
# else. The three valves that stand on the top lid press into cradles printed in
# it, which take neither.
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

# Electronics-shelf hardware (Zone B, assembly/electronics-bay.md). The electronics bay
# bolts to `enclosure-back-top`'s +X wall: `enclosure_assembly.wall_mounts` stands ONE BOSS PER
# HOLE in each body's own mounting pattern, and each boss is bored for a ruthex short.
# So the count is the pack's, not a number typed here — a body that gains a hole gains a
# boss, an insert and a screw together. No printed part on the shelf carries a boss of
# its own and no tray ships, so this is the whole of the shelf's retention.
shelf_inserts_per_build = len(_east_bosses)
# One SHCS in through each body from the room, into its boss's insert — 1:1 with the
# bosses. Every insert is a 4 mm short in a bore of about 6 mm, so each body's length is
# its own clamp stack and each body's own pattern counts its screws. The PSU's moulded
# ears are 6.7 mm and the ground stack fans ring terminals under its head: M3 × 10. The
# main board's 1.6 mm stands over an insert recessed 2.25 mm: M3 × 8. A relay's 1.5 mm
# board sits on a flush insert: M3 × 6.
shelf_screws_per_build = shelf_inserts_per_build
shelf_psu_screws_per_build = len(_psu.holes)
shelf_ground_screws_per_build = len(_gnd.holes)
shelf_pcba_screws_per_build = len(_pcba.board.holes)
shelf_relay_screws_per_build = (sum(1 for name in _placed if name.startswith("relay-"))
                                * len(_relay.holes))

# Floor-slab hardware (assembly/enclosure-mechanical.md §5). The compressor is the one body in
# the box bolted DOWN to it: `enclosure_assembly.floor_mounts` stands ONE POST PER HOLE in the
# compressor's own plate pattern, each post rising through that hole's rubber grommet to its
# crown and bored there for a ruthex M5. So the count is the pack's the way the shelf's is — a
# body arriving on the floor with a hole pattern brings its posts, inserts and screws with it.
#
# THE FLOOR IS THE ONE M5 STATION IN THE APPLIANCE. A post stands in a Ø14 grommet bore rather
# than on a board between its pin fields, so it takes the section for the larger insert.
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

# The pump clamp's two, read off its centre lane. ONE TOP CLAMP CLOSES ON BOTH STAMPED
# BRACKETS (`enclosure.build_pump_cap`) and `cap_screw_ys` strikes a pair either side of the
# lane's mid-depth, so it is two screws and two inserts however many pumps the cradle carries.
# They are the box's only M3 x 60 — `enclosure.cap_screw_len` is the under-head length, the
# clamp's whole filled field from a counterbore in its crown to a long insert in the cradle
# spine. The lower cradle carries pump weight; these screws keep the clamp pressed onto the
# brackets.
pump_cap_inserts_per_build = len(_enc.cap_screw_ys(_f.box["inner"], _f.box["collet_plate"]))
pump_cap_screws_per_build = pump_cap_inserts_per_build

# Each permanent receiver has one flat keeper and a factory-only M3×8 lock screw.
dock_keepers_per_build = len(_f.box["collet_plate"]["holes"])
dock_keeper_inserts_per_build = dock_keepers_per_build
dock_keeper_screws_per_build = dock_keepers_per_build
dock_rear_support_locks_per_build = len(_enc._dock.support_lock_x(_f.box['collet_plate']))

# The C14 inlet's two, read off the receptacle's own flange. `enclosure._c14_tunnel_geometry`
# stands a TUNNEL off the +Y wall's inner face and bores ONE INSERT PER PANEL SCREW the moulding
# declares, so this count is the donor's the way the shelf's is the pack's — a receptacle with a
# different flange brings its own stations.
#
# THE CORD IS THE ONLY THING A CUSTOMER PLUGS INTO THIS MACHINE, and these two screws are what
# hold the socket it plugs into. The tunnel is `c14_tunnel_len` — one `heatset_depth` — deep and
# no deeper, because what stands over the insert's blind end is the wall the cord passes
# through: a bore run further would open the outside of the appliance at the one station a hand
# pushes against. So this pair is SHORT-BODY by construction and not by preference.
c14_inserts_per_build = len(_c14.panel_screws())
c14_screws_per_build = c14_inserts_per_build

# THE PLATE AND ITS RING ARE PRINTED PARTS AND §7 BILLS BOTH: the plate a row of its own, the
# gasket a line in the soft-seal sentence that carries every TPU seal in the machine. A body
# the machine places and the ledger does not buy is a part nobody prints.
_display_stack = {"display-cover", "display-gasket"} - set(_f.bodies)
assert not _display_stack, (
    f"the machine no longer stands {sorted(_display_stack)} — bom.md §7 bills the display's "
    f"snap-retained cover and its gasket")

# Four M5 seam screws pass through the printed corner blocks. Each screw carries
# one ordinary flat washer and threads into a ruthex M5 insert in its anchor block.
# The two lower screws enter from the handholds; the two upper screws enter from
# the roof. The Z seams retain their sliding hooked rails.
_seam_rods = _enc.y_stack_rods(_f.box["inner"])
enclosure_seam_rods_per_build = 2 * len(_seam_rods)
enclosure_seam_long_rods_per_build = 2 * sum(1 for r in _seam_rods if r[0] == "lower")
enclosure_seam_short_rods_per_build = 2 * sum(1 for r in _seam_rods if r[0] == "upper")
enclosure_seam_inserts_per_build = enclosure_seam_rods_per_build
enclosure_seam_washers_per_build = enclosure_seam_rods_per_build

# Every M3 × 8 in the build: the main board's four, the condenser's aft pair, the faucet
# base, C14 inlet and permanent receiver keepers. The inlet's 3.25 mm flange ear stands 1.84 mm off the tunnel's
# seating face on the receptacle's rim, so an 8 leaves 2.9 mm in the 4 mm insert.
m3x8_per_build = (shelf_pcba_screws_per_build + cond_screws_per_build
                  + nameplate_screws_per_build + display_cover_screws_per_build
                  + faucet_display_cover_screws_per_build + c14_screws_per_build
                  + touchflo_screws_per_build + dock_keeper_screws_per_build
                  + dock_rear_support_locks_per_build)

# And every M3 x 10: the PSU's four and the ground-stack clamp's one.
m3x10_per_build = shelf_psu_screws_per_build + shelf_ground_screws_per_build

# And every M3 x 6: the relays'.
m3x6_per_build = shelf_relay_screws_per_build

# THE SHELF'S AND THE INLET'S SCREW STACKS, each read off what stands under the head and the
# bore the screw lands in. A +X wall insert seats on its boss where the boss stands, on the
# wall where the wall is the body's mounting face, and behind a recess where the main board's
# tails need one (`enclosure.east_boss_insert_setback`); its bore runs as far as
# `enclosure.east_boss_bore_end` lets it. The reach past the insert's mouth fills the 4 mm
# insert, or nearly, and stops short of the blind end.
psu_screw_len, pcba_screw_len, relay_screw_len, c14_screw_len = 10.0, 8.0, 6.0, 8.0


def _east_seats():
    """Each +X wall station as `(stands, insert setback, bore depth from the insert's seat)`."""
    inner, outer = _f.box["inner"], _f.box["outer"]
    for station in _east_bosses:
        sy, sz, tip = station[:3]
        piece = ("front" if sy <= _f.box["y_joint"] else "back",
                 "top" if sz > _enc.z_seam else "bottom")
        root = _enc.piece_root_faces(inner, *piece)[1]
        stands = root - tip >= _enc.east_boss_min_stand - _enc.stated_bound_tol
        setback = _enc.east_boss_insert_setback(station)
        seat = (tip if stands else root) + setback
        yield stands, setback, _enc.east_boss_bore_end(sy, seat, outer) - seat


_seats = list(_east_seats())
pcba_insert_recess = max(setback for _stands, setback, _depth in _seats)
pcba_bore = min(depth for _stands, setback, depth in _seats if setback)
psu_bore = min(depth for stands, setback, depth in _seats if not stands and not setback)
relay_bore = min(depth for stands, setback, depth in _seats if stands and not setback)
psu_screw_reach = psu_screw_len - _psu.ledge_h
pcba_screw_reach = pcba_screw_len - _pcba._thickness - pcba_insert_recess
relay_screw_reach = relay_screw_len - _relay.pcb_t
c14_screw_reach = c14_screw_len - _c14.FLANGE_T - _c14.RIM_PROUD

# One screw and insert per ear, on each of the magnetic pair's two halves.
pogo_fasteners_per_build = 2 * len(_enc._pogo.ear_xs())

# And every M3 x 60: the pump clamp's two, the one station whose screw is as long as the field
# it crosses.
m3x60_per_build = pump_cap_screws_per_build

# Black-oxide M3 × 12 screws have no stations in this build.
m3x12_per_build = 0

# WHICH M3 BODY EACH STATION TAKES. ruthex's short and full-length M3 are the same insert but
# for the body — same knurl, same recommended hole — so this split is a statement about BORE
# DEPTH and nothing else. A station is on the long list when the bore it already cuts is deeper
# than 5.7 mm of brass plus the relief its own screw needs; it is on the short list when giving
# it that depth would cost geometry the machine is spending elsewhere.
#
# Short insert families and the stock available behind their seats:
#   touch-flo base pods  — the blind pilots receive 4 mm inserts above the locating sockets
#   +X wall bosses       — the bore ends at `flute_backing`; deeper walks the electronics bay in
m3_long_inserts_per_build = (
    foam_cap_inserts_per_build
    + reservoir_cap_inserts_per_build
    + cond_inserts_per_build
    + nameplate_inserts_per_build
    + display_cover_inserts_per_build
    + pump_cap_inserts_per_build
)
m3_short_inserts_per_build = (
    touchflo_inserts_per_build
    + shelf_inserts_per_build
    + faucet_display_cover_inserts_per_build
    + c14_inserts_per_build
    + dock_keeper_inserts_per_build
    + dock_rear_support_locks_per_build
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
    + pump_cap_screws_per_build
    + c14_screws_per_build
    + dock_keeper_screws_per_build
    + dock_rear_support_locks_per_build
)
total_m5_screws_per_build = floor_screws_per_build + enclosure_seam_rods_per_build

# Reservoir-cap vent filters per build (2).
vent_filters_per_build = vent_filters_per_reservoir_cap * reservoirs_per_build

# --- what a zip tie has to close, at every seat printed for one -------------
#
# WHAT PICKS THE LENGTH IS THE LOOP AND NOT THE WIDTH. A zip tie turns INSIDE its cavity, so
# what it reaches round is the body together with the web behind it — the convex perimeter of
# that pair — and the §11 rows quote it because that figure is what puts a seat on the 4", the
# 6" or the 8". Every one below is read off the module that draws the seat, so a wall or a slip
# that moves carries the rows with it.
#
# A SEAT IS ALL THE HULL KNOWS. `enclosure.tube_anchor_tie_loop` is the ribs' and the meter's
# alike — a flow-meter anchor reaches `flow_meter_anchor_wall` off the arm's axis where a rib
# reaches `wall`, and both are the box's own three millimetres.
digiten_tie_loop = _enc.tube_anchor_tie_loop(_digiten.port_dia / 2.0 + _ea.DIGITEN_SEAT_SLIP)
# EVERY RIB HOLDING A RUN IS BORED FOR THE ONE STOCK, which is why the row quotes one figure for
# all of them rather than reading them apiece.
_run_seats = {round(station[3], 6) for station in _f.pack["tube_anchors"]}
if len(_run_seats) != 1:
    raise ValueError(
        f"the box's run anchors are bored at {sorted(_run_seats)} and bom.md §11 quotes one loop "
        f"for every rib holding a tube. Either they go back on one stock or the row reads them "
        f"apiece.")
run_tie_loop = _enc.tube_anchor_tie_loop(next(iter(_run_seats)))
# THE RIBS BORED FOR A BODY take whatever section that body offers, so each answers on its own.
# `BODY_ANCHOR_SITES` is the table `check_body_seated` grades the built pieces against, and the
# radius is the reference module's — read here by name rather than off a row's position.
_body_seats = {name: section()[1] + _ea.BODY_ANCHOR_SLIP
               for name, section, _root, _piece in _ea.BODY_ANCHOR_SITES}
# The seat is the row's own fourth field, the same station `tube_anchors` reads above —
# named by index from the FRONT because a row may carry more behind it, and a read off
# its last position turns whatever is appended next into this radius.
_bored = {round(station[3], 6) for station in _f.pack["body_anchors"]}
_missing = sorted(n for n, r in _body_seats.items() if round(r, 6) not in _bored)
if _missing:
    raise ValueError(
        f"{_missing} name a section this table quotes a loop for and the last build bored no rib "
        f"at that radius. The row reads the seat a body offers, so a body whose section moved "
        f"without its rib is a figure with nothing behind it.")
body_tie_loops = {n: _enc.tube_anchor_tie_loop(r) for n, r in _body_seats.items()}
# The flavour tap's two barrels are quoted separately: each loop follows its
# body's own seat radius through SPLIT_LOOP and FLOWREG_LOOP below.
# AND THE COLD CORE'S CAP CARRIES THE OTHER FAMILY, on its own wall and its own fastener.
# `_cold_core_interface` owns both hulls; the two chain ribs are one section, and the two side
# posts are not — a post's loop clears its own crown, which stands a wall proud of the pipe.
_chain_loops = {n: f"{cap_anchor_tie_loop(n):.3g}" for n in ("discharge-chain", "suction-chain")}
if len(set(_chain_loops.values())) != 1:
    raise ValueError(
        f"the cap's two chain ribs close {_chain_loops} and bom.md §11 quotes one figure for "
        f"both. Either they go back on one section or the row reads them apiece.")
chain_tie_loop = cap_anchor_tie_loop("discharge-chain")


def pack_line_cost(quantity, pack_price, pack_quantity):
    """Allocate the exact paid/list pack price; round only the final line."""
    allocated = Decimal(str(quantity)) * Decimal(pack_price) / Decimal(str(pack_quantity))
    return f"${allocated.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}"


def main(*, only_bom=False):
    casting = casting_estimate()
    receiver_slice = json.loads((_here.parent / "printed-parts" / "enclosure" /
        "pump-dock" / "print-preparation" / "2026-10-18-receivers-siraya85a-mark1" /
        "native-readback.json").read_text())
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
        "DOCK_MAGNETS": f"{dock_magnets_per_build:.4g}",
        "DOCK_MAGNET_COST": pack_line_cost(dock_magnets_per_build, "70.54", 50),
        # Reeds.
        "REEDS_PER_RES": f"{reeds_per_reservoir:.4g}",
        "CARB_REEDS": f"{reeds_per_carbonator:.4g}",
        "RES_REEDS_TOTAL": f"{reservoir_reeds_total:.4g}",
        "REEDS_TOTAL": f"{total_reeds_per_build:.4g}",
        # Flavor subsystem.
        "SOLENOIDS": f"{solenoid_count:.4g}",
        "TEES": f"{tee_count:.4g}",
        "FOUR_INCH_TIES": f"{four_inch_ties_per_build:.4g}",
        "FOUR_INCH_TIES_COST": pack_line_cost(four_inch_ties_per_build, "4.28", 200),
        "SIX_INCH_TIES": f"{six_inch_ties_per_build:.4g}",
        "SIX_INCH_TIES_COST": pack_line_cost(six_inch_ties_per_build, "6.42", 100),
        "PP1208E_PANEL": f"{panel_umbilical_bulkheads:.4g}",
        "PP1208E_INLET": f"{panel_water_inlet_bulkheads:.4g}",
        "PP1208E_TOTAL": f"{pp1208e_per_build:.4g}",
        # The loops the §11 zip tie rows are picked by — one per seat printed for a tie,
        # each off the module that draws it. `ANCHOR_LOOP` and `WR1110_LOOP` are the same
        # names `_cold_core_interface` and `_internal_plumbing_sync` write elsewhere, so
        # `docgen.lint` holds this row against those pages rather than letting the two drift.
        "DIGITEN_LOOP": f"{digiten_tie_loop:.3g} mm",
        "CARB_1_LOOP": f"{run_tie_loop:.3g} mm",
        "WATER_3_POST_LOOP": f"{cap_side_anchor_tie_loop('water-3'):.3g} mm",
        "FLUID_18_POST_LOOP": f"{cap_side_anchor_tie_loop('fluid-18'):.3g} mm",
        "SPLIT_LOOP": f"{body_tie_loops['water-split']:.3g} mm",
        "FLOWREG_LOOP": f"{body_tie_loops['flow-regulator']:.3g} mm",
        "ANCHOR_LOOP": f"{chain_tie_loop:.3g} mm",
        "WR1110_LOOP": f"{body_tie_loops['wr1110']:.3g} mm",
        "GAS_CHECK_LOOP": f"{body_tie_loops['gasher-co2']:.3g} mm",
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
        "SHELF_SCREWS_PCBA": f"{shelf_pcba_screws_per_build:.4g}",
        "SHELF_SCREWS_RELAY": f"{shelf_relay_screws_per_build:.4g}",
        "COND_INSERTS": f"{cond_inserts_per_build:.4g}",
        "COND_SCREWS": f"{cond_screws_per_build:.4g}",
        "SHORT_INSERT_LEN": f"{_enc.heatset_len:g}",
        "PSU_EAR_T": f"{_psu.ledge_h:g}",
        "PSU_BORE": f"{psu_bore:.3g}",
        "PSU_SCREW_REACH": f"{psu_screw_reach:.3g}",
        "PSU_SCREW_TIP": f"{psu_bore - psu_screw_reach:.3g}",
        "PCBA_BOARD_T": f"{_pcba._thickness:g}",
        "PCBA_INSERT_RECESS": f"{pcba_insert_recess:.3g}",
        "PCBA_BORE": f"{pcba_bore:.3g}",
        "PCBA_SCREW_REACH": f"{pcba_screw_reach:.3g}",
        "PCBA_SCREW_TIP": f"{pcba_bore - pcba_screw_reach:.3g}",
        "RELAY_BOARD_T": f"{_relay.pcb_t:g}",
        "RELAY_BORE": f"{relay_bore:.3g}",
        "RELAY_SCREW_REACH": f"{relay_screw_reach:.3g}",
        "RELAY_SCREW_TIP": f"{relay_bore - relay_screw_reach:.3g}",
        "C14_FLANGE_T": f"{_c14.FLANGE_T:g}",
        "C14_RIM_PROUD": f"{_c14.RIM_PROUD:g}",
        "C14_BORE": f"{_enc.heatset_depth:g}",
        "C14_SCREW_REACH": f"{c14_screw_reach:.3g}",
        "C14_SCREW_TIP": f"{_enc.heatset_depth - c14_screw_reach:.3g}",
        "M3X6_TOTAL": f"{m3x6_per_build:.4g}",
        "M3X6_COST": pack_line_cost(m3x6_per_build, "7.12", 120),
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
        "M3X60_TOTAL": f"{m3x60_per_build:.4g}",
        "M3X12_TOTAL": f"{m3x12_per_build:.4g}",
        "SEAM_RODS": f"{enclosure_seam_rods_per_build:.4g}",
        "SEAM_LONG_RODS": f"{enclosure_seam_long_rods_per_build:.4g}",
        "SEAM_SHORT_RODS": f"{enclosure_seam_short_rods_per_build:.4g}",
        "SEAM_WASHERS": f"{enclosure_seam_washers_per_build:.4g}",
        "SEAM_LONG_SCREWS_COST": pack_line_cost(enclosure_seam_long_rods_per_build, "12.07", 5),
        "SEAM_SHORT_SCREWS_COST": pack_line_cost(enclosure_seam_short_rods_per_build, "7.50", 40),
        "SEAM_WASHERS_COST": pack_line_cost(enclosure_seam_washers_per_build, "7.23", 100),
        "SEAM_INSERTS": f"{enclosure_seam_inserts_per_build:.4g}",
        "DOCK_STEMS": f"{len(_f.box['collet_plate']['holes'])}",
        "DOCK_RECEIVERS": f"{len(_f.box['collet_plate']['holes'])}",
        "DOCK_TPU_PLATE_G": f"{receiver_slice['estimated_filament_g']:.2f}",
        "DOCK_KEEPERS": f"{dock_keepers_per_build:.4g}",
        "DOCK_KEEPER_INSERTS": f"{dock_keeper_inserts_per_build:.4g}",
        "DOCK_KEEPER_SCREWS": f"{dock_keeper_screws_per_build:.4g}",
        "DOCK_REAR_SUPPORT_LOCKS": f"{dock_rear_support_locks_per_build:.4g}",
        "DOCK_LOCK_WASHERS": f"{dock_keeper_screws_per_build + dock_rear_support_locks_per_build:.4g}",
        "DOCK_LOCK_WASHERS_COST": pack_line_cost(
            dock_keeper_screws_per_build + dock_rear_support_locks_per_build, "7.82", 200),
        "PUMP_CAP_INSERTS": f"{pump_cap_inserts_per_build:.4g}",
        "PUMP_CAP_SCREWS": f"{pump_cap_screws_per_build:.4g}",
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
        "CAP_CRADLES": f"{len(cap_cradles):.4g}",
        "TOTAL_M3_INSERTS": f"{total_m3_inserts_per_build:.4g}",
        "M3_LONG_INSERTS": f"{m3_long_inserts_per_build:.4g}",
        "M3_LONG_INSERTS_COST": pack_line_cost(m3_long_inserts_per_build, "10.71", 100),
        "M3_SHORT_INSERTS": f"{m3_short_inserts_per_build:.4g}",
        "M3_SHORT_INSERTS_COST": pack_line_cost(m3_short_inserts_per_build, "10.71", 100),
        "POGO_FASTENERS": f"{pogo_fasteners_per_build:.4g}",
        "POGO_INSERTS_COST": pack_line_cost(pogo_fasteners_per_build, "8.57", 200),
        "POGO_SCREWS_COST": pack_line_cost(pogo_fasteners_per_build, "8.78", 50),
        "POGO_INSERT_SETBACK": f"{_enc.pogo_heatset_setback:.4g}",
        "POGO_INSERT_HOST_DEPTH": f"{_enc._pogo.ear_back() + _enc.pogo_heatset_setback + _enc.pump_contact_face_recess:.4g}",
        "POGO_THREAD_ENGAGEMENT": f"{max(0.0, min(_enc.pogo_heatset_len, _enc._pogo.EAR_FACE + _enc.pogo_screw_len - _enc._pogo.ear_back() - _enc.pogo_heatset_setback)):.4g}",
        "POGO_SCREW_TIP_AIR": f"{_enc._pogo.ear_back() + _enc.pogo_heatset_setback + _enc.pogo_heatset_len + _enc.pogo_heatset_relief - _enc._pogo.EAR_FACE - _enc.pogo_screw_len:.4g}",
        "DOCK_KEEPER_PILOT_DEPTH": f"{_enc._receiver.WALL_THICKNESS:.4g}",
        "DOCK_KEEPER_THREAD": f"{8.0 - _enc._receiver.KEEPER_THICKNESS - _enc._dock.LOCK_WASHER_T:.4g}",
        "DOCK_KEEPER_MOVING_AIR": f"{_enc._receiver.WALL_THICKNESS - (8.0 - _enc._receiver.KEEPER_THICKNESS - _enc._dock.LOCK_WASHER_T) + _enc.bay_back_y(_f.box['collet_plate']) - _enc.pump_cartridge_aft_y(_f.box['pump_trays'], _f.box['collet_plate']):.4g}",
        "C14_INSERTS": f"{c14_inserts_per_build:.4g}",
        "C14_SCREWS": f"{c14_screws_per_build:.4g}",
        "TOTAL_M5_INSERTS": f"{total_m5_inserts_per_build:.4g}",
        "M5_INSERTS_COST": pack_line_cost(total_m5_inserts_per_build, "10.71", 50),
        # Vent filters.
        "VENT_FILTERS": f"{vent_filters_per_build:.4g}",
        # Evaporator-coil copper (§5 GOORY row). LAID_FT is the copper a build CONSUMES —
        # the wrap as it lies on the carbonator, bridge lift and all. The mandrel's two shorter
        # readings are MANDREL_FT (what the tool holds) and SPRUNG_FT (what the same wraps
        # come to once off it) — three lengths, three names, so a doc says which it quotes.
        "PITCH": f"{_coil_mandrel_gen.pitch:.4g} mm",
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
        "WHITE_A_CUT": f"{_faucet_gen.white_cut_length(+1):g}",
        "WHITE_B_CUT": f"{_faucet_gen.white_cut_length(-1):g}",
        "WHITE_FLAVOR_FT": f"{_white_flavor_mm / 304.8:.2f}",
        "WHITE_FLAVOR_COST": f"${_white_flavor_mm / 304.8 * 0.14002:.2f}",
        "SODA_FAUCET_CUT": f"{_faucet_gen.soda_faucet_cut_length:g}",
        "SODA_FAUCET_FT": f"{_faucet_gen.soda_faucet_cut_length / 304.8:.2f}",
        "FAUCET_UNIONS": f"{len(_faucet_gen.flavor_sides):d}",
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
            "SEAM_LONG_RODS": f"{enclosure_seam_long_rods_per_build:.4g}",
            "SEAM_SHORT_RODS": f"{enclosure_seam_short_rods_per_build:.4g}",
            "SEAM_WASHERS": f"{enclosure_seam_washers_per_build:.4g}",
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
            "PUMP_CAP_SCREWS": f"{pump_cap_screws_per_build:.4g}",
            "DOCK_LOCKS": f"{dock_keeper_screws_per_build + dock_rear_support_locks_per_build:.4g}",
            "C14_SCREWS": f"{c14_screws_per_build:.4g}",
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
