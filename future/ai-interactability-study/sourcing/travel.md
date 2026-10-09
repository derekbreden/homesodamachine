# Sourcing: travel

Observed 2026-09-28 and, for entries 19 to 34, 2026-09-29 (Lincoln 68520 delivery address on the account; delivery dates are relative to that day). Nothing was ordered, added to a cart or sent to a vendor. Representative sources only, one to three per idea, not a shopping list.

**Amazon rule (CLAUDE.md):** only Prime listings count. Method: searches used the Prime-eligible filter in the URL (`rh=p_85:2470955011`), only result cards carrying the Prime badge were read, and each entry below marked "buy box" was then checked on its product page: the buy box shows the Prime badge and a free-delivery date. Entries marked "card" were seen only as a Prime-badged search card; their product pages were not opened. Non-Prime listings were not read.

**Sales evidence** is what the page states: review count, star rating, "bought in past month" badge. A review count is a lower-quality proxy for volume, not proof of it. "None" means the listing showed no volume evidence.

## What the ideas need, and what turned up

| For | Need | Entry |
|---|---|---|
| T1 tube travels | small XY cross-slide under the rotator | 1, 2 |
| T1 tube travels | long, straight-guided motorised axis (shuttle, or fine axes) | 3, 4, 5 |
| T1 tube travels | Z lift | 6 |
| T1 tube travels, T4 | shuttle by drawer slide with a hard stop | 7 |
| D1 monitor arm | gas-spring arm | 8 |
| T4 return seat | balls and magnets for a kinematic seat | 9, 10 |
| T6 hand moves, software reads | digital scales | 11 |
| T5 nest driver, T2 | a probe | 12 |
| T8 cable travel | balancer | 13 |
| T9 ratio devices, T2 follow stage | reduction | 14, 15, 16 |
| T12 print to adjust | shim stock | 17 |
| room-scale frames | T-slot extrusion | 18 |

## Entries

### 1. MYSWEETY compound slide table (dovetail XY table, 330 x 95 mm)
- Vendor: Amazon. https://www.amazon.com/dp/B07GXH3HWZ
- Price $59.99. "Only 15 left in stock". Free delivery Fri Oct 2 (observed 2026-09-28, ordered-within countdown shown).
- Stated: table 330 x 95 mm; X travel 190 mm, Y travel 65 mm; handwheel ring = 1.5 mm; dovetail aluminium alloy. No load rating stated.
- Sales evidence: 4.1 stars, 1,068 reviews; no "bought in past month" badge shown.
- Prime: buy box (Prime badge present).
- Note: a manual table, so it is what a hand-cranked T1/T6 stack would use. Dovetail slides have backlash and are not tilt-stiff; whether it carries a rotator and tube (mass unknown) with acceptable tilt is not known.

### 2. VEVOR milling working table, 17.7 x 6.7 in, compound 2-axis
- Vendor: Amazon. https://www.amazon.com/dp/B0DL9BFTGH
- Price $135.90; free delivery Fri Oct 2 (search card).
- Sales evidence: 3.9 stars, 80 reviews, "50+ bought in past month".
- Prime: card.
- Note: same family as entry 1, larger and heavier; stated load not read.

### 3. ZBX80 300 mm CNC linear stage with stepper
- Vendor: Amazon. https://www.amazon.com/dp/B09MY7XP9L
- Price $159.00; free delivery Wed Sep 30.
- Stated: stroke 300 mm; horizontally loadable 80 kg, vertical 20 kg; width 80 mm; total length with the stepper motor 530 mm. Stated resolution / repeatability: not read.
- Sales evidence: 4.7 stars, 32 reviews.
- Prime: buy box.
- Note: a long motorised axis, the shape a shuttle or a long tangent slide would take. Sold for CNC routers, i.e. an unrelated purpose.

