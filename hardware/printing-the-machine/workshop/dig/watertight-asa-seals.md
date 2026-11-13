Aliases: H=/Users/derekbredensteiner/Developer/homesodamachine; R=$H/hardware/printed-parts/cold-core/reservoir; F=$H/hardware/printed-parts/cold-core/magnetic-float; P=$H/hardware/printed-parts; M=$P/zone-c/funnel-mold; E=$H/future/pump-elbow-exploration. "(c abc)" is the commit whose Derek: trailer holds the quote; a quote with no reference is in that lesson's first evidence file. Cited files are in the working tree unless a SHA is shown.

A. STORY
2026-05-22: the first reservoir, off-brand PETG at 240 °C, leaked. A week later a test cup, then the reservoir, held water in Bambu clear PETG at 260 °C and flow 1.02. The saved project then changed; September's two holds used a 30 mm/s recipe taking 20 and 26 hours. In October, on a redesigned flat floor, that recipe "leaked many places", the May recipe at stock speed leaked where floor fill meets wall, and a walls-only floor leaked along its loop junctions. Derek's four requests at once (flow 1.05, five walls, overlap 30%, +10 °C) held; temperature went back alone and still held; a two-hour weep took overlap to 50%. Derek, 2026-11-12: "all reservoir prints after that setting change have been holding water since" ($H/hardware/ledger/fitted.json).

B. LESSONS (rule | what was seen | evidence | Derek | scope | status)
1. Floor weep in PETG: raise Infill/Wall overlap (15%, 30, then 50). | At 15% droplets sat on the line where floor fill meets wall loops; at 30% one article wept after two hours; 30 to 50 was the only change. | $R/recipe-reviews/2026-10-26-overlap50/README.md | "It does appear to be precisely in the line between wall and infill." (c 0c28884a5) | clear PETG, 0.8 mm nozzle, flat 3 mm floor | stated; internal path untraced.
2. Flow 1.05 (stock 0.97) and the fewest loops that leave no fill in the wall: five. | Changed with overlap and heat; the log "does not isolate which change supplied the improvement". | $R/recipe-reviews/2026-10-22-flow105-overlap30/ | "enough walls for our actual walls to be entirely walls, no more" (c 4c7fab10a) | 3 mm walls, Arachne, 0.8 mm lines | stated, not isolated.
3. A flat floor of concentric loops leaked; the recipe's floor is solid zig-zag. | Drops followed the line where nested loops converge; the slice shows pockets there on all twelve floor layers. A 59° Arachne setting cut the computed pocket about 72%; the leak stayed. | $R/prints/2026-10-21-mark1-walls-only-right08-z000-a4/ | "Leaks along the seam" (c 18652233a) | flat floors | results stated; generalisation mine.
4. Slow walls and extra heat were not needed. | Holds exist from the 30 mm/s recipe (20 h) and the stock-speed one (5 h 42 min); 255/260 °C held like 265/270. | $R/history/seal-trial.md; $R/print-log.md | "something usable there, even if a bit slow" (c 67994c7ef) | Bambu clear PETG | inferred.
5. One setting per trial, confirmed in the G-code; then fill and wait; keep the exact project file. | Trials are diffed command by command; verdicts are Derek's fill-and-watch reports at one hour, two hours and days. No pressure, dye or weighing test, fill height or temperature is recorded. The May project was resaved and went unfound for months. | $R/print-log.md; $R/water-hold-acceptance.json | "a failure to find and repeat those settings. Sigh." (c 67994c7ef) | sealing trials | practice in the records.
6. Nothing pierces the cup below its rim; lines enter the lid through TPU grommets; the lid clamps a flat gasket. | The floor port went on 2026-10-19; the flat floor it left is where the next leaks appeared. | $R/watertight-petg.md | "because we no longer have the much thicker and sloped floor" ($R/prints/2026-10-21-mark1-may-water-right08-z000/physical-result/physical-result.json) | vented vessel | stated.
7. Clear PETG: zero added Z trim, no brim, no ironing, glued Engineering Plate. | Under PET-GF's +0.18 mm trim first-layer lines did not touch; textured PEI lifted repeatedly. | $R/prints/2026-10-20-mark1-right08/physical-result/; $R/corner-lifting/README.md; $R/ironing-study/README.md | "the "OFF" one is the best result by a long shot" (c 20e19fc57) | 0.8 mm nozzle | stated.
8. Mold halves: flow 0.88, six walls, 15% gyroid. | At 100% infill material rose above the layer and the nozzle dug in near layer 375; the log calls accumulating excess a working hypothesis. | $M/print-log.md | "Certainly less of ‘the problem’ that I refer to as ‘overflow’." | PETG Translucent, 0.4 mm | stated; no cast recorded.
9. ASA Aero: glued Engineering Plate, external dry box, added priming strip, nested walls only, parts 2 mm apart. | The startup line and first loops lifted; bits were carried on every travel, which Derek puts down to expansion in the hot nozzle (unconfirmed). | $F/mark2-aero-print/ | "just do like 300 walls so that it is all walls and we get concentric the whole way, and no jumps." (c 2ebd64f2a) | Mark2, 0.4 mm, flow 0.52 | stated.
10. Float: 5 g spare lift at an assumed 0.65 g/cm³, no sealing shell. | Maker: 0.46 at flow 0.45; preset flow 0.52 computes to about 0.52. In the PETG-shelled design 0.6 mm more wall cut lift from 4.96 to 2.87 g. Nothing weighed or floated is recorded. | $F/all-aero/README.md; $F/petg-shell.md | "Maybe one more layer of space needed above the magnet for next time" ($F/all-aero/physical-observations.json) | 36 × 28 mm, magnet seated at a pause | calculation.
11. TPU: hardness first; thin sleeves cap-down; flat gaskets solid on the stock profile. | In 95A the sleeve fitted tube or bore alone, not both; an 85A print with a thicker wall seated; 68D was "too stiff". | $P/faucet/tpu-o-ring/print-log.md; $P/gaskets-print-log.md | "But attempting both at the same time? Nah, not happening." | Bambu 85A, 90A | stated; two things changed.
12. Hollow soft TPU: fan at 100%; travels replaced by deposited paths. | Fan to 50% curled both lips at once. Laps, hops and a joining web left threads; printing through the transfers left none. | $E/README.md | "if you stop printing and you travel south and then you travel east, you end up drawing a diagonal thread in the southeast direction." ($E/prints/2026-10-16-vertical-center-web-tpu85a-mark1/physical-result.json) | Siraya 85A, 0.6 mm | stated.
13. Infill: two walls, 15% gyroid. Insulation: foam poured into printed shells. | In a 3 mm wall four loops left no sparse infill to vary; the strips and the clear foam-fill pieces have no result. | $H/hardware/print-tests/enclosure-infill/README.md; $H/hardware/print-tests/foam-fill/README.md | on earlier pours into PETG: "nothing melted and nothing was too hot to touch" (c b3226a922) | PET-GF enclosure | stated, untested.

