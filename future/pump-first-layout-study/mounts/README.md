# Bay electronics mounts

The relay modules stand beneath the horizontal supply on a single platform
joined to the retained cold-core lid. The eight distribution and signal WAGOs
stand on one west-wall/roof host. `candidate.json` includes the exact rotated
reference devices, every screw and tubular spacer, both printed hosts, blind
pilot cutters, nominal terminal mouths, and individual lever/wire working space.

## Relay floor

Both relay PCBs span X−24.5..45.5 at mounting face Z259.65. Relay1 occupies
Y423.5..440.5 and relay2 Y443.8..460.8. Their complete reference bodies span
Z257.65..276.65. The platform is 3 mm thick at Z253.4..256.4 and roots into the
5.4 mm retained lid. A 3 mm divider spans Y440.65..443.65 and finishes at Z278.
The relay crown has 13.1 mm air beneath the supply; the divider has 11.75 mm.

The accepted reservoir-A reed cable bore at (−31,458.3,253.4), diameter6.8 mm,
remains open normally. A nominal 35 mm vertical clearance reserve measured from
the lid base has 1.1 mm air to the platform,3.1 mm to relay2's PCB, and 2.365 mm to the
nearest screw. That reserve checks the host; it is not a measured rigid lead or
a manufacturer minimum straight exit. The controls candidate uses an immediate
bare-wire flattening region above the unchanged bore, with its individual bends
and finished lead dressing explicitly unqualified.

The eight calipered PCB hole axes are native. Four contact-end corners use
standard M3×20 screws over Ø4.5/ID3.2×12 mm tubular spacers. Their6.5 mm penetration
fully engages the 5.7 mm insert, with 2 mm tip reserve in an 8.5 mm blind pilot and
3.15 mm cover above the lid underside. Four other corners use M3×6 with a 4 mm
short insert,4.5 mm penetration,5.25 mm pilot and 0.75 mm tip reserve. The exported
pilot cutters are recut after the platform is fused into the lid.

Representative terminal-block top faces are explicit. Relay1 logic centre is
(36.5,432,271.15) and relay2 logic centre (36.5,452.3,271.15), facing +Z. Contact
centres are (−14.5,432,271.15)/(−14.5,452.3,271.15). Individual clamp pitch and
finished plug geometry remain reference reservations. Factory prewiring precedes
supply installation.

## Roof junctions

Horizontal-entry junctions stand on Z333.25..336.25 full 3 mm stock, leaving
10 mm air above the supply and 2.133 mm above the exact chosen diagonal regulator
crown. All horizontal bodies end at Z344.65; their explicit6.85 mm upward lever
reserve ends at Z351.5. Local ceiling pockets end at Z352, leaving0.5 mm lever
air and at least 3 mm exterior roof stock.

| Device | Native X range | Native Y range | Wire mouth |
|---|---|---|---|
| Main H | −96.35..−77.55 |334.55..353.15 |Fore, Z340.45 |
| Main N | −74.25..−55.45 |334.55..353.15 |Fore, Z340.45 |
| Main G | −52.15..−33.35 |334.55..353.15 |Fore, Z340.45 |
| Main V12 | −96.35..−77.55 |356.45..375.05 |Aft, Z340.45 |
| Main GND | −74.25..−55.45 |364.3..382.9 |Fore, Z340.45 |
| Reeds A | −96.35..−66.35 |394.05..412.65 |Fore, Z340.45 |
| Sensors | −63.05..−33.05 |394.05..412.65 |Fore, Z340.45 |
| Reeds B, 420 | −47.9..−18.1 |364.15..379.95 |Two upward rows, Z340.9 |

The420 body stands at Z322.6..340.9 on a low3 mm floor in the eastern native void,
with its own full 3 mm roof-rooted pier outside its body and wire field. Its two
opposed lever fields are explicit. The low floor lies wholly forward of the
supply. The aft cold-core wells end at Y415.8 before the full braided discharge
hose return at Y418.65.

Each well grips the blank rear half with 3 mm walls/floor and 0.15 mm per-side slip.
The working entry half and its descending wire-turn window remain open.
The H/N/G fore working floor opens continuously through the west edge across
X−99.5..−29.9/Y331.4..343.7, allowing the complete lower power-wire fanout.
The west root from Y343.7 aft and every rear blank-half grip remain intact;
the revised host and its wall fusion are each valid single solids.
`junction-port-approaches.json` gives every nominal groove-face mouth, outward
axis,2/4 mm straight approach and exact R3.4 geometric quarter turn. Main-wire
OD3.2 mm is conservative drafting stock; signal OD1.7 mm follows the bought 22 AWG
ribbon section. These occupied reserves do not qualify actual terminal clamps,
wire bends, ferrules, retention or the purchased main-wire jacket.

`roof-candidate.json` records native checks of joined stock, all closed devices,
the selected regulator, the complete pump hose, every individual opened lever,
and every other connector's entry wires. Measured221-413 lever reach is applied
as an explicit family reserve; actual 415/420 lever travel needs its purchased
geometry. Simultaneous lever operation is not assumed.

## Regulator retention

`wr-candidate.json` retains the scanned 18.87 mm central barrel with a 9.5 mm seat,
0.15 mm radial slip,3 mm bearing/end webs and a 3.5 mm central tie passage. Its west
roots join the wall and the junction carrier. A complete 2.5×1 mm nominal 6 in tie
follows the tangent barrel/rib loop; its87.33 mm closure is within the documented
110 mm capacity. The explicit8×8×5 mm locking-head reserve remains unmeasured.
The carrier is recut only through non-bearing stock, preserving both full 3 mm
end webs. Joined geometry and the tie's occupied passage are checked together.

## Matching shell and tray

`build_shell_post.py` consumes the parent supplied back shell. It preserves the
accepted translated C14 ceiling profile, opens localized roof pockets, restores
the obsolete tray slot and opens the matching new9 mm-wall slot at
Y283.35..334.85/Z253.9..266.65. The final tray spans
X−107.5..−1/Y279.6..338.6/Z254.4..266.4. All26 sampled nominal and gravity-settled
west extraction poses pass. Gravity settlement is 0.5 mm and leaves0.5 mm air above
the fixed lid. The supplied shell below Z253.4 is unchanged by this post-process.

The shell, platform and their fused print are valid single solids. The32 matching
shell checks include actual devices, explicit lever/wire envelopes, inlet,
joined root and tray motion. Printed capacity, insert pull-out, thermal cycling,
insulation, creep and lifetime remain separate physical properties.

## Rebuild

Run `floor_relays.py --x-shift25`, `roof_wagos.py`, `open_power_channel.py`,
`build_candidate.py`, then
`build_shell_post.py` after the parent shell is fresh. `publish_junction_ports.py`
emits the nominal mouth table. Run `wr_regulator.py` after composing the current
carrier so its tie passage binds to that exact native shape. The parent
`mounts/compose_body_hosts.py` merges the purchased-body restraints, and
`structure/assemble_prints.py`
fuses declared shell/lid roots and recuts the exact blind pilot cavities.