### 4. FSL40 V2.0 linear module (rail guide with ball screw)
- Vendor: Amazon. https://www.amazon.com/dp/B0CG5S1C8T
- Price $170.00; free delivery Fri Oct 2.
- Sales evidence: 4.6 stars, 71 reviews.
- Prime: buy box.
- Note: comparison for entry 3; ball-screw specification not read.

### 5. MGN12H 300 mm linear rail with carriage
- Vendor: Amazon. https://www.amazon.com/dp/B07ZVFFXQZ
- Price $20.49; free delivery Thu Oct 1.
- Stated: bearing-steel rail 300 mm, MGN12H pre-loaded stainless carriage.
- Sales evidence: 4.2 stars, 615 reviews. (These are the 3D-printer-class rails; a very common widely used ecosystem.)
- Prime: buy box.
- Note: the guide for a printed or plate-built fine stage. Pairs with a T8 lead screw or a micrometer head.

### 6. LabZhang 6 x 6 in stainless lab jack (scissor)
- Vendor: Amazon. https://www.amazon.com/dp/B085RQX3PH
- Price $22.99; free delivery Tomorrow (Sep 29).
- Stated: lift 74-275 mm; maximum support weight 25 kg (55 lb); hand wheel.
- Sales evidence: 4.3 stars, 458 reviews, "50+ bought in past month".
- Prime: buy box.
- Note: scissor jacks tilt and wander; see `calc/03-abbe-and-stack.mjs` (0.3 degree illustrative). A hand-set Z coarse stage, not a fine one.

### 7. VEVOR heavy duty locking drawer slides, 20 in, one pair
- Vendor: Amazon. https://www.amazon.com/dp/B0DYMW7WVB
- Price $24.90; free delivery Fri Oct 2.
- Stated: 250 lb capacity, steel 0.77 in (19.5 mm) thick, locking.
- Sales evidence: 4.3 stars, 213 reviews, "50+ bought in past month".
- Prime: buy box.
- Note: the cheap long axis for a shuttle with a hard stop; play and tilt are large (not read), which is why the design leans on the stop and not the slide.

### 8. HUANUO single monitor mount, gas spring (13-32 in)
- Vendor: Amazon. https://www.amazon.com/dp/B0CTJYYSML
- Price $39.99; free delivery Tomorrow (Sep 29).
- Stated: holds 4.4-19.8 lb; VESA 75 x 75 and 100 x 100 mm; clamp mount; gas spring.
- Sales evidence: 4.6 stars, 16,507 reviews, "1K+ bought in past month". This is the clearest high-volume evidence in this file.
- Prime: buy box.
- Note: Derek's monitor-arm example. Payload window (4.4-19.8 lb) brackets a gun in a shell plus part of a cable; joint play is not stated.

### 9. uxcell 8 mm precision balls, G10 solid chrome steel
- Vendor: Amazon. https://www.amazon.com/dp/B081SQYW4D
- Price $5.79; free delivery Tomorrow (Sep 29).
- Sales evidence: 4.7 stars, 128 reviews. (Other grades seen as Prime cards: G25 60-pack, 4.8 stars, 29 reviews; 304 stainless G100, 4.6 stars, 253 reviews, "100+ bought".)
- Prime: buy box.
- Note: the three balls of a return seat. Grooves would be printed or machined; not sourced.

### 10. N52 neodymium cup magnets with countersunk hole, 4/5 in
- Vendor: Amazon. https://www.amazon.com/dp/B0FL74BSHV
- Price $23.99; free delivery Fri Oct 2.
- Sales evidence: 4.4 stars, 38 reviews.
- Prime: buy box.
- Note: preload for the seat. Pull force not read; sizing against gun mass and cable pull is not possible until those are measured.

### 11. TOAUTO 3-axis digital readout with optical linear scales (350 mm example)
- Vendor: Amazon. https://www.amazon.com/dp/B08Y5YVJ6N
- Price $85.99; free delivery Thu Oct 1.
- Stated: optical scale, travel in 50 mm steps to 1000 mm; scale length = travel + 140 mm. Resolution and the display's data output: not read.
- Sales evidence: 4.6 stars, 6 reviews. Low volume. Prime buy box.
- Note: the "hand moves, software reads" idea needs a scale whose count software can read (quadrature or serial); whether this display exposes it is not known. iGaging-type scales are a known alternative: not checked.

