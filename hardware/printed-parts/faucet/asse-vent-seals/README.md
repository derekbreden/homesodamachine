# ASSE vent-cavity seals and assembly tool

Simply having a 1022 already puts us ahead of most of these products. A 1022 that vents into the bowl at the faucet would be the only home arrangement I've found where the vent's discharge is defined, drained and visible.

Two one-piece TPU bungs bound the faucet's circular discharge cavity. Both
have separate holes for the soda tube, two flavor tubes and four insulated
display wires. The upstream bung also has the drain-tube hole. The drain
ends square inside the cavity; the downstream bung has no drain hole.
Discharge flows around the continuous drink tubes to the underside port.
The cavity, its glands and the port belong to the tip piece, keeping the
curved shell joint outside the contained liquid region.

## Files

| Part | Material | Print file | Exact solid |
| --- | --- | --- | --- |
| Upstream bung | Bambu TPU 85A | [STL](asse-vent-upstream-bung.stl) | [STEP](asse-vent-upstream-bung.step) |
| Downstream bung | Bambu TPU 85A | [STL](asse-vent-downstream-bung.stl) | [STEP](asse-vent-downstream-bung.step) |
| Slotted perimeter insertion tool | Fiberon PET-GF15 | [STL](asse-vent-perimeter-tool.stl) | [STEP](asse-vent-perimeter-tool.step) |

The [generator](../vent_seals.py) shares tube positions and bend geometry
with [faucet paths](../faucet_paths.py). Its [manifest](manifest.json) binds
the STEP/STL hashes, part bounds, volumes and nominal geometry checks to
their source. It records native export provenance and the current geometry
binding separately. The [complete faucet audit](../faucet-shell/centered-vent-check.json)
passes 164 checks against the current builders and saved print surfaces, including
the cavity, gland stock, seals, tube routes and tool access. The
[retained-part witness](lower-body-correction-check.json) binds the exact saved
tip, free seals, tool, mounting parts and covers to the current shared upper
construction. STL surface tolerance is 0.005 mm and angular tolerance is
0.04 radians. The bungs print flange-down; the insertion tool prints on its
flat handle face. Only the two bungs ship in the faucet.

