Paths: R = /Users/derekbredensteiner/Developer/homesodamachine; E = R/future/pump-elbow-exploration/prints; W = E/2026-10-16-vertical-center-web-tpu85a-mark1; PP = R/hardware/printed-parts. Quotes sit in the cited record unless a commit is named.

A. STORY
The pump elbow is a one-piece TPU 85A joint: one socket stretches over a pump barb, the other grips 1/4" LLDPE, and the 90° turn is inside the print, where a loose strand would reach the pump's valves. E holds 17 trial folders (14 sent to a printer), 2026-10-13 to 10-22. First came shape (two at once failed; a "full base" was rejected), then hardness (TPU for AMS too stiff), then 45° lips curling on Bambu 85A. Siraya 85A at a verified 10 mm/s lip came out "perfect" outside, stringy inside. Seam routing, wall-following travel, wiping laps, fins and a centre web all left strings; printing through every turn ended them. The tube bend holders are PET-GF, not TPU.

B. LESSONS
1. Never stop extruding at a turn; make any non-extruding hop a short straight chord inside material. Why: a free strand straightens between its last attachment and the nozzle, whatever route the nozzle took. Ev: W/free-strand-review.json (78 of 118 detours could span a bore) against E/2026-10-16-deposited-links-siraya85a-mark1/emitted-command-review.json (6,118 hops contained, no retraction or Z-hop, 1.21% extra plastic) and E/2026-10-22-deposited-links-siraya85a-mark2/physical-result.json; deposited_links.py at 2f2d9c94a. Derek (W/physical-result.json): "if you stop printing and you travel south and then you travel east, you end up drawing a diagonal thread in the southeast direction." Scope: Siraya 85A finned pair. Stated.

2. Read the emitted speed at the feature, not the setting. Why: Bambu Studio's overhang table (50 and 30 mm/s entries) overrode "outer wall 10"; two trials ran the lip at 14-22 mm/s. Ev: E/2026-10-13-compact-single-tpu85a-overhang10-engineering-z000-mark1/README.md. Derek (commit 3d2e975a9): "Maybe we can try slowing down that outer edge more?" Scope: Bambu Studio. Stated.

3. Keep part cooling at 100% on soft overhanging lips. Why: halving the fan worsened curl at once; the lip sprang back under the nozzle and a glob tore off. Ten degrees cooler did not help. Ev: E/2026-10-13-compact-single-tpu85a-engineering-z000-mark1/physical-result.json; E/2026-10-13-compact-single-tpu85a-t215-engineering-z000-mark1/physical-result.json. Derek: "like instantly we got more curl on that left edge". Scope: Bambu 85A. Stated; cause unestablished.

4. Choose hardness by the fit, not printability. Why: 95A and TPU for AMS (68D, 12 mm³/s against 2.2) print fast but cannot stretch over rigid interfaces. Ev: PP/faucet/tpu-o-ring/print-log.md; E/2026-10-13-compact-single-tpuams-mark1/physical-result.json. Derek: "That was too stiff."; "85A is the only one that flexes enough here." (commit af13560ec). Scope: stretch-fit seals. Stated.

5. Siraya 85A Clear at 215 °C (225 first layer), flow 0.96, retraction 0.8 mm, auxiliary fan off, 10 mm/s outer and 25 mm/s inner walls, printed the lips cleanly; Bambu 85A at 225 curled. Why: unknown; brand, temperature, lip speed and a fresh spool changed together. Ev: E/2026-10-14-compact-single-siraya85a-overhang10-engineering-z000-mark1/physical-result.json, material-profile.json. Derek: "Turned out perfect." Scope: one geometry. Stated, confounded.

6. Orient so every underside is 45° or steeper and no bore needs support; check undersides, not axes; added base stock must be solid to the bed. Why: both legs lean 45°, yet the big cuff's underside is 45° (82% bead overlap) and the tapering neck's about 66° (92%); the 45° side curled first. Ev: underside-side-comparison.json beside lesson 3's first record; E/2026-10-13-full-base-single-tpu85a-mark1/physical-result.json. Derek: "Sure you got the same gradual angle on the underside on left and right?" (commit 3d2e975a9); "you left a gap that makes the below useless". Scope: unsupported soft parts. Stated.

7. Print one TPU object at a time, or keep neighbours 2 mm apart. Why: every stop and start oozes; arriving from another object throws a loop at the wall start. Ev: PP/fixtures/tube-insertion/prints/2026-10-12-tpu-liners-mark1/failure.json; R/tools/bambu-printers.md. Derek: 'the distance between objects increases risk of problems on these "unclean start/stop" filaments.' Scope: TPU, ASA Aero. Stated; unmeasured.

8. To print a pair, make it one island: cut-away fins and a vertical centre web, two beads wide with one-bead necks. Why: the web is the deposited bridge the continuous tour crosses; alone it cured nothing. Ev: W/README.md; E/2026-10-16-cutaway-web-tpu85a-mark1/physical-result.json. Derek: "Why didn't you make the fin between the two objects a vertical fin at the center point of them?" Scope: fins are cut, not torn. Stated.