### 12. HDLNKAK digital dial indicator, 1 in / 25.4 mm range
- Vendor: Amazon. https://www.amazon.com/dp/B09XN5FXTR
- Price $23.99; free delivery Tomorrow (Sep 29).
- Sales evidence: 4.4 stars, 101 reviews.
- Prime: buy box.
- Note: read-out only in the text I saw; no data output stated. A separate Prime card, "RS232 data cable for digital dial indicators" (B0F3J171Y5, $39.99, 2 reviews), suggests some indicators have a data port. A micron-class, software-readable probe is the gap for the nest-driver idea and remains **unresolved**: no Prime laser or inductive displacement sensor at that resolution surfaced in three searches.

### 13. YJINGRUI retractable spring balancer, 1-3 kg
- Vendor: Amazon. https://www.amazon.com/dp/B08HD3XZG2
- Price $39.22; free delivery Tomorrow (Sep 29).
- Sales evidence: 4.6 stars, 13 reviews. Low volume. Prime buy box.
- Note: a light tool balancer; the umbilical mass and stiffness are unknown so its range is not checked.

### 14. STEPPERONLINE planetary gearbox 50:1 for NEMA 17
- Vendor: Amazon. https://www.amazon.com/dp/B0BPH7LQBD
- Price $30.00; free delivery Tomorrow (Sep 29).
- Stated in the title: gear ratio 50:1, backlash "50" (unit cut off in the text I read).
- Sales evidence: no rating shown for this listing. Prime buy box.
- Note: an angular reduction for a stepper on an arc or hinge (dot-centred idea); the 50:1 ratio turns 0.9 degree full steps into 0.018 degree at the output before backlash.

### 15. Keenso XY micrometer cross-roller stage (60 mm class)
- Vendor: Amazon. https://www.amazon.com/dp/B07QW8MCVY
- Price $116.58 (SEMY60-AC); free delivery, Prime card.
- Sales evidence: 5.0 stars, 2 reviews. Low volume.
- Prime: card.
- Note: shows the micrometer-stage form of a fine stage; the load of a gun and shell is probably too much for a 60 mm stage; not checked.

### 16. Ratchet micrometer head, 0-25 mm
- Vendor: Amazon. https://www.amazon.com/dp/B07VHMYCGD
- Price $15.99; 3.7 stars, 8 reviews. Low volume. Prime: card.
- Note: the reduction element of a hand or motorised fine stage.

### 17. Brass shim stock assortment, 24 pieces, 1 x 6 in
- Vendor: Amazon. https://www.amazon.com/dp/B0BS3P7FMM
- Price $15.99; free delivery Tomorrow (Sep 29).
- Stated: six thicknesses, 0.002, 0.004, 0.006, 0.008, 0.012, 0.016 in (0.05 to 0.41 mm).
- Sales evidence: 4.5 stars, 253 reviews, "100+ bought in past month".
- Prime: buy box.
- Note: Z or radial adjustment in 0.05 mm steps without a stage.

### 18. 2020 T-slot aluminium extrusion, 500 mm, 4-pack
- Vendor: Amazon. https://www.amazon.com/dp/B08Y8KCJW4
- Price $30.99; Prime card. Sales evidence: 4.7 stars, 984 reviews, "50+ bought".
- Note: frames and holder posts.

## Wave 2 additions (observed 2026-09-29, same method: Prime-eligible filter in the search URL, Prime-badged cards read; one product page checked)

| For | Need | Entry |
|---|---|---|
| travel-14 crown seat | spring pads / plungers | 19 |
| travel-14 crown seat | wire pair for the free-axis tether | 20 |
| travel-14 crown seat | strain gauge for the drag torque | 21 |
| datum-09 preplaced filler ring (comment, travel-16) | 0.035 in ER316L wire | 22 |
| datum-12 (travel-17) | 12 in lazy Susan bearing for wedge rings | 23 |