The supported TPU recipe uses the H2C right Standard 0.6 mm hotend with
external low-friction feed. The [Bambu guide](https://us.store.bambulab.com/products/tpu-85a-tpu-90a/)
requires dry material and lists the supported nozzle sizes. The native
faucet readiness project carries the actual settings and toolpath review.
Check the narrow tube webs and all four 1.05 mm wire openings in that slice;
the smallest free CAD web at a bore lead is 0.90 mm.

## Seal interfaces

| Interface | Free seal | Rigid mating feature |
| --- | --- | --- |
| Outer body | Ø22.4 × 4.0 mm | Ø22.0 × 4.0 mm seat; 0.20 mm radial interference |
| Retaining flange | Ø23.0 × 0.8 mm | Ø22.8 × 0.9 mm groove; 0.10 mm radial interference, 0.10 mm axial allowance |
| Soda tube | Ø9.225 mm bore | Ø9.525 mm nominal tube |
| Flavor tubes | Two Ø6.05 mm bores | Two Ø6.35 mm nominal tubes |
| Upstream drain tube | Ø3.70 mm bore | Ø4.0 mm nominal tube |
| Four wires | Four Ø1.05 mm bores at 2.2 mm pitch | Individually separated, insulated ribbon conductors |

Each gland has a 1.2 mm upstream keeper, the flange groove, the 4 mm body
seat and a 1.2 mm distal backstop. The keeper opens at Ø22 mm. The
upstream backstop opens at Ø22 mm for passage of the distal bung and
tool; its flange is captured between the keeper and the body-seat
shoulder. The downstream backstop opens at Ø20 mm. The 7.3 mm gland retains the bung entirely in
the tip. Sealing comes from radial interference; the shell joint supplies
no gasket compression and no adhesive bonds to the polyethylene tubes.
The 0.3 mm keeper lead-in guides the flange through the keeper. A 0.2 mm
lead at both ends of each small bore eases tube and wire threading while
leaving 4.4 mm of full-diameter contact length.

The keeper and backstop leave open inner annuli for the elastomer to bulge
axially after tube insertion and outer squeeze. The generated volume
budget reserves about 546 mm³ there, versus about 101 mm³ needed beyond
the body/groove space; the complete upstream gland is about 74% filled at the
maximum stated wire envelope. Keep those openings clear. The assembly's
`build_installed_bung()` contact envelope locates the seat and curved tube
surfaces; it is not a volume-conserving elastomer deformation calculation.

At the seal stations the tube centers, relative to soda center, are:
S=(0,0), D=(0,7.5625), F1/F2=(±5.87398,6.46841) mm. These leave 0.8 mm
between actual nominal tubes. The corresponding uninstalled TPU webs are
1.10 mm. They locate each tube independently. The four wire centers are X=−3.3, −1.1,
+1.1 and +3.3 mm, at N=11.0125 mm. Their free webs are 1.15 mm.

The [wire supplier](https://bntechgo.com/bntechgo-28-gauge-silicone-ribbon-cable-copper-wire-4p-flat-cable-28-awg-flexible-soft-silicone-rubber-parallel-wire-stranded-tinned-copper-wire-4-pin-black-50-ft//)
states a 1.2 × 4 mm ribbon envelope with ±0.1 mm tolerance. Separate round
wire bores provide a defined mechanical seal around each continuous jacket.
The native aperture through every wire-bore layer must stay at least
0.915 mm. That bound keeps neighboring wire-web compression at or below
30% with the supplier's maximum Ø1.3 mm jacket and 2.2 mm wire pitch.
The intended slice gives additional allowance above that boundary.

The every-layer native bead reviews for the
[sculpted](vent-bungs-tpu85a.bead-review.json) and
[industrial](vent-bungs-industrial-tpu85a.bead-review.json) plates retain
separate wire-bore contours and connected material paths between bores.
The full-contact cores have centered clear diameters of 0.952–0.994 mm;
their largest circumscribed wire void is 1.045 mm. The reviews record
enclosed pores and local straight-span gaps as well. These commanded-road
measurements support threading and material continuity; the complete
faucet's water-containment acceptance establishes sealing.

The rendered Ø1.3 mm conductors represent the supplier's maximum jacket
envelope. Minimum Ø1.1 mm jackets have 0.025 mm nominal radial interference
with the free bores; a rigid curved wire would shift about 0.024 mm over
the body. The flexible wires can follow the straight seal bores between
the curved runs. Actual circumferential contact also depends on outer
bung compression, printed bore size and the jacket. The rendering does
not establish containment with the smallest jacket; the assembled
containment procedure covers that property.

## Factory assembly

1. Keep the base separate from the tip. The tip's female socket opens to
   its full round cavity for bung and insertion-tool access. Clear the socket, all gland lips, the tube
   guides and underside port of supports before loading anything.
2. Keep the display end of SIG-6 unterminated. Separate its four insulated
   conductors from that end back to the start of the local spread, leaving
   the lower stem and umbilical ribbon joined. Preserve wire order and
   inspect the jacket at each peeled web. Reject a cut or nicked jacket;
   no conductor is stripped within either seal.
3. Wet the tube/wire bores with clean water. From the free beverage/display
   ends, thread the upstream bung first onto S, F1, F2 and the four separate
   wires; leave its D hole empty and park this bung on the loose tail clear
   of the insertion tool's complete stroke. Then thread the downstream bung
   onto those same tubes and wires. Both flanges face the open joint. Keep D
   outside the tip while advancing the downstream bung: that bung has no D
   hole. Feed the beverage ends and wires into the tip and its dry outlet guides.
4. Place the open insertion tool around the bundle through its 19 mm
   slot. Its leading annulus bears only on the bung perimeter. Follow the
   tool's curve into the socket by rotation about the gooseneck arc
   center; do not drive the curved tool as a straight plunger. Advance the
   distal bung through the empty upstream gland until its body meets the
   distal gland backstop and its flange occupies the retaining groove.
   Its soft flange deflects inward 0.5 mm while passing the Ø22 openings;
   the body deflects 0.2 mm. Check complete seating.
5. Withdraw the tool along the same curve until it is fully outside the
   socket, then lift it off the continuous bundle through its open side.
   Feed D through the pre-threaded upstream bung while the bung remains
   outside the tip. Set D's square-cut end 8.0 ± 0.2 mm from the flange's
   front face toward the body and cavity. This is the flange face facing
   the open joint and contacted by the insertion tool. Refit the tool
   around the bundle and advance D and the upstream bung together along
   the curve until the flange seats in the groove against the body-seat
   shoulder. The upstream Ø22 backstop admits passage; axial location comes
   from the captured flange. Do not seek a body-end stop there.
6. Check that both flanges are captured, all tube/wire bores are occupied,
   D's open end projects into the circular wet cavity and the bottom port
   remains fully open. Confirm the three drink tubes reach their dry
   channels and exact symmetric outlet pattern. Close the dry curved
   shell joint using the shell's retention procedure. Terminate the
   display wires only after they are seated through both bungs.

The exposed 8.0 mm D setting is nominal. The modeled curved route projects
7.8515 mm from the seated flange front to its cut face, or 7.8555 mm along
the tube centerline. The modeled cut's nearest edge lies about 1.72 mm
beyond the upstream gland's distal exit. The factory setting places the
end about 0.15 mm farther into the open cavity; its stated tolerance keeps
the tube clear of that exit while preserving full seal engagement.

The tool's 21.5 mm outside diameter passes through both 22 mm keepers.
Its 19.7 mm inner opening clears the nominal tube pack by at least 0.314 mm.
The curved sleeve keeps at least 0.139 mm nominal clearance at the planar
keeper edge throughout rotation; the native actual-tool result agrees with
the analytical corner bound.
The 19 mm side slot clears the 18.098 mm nominal bundle width. Its thin
0.90 mm sleeve is factory tooling; the larger handle stays outside the
socket. Tool supports, if used by its saved native slice, are accessible
through the full-length side opening. Remove all residue from its bearing
face and inner sleeve before it touches a loaded seal.

The tool and gland share one local frame. At seated position its curved
sleeve is concentric with the neck; its front is clipped flat to the
bung's flange face at local Z=1.3 mm. Advance it by rotation about the
actual neck arc center. The shared frame preserves that curvature center
while the tool's leading face meets the planar flange.

The [native motion witness](tool-motion-check.json) checks a continuous
annular sleeve bound through the actual socket and cavity, complete-tool
rotational poses against S/F/D and wire routes, and withdrawal through the
open side. A full-rotation bound containing the entire tool and handle,
filled toward the rotation axis, also covers the specified continuous
side-removal motion. It clears the actual lower ribbon's mounting exit
and turn by 50.49 mm. The 19 mm slot leaves 0.902 mm total width allowance
around the nominal 18.098 mm pack. The distal bung's flange passes the empty upstream
gland elastically; its required radial deflection is 0.5 mm. A conservative
volume budget through a uniform Ø22 passage needs 5.385 mm compressed
axial length, versus the 4.8 mm free length and 7.3 mm gland. This establishes
space for axial bulging, with insertion force and capture left to physical
acceptance.

The [bearing witness](tool-bearing-check.json) measures the flange-bearing
area through the native slice's last model layer, including the continuous
lower annulus. The highest open-slot endpoints supply excess bearing area;
the main bearing must remain flat after support cleanup. The current slice
retains 99.04% of that bearing area through its last model layer. The
[native tool review](vent-seal-tool-petgf.tool-review.json) and bearing
witness bind the same tool mesh, native archive and G-code hashes. The
[cable witness](ribbon-native-check.json) checks every short span, the four
separate insulated conductors, the complete connected cable and its
clearance lane.

## Engineering evidence

The nominal gland groove retains 2.10 mm radial casing stock within a
27 mm neck. The gland body midpoint, local Z=4.1 mm, aligns to the
arc station 3.882232 mm beyond its nominal mouth station. The local
origin is 4.1 mm back along that station's tangent. This keeps the largest
nominal tube-center deviation within the straight body below 0.028 mm,
leaving at least 0.122 mm nominal radial tube interference. The analytical
minimum groove-crown wall is 2.052 mm. The shell audit also checks the
actual curved exterior and planar cavity boundaries. The gland helpers are local solids in
X/lateral, Y/outward relative to shell center, Z/downstream tangent.
`build_gland_cutter()` cuts solid neck stock; unioning a Ø23 cavity cutter
through the gland would erase its keeper and backstop.

The [Sculpted shell](../faucet-shell/faucet_shell.py) has a 30 × 31 mm
elliptical shoulder section at Z=59 mm, centered at Y=11.5 mm. It
transitions to the Ø27 mm circular neck at Z=65 mm. These outer sections
preserve the tube routes, rear mounting bundle and purchased steel plate.

[Parker's static-seal guidance](https://www.parker.com/content/dam/Parker-com/Literature/O-Ring-Division-Literature/ORD-5700.pdf)
supports positive interference and room for elastomer deformation. Its
general 30% static squeeze ceiling is a design reference: the nominal
tube-web compression here is 27.3%. It does not qualify this printed TPU
shape, extrusion tolerance or lifetime. The
[accepted 85A thimble seating](../tpu-o-ring/print-log.md) establishes that
identified Westbrass/tube fit only; the
[reservoir water-hold record](../../cold-core/reservoir/water-hold-acceptance.json)
belongs to those reservoir assemblies and print recipes.

The generated checks establish nominal packing, keeper/tool access,
separate sealing webs, valid CAD solids and emitted mesh integrity. Actual
bung insertion, complete flange capture, tube flow, water containment and
retained sealing through aging remain the physical acceptance scope for
the complete faucet. Acceptance uses the intended assembled drain path
and the faucet flow procedure; source dimensions alone do not supply
those results.

The [postpublication mounting lint](rear-mounting-lint-check.json) has no
findings on either above-counter plate or either countertop gasket.
Those STEP, STL and viewer payload hashes are retained exactly. The
record preserves its executed publication and source bindings; reuse
requires matching the actual artifact hashes. The
[current body and tip lint](../vent-qualification/postpublication-lint-execution.json)
has no open findings on either body or the shared tip. Its roof answers link
complete native stock and current emitted support paths. The
[mounting lint record](rear-mounting-lint-check.json) binds the separate
unchanged mounting meshes to their executed witness.
The cover's [lower-land witness](../faucet-display-cover/lower-land-lint-check.json)
measures 160.56 mm² of flat seating land on the bed in its saved print pose.

Regenerate with:

```sh
tools/cad-venv/bin/python hardware/printed-parts/faucet/vent_seals.py
```

Run the native engineering witnesses from the repository root:

```sh
tools/cad-venv/bin/python hardware/printed-parts/faucet/asse-vent-seals/check_tool_motion.py
tools/cad-venv/bin/python hardware/printed-parts/faucet/asse-vent-seals/check_tool_bearing.py --last-model-layer-z 80.84
tools/cad-venv/bin/python hardware/printed-parts/faucet/asse-vent-seals/check_ribbon_native.py
```

The motion check's `--refresh-bounds` option refreshes the actual socket,
cavity, per-feature casing gaps and continuous lower-ribbon bound while
preserving the sampled-motion witness and its original source hashes.
It requires identical tool and
tube-path sources. A change to either requires the complete motion run.
