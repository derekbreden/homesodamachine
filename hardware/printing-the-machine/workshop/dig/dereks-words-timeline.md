All dates 2026. Quotes are exact; "..." marks a cut. Each is a `Derek:` trailer unless marked [log] (print log, in history) or [body] (commit body; git parses the trailers only from 10-02, the 09-21 to 09-24 ones sit in bodies).

1. THEMES

Bridges and overhangs
Q1 "You can't print in the open like this. The only reason a bridge works is because it *is* a bridge that actually has a column supporting both ends." a8f24b2b5 11-12
Q2 "... all of these problems go away if we simply don't have an overhang here ..." 407a88305 10-04
Q3 "... simply add a corbel to avoid the ugly overhang here. We don't need any fine layers." c8ce1f979 11-09
Q4 "The overhang from an underside ... actually takes up more space because the roof hangs lower." 17c0c55ba 10-28
Q5 (a bridged ceiling) "... strictly worse than a supported underside, and supported undersides are not great." ee0258099 10-14

Supports
Q6 "Do we not have documented anywhere how horribly difficult normal supports are to remove ..." f8f4e7f01 10-09
Q7 ""Auto" is fine ... it's when you choose to put normal somewhere that it introduces problems." 684dc2f2b 10-09
Q8 "lol, lmfao, it is *every* support here ... throw it away" 684dc2f2b 10-09
Q9 "... the tree supports in those rail cavities *are* easy to remove, as long as they are actually in that cavity ..." d5bf35612 11-08
Q10 "... when there's not a clear path for the screwdriver ... I need those to be printed without supports entirely." 642e1aaa3 11-06

Edges, thickness, material
Q11 "... an attempt to use less material when less material is basically the opposite of our goal." 444346f44 10-19
Q12 "Very few edges is the key factor here, as it is in all of our designs." 23db8c58e 10-08
Q13 "if we're making any edge less than 3 mm we need to have a good reason for doing so ..." 19ec785d8 10-26
Q14 "... we prefer larger, and its all compromises, please don't focus too much on just one number or limit. It is a spectrum." a60c04aec 10-10
Q15 "No chamfers. No ramps. Just keep it simple and don't complicate the print unless there's a good reason to." bd0bdfd4e 10-29

Fit and clearance
Q16 "You do realize our clearances are not filled with free space but are actually filled with rough edges of materials? ... if you put a 1mm object next to a 1mm object pressed with several lbs of fource you still don't get a 2 mm object, you get a 2.15 mm one." f87d2686b 10-22
Q17 "Our clearance rules are not "we need more free space", they are "this is the reality of what these surfaces are"" f87d2686b 10-22
Q18 A cavity floor "is almost guaranteed to narrow at the tip because of the layer transitions resulting in very slight rounding" 87b6b440f 09-23 [body]

Layers and the slicer
Q19 "Do not use finer layers anywhere - that is not an option - that is a completely different variable" 2f17ad737 11-12
Q20 "... if I don't have a reason to muck with a bambu default choice, I don't muck with it." b58ee4350 10-25
Q21 "There's just so many variables, and you really have to look at the slice and how the lines actually print and what they are connected to and how all the lines of filament are actually laid down and connected and it is just a lot." 9760da947 10-20

Bed and first layer
Q22 "You can't print that close to the edge of the bed on a plate that hasn't been seasoned properly first." 464f0465c 10-06
Q23 "The +0.04 trim was a *special* case for a problem with a *specific* print - not a change to the rule for Mark1." 8d7be0e3c 10-08
Q24 "... brims are useless for this problem, the larger objects breaks away from the brim easily as it curls up." f81fdc301 10-21 (again 4fc398c20 10-26; e91424129 11-11 "Remove this brim.")

Materials
Q25 PET-GF: "We can use 100% cooling if we want, but only on the places that actually need it ..." 9ae148e1d 10-17
Q26 PETG, watertight: "I think I'd rather continue the walls forever ... Another agent suggested at some point infill works better, but I haven't seen that." 5572299f3 10-21
Q27 TPU, ASA Aero: "... the distance between objects increases risk of problems on these "unclean start/stop" filaments." c20b80fb1 10-12
Q28 PET-CF: "the direction that things are falling are actually the direction they are being pulled ... So my thought is 'less velocity' => 'less force'." 2b1fad60c 06-14 [log]