### 19. NACX ball plunger set, 10 pcs (8 x 9 mm, 12 N)
- Vendor: Amazon. https://www.amazon.com/dp/B08SWJ63PM
- Price $8.99; free delivery Tomorrow (Sep 30).
- Stated in the title: 8 x 9 mm, 12 N (end force; stroke not read).
- Sales evidence: 4.4 stars, 91 ratings. (Other Prime cards for the same class: 20 pcs 0.12 in ball plungers $7.99, 9 ratings; M10 and M12 push-fit spring plungers $10-17, fewer than 10 ratings each.)
- Prime: card.
- Note: an off-the-shelf detent plunger is a light spring (12 N end force over a stroke of a millimetre or two is on the order of 5 to 10 N/mm, not read), well below the 40 to 50 N/mm the crown seat calc asks of a centring pad (`calc/08`). It seats the ring; a coil or leaf spring pad, or a lock, is what holds it. A printed pad on a steel leaf is the other route.

### 20. 1/16 in 304 stainless wire rope (7x7), 100 ft with ferrules and crimp tool
- Vendor: Amazon. https://www.amazon.com/dp/B0CSJVCSF3
- Price $24.99; free delivery Today 5-10 PM on $25 of qualifying items.
- Sales evidence: 4.5 stars, 1.1K ratings, "300+ bought in past month". (Second card: same class, 165 ft with 100 ferrules, $32.99, 4.6 stars, 859 ratings, "100+ bought".)
- Prime: card.
- Note: the wire pair wrapped on the ring (`travel-14-exact-crown`): a pre-tensioned tangential couple, stiff about the tube axis. 1/16 in (1.6 mm) rope is a little more than the 1.5 mm assumed; stiffness, pretension and creep of a crimped run are not known. Turnbuckle-style tensioners are sold in kits of the same class ($22.99, 28 ratings).

### 21. SparkFun load cell amplifier HX711
- Vendor: Amazon. https://www.amazon.com/dp/B079LVMC6X
- Price $11.50; free delivery Tomorrow (Sep 30).
- Sales evidence: 4.6 stars, 75 ratings, "100+ bought in past month". (Cheaper 5 kg cell plus HX711 combo packs: $6.79 with 14 ratings; 2-set packs $9.99 with 100+ bought in past month.)
- Prime: card.
- Note: a strain-gauge amplifier, 24-bit; the gauge on one wire of the tether pair reads the drag torque nobody has measured. Needs a cell or a foil gauge matched to newtons, not kilograms: not sized.

### 22. Stainless MIG wire ER316L .035 in, 2 lb roll
- Vendor: Amazon. https://www.amazon.com/dp/B09BKG56JY
- Price $31.00; Two-Day free delivery Thursday Oct 1; ships from Amazon, sold by Welding Partners.
- Stated: AWS A5.9 ER316/ER316L, .035 in (0.89 mm), 4 in spool.
- Sales evidence: 4.3 stars, 22 ratings.
- Prime: buy box (Prime badge and free delivery shown).
- Note: the wire class for datum-09's ring (0.89 mm has 0.62 mm^2, 91 percent of the 0.684 mm^2 the recorded fillet needs). The ring is wound on a printed mandrel by hand; nothing about fusing it is checked. Common size in the MIG ecosystem, so unlike the 0.030 in feed wire it is not a niche part.

### 23. 12 in (300 mm) lazy Susan bearing, heavy-duty metal turntable
- Vendor: Amazon. https://www.amazon.com/dp/B01L8EHD6K
- Price $22.99; free delivery Today 5-10 PM on $25 of qualifying items.
- Sales evidence: 4.6 stars, 2.6K ratings, "200+ bought in past month". (Cheaper: $13.99 with 341 ratings, "200+ bought".)
- Prime: card.
- Note: the ring bearing for a Risley pair of wedge rings under the rotator (`calc/11-wedge-abbe.mjs`), or the upper ring of a crown (datum-03 cites a 6 in unit; a 12 in one is too large for the 127 mm tube but fits the wedge use). Axial and tilt play are not stated and matter: the rotator stands 232 mm above it.

