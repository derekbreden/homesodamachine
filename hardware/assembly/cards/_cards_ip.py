"""IP / WR / FU — every fluid line the bench closes inside the box, the wiring
that lands on what those lines put there, and the umbilical that arrives at the
same wall.

One subsystem function, registered in `_cards_sync.SUBSYSTEMS`. The rules it
follows are that file's: read the figure off the built appliance, prefer a
structural reading to a coordinate, and assert the structure the sentence around
it stands on.

The three prefixes are one subsystem because they are one wall and one set of
runs seen three times. `internal-plumbing.md` closes the lines onto the back
wall's bodies; `wiring.md` lands a loom on the meter those lines hang; and
`faucet-and-umbilical.md` builds the bundle that pushes into the same row of
unions from outside. A pitch or an end-of-row stated on an FU card and on an IP
card is one fact, and the deck's one namespace is what stops the two disagreeing.
"""

DIA = "&#8960;"     # ⌀


def internal_plumbing(m):
    """The runs `_lines.py` draws between the bodies `front_half.py` places, the
    manifold's own census, and the row of unions the risers land on."""
    import front_half as _fh
    import manifold_layout as _ml
    import _lines
    import _scorecard as _card
    import digiten_flow_sensor as _digiten
    import drip_pan as _pan
    from _cold_core_interface import cap_conduit_bore_radius, cap_cradles

    a, pack, box = m.a, m.pack, m.box
    runs = {r.id: r for r in a.runs}
    frames = a.frames

    def port(body, name):
        """One placed body's mouth, as `(position, axis)` in world."""
        pos, axis, _d = frames[body].ports[name]
        return tuple(pos), tuple(round(v, 6) for v in axis)

    def corners(rid):
        """How many times a run turns. A run with none is a butt-length of stock
        cut to two mouths facing each other, which is a different bench job."""
        return len(runs[rid].pts) - 2

    def mm(rid):
        return f"{runs[rid].length:.0f} mm"

    DOWN = (0.0, 0.0, -1.0)
    UP = (0.0, 0.0, 1.0)
    EAST = (1.0, 0.0, 0.0)

    # ── the CO2 path (IP-01) ───────────────────────────────────────────────
    # IP-01's title, its chain and its whole picture say the gas comes in at the
    # BACK WALL. Nothing is cut in the front wall at all, and that has no number
    # in it to drift — so this assertion is the only thing that can put the card
    # back if a front-face bore ever appears.
    assert not pack.front_ports and not box.front_ports, (
        f"{len(box.front_ports)} station(s) are cut in the front wall — IP-01 brings the CO2 "
        f"in at the back and says nothing at all is cut in the front")
    # The bore, off the call that STRIKES it rather than a second copy of its
    # arithmetic: `co2_wall_port` is what `front_half.pack` fills `back_ports` with,
    # so a change to how the hole is struck arrives here instead of leaving this
    # assertion checking the wall against a rule it no longer follows.
    co2_bore = _fh.co2_wall_port(a.co2_inlet_carry)[3]
    assert any(p[0] == "round" and abs(p[3] - co2_bore) < 1e-6 for p in box.back_ports), (
        f"no {co2_bore:.4g} mm bore stands in the back wall — IP-01 threads the GASHER onto a "
        f"DERPIPE clamped through it, and the back wall is where the card sends the bench")
    # The regulator threads onto NOTHING: a tube reaches it and a tube leaves it,
    # which is the fitting count bom.md §4 buys and the reason IP-01 draws it
    # standing apart from the check rather than screwed to it.
    assert (runs["co2-1"].frm, runs["co2-1"].to) == ("gasher-co2.outlet", "wr1110.inlet"), (
        f"`co2-1` runs {runs['co2-1'].frm} → {runs['co2-1'].to} — IP-01 hops check to regulator")
    assert runs["co2-2"].frm == "wr1110.outlet" and runs["co2-2"].to == "foam-assembly.co2-in", (
        f"`co2-2` runs {runs['co2-2'].frm} → {runs['co2-2'].to} — IP-01 takes the regulator's "
        f"outlet down onto the cold core's own `co2-in` cap conduit")
    # Every warm-side termination on the core opens UPWARD on the lid, so a line
    # arrives at the deck and leans into a countersunk lip. IP-01 and IP-05 both
    # draw that, and neither is drawing a fitting.
    for conduit in ("co2-in", "water-in", "carb-water-out"):
        assert port("foam-assembly", conduit)[1] == UP, (
            f"the core's `{conduit}` no longer opens upward — IP-01/IP-02/IP-05 lay a tube end "
            f"into it from the deck the electronics shelf stands on")

    # ── the water path (IP-02) ─────────────────────────────────────────────
    # THERE IS NO `water-1`. The bulkhead's inboard collet and the ASSE chain's
    # inlet collet meet face to face down one axis, so the first tube in the
    # machine is a length of stock both grips swallow whole. A run reappearing
    # between them is a joint IP-02 does not build.
    assert "water-1" not in runs, "`water-1` is drawn again — IP-02 butts the bulkhead's "\
        "inboard collet straight onto the ASSE chain's inlet"
    assert port("bulkhead-water", "inboard")[0] == port("asse1022-assembly", "tube-in")[0], (
        "the back-wall union's inboard collet and the ASSE chain's inlet no longer stand on one "
        "point — IP-02 meets them face to face with nothing between them to turn")
    # The split's branch looks straight DOWN at the storey the pump stands on, so
    # `water-3` leaves the west lane by falling out of it. IP-02 and IP-04 both
    # draw that branch, and IP-04's caption is about which way it points.
    split_branch = port("water-split", "to-vk")[1]
    assert split_branch == DOWN, (
        f"the water split's branch points {split_branch} — IP-02 drops `water-3` out of the west "
        f"lane and IP-04's caption is about that branch")
    # A run with no corner is a butt-length cut to two grips; a run with corners
    # is a route. Four of this procedure's lines are the first kind and the cards
    # say so in those words.
    for rid in ("water-2", "water-4", "co2-1", "carb-2", "fluid-1"):
        assert corners(rid) == 0, (
            f"`{rid}` now turns {corners(rid)} time(s) — the cards cut it as a straight length "
            f"between two mouths facing each other")

    # The two pump-port stubs: the only runs on the machine drawn on the reinforced
    # PVC's own bend floor, which is what makes them the only clamped joints. Both
    # ends of each is a barb, and IP-02 closes a clamp on every one — so the clamp
    # count is that census and not a number kept beside it. IP-06 witnesses the same
    # clamps, so the two cards cannot count them differently.
    hose_stubs = sorted(rid for rid, r in runs.items() if r.bend == _lines.HOSE_BEND)
    assert hose_stubs == ["water-6", "water-7"], (
        f"the reinforced-PVC stubs are {hose_stubs} — IP-02 cuts the pump's two ports and "
        f"IP-06 witnesses their clamps, and every other line on the machine is push-fit")
    pump_clamps = 2 * len(hose_stubs)

    # The carbonated riser is cut per run, and the meter standing between the two runs
    # is what makes its insulation two pieces rather than one. A meter that moved off
    # the riser would leave one run, and FU-03 would sleeve one piece.
    carb_runs = sorted(rid for rid in runs if rid.startswith("carb-"))
    assert carb_runs == ["carb-1", "carb-2"], (
        f"the carbonated riser is {carb_runs} — IP-05 climbs it in two lengths with the "
        f"DIGITEN made up between them, and FU-03 foams one piece per run")

    # ── the flavor manifold (IP-03, IP-04) ─────────────────────────────────
    valves = sorted(n for n in _ml.P if n.startswith("V-"))
    tees = sorted(n for n in _ml.P if n.startswith("Y-"))
    # IP-03 lays out the junctions BY NAME. Y-E and Y-H were the two reservoir
    # junctions; neither reservoir has one now, so the names have to be read off
    # the pack rather than typed beside the count.
    assert tees == ["Y-A", "Y-B", "Y-C", "Y-D", "Y-F", "Y-G"], (
        f"the pack's junctions are {tees} — IP-03 lays them out by name and IP-04 maps them")
    assert not _ml.JOINS, (
        f"{len(_ml.JOINS)} elbow(s) are posed in the pack — IP-03 says every junction is a Tee "
        f"and every valve is butted collet to collet, so an elbow is a fitting no card fits")
    # NEITHER RESERVOIR HAS A JUNCTION. Each carries two mouths of its own, so a
    # fill valve reaches its fill conduit and a draw conduit reaches its draw
    # valve with nothing standing between — which is what IP-04's channel map
    # draws, and what a returning Y would silently make wrong.
    for rid, end in (("fluid-14", "reservoir-a-fill"), ("fluid-24", "reservoir-b-fill")):
        assert runs[rid].to == f"foam-assembly.{end}", (
            f"`{rid}` lands on {runs[rid].to} — IP-04 takes the fill valve's outlet straight "
            f"onto the reservoir's own fill conduit, with no junction between")
    for rid, end in (("fluid-16", "reservoir-a"), ("fluid-26", "reservoir-b")):
        assert runs[rid].frm == f"foam-assembly.{end}", (
            f"`{rid}` starts at {runs[rid].frm} — IP-04 draws the reservoir's own draw conduit "
            f"straight up into its valve, with no junction between")
    # The manifold's tube inventory comes out of `fluid-topology.md`'s own tables
    # via the scorecard, so IP-03's pre-cut count cannot drift from the topology
    # the bench tags each segment against.
    conns = _card.load_connections(a.runs)
    fluid = [c for c in conns if c.kind == "fluid"]
    butted = sum(1 for c in fluid if c.made == "butt")
    hairpins = sum(1 for c in fluid if c.made == "fold")

    # ── the umbilical row and the risers (IP-05, FU-04, WR-05) ─────────────
    # Read as an ARRANGEMENT: three unions, one line, one pitch, and which end of
    # the row each tube lands on. IP-05 and FU-04 both describe that row, and
    # both used to describe a triangle.
    row = sorted(_fh.PANEL_X.items(), key=lambda kv: kv[1])          # west → east
    zs = {round(port(n, "tube-in")[0][2], 6) for n in _fh.PANEL_X}
    assert len(zs) == 1, (
        f"the umbilical unions stand on {len(zs)} stratum/strata — IP-05 and FU-04 present the "
        f"bundle to ONE line and flex the three tubes apart along it")
    order = [n for n, _x in row]
    assert order == ["bulkhead-flavor-b", "bulkhead-flavor-a", "bulkhead-carb"], (
        f"the row reads {order} west to east — IP-05 sends each riser to a named place in it")
    # The meter splits the riser rather than hanging off it: both its mouths are
    # the riser's, it lies on the carb union's own column and stratum, and it
    # stands FORWARD of the union it feeds. WR-05 lands SIG-4 on it there.
    meter_in, meter_out = port("digiten-flow", "inlet"), port("digiten-flow", "outlet")
    union_in = port("bulkhead-carb", "tube-in")
    assert meter_out[0][0] == union_in[0][0] and meter_out[0][2] == union_in[0][2], (
        "the DIGITEN no longer lies on the carb union's own column and stratum — WR-05 and IP-05 "
        "both put it inline on the riser, and `carb-2` is a straight because of it")
    assert meter_out[0][1] < union_in[0][1] and meter_in[0][1] < meter_out[0][1], (
        "the DIGITEN no longer lies fore and aft forward of the carb union — IP-05 closes "
        "`carb-1` into its inlet from the deck and `carb-2` out of its outlet into the union")
    boss = a.carries["digiten-flow"](_digiten.wire_exit())[1]
    boss = tuple(round(v, 6) for v in boss)
    assert boss == EAST, (
        f"the meter's pigtail boss points {boss} — WR-05 reaches it from the +X flank the "
        f"controller board stands on")
    # `fluid-18` is the appliance's longest single run, which is the whole reason
    # IP-05 warns the bench about it.
    longest = max(a.runs, key=lambda r: r.length).id
    assert longest == "fluid-18", (
        f"the longest run in the appliance is `{longest}` — IP-05 calls the flavor-A riser that")

    # ── V-K and the vent (WR-04, IP-06) ────────────────────────────────────
    # V-K is the one valve outside the manifold. It presses into a cradle the cold core's
    # cap lid prints for it — four corner posts into four sockets, nothing bolted — forward
    # of the suction chain and firing aft. Not the back wall beside the water inlet, which
    # is where a wiring card looking for it would otherwise send the bench.
    #   THE CORE'S BOX TOP IS NOT THE FACE IT STANDS ON. That same lid stands a taller pad
    # under each flavour valve, so the solid's `zmax` is one of THOSE seats and a body placed
    # on it would be standing on another valve's cradle. `front_half.cap_face` is the lid's
    # own outer face and `cap_cradles` is the seat each valve takes over it, which is the pair
    # this reads V-K against.
    vk, pump = _fh.box(a.pack_solids["vk-solenoid"]), _fh.box(a.pack_solids["seaflo-pump"])
    chain = _fh.box(a.pack_solids["suction-chain"])
    vk_x = (vk.xmin + vk.xmax) / 2.0
    assert "vk-solenoid" in cap_cradles, (
        f"the cold core's cap prints cradles for {sorted(cap_cradles)} and none of them is "
        f"V-K's — WR-04 sends the DC-9 branch to a valve standing on that cap, and a valve "
        f"with no cradle there stands somewhere else")
    vk_seat = cap_cradles["vk-solenoid"].seat
    face = _fh.cap_face(a.pack_solids["foam-assembly"])
    assert abs(vk.zmin - (face + vk_seat)) <= _fh.CRADLE_TOL, (
        f"V-K's mounting plane stands {vk.zmin - face:.4g} mm over the cold core's cap face "
        f"and its cradle seats it at {vk_seat:.4g} mm — WR-04 sends the DC-9 branch to a "
        f"valve pressed home in that cradle")
    assert vk.ymax <= chain.ymin, (
        "V-K no longer stands forward of the suction chain — IP-02 has it firing aft into the "
        "collet that feeds the pump")
    assert port("vk-solenoid", "outlet")[1] == (0.0, 1.0, 0.0), (
        "V-K no longer fires aft into the collet that feeds the pump — IP-02 mounts it taking "
        "no turn at all because its own frame already runs the flow that way")
    # The vent weeps to atmosphere and the drip IS the telltale, so IP-06 walks
    # the column straight down from its tip to the pan.
    assert port("asse1022-assembly", "vent-tip")[1] == DOWN, (
        "the ASSE vent no longer hangs straight down — IP-06 checks the fall's column clear from "
        "the stub's tip to the drip pan")

    facts = {
        # CO2 — IP-01.
        "CO2_1_LEN": mm("co2-1"),
        "CO2_2_LEN": mm("co2-2"),
        "CO2_2_CORNERS": f"{corners('co2-2')}",
        "CAP_CONDUIT_D": f"{DIA}{2 * cap_conduit_bore_radius:.4g} mm",
        # Water — IP-02, IP-06. The two pump-port stubs are the only 3/8" in the
        # machine and the only clamped joints; one count under one name, because
        # IP-02 closes them and IP-06 witnesses them.
        "WATER_2_LEN": mm("water-2"),
        "WATER_3_CORNERS": f"{corners('water-3')}",
        "WATER_4_LEN": mm("water-4"),
        "WATER_5_CORNERS": f"{corners('water-5')}",
        "SUCTION_STUB_LEN": mm("water-7"),
        "DISCHARGE_STUB_LEN": mm("water-6"),
        "PVC_BEND_R": f"{runs['water-7'].bend:.4g} mm",
        "PUMP_CLAMPS": f"{pump_clamps}",
        "VENT_GAP": f"{_pan.VENT_GAP:.4g} mm",
        # The manifold — IP-03, IP-04.
        "MANIFOLD_VALVES": f"{len(valves)}",
        "MANIFOLD_TEES": f"{len(tees)}",
        "MANIFOLD_SEGMENTS": f"{len(fluid)}",
        "MANIFOLD_LIMBS": f"{len(_ml.LIMBS)}",
        "MANIFOLD_BUTTS": f"{butted}",
        "MANIFOLD_HAIRPINS": f"{hairpins}",
        "BARB_TEES": f"{len(_ml.BARB_OF)}",
        "SPLIT_BRANCH": "down",
        # The row on the back wall — IP-05, FU-04.
        "UMBILICAL_UNIONS": f"{len(_fh.PANEL_X)}",
        "FLAVOR_A_STATION": "middle",
        "FLAVOR_B_END": "west",
        # The three risers — IP-05, WR-05.
        "CARB_1_LEN": mm("carb-1"),
        "CARB_1_CORNERS": f"{corners('carb-1')}",
        "CARB_2_LEN": mm("carb-2"),
        "FLUID_18_LEN": mm("fluid-18"),
        "FLUID_28_LEN": mm("fluid-28"),
        "CARB_FOAM_PIECES": f"{len(carb_runs)}",
        # WR — where the two bodies a loom reaches actually stand. WR-04 walks the
        # bench to V-K OFF THE PUMP, the one body on that side a hand cannot miss, so
        # the side is read against the pump rather than against the machine's centreline.
        "VK_SIDE": "east" if vk_x > (pump.xmin + pump.xmax) / 2.0 else "west",
        "METER_BOSS": "east" if boss == EAST else "west",
    }

    cards = {
        "ip-01-co2-path": {
            "CO2_HOLE_D", "CO2_1_LEN", "CO2_2_LEN", "CO2_2_CORNERS", "CAP_CONDUIT_D"},
        "ip-02-water-path": {
            "WATER_2_LEN", "WATER_3_CORNERS", "WATER_4_LEN", "WATER_5_CORNERS",
            "SUCTION_STUB_LEN", "DISCHARGE_STUB_LEN", "PVC_BEND_R", "PUMP_CLAMPS"},
        "ip-03-manifold-valves-tees": {
            "MANIFOLD_VALVES", "MANIFOLD_TEES", "MANIFOLD_SEGMENTS", "MANIFOLD_LIMBS",
            "MANIFOLD_BUTTS", "MANIFOLD_HAIRPINS"},
        "ip-04-manifold-pumps-channels": {
            "MANIFOLD_VALVES", "MANIFOLD_TEES", "BARB_TEES", "SPLIT_BRANCH"},
        "ip-05-risers": {
            "UMBILICAL_UNIONS", "UMBILICAL_PITCH", "CARB_END", "FLAVOR_A_STATION",
            "FLAVOR_B_END", "CARB_1_LEN", "CARB_1_CORNERS", "CARB_2_LEN", "FLUID_18_LEN",
            "FLUID_28_LEN", "CARB_FOAM_PIECES"},
        "ip-06-witness-tidy": {"PUMP_CLAMPS", "VENT_GAP"},
        "wr-04-cabinet-12v-runs": {"VK_SIDE"},
        "wr-05-signal-looms": {"CARB_2_LEN", "METER_BOSS"},
        "fu-04-sleeve-the-bundle": {"UMBILICAL_UNIONS", "UMBILICAL_PITCH", "CARB_END"},
    }
    return facts, cards