C. BAKED-IN BASICS
- Print logs open "Format: facts only. Direct quotes from Derek where applicable." $H/calibration/Principle.md: "any rule is better encoded as an example." A hook pointed my scratch draft there; guide text written here will meet it too.
- Settings are read back from emitted G-code: an overhang table overrode a 10 mm/s wall setting; flow is stored per nozzle variant; a 3MF's nozzle_diameter names the profile.
- Wet parts are clear PETG; bodies print mouth up, floor on the bed; lids face down, ports support-free on 45° countersinks.
- Filament is dried per $H/hardware/ledger/tools.md and fed from a sealed box; TPU bypasses the AMS.

D. PICTURES
1. $R/prints/2026-10-21-mark1-may-water-right08-z000/physical-result/photo-3.jpg: droplets in a row where diagonal floor fill meets the perimeter band. Lesson 1.
2. $R/prints/2026-10-21-mark1-walls-only-right08-z000-a4/physical-result/photo-1.jpg: walls-only floor, drops along the branching loop junction. Lesson 3.
3. $R/prints/2026-10-21-mark1-walls-only-right08-z000-a4/floor-wall-paths.png: that floor's toolpaths, junction pockets in red; beside 2.
4. $R/water-hold-evidence/2026-10-26-two-hour-leak/photo-1-base-crop.jpg: specks of water beside the base after two hours. Lessons 1, 5.
5. $R/prints/2026-10-20-mark1-right08/physical-result/photo-1.jpg: clear first layer whose lines do not touch. Lesson 7.
6. $E/prints/2026-10-16-vertical-center-web-tpu85a-mark1/result-photo.jpg: black TPU elbows, bores full of threads. Lesson 12.
7. $E/prints/2026-10-14-compact-single-siraya85a-overhang10-engineering-z000-mark1/finished-elbow-1.jpg: a clean clear elbow, beside 6.
8. $F/all-aero/mark2-print/v1/evidence/magnet-insertion-overprint-2026-10-03.jpg: the foam float under the nozzle as it prints over the magnet. Lesson 10.
9. $M/print-photos/2026-09-20-flow088/photo-1.jpg: leftover "overflow" roughness; photo-3.jpg beside it is the finished cavity. Lesson 8.
No photo shows a reservoir holding water. Downscaled previews: /private/tmp/claude-501/-Users-derekbredensteiner--claude-spares-spare-R8DUrN/f08a8255-97ac-445e-9478-10dd59e4e1e7/scratchpad/agent-watertight

E. SURPRISES
1. Stock speed sealed as well as a recipe over three times slower.
2. Pockets of about 0.1% of the floor area, on every layer, sat where the walls-only floor dripped.
3. One PETG family runs at flow 1.05 in the reservoir and 0.88 in the mold.
4. Less fan curled TPU more; more deposition, not retraction, ended its threads.

F. GAPS AND CONTRADICTIONS
- $R/print-settings.json binds the right body to the 30% overlap settings. $R/watertight-petg.md and $R/README.md call 50% "pending" and say reservoir.3mf holds 265/270 °C and 30%; the file holds 255/260 and 50%.
- September's 0.97-flow recipe held; its October repeat "leaked many places", with floor, printer, trim and ironing all different.
- Flow 1.05 was never isolated; in May Derek said 1.02 "results in noticeable bulges" (print-log at f25975cd0).
- Float density, mass, buoyancy and water uptake are unmeasured; the three-float plate has no result. $F/asa-aero-research.md records the maker calling ASA Aero unsuitable for food contact; the float sits bare in flavoring, and concerns.md has no row.
- No silicone cast, foam-fill pour, gasket pressure test or infill-strip verdict is recorded.

Nothing in the repo was changed.