## Wave 3 additions: bought arms and other multi-axis positioners (observed 2026-09-29)

Same method: Prime-eligible filter in the search URL (`rh=p_85:2470955011`); only Prime-listed results were read; the product pages marked "buy box" were opened in my own Chrome tab and the buy box showed the Prime badge and a free-delivery date. Other vendors (the arm makers' own stores, resellers) are ordinary retail and are recorded as such. Nothing was ordered, added to a cart or sent to a vendor; the tab was closed when done.

| For | Need | Entry |
|---|---|---|
| travel-20 to 22 (an arm holds the gun) | an arm that carries a gun of about 1 to 1.5 kg | none on Prime; 31 to 33 (maker stores, datasheet, reseller pages) |
| travel-20 to 22 | a desk arm to carry a camera or a stylus, or to read joint angles | 24 to 29 (Prime; 0.25 to 0.5 kg) |
| travel-20 (SCARA, delta, hexapod, gantry classes) | Prime listings of the class | SCARA, delta and hexapod searches returned only educational arm kits (34); gantry axes are entries 3, 4 and 5 |
| travel-20, 21 (coarse arm, fine stage) | a fine XYZ stage at the flange or under the work | 30 (and 12, 15, 16 for a motorised one) |

### 24. Dobot Magician Lite, K12 platform (4-axis desktop arm)
- Vendor: Amazon. https://www.amazon.com/dp/B086V7XJLY
- Price $999.00; free delivery Thu Oct 1 (ordered-within countdown shown); "Only 2 left in stock".
- Stated on the page: maximum reach 340 mm; maximum load 0.25 kg; repeatability 0.2 mm; 12 expansion interfaces; graphical programming.
- Sales evidence: 5.0 stars, 2 ratings. Low volume.
- Prime: buy box.
- Note: below the gun's mass by a factor of four or more. A 4-axis arm of the SCARA-like class (x, y, z, rotation); the maker's software interface lists Python and other languages (page: "20 coding languages"): not tried. Carries a camera or a stylus, not the gun.

### 25. Dobot Magician educational kit, advanced (4-axis desktop arm)
- Vendor: Amazon. https://www.amazon.com/dp/B01N3SFOHT
- Price $1,999.00; free delivery Thu Oct 1; "Only 1 left in stock".
- Sales evidence: 4.3 stars, 9 ratings. Low volume. Prime: buy box.
- Stated by the maker's specification sheet (found by search, not the Amazon page): 4 axes, 500 g payload, 320 mm reach, position repeatability 0.2 mm; USB, Wi-Fi, Bluetooth.
- Note: the 500 g class; same conclusion as 24.

### 26. DOBOT Magician educational programming robot, basic version
- Vendor: Amazon. https://www.amazon.com/dp/B01J3Q2Q1M
- Price $1,799.00; free delivery Oct 2 to 6 for Prime members. Sales evidence: 3.0 stars, 1 rating. Prime: buy box.
- Stated: 4-axis; 13 external ports and an integrated API "designed for 2nd development"; 20 coding languages.

### 27. wlkata Mirobot professional kit (6-axis desktop arm)
- Vendor: Amazon. https://www.amazon.com/dp/B094FRPJ16. $2,050.00; free delivery Sun Oct 4 for Prime members; "Only 2 left in stock"; 4.0 stars, 5 ratings; Prime card (first read in `sourcing/borrowed.md`).
- Note: payload 0.25 kg standard per the maker (search); below the gun.

### 28. Hiwonder SO-ARM101 AI robotic arm kit (6-axis, 12 servos)
- Vendor: Amazon. https://www.amazon.com/dp/B0GT9D7PGP. $459.99; free delivery Tomorrow, Sep 30; 4.4 stars, 4 ratings, "50+ bought in past month"; Prime card.
- Note: 12-bit magnetic servo encoders per the listings' class (0.088 degree per count, `sourcing/borrowed.md`): the cliff the encoder-bits slider in `travel-20` shows (0.1 to 0.5 mm per count at the dot); payload about 0.5 kg per borrowed's search summary. Not a gun carrier; the "leader arm" role (a hand moves it, encoders read) is borrowed-03's.

### 29. reBot B601-DM assembled arm kit, 6+1 DoF (Python SDK, ROS1/ROS2)
- Vendor: Amazon. https://www.amazon.com/dp/B0H2TWVFSW. $1,899.00; free delivery Tomorrow, Sep 30; no rating shown; Prime card.
- Note: the most expensive desk-size arm with a stated SDK and ROS on Prime; payload not read on the card.

### 30. XYZ 3-axis manual linear stage, 60 x 60 mm
- Vendor: Amazon. https://www.amazon.com/dp/B07D7NM2WF. $130.00; free delivery Tomorrow, Sep 30. Sales evidence: 3.8 stars, 19 ratings. Prime: buy box.
- Stated: XY travel 6.5 mm, Z travel 10 mm; 0.01 mm minimum scale resolution; 0.03 mm accuracy and 0.03 mm parallelism; 0.75 kg; supports up to 24.5 N (3 kgf).
- Note: the fine stage class for the flange or the tip: a 3 kgf load rating brackets a 1.2 to 1.5 kg gun with little margin and puts the stage in the load path (`travel-20`, "stage at the flange"). Manual; a motorised version is micrometer heads with steppers (entry 16). Its travel (6.5 and 10 mm) covers the trim range with room; its stiffness and backlash are not stated.

### 31. Fairino FR3 collaborative robot (maker's US store, ordinary retail)
- Vendor: fairino.us, https://www.fairino.us/collaborative-robot/fairino/fr3. Price $6,799.00 with an Add To Cart button; no lead time stated on the page (read 2026-09-29); the page's comparison table lists an 18-month manufacturer warranty and 5 years of US-based support. (The "(WMS)" and "(WML)" variants are $7,499 per search summaries.)
- Stated: 3 kg payload, 622 mm reach, pose repeatability +-0.02 mm (ISO 9283), 6 axes, typical TCP speed 1 m/s, footprint 128 mm, 15 kg; tool I/O 24 V / 1.5 A; two digital and two analog I/O, two high-speed pulse inputs, RS485.
- Interface (search summary of the maker's documentation and the GitHub SDK, unchecked on the pages): Python and C++ SDKs; `ServoJ` (joint) and `ServoCart` (Cartesian, absolute or offset) accept commands at 60 to 1000 Hz (1 to 16 ms between calls); the pulse inputs could take the rotator's encoder.
- Sales evidence: none stated. Not a Prime listing (ordinary retail).

### 32. Universal Robots UR3e (datasheet; ordinary retail through distributors)
- Datasheet: https://www.universal-robots.com/media/1807464/ur3e_e-series_datasheets_web.pdf (read 2026-09-29): 3 kg payload, 500 mm reach, pose repeatability +-0.03 mm (ISO 9283), six rotating joints of +-360 degrees, base joint 180 degrees/s, tool-flange force/torque sensor (range +-30 N, precision +-2.0 N, accuracy +-3.5 N; torque +-10 N.m, precision 0.1 N.m), four quadrature digital inputs, Modbus-TCP, EtherNet/IP, PROFINET, ROS/ROS2; a payload chart that falls from 3 kg at small centre-of-gravity offsets to about 2 kg at 250 mm and 1.3 kg at 400 mm (read by eye); link lengths 151.8, 243.5, 213.2, 131.05, 85.35 and 92.1 mm (used in `travel-20`).
- Interface (UR's RTDE page, read): a TCP/IP protocol on port 30004 that streams joint and tool positions, velocities and forces and lets a client write registers, at up to the control frequency (500 Hz on e-Series, per search).
- Price: $33,011 in Fairino's own comparison table (a competitor's figure, unverified); no distributor page read; lead time not observed.

### 33. Other arms found by search (maker or reseller pages; not read on the vendor page)
- Dobot Nova 2 (2 kg, 625 mm reach, +-0.05 mm) $12,790 and Dobot CR3A (3 kg, 620 mm, +-0.02 mm) $22,200 at top3dshop.com (search summaries); TCP/IP, Modbus TCP/RTU and a Python SDK on GitHub (`Dobot-Arm/TCP-IP-Python-V3`). Delivery not observed.
- UFACTORY Lite 6 (0.6 kg, 440 mm, +-0.5 mm) and xArm 6 (5 kg, 700 mm, +-0.1 mm) at RobotShop and others; RobotShop's page returned HTTP 403, so no price or delivery was read; the search summary says the xArm 6 is "contact for pricing" at most retailers and names an open-source Python/C++ SDK and ROS/ROS2 packages.

### 34. Not on Prime: delta, SCARA, hexapod
- Prime-filtered searches for "SCARA robot arm", "delta robot parallel arm kit", "hexapod stewart platform 6 dof" and "delta 3d printer" returned educational arm kits and unrelated items (a Dobot Magician is the nearest to a SCARA: entries 24 to 26). No Prime listing states a payload above 0.5 kg for any arm. Hexapod parts routes are in `sourcing/borrowed.md`; the Physik Instrumente H-811 hexapod is a quote product (borrowed's search summary).

## Non-Amazon observations

- **XLaserlab X1 Pro, xlaserlab.com**, https://www.xlaserlab.com/products/xlaserlab-x1-pro-laser-welder-cleaner-cutter (read 2026-09-28): states a 21 kg desktop unit; the gun weight, gun dimensions, fibre length, wobble parameters and PC/RS232 control are **not stated** on the page. Gun mass is therefore still unknown to this study; the search snippets that give 19 kg or 21 kg refer to the whole machine.
- **General handheld-gun explainer, chutian-laser.com** (a different manufacturer, not the X1 Pro), https://chutian-laser.com/dive-into-the-handheld-laser-welding-gun/ (read 2026-09-28): the red pilot light is a separate diode aligned parallel to the main beam; software can offset the red light to match the beam; adjusting it moves only the red light, not the welding beam. Nothing on galvo or wobble centre adjustment. This bears on `travel-12-heads-own-stage`: for the X1 Pro the "red light alignment" screen probably calibrates the pilot, not the weld, **unchecked for this machine**.
- **Kinematic coupling repeatability, literature**, e.g. https://pure.tue.nl/ws/files/1439398/605178.pdf (TU Eindhoven, "Design of a kinematic coupling for precision applications") and search results citing Slocum, *Precision Machine Design* (1992): repeatability below 1 micron, about +-0.25 micron in preliminary experiments, for precision-ground contacts. **Not checked** for printed grooves with steel balls, which will be much worse; the study does not assume a number.

## Gaps

- Wave 3: no Prime listing of an arm that carries a gun (payload of 1 kg or more); the two arms found that state 3 kg and +-0.02 to +-0.03 mm are sold by their makers; no delivery time was observed for either. No stiffness, lost-motion or thermal-drift figure for any arm read; no flange stiffness on any datasheet.
- Wave 3: the arm makers' software interfaces are recorded from search summaries and one datasheet; none has been tried against a real arm.

- A micron-class, software-readable probe on Prime (nest driver, cascade): not found.
- Gun mass and umbilical pull: neither the manual nor the vendor page states them; Derek can weigh the gun.
- Stated stiffness, tilt or backlash of any stage above: none read; entries give capacity and travel only.
- A spring pad of 40 to 50 N/mm: the detent plungers seen (entry 19) are a 12 N end-force class; no Prime listing states a spring rate.
- Torsion or stretch stiffness of pre-tensioned wire rope (entry 20): the listings give diameter and strand only.