Method and memory
Q29 "Please don't keep doubling down on changes already tried ... pick one specific thing to change ..." 9f5865af2 10-09
Q30 "And I don't want you to keep wasting my time printing the same control over and over again." 7fde4f2a4 10-15
Q31 "This amount of TPU costs less than your tokens, so please just start a print once you are ready." d8271f3b3 10-13
Q32 "Fixtures we may print again. Trials will never be reprinted, we'll just make new trials instead." a088db31d 11-02
Q33 (a lost reservoir recipe) "... a failure to find and repeat those settings. Sigh." 67994c7ef 10-05
Q34 "I'd like the repo to be a clear memory to all agents, a written memory that builds FDM print expertise progressively as and when needed." 2f17ad737 11-12

2. LESSONS HE REPEATED

A. Normal supports do not come out; cavity-rooted trees do. 922c8d6f4 10-04 "nearly impossible to remove"; Q6; Q8; 78eb4b6f8 10-11 "spindly tiny incredibly long fragile supports"; d57670e38 10-25 "impossible to remove supports"; 65066d840 11-06 "The normal supports aren't removable."; Q9; 1fe50e4ff 11-10 "not able to remove the supports".
B. Fewer edges, more material. b20e7d208 10-05 "There should be guidance in the repo about this"; Q12; 498369996 10-10 "this is just insane"; Q11; e681cc367 10-19 "tiny abhorrent pointless difficult-to-print too-many-edges complexity"; 7c311ff22 10-25 "fewer edges and more material"; c82784774 10-27 "very very very very likely to break"; 9a96de823 11-01 "at least twice as thick"; a8f24b2b5 11-12 "incredibly impossibly thin".
C. Proven settings must reach the next print. Q33; ba17c3430 10-14 "is that committed to petgf.3mf yet?"; cb5632d2c 10-15 "***EVERYTHING*** we've learned"; 948e0bff4 10-26 "Did that not carry over?"; 3ccd9d1e9 11-07 "I thought we had made all the tips pointier"; ec257a4db 11-11 "without removing any of the things it had right already".
D. Z trim belongs to one printer, plate and filament. Q23; a86ede62e 10-13 "not our usual 0.18 offset"; 7248987e1 10-25 "I hope we didn't have a Z offset before."; 926988d8a 11-06 "documented as for pet-gf on textured plate".
E. One variable, no repeated controls. Q29; Q30; d85cd06c1 11-08 "change just that one variable"; 908851a7a 11-09 "you don't need to repeat anything"; Q19.
F. Off the edges of an unseasoned plate, parts close. 5d2b1b080 10-04 "that plate is not well seasoned there yet"; Q22; 723faaef7 10-10 "close to the edge when they need not be"; c20b80fb1 10-12 "put the objects closer together".
G. Fan on overhangs and bridges, everywhere, and nowhere else. 7fde4f2a4 10-15 "make sure that they're everywhere"; Q25; 8c7b1786b 10-26 "major part fan cooling and time between layers"; f62c528c4 11-06 "like we have tested and proven"; 4494e83e3 11-12 "surfaces that are rough on both sides".

3. TASTE AS A MAKER

- "Good enough" is the bar, flaw noted: "There's still a gap, so make a note of it ... It's fine. It's good enough." bea5c6e06 10-25
- Print the real, whole part: "I'd rather see a full size print, a complete faucet, with our best attempt." 02920776a 10-12
- Coupons in production pose, one control, steps either side, about an hour: "have one control, and have variations in both directions ... aiming for 60 minutes" 5d20beae4 10-11
- Idle printers are waste: "Both printers are available and its my bed time. Print as you see fit." 7fde4f2a4 10-15
- Start simple, stay stock (Q20): "starting simpler seems better to me, generally speaking." 18cc9fbf0 10-03
- Trusts handled parts over drawn ones: "Its the print and verification history there that excludes it." 52da8e2ed 10-22
- Finish counts where nobody looks: "We care what the inside of our device looks like." f158a7c79 10-15

4. TIMELINE