9. Slicer travel hygiene is necessary, not sufficient. Why: avoid-crossing-wall cut bore travels from 492 to 15 per elbow, timelapse-off removes 184 photo trips, a wiping lap at best thinned threads; strings stayed. Ev: R/future/pump-elbow-exploration/stringing-candidates.md; E/2026-10-16-departure-lap040-normal-lift-tpu85a-mark1/physical-result.json. Derek: "there's still threads, even if those threads are a tiny bit thinner." Scope: Bambu 85A. Stated.

10. Trust the slicer preview over an analysis that simplifies geometry. Why: a check that filled holes under 5 mm² reported zero off-wall travel while the file crossed 3.84 mm of bore. Ev: W/travel-opening-review.json. Derek (commit ff629ceda): "there are a number of places the travel goes outside the outside wall." Scope: any path check. Stated.

11. Soft-TPU bed: glued Engineering Plate, 35 °C, zero user Z trim, sliced for the plate installed. Why: unwritten; Derek asked for zero after a liner fell over at the PET-GF trim; the printer flags a plate mismatch before printing. Ev: PP/faucet/tpu-o-ring/prints/2026-10-23-black-tpu85a-right06-mark2/cancelled-plate-mismatch/cancellation.json. Derek (commit a86ede62e): "So not our usual 0.18 offset, but with zero offset." Scope: 85A since 10-13; the 10-16 white 90A gasket kept +0.18. Inferred.

12. Start a thin soft wall on a solid cap, and read the cap from the slice. Why: a 0.375 mm ring gave "empty initial layer"; in spiral mode a 2.1 mm CAD cap prints 0.66 mm solid. Ev: PP/faucet/tpu-o-ring/print-log.md, README.md. Scope: thin sleeves. Stated.

13. (PET-GF) Hold a tight tube bend with a D on its back and a teardrop channel. Why: supports could never leave a curved tunnel; a 2 mm wall with 3 mm legs held R14. Ev: R/future/tube-bend-holder-exploration/README.md. Derek (commit 8633ad75b): "I'm imagining a D shape on its back, with a teardrop channel cut in it." Scope: PET-GF15, 1/4" LLDPE. Stated.

C. BAKED-IN BASICS
- TPU feeds from the right external spool to the right hotend, 0.6 mm nozzle; no AMS feeds TPU, and the AMS HT is only its dryer, 75 °C for 18 h (R/hardware/ledger/tools.md).
- The flow cap (2.2 mm³/s for 85A, 2.8 for 90A) sets the speed, about 20-30 mm/s at these bead sizes (inferred).
- Sealing parts are solid: 100% zig-zag, six walls on the elbow, two on gaskets and liners, no supports; the thimble is one spiral wall.
- Maker's profile first, one change per trial, emitted G-code read back before sending.
- A processed .gcode.3mf is printed as-is: reslicing drops the path and the command-line slicer runs no scripts (archive at 33d50d2ec).
- Fit is tried on the ugly print first; every bore is checked against a light.

D. PICTURES (2 and 5 are already in R/hardware/fdm-print-guide/art)
1. E/2026-10-13-compact-single-tpu85a-engineering-z000-mark1/curl-left-edge.jpg: nozzle over the cuff, lip curled, torn glob on the bed (3).
2. E/2026-10-13-compact-single-tpu85a-outer10-engineering-z000-mark1/underside-sag-photo-1.jpg: black Bambu 85A V, ragged 45° edges (2, 5).
3. E/2026-10-14-compact-single-siraya85a-overhang10-engineering-z000-mark1/finished-elbow-1.jpg: clean clear Siraya elbow, beside 2 (5).
4. W/result-photo.jpg: finned black pair, bores full of threads; the best failure (1, 8).
5. E/2026-10-16-deposited-links-siraya85a-mark1/deposited-path-review.png: layer-49 tour, hops blue, the failed span dashed red (1).
6. PP/fixtures/tube-insertion/prints/2026-10-12-liners-d775-mark1/wall-start-physical-1.jpg: loops along one liner edge (7).
7. R/future/tube-bend-holder-exploration/prints/2026-10-23-legs-123-w2-petgf-left04-z018-mark1/photos/02-flat-back.jpg: PET-GF holder on white tube (13).
No photo exists of the accepted finned pair.

E. SURPRISES
1. With zero nozzle travel off the model a strand could still span 3.98 mm of bore; the cure used no retraction and no Z-hop.
2. Two trials "at 10 mm/s" never printed the lip at 10.
3. Less fan made TPU curl more.
4. The easy TPUs (95A, 68D "for AMS") were useless; the working pair is 8.5 g in two hours.
5. A 2 mm PET-GF wall, loaded across its layers, holds LLDPE at its tightest bend.

F. GAPS AND CONTRADICTIONS
- The win confounds path with material: deposited paths never ran on a Bambu 85A elbow; Bambu at a true 10 mm/s lip was printed but its exterior never judged.
- "Seal seems as good as before" names no pressure, duration or "before" article.
- Still "pending": two-elbow Siraya (10-14), Mark1 deposited paths (10-16), continuous-layer gasket (10-23).
- R/hardware/ledger/fitted.json dates the acceptance 2026-10-21; the print launched 10-22.
- R/hardware/fdm-print-guide/09-tpu.html labels picture 2 as sagged; Derek withdrew that reading: "Oh, maybe it is curling."
- Moisture never isolated: the Bambu spool went to the dryer under a 90A preset, completion unrecorded; Siraya printed fresh.
