"""Doc-sync driver for hardware/ledger/bom.md.

Run: tools/cad-venv/bin/python hardware/scripts/_bom_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent  # = hardware/scripts/
sys.path.insert(0, str(_here.parent / "printed-parts" / "cadlib"))
sys.path.insert(0, str(_here.parent / "printed-parts" / "cold-core"))
sys.path.insert(0, str(_here.parent / "printed-parts" / "cold-core" / "reservoir"))
sys.path.insert(0, str(_here.parent / "printed-parts" / "faucet"))
sys.path.insert(0, str(_here.parent / "printed-parts" / "faucet" / "faucet-shell"))
sys.path.insert(0, str(_here.parent / "reference" / "beduan-solenoid"))
sys.path.insert(0, str(_here.parent / "manifold-layout"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

from _cold_core_interface import (attachment_xy_positions, cap_anchor_tie_loop,
                                  cap_cradles, cap_side_anchor_tie_loop, deck_mounts,
                                  deck_mount_xy)
from _reed_channels import reeds_per_reservoir
from docgen import load_module, substitute_md
from reservoir import insert_positions_for_side_plus_1
from faucet_shell import base_pod_centers, display_cover_screw_s

import manifold_layout as ml
import _facts
import enclosure_assembly as _ea  # noqa: F401  — holds the closure these docs watch
import ground_ring_stack as _gnd  # on the path once `enclosure_assembly` is imported
import enclosure as _enc  # likewise
import nameplate as _np  # likewise
import digiten_flow_sensor as _digiten  # likewise — the arm the meter's anchors bore for

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


# Pressure vessel geometry: two laser-welded SS endcap plates per
# vessel, four 1/4" NPT ports tapped into the plates (water in, water
# out, CO2 in, PRV).
end_cap_plates_per_carbonator = 2
carbonator_ports = 4

# Flavor reservoirs per appliance.
reservoirs_per_build = 2

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

# The placed pack turns no line on a fitting, so there is no union-elbow row in
# the BOM. `manifold_layout.JOINS` is empty — every valve is butted collet to
# collet down its limb, every junction is a Tee, and each pump barb is taken by a
# tee's branch, which is what puts that tee's run across the head's face.
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

# And the cradles hold valves this machine actually has. A row for a body the pack does not
# place is a seat printed into the lid for nothing, which costs material on every build.
_orphans = sorted(set(cap_cradles) - _placed)
assert not _orphans, (
    f"the cold core's cap prints a cradle for {_orphans}, and the machine places no such "
    f"body — a cradle is a valve seat, and a seat with no valve is a pad on the lid")

# Foam-cap hardware: 6 clamp inserts + 6 M3 × 25 screws per face, both faces, PLUS
# the top cap's deck-mount columns — each takes a ruthex short in its top bore, and
# each is a bolt station, and the water pump is the one module that uses any: the
# clamp screws are 1:1 with the clamp inserts, and a deck column takes a screw only
# where a module bolts into it — which today is `seaflo-pump`'s four and nothing
# else. The three valves that stand on the top lid press into cradles printed in
# it, which take neither.
foam_cap_deck_inserts_per_build = sum(len(deck_mount_xy(n)) for n in deck_mounts)
pump_mount_screws_per_build = len(deck_mount_xy("seaflo-pump"))
foam_cap_clamp_inserts_per_build = inserts_per_foam_cap_face * foam_cap_faces
foam_cap_inserts_per_build = (foam_cap_clamp_inserts_per_build
                              + foam_cap_deck_inserts_per_build)
foam_cap_screws_per_build = foam_cap_clamp_inserts_per_build  # 1:1 clamp only

# Reservoir-cap hardware (12 inserts + 12 M3 × 12 screws).
reservoir_cap_inserts_per_build = inserts_per_reservoir_cap * reservoirs_per_build
reservoir_cap_screws_per_build = reservoir_cap_inserts_per_build  # 1:1

# Touch-flo plate-to-shell hardware (3 inserts + 3 M3 × 12 screws, one
# per base pod).
touchflo_inserts_per_build = len(base_pod_centers)
touchflo_screws_per_build = touchflo_inserts_per_build  # 1:1

# The faucet display's face plate: one station on the tip's centreline
# above the device's north edge, so one insert in the shell and the one
# M3 x 8 that threads it.
faucet_display_cover_stations = ((0.0, display_cover_screw_s),)
faucet_display_cover_inserts_per_build = len(faucet_display_cover_stations)
faucet_display_cover_screws_per_build = faucet_display_cover_inserts_per_build

# Electronics-shelf hardware (Zone B, assembly/power-column.md). The power column
# bolts to `enclosure-back-top`'s +X wall: `enclosure_assembly.wall_mounts` stands ONE BOSS PER
# HOLE in each body's own mounting pattern, and each boss is bored for a ruthex short.
# So the count is the pack's, not a number typed here — a body that gains a hole gains a
# boss, an insert and a screw together. No printed part on the shelf carries a boss of
# its own and no tray ships, so this is the whole of the shelf's retention.
shelf_inserts_per_build = len(_east_bosses)
# One SHCS in through each body from the room, into its boss's insert — 1:1 with the
# bosses. The ground stack's is the long one: it comes down through a fan of ring
# terminals before it reaches its insert, so its own pattern is what counts the M3 × 10s.
shelf_screws_per_build = shelf_inserts_per_build
shelf_long_screws_per_build = len(_gnd.holes)
shelf_short_screws_per_build = shelf_screws_per_build - shelf_long_screws_per_build

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
# the same screw the shelf's sixteen are.
cond_screws_per_build = cond_inserts_per_build

# Nameplate hardware (assembly/finish-pack-ship.md §3). `enclosure._nameplate` stands ONE BOSS
# PER SCREW STATION the plate declares, each bored for a ruthex short — so this count is the
# plate's the way the shelf's is the pack's.
nameplate_inserts_per_build = len(_np.screw_stations())
# One M3 × 8 in from outside through each counterbore into its boss's insert — 1:1 with the
# bosses, and the same screw the shelf's sixteen and the condenser's two are.
nameplate_screws_per_build = nameplate_inserts_per_build

# Display cover-plate hardware (assembly/enclosure-mechanical.md §8). THE PLATE IS THE
# DISPLAY'S ONLY FASTENING, so this pair of stations is what holds the screen in the facet.
# They are a mirrored pair on the facet's centreline at ±`enclosure.display_screw_x`:
# `enclosure._display_cuts` sinks a pad pocket at each and bores a ruthex short under its
# floor, and `display_cover` stands one pad on each — so the plate and the inset are cut for
# the same stations or neither drops into the other.
display_cover_stations = tuple(s * _enc.display_screw_x for s in (-1.0, +1.0))
display_cover_inserts_per_build = len(display_cover_stations)
# One M3 × 8 down each — the same screw the shelf's sixteen, the condenser's two and the
# nameplate's two are, reaching the land, the insert and the relief bored under it.
display_cover_screws_per_build = display_cover_inserts_per_build

# The pump clamp's two, read off its centre bridges. ONE TOP CLAMP CLOSES ON BOTH STAMPED
# BRACKETS (`enclosure.build_pump_cap`) and `cap_screw_ys` strikes a pair either side of the
# lane's mid-depth, so it is two screws and two inserts however many pumps the cradle carries.
# They are the box's M3 x 10 — `enclosure.screw_len` is the under-head length and each head
# sinks into a top-access counterbore. The lower cradle carries pump weight; these screws keep
# the clamp pressed onto the brackets.
pump_cap_inserts_per_build = len(_enc.cap_screw_ys(_f.box["inner"], _f.box["collet_plate"]))
pump_cap_screws_per_build = pump_cap_inserts_per_build

# THE COLLET PLATE'S OWN FIGURE, off `enclosure.plate_outline` and the hole row struck through
# it. §8 sells a shop a plain rectangle and sends the bench to `collet-plate.dxf` to hold the
# steel against, so what that row says about the shape is read here rather than typed there.
_collet_plate = _f.box["collet_plate"]
_collet_ring = _enc.plate_outline(_collet_plate)
_collet_x = [x for x, _ in _collet_ring]
_collet_z = [z for _, z in _collet_ring]
_collet_w = max(_collet_x) - min(_collet_x)
_collet_h = max(_collet_z) - min(_collet_z)
_collet_length_in = _collet_w / 25.4
_collet_area_in2 = _collet_w * _collet_h / 25.4 ** 2
_collet_stock_in = _ea.PLATE_T / 25.4
_collet_volume_in3 = _collet_area_in2 * _collet_stock_in
_collet_cost = 6.29 * _collet_volume_in3 + 1.89
# AND WHETHER IT IS STILL PLAIN. Zero is the whole of "no notch", and nothing else is: a closed
# outline lies inside the rectangle it is measured across, so equal areas leave it nowhere to be
# but ON that rectangle. A bite out of an edge, a chamfered corner and a stepped end each take
# area and leave the rectangle where it was — and so does a four-point outline that is not a
# rectangle, which is the reading a corner count cannot take.
_collet_notch = _collet_w * _collet_h - abs(sum(
    xa * zb - xb * za
    for (xa, za), (xb, zb) in zip(_collet_ring, _collet_ring[1:] + _collet_ring[:1]))) / 2.0
if _collet_notch > 1e-6:
    raise ValueError(
        f"the collet plate's outline falls {_collet_notch:.2f} mm² short of the "
        f"{_collet_w:.2f} × {_collet_h:.2f} mm rectangle it stands in, so something is cut "
        f"out of it. The §8 row is written for a plain rectangle — it prices the envelope as "
        f"solid stock and tells the bench a notched plate is the wrong steel. It needs "
        f"rewriting, not resyncing.")

# THE PLATE AND ITS RING ARE PRINTED PARTS AND §7 BILLS BOTH: the plate a row of its own, the
# gasket a line in the soft-seal sentence that carries every TPU seal in the machine. A body
# the machine places and the ledger does not buy is a part nobody prints.
_display_stack = {"display-cover", "display-gasket"} - set(_f.bodies)
assert not _display_stack, (
    f"the machine no longer stands {sorted(_display_stack)} — bom.md §7 bills the display's "
    f"cover plate and its gasket, and §13 bills the plate's two inserts and two M3 × 8")

# The enclosure's own SEAM SCREWS — the Y seam's cross-pins, the box's ONLY screws, and
# the heat-sets they land in. Every one drives from a ±X EXTERIOR face, so the bench
# closes the box from outside and nothing reaches in for them. Counted off the box's own
# stations rather than named here: the Y seam's `y_bosses`, a level for each end of each
# piece crossing it — the under-floor level pins the two bottoms, the under-ceiling one
# the two tops. The Z seams take no screw at all: each column's top SLIDES home on its
# hooked rails and the other column, screwed on at these four, is what blocks the way
# back out (`enclosure._z_rail_heads`). The heat-set is in the RECEIVING piece every
# time — the front pieces, on the Y seam.
enclosure_seam_screws_per_build = len(_f.box["y_bosses"])
# One insert per screw, pressed into the piece that screw lands in.
enclosure_seam_inserts_per_build = enclosure_seam_screws_per_build

# Every M3 × 8 in the build: the shelf's short ones, the condenser's aft pair, the nameplate's
# and the display cover plate's.
m3x8_per_build = (shelf_short_screws_per_build + cond_screws_per_build
                  + nameplate_screws_per_build + display_cover_screws_per_build
                  + faucet_display_cover_screws_per_build)

# And every M3 x 10: the ground-stack clamp's one, the pump clamp's two, and the enclosure's four
# seam screws.
m3x10_per_build = (shelf_long_screws_per_build + pump_cap_screws_per_build
                   + enclosure_seam_screws_per_build)

# And every M3 x 12 of the black-oxide 12.9 kind: the touch-flo plate's. (The 304
# stainless M3 x 12 is a different row — the reservoir caps' wetted-zone hardware — and
# is not counted here.)
m3x12_per_build = touchflo_screws_per_build

# WHICH M3 BODY EACH STATION TAKES. ruthex's short and full-length M3 are the same insert but
# for the body — same knurl, same recommended hole — so this split is a statement about BORE
# DEPTH and nothing else. A station is on the long list when the bore it already cuts is deeper
# than 5.7 mm of brass plus the relief its own screw needs; it is on the short list when giving
# it that depth would cost geometry the machine is spending elsewhere.
#
# The five short families and what each is paying for:
#   touch-flo base pods  — the pod is 8 boss hole + pocket + 3 cap = the visible base cylinder
#   +X wall bosses       — the bore ends at `flute_backing`; deeper walks the power column in
#   pump-clamp bosses    — the screw is thread-limited at 4 mm anyway, over 2.2 mm of cradle
#   faucet display cover — the shell's own land, one screw
#   Y-seam sockets       — pilot is `screw_len - seam_pin_shank_len`; longer wants an M3x12
m3_long_inserts_per_build = (
    foam_cap_inserts_per_build
    + reservoir_cap_inserts_per_build
    + cond_inserts_per_build
    + nameplate_inserts_per_build
    + display_cover_inserts_per_build
)
m3_short_inserts_per_build = (
    touchflo_inserts_per_build
    + shelf_inserts_per_build
    + faucet_display_cover_inserts_per_build
    + pump_cap_inserts_per_build
    + enclosure_seam_inserts_per_build
)

# Combined heat-set insert count across the appliance, by thread.
total_m3_inserts_per_build = m3_long_inserts_per_build + m3_short_inserts_per_build
total_m5_inserts_per_build = floor_inserts_per_build

# And the screws that go into them. EVERY INSERT IN THIS BUILD TAKES ONE SCREW, which is what
# the equality below says — an insert with no screw is a threaded hole nobody reaches, and the
# bench presses it anyway. `labor.md` §8 prices both passes off these two figures.
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
    + enclosure_seam_screws_per_build
)
total_m5_screws_per_build = floor_screws_per_build
for _thread, _inserts, _screws in (("M3", total_m3_inserts_per_build, total_m3_screws_per_build),
                                   ("M5", total_m5_inserts_per_build, total_m5_screws_per_build)):
    assert _screws == _inserts, (
        f"the build presses {_inserts} {_thread} heat-set inserts and drives "
        f"{_screws} {_thread} screws into them — name the body that bolts to the "
        f"{_inserts - _screws} left over, or stop printing them")

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
_run_seats = {round(r, 6) for *_s, r in _f.pack["tube_anchors"]}
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
_bored = {round(r, 6) for *_s, r in _f.pack["body_anchors"]}
_missing = sorted(n for n, r in _body_seats.items() if round(r, 6) not in _bored)
if _missing:
    raise ValueError(
        f"{_missing} name a section this table quotes a loop for and the last build bored no rib "
        f"at that radius. The row reads the seat a body offers, so a body whose section moved "
        f"without its rib is a figure with nothing behind it.")
body_tie_loops = {n: _enc.tube_anchor_tie_loop(r) for n, r in _body_seats.items()}
# THE FLAVOUR TAP'S PAIR IS QUOTED AS ONE. Their two barrels are within a hair of each other, so
# the row says "either" — which holds only while both read the same at the precision it prints.
_tap = {n: f"{v:.3g}" for n, v in body_tie_loops.items() if n != "wr1110"}
if len(set(_tap.values())) != 1:
    raise ValueError(
        f"the flavour tap's two barrels close {_tap} and bom.md §11 quotes one figure for either "
        f"of them. Either they go back on one section or the row reads them apiece.")
# AND THE COLD CORE'S CAP CARRIES THE OTHER FAMILY, on its own wall and its own fastener.
# `_cold_core_interface` owns both hulls; the two chain ribs are one section, and the two side
# posts are not — a post's loop clears its own crown, which stands a wall proud of the pipe.
_chain_loops = {n: f"{cap_anchor_tie_loop(n):.3g}" for n in ("discharge-chain", "suction-chain")}
if len(set(_chain_loops.values())) != 1:
    raise ValueError(
        f"the cap's two chain ribs close {_chain_loops} and bom.md §11 quotes one figure for "
        f"both. Either they go back on one section or the row reads them apiece.")
chain_tie_loop = cap_anchor_tie_loop("discharge-chain")


def main():
    variables = {
        # Carbonator.
        "END_CAPS": f"{end_cap_plates_per_carbonator:.4g}",
        "CARBONATOR_PORTS": f"{carbonator_ports:.4g}",
        # Reservoirs.
        "RESERVOIRS": f"{reservoirs_per_build:.4g}",
        "RESERVOIR_CAP_COUNT": f"{reservoirs_per_build:.4g}",
        # Reeds.
        "REEDS_PER_RES": f"{reeds_per_reservoir:.4g}",
        "CARB_REEDS": f"{reeds_per_carbonator:.4g}",
        "RES_REEDS_TOTAL": f"{reservoir_reeds_total:.4g}",
        "REEDS_TOTAL": f"{total_reeds_per_build:.4g}",
        # Flavor subsystem.
        "SOLENOIDS": f"{solenoid_count:.4g}",
        "TEES": f"{tee_count:.4g}",
        "PP1208E_PANEL": f"{panel_umbilical_bulkheads:.4g}",
        "PP1208E_INLET": f"{panel_water_inlet_bulkheads:.4g}",
        "PP1208E_TOTAL": f"{pp1208e_per_build:.4g}",
        # The collet plate's shape, the whole of what §8 asks a shop to cut. `PLATE_CORNERS`
        # and `PLATE_HOLES` are the same names `_enclosure_mechanical_sync` writes into §4 of
        # the assembly, each driver reading the same outline, so `docgen.lint` holds the two
        # sentences together rather than letting the ledger and the bench count differently.
        "PLATE_PLAN": f"{_collet_w:.2f} × {_collet_h:.2f} mm",
        "PLATE_LENGTH_IN": f"{_collet_length_in:.3f}",
        "PLATE_AREA": f"{_collet_area_in2:.2f}",
        "PLATE_VOLUME": f"{_collet_volume_in3:.2f}",
        "PLATE_COST": f"${_collet_cost:.2f}",
        "PLATE_CORNERS": f"{len(_collet_ring)}",
        "PLATE_HOLES": f"{len(_collet_plate['holes'])}",
        "PLATE_HOLE_D": f"Ø{_collet_plate['hole_d']:g}",
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
        # Heat-set insert + screw hardware.
        "FOAM_INSERTS": f"{foam_cap_inserts_per_build:.4g}",
        "FOAM_CLAMP_INSERTS": f"{foam_cap_clamp_inserts_per_build:.4g}",
        "FOAM_SCREWS": f"{foam_cap_screws_per_build:.4g}",
        "RES_INSERTS_PER_CAP": f"{inserts_per_reservoir_cap:.4g}",
        "RES_INSERTS": f"{reservoir_cap_inserts_per_build:.4g}",
        "RES_SCREWS": f"{reservoir_cap_screws_per_build:.4g}",
        "TOUCHFLO_INSERTS": f"{touchflo_inserts_per_build:.4g}",
        "TOUCHFLO_SCREWS": f"{touchflo_screws_per_build:.4g}",
        "FAUCET_DISPLAY_INSERTS": f"{faucet_display_cover_inserts_per_build:.4g}",
        "FAUCET_DISPLAY_SCREWS": f"{faucet_display_cover_screws_per_build:.4g}",
        "SHELF_INSERTS": f"{shelf_inserts_per_build:.4g}",
        "SHELF_SCREWS": f"{shelf_screws_per_build:.4g}",
        "SHELF_SCREWS_M3X8": f"{shelf_short_screws_per_build:.4g}",
        "COND_INSERTS": f"{cond_inserts_per_build:.4g}",
        "COND_SCREWS": f"{cond_screws_per_build:.4g}",
        "M3X8_TOTAL": f"{m3x8_per_build:.4g}",
        "NAMEPLATE_INSERTS": f"{nameplate_inserts_per_build:.4g}",
        "NAMEPLATE_SCREWS": f"{nameplate_screws_per_build:.4g}",
        "DISPLAY_COVER_INSERTS": f"{display_cover_inserts_per_build:.4g}",
        "DISPLAY_COVER_SCREWS": f"{display_cover_screws_per_build:.4g}",
        "SHELF_SCREWS_M3X10": f"{shelf_long_screws_per_build:.4g}",
        "M3X10_TOTAL": f"{m3x10_per_build:.4g}",
        "M3X12_TOTAL": f"{m3x12_per_build:.4g}",
        "SEAM_SCREWS": f"{enclosure_seam_screws_per_build:.4g}",
        "SEAM_INSERTS": f"{enclosure_seam_inserts_per_build:.4g}",
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
        "M3_SHORT_INSERTS": f"{m3_short_inserts_per_build:.4g}",
        "TOTAL_M5_INSERTS": f"{total_m5_inserts_per_build:.4g}",
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
    }

    substitute_md(
        _here.parent / "ledger" / "bom.md",
        variables=variables,
    )
    print("-> bom.md")

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
            "FOAM_CLAMP_INSERTS": f"{foam_cap_clamp_inserts_per_build:.4g}",
            "FOAM_SCREWS": f"{foam_cap_screws_per_build:.4g}",
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
            "NAMEPLATE_SCREWS": f"{nameplate_screws_per_build:.4g}",
            "FLOOR_SCREWS": f"{floor_screws_per_build:.4g}",
            "SOLENOIDS": f"{solenoid_count:.4g}",
        },
    )
    print("-> labor.md")


if __name__ == "__main__":
    main()