03-22 first Bambu H2C ordered, with PLA, PETG, ABS, PA6-CF, TPU 95A (purchases.md); renamed Mark1 on 10-06 ef6f39a90
04-02 6d45592d5 first test prints, snap struts
04-05 243585ffb he deletes "AI written non-specific FDM advice"
04-23 24fb8ed9b printed pressure vessel abandoned
05-02 4a2b166a9 PET-CF faucet log opens: clogs, failed calibration, printing air
05-04 hotend wrecked clearing a clog; second H2C ordered (purchases.md), later Mark2
05-10 1d9d393a8 faucet attempt 9, "Actual success", on a 0.6 carbide nozzle
05-21 1f98b24a5 snaps removed: PET-CF too brittle
05-22 8c9128a94 first printed reservoir leaks
05-30 8d44f5c86 first watertight reservoir; 5e8ae8695 TPU 85A thimble seats
06-14 5f9d951f2 faucet attempt 20, fits converge; 35adbe9d4 first magnet sealed in at a pause
06-18 a43042fe0 enclosure split for the bed; first fit coupons
08-12 0cfe5dd8b first full enclosure quadrant sliced, PETG
08-15 cfcaf5dfc first enclosure piece in PET-GF15: "very beautiful wall surface"
08-20 ee8a64eb8 "Switching to 0.4 mm for all enclosure exterior printing"
08-28 to 08-31 6d7ede349 first-layer Z-trim ladder; textured plates ordered
09-13 6f82e4d01 agents get printer controls
09-14 7eabe588c sixteen-specimen PET-GF support trial
09-18 14594f74e white Sculpted and black Industrial faucets, PET-GF
09-21 to 09-23 d4a0ede34 three enclosure quadrants in PET-GF; eb6f0d619 0.08 mm bands
10-02 dc8b60ba0 first ASA Aero print; 10-03 fb4c6904f all-Aero float accepted
10-04 922c8d6f4 front-top rejected for supports; 10-09 684dc2f2b back-top thrown away
10-13 3e4d677f5 first TPU 85A elbow fits; 10-22 5b0d29be2 string-free
10-14 0836e734f fin, bridge and ramp plates; 10-15 942ac2244 arc fins accepted
10-14 5660c51dc Industrial faucet approved; 10-25 bea5c6e06 uniform 0.24 mm layers
10-17 9ae148e1d white covers crack; fan limited to bridges and overhangs
10-18 bc2b2e189 printed prototype pours soda
10-21 9c40265a5 two walls, 15% gyroid; 5572299f3 reservoirs leak again
10-26 d8b36a14b reservoirs hold at 50% overlap
11-08 6eacc82f3 long snap tips; 11-10 4642937f9 Support D adopted
11-12 a8f24b2b5 Wago roof fails in the open; 2f17ad737 FDM print guide; d0585e384 fitted record

March was a working prototype and a printer order, and April was one H2C on PLA, PETG and ABS: snap coupons, a warping foam shell, an abandoned printed pressure vessel. May was the hardest month, eighteen PET-CF faucet attempts through clogs, a wrecked hotend and toppled supports, ending with the first watertight PETG reservoir. June and July went to CAD, boards and molds, with coupons standing in for sixteen-hour prints. It turned on 15 August, when the first PET-GF15 enclosure piece came off with a wall he called beautiful, and by late September two printers were turning out quadrants and faucets. October and November were tuning by the hour, and the record is his corrections: supports that would not come out, cooling that made white parts brittle, leaks at the wall-fill line.

5. FIVE FOR A PAGE EACH
Q1, Q16, Q11, Q21, Q20; Q34 as the epigraph.

Scratch data:
- /private/tmp/claude-501/-Users-derekbredensteiner--claude-spares-spare-R8DUrN/f08a8255-97ac-445e-9478-10dd59e4e1e7/scratchpad/agent-words/quotes_verified.json holds the full uncut text of 150 printing quotes, by theme.
- /private/tmp/claude-501/-Users-derekbredensteiner--claude-spares-spare-R8DUrN/f08a8255-97ac-445e-9478-10dd59e4e1e7/scratchpad/agent-words/sel_broad.txt holds every printing passage, by date.
