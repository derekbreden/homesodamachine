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
sys.path.insert(0, str(_here.parent / "printed-parts" / "faucet" / "touch-flo-shell"))
sys.path.insert(0, str(_here.parent / "reference" / "beduan-solenoid"))
sys.path.insert(0, str(_here.parent / "manifold-layout"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

from _cold_core_interface import (attachment_xy_positions, cap_cradles, deck_mounts,
                                  deck_mount_xy)
from _reed_channels import reeds_per_reservoir
from docgen import load_module, substitute_md
from reservoir import insert_positions_for_side_plus_1
from touch_flo_shell import base_pod_centers

import manifold_layout as ml
import _facts
import enclosure_assembly as _ea  # noqa: F401  — holds the closure these docs watch
import ground_ring_stack as _gnd  # on the path once `enclosure_assembly` is imported
import nameplate as _np  # likewise

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

# The evaporator wrap AS DRAWN ON THE TANK (§5) — `coil_mandrel` strikes the helix, and
# `cold-core-layout/_coil` is where it is actually laid: sprung out to the tank's own radius
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
end_cap_plates_per_vessel = 2
vessel_ports_per_vessel = 4

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

# Rear-wall PP1208E bulkheads. Umbilical port: 3 on the rear wall
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
    f"the manifold poses {len(ml.JOINS)} elbow(s) ({sorted(ml.JOINS)}) and bom.md §4 buys "
    f"none — add the PP0308E row back with this count behind it")

# EVERY VALVE IN THIS MACHINE STANDS IN FOUR BOSSES (`valve_seat`) PRINTED INTO A PART §7
# ALREADY BILLS — three on the cold core's cap lid (`_cold_core_interface.cap_cradles`), eight on
# the two valve panels, which are `enclosure-front-top`'s own material
# (`enclosure._valve_panels`) — and both flavour pumps hang in a tray of that same piece's
# material (`enclosure._pump_trays`). So §7 carries no seat row of its own, and a plate appearing
# in the machine as a body rather than as a wall is what fails here.
_trays = sorted(n for n in _placed if "tray" in n or n.startswith("valve-panel"))
assert not _trays, (
    f"the machine places {len(_trays)} body(ies) under its valves and pumps ({_trays}) — a seat "
    f"is printed into the piece that carries it, and bom.md §7 bills no part standing under one")

# NO SHEET-METAL COVER SHIPS OVER THE COMPRESSOR, and that too is read off the placed machine.
# The compressor stands bare on the floor slab, bolted down through its own plate holes, with
# its terminal block and clip-on PTC open to the cabinet — the fire-enclosure gap `regulatory.md`
# carries against 60335-2-24. So §5 buys no cut cover, no pass-through gland and no bond stud for
# one, and THAT ONE BODY appearing in the placed machine is what fails here.
#
# Named, not matched on a substring. `prv-shroud` (`printed-parts/cold-core/prv-shroud/`) is a
# live printed part with a §7 row and a mass of its own, and the day it joins the pack a
# substring test would fail here holding out §5's compressor rows for a part that is not the
# compressor's.
COMPRESSOR_COVER = "compressor-shroud"
_cover = {COMPRESSOR_COVER} & _placed
assert not _cover, (
    f"the machine places `{COMPRESSOR_COVER}` and bom.md §5 bills no cover over the compressor "
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

# Electronics-shelf hardware (Zone B, assembly/electronics-shelf.md). The power column
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
# Every M3 × 8 in the build: the shelf's short ones, the condenser's aft pair and the plate's.
m3x8_per_build = (shelf_short_screws_per_build + cond_screws_per_build
                  + nameplate_screws_per_build)

# Combined heat-set insert count across the appliance, by thread.
total_m3_inserts_per_build = (
    foam_cap_inserts_per_build
    + reservoir_cap_inserts_per_build
    + touchflo_inserts_per_build
    + shelf_inserts_per_build
    + cond_inserts_per_build
    + nameplate_inserts_per_build
)
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


def main():
    variables = {
        # Carbonator vessel.
        "END_CAPS": f"{end_cap_plates_per_vessel:.4g}",
        "VESSEL_PORTS": f"{vessel_ports_per_vessel:.4g}",
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
        # Heat-set insert + screw hardware.
        "FOAM_INSERTS": f"{foam_cap_inserts_per_build:.4g}",
        "FOAM_CLAMP_INSERTS": f"{foam_cap_clamp_inserts_per_build:.4g}",
        "FOAM_SCREWS": f"{foam_cap_screws_per_build:.4g}",
        "RES_INSERTS_PER_CAP": f"{inserts_per_reservoir_cap:.4g}",
        "RES_INSERTS": f"{reservoir_cap_inserts_per_build:.4g}",
        "RES_SCREWS": f"{reservoir_cap_screws_per_build:.4g}",
        "TOUCHFLO_INSERTS": f"{touchflo_inserts_per_build:.4g}",
        "TOUCHFLO_SCREWS": f"{touchflo_screws_per_build:.4g}",
        "SHELF_INSERTS": f"{shelf_inserts_per_build:.4g}",
        "SHELF_SCREWS": f"{shelf_screws_per_build:.4g}",
        "SHELF_SCREWS_M3X8": f"{shelf_short_screws_per_build:.4g}",
        "COND_INSERTS": f"{cond_inserts_per_build:.4g}",
        "COND_SCREWS": f"{cond_screws_per_build:.4g}",
        "M3X8_TOTAL": f"{m3x8_per_build:.4g}",
        "NAMEPLATE_INSERTS": f"{nameplate_inserts_per_build:.4g}",
        "NAMEPLATE_SCREWS": f"{nameplate_screws_per_build:.4g}",
        "SHELF_SCREWS_M3X10": f"{shelf_long_screws_per_build:.4g}",
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
        "TOTAL_M5_INSERTS": f"{total_m5_inserts_per_build:.4g}",
        # Vent filters.
        "VENT_FILTERS": f"{vent_filters_per_build:.4g}",
        # Evaporator-coil copper (§5 GOORY row). LAID_FT is the copper a build CONSUMES —
        # the wrap as it lies on the tank, bridge lift and all. The mandrel's two shorter
        # readings are MANDREL_FT (what the tool holds) and SPRUNG_FT (what the same wraps
        # come to once off it) — three lengths, three names, so a doc says which it quotes.
        "PITCH": f"{_coil_mandrel_gen.pitch:.4g} mm",
        "NET_UNDERSIZE": f"{_coil_mandrel_gen.net_undersize:.4g} mm",
        "LAID_FT": f"{_wrap_mm / 304.8:.4g} ft",
        "MANDREL_FT": f"{_coil_mandrel_gen.mandrel_wrap_length / 304.8:.4g} ft",
        "STUB_INLET": f"{_coil_mandrel_gen.stub_allowance['inlet']:.4g} mm",
        "STUB_OUTLET": f"{_coil_mandrel_gen.stub_allowance['outlet']:.4g} mm",
        "ROLL_SHARE": f"1/{_coil_mandrel_gen.vessels_per_roll}",
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
            "SHELF_INSERTS": f"{shelf_inserts_per_build:.4g}",
            "SHELF_SCREWS": f"{shelf_screws_per_build:.4g}",
            "COND_SCREWS": f"{cond_screws_per_build:.4g}",
            "NAMEPLATE_SCREWS": f"{nameplate_screws_per_build:.4g}",
            "FLOOR_SCREWS": f"{floor_screws_per_build:.4g}",
            "SOLENOIDS": f"{solenoid_count:.4g}",
        },
    )
    print("-> labor.md")


if __name__ == "__main__":
    main()
