# Back Panel Port Geometry — John Guest PP1208W Bulkhead Union

Research for the enclosure rear wall external connection ports. The enclosure carries 5 external connections: carbonated water inlet, carbonated water outlet, tap water inlet, and two flavor dispense outlets. The vision specifies all external connections use 1/4" hard tubing with John Guest quick connects.

---

## 1. Fitting Identification

**Part number: PP1208W-US** (Polypropylene White Bulkhead Union, 1/4" OD x 1/4" OD)

This is the correct fitting for through-panel mounting of 1/4" OD tubing. It provides a push-fit connection on each side of the panel, allowing tubing to be inserted from either face. The fitting body passes through the panel hole; a locking nut on the interior face clamps the fitting in place.

This is the same fitting family used for the pump cartridge dock (PP1208W), but at the enclosure rear wall the application is panel mounting rather than cartridge docking.

**Variants in the same family:**
- PP1208W-US — 1/4" OD tube, 0.67" (17.0 mm) mounting hole
- PP1212W-US — 3/8" OD tube, 0.83" (21.1 mm) mounting hole
- PP1216W-US — 1/2" OD tube, 1.06" (26.9 mm) mounting hole

The design uses only 1/4" tubing throughout, so PP1208W-US is the correct fitting for all 5 rear wall ports.

**Material:** White polypropylene body, food-grade EPDM O-ring, acetal collet with stainless steel grip teeth. NSF 51 and NSF 61 listed. Suitable for potable water and food-contact applications.

**Source:** John Guest Fluid System Products Catalog 2025 (official), John Guest US product page for Polypropylene White Bulkhead Union.

---

## 2. Panel Hole Dimensions

**Mounting hole diameter: 0.67 inches = 17.0 mm**

This is confirmed directly from two official John Guest sources:
1. The 2025 Fluid System Products Catalog (page 13), which lists the Bulkhead Union table with columns "Tube OD" and "Mounting Hole Dia." — PP1208W-US reads 1/4" and 0.67".
2. The John Guest US product page at johnguest.com/us/en/od-tube-fittings/polypropylene-white/bulkhead/bulkhead-union, which lists the same 0.67 in. value.

**For a printed part**, the 17.0 mm nominal hole must be adjusted per FDM printing constraints: holes print smaller than designed. Per requirements.md, add 0.2 mm for loose fit or 0.1 mm for press fit. The fitting needs to slide in easily for assembly, so design the hole at **17.2 mm diameter** (17.0 mm + 0.2 mm loose fit allowance). Verify empirically with a test print.

---

## 3. Panel Thickness Range and Retention Geometry

**Maximum panel thickness: approximately 15–16 mm** (0.59–0.63 in.)

The fitting body has a threaded section that passes through the panel hole. A separate locking nut (supplied with the fitting) threads onto the body from the interior face and clamps the fitting in place. The locking nut on the PP1208W is a **hexagonal plastic nut** visible in catalog photos.

**Retention mechanism:** Threaded body + separate locking nut. Not a snap ring or clip. The nut engages the body thread and tightens against the interior panel face. The exterior shoulder/flange on the fitting body bears against the exterior panel face.

**Thread on the fitting body (inferred from catalog photos and AI overview):** The PP1208W body thread is in the range of 3/8" nominal. The exact thread pitch is not published by John Guest in their public documentation, but the locking nut is a captive nut supplied with the fitting — it is not separately sourced.

**Nut outer diameter (across flats):** Visible in catalog photos as approximately 21–22 mm across flats for the 1/4" fitting, consistent with a standard hex nut that fits a 17 mm hole body. This is an estimate from scaled product photos; measure physically to confirm.

**For the enclosure rear wall:** The wall thickness must be 15 mm or less for the fitting to mount correctly. The enclosure vision specifies no required wall thickness for the rear wall, but the pump cartridge research established 3–4 mm as typical printed wall thickness. **A 3–4 mm printed rear wall is well within the 15–16 mm maximum panel thickness**, leaving 11–12 mm of thread engagement available on the body — more than adequate for the nut to engage and clamp firmly.

**Design value:** Rear wall thickness of 3.0–4.0 mm is appropriate. The fitting will have significant engagement depth on the nut with this thin wall, which is fine — the nut simply threads further before clamping.

---

## 4. Overall Fitting Dimensions

**Overall body length (end-to-end, tube entry to tube entry): approximately 34.9–35 mm** (1.375–1.38 in.)

This is the distance from one collet face to the other collet face. At a 3–4 mm panel, the fitting extends approximately:
- **Exterior protrusion** (outside rear face): the exterior shoulder/flange and push-fit collet face. Based on the 35 mm total length minus the 3–4 mm panel thickness minus the nut-engaged length, the exterior protrusion is approximately **18–20 mm** from the exterior panel face.
- **Interior protrusion** (inside enclosure): the remaining collet face and body, approximately **12–14 mm** inside the enclosure wall.

These are estimates derived from the total body length and typical bulkhead union geometry (symmetric body, shoulder at mid-point). For precise values, measure a physical PP1208W fitting with calipers.

**Body outer diameter (maximum, at shoulder/flange):** Based on the 17.0 mm hole and the need for the shoulder to bear against the panel exterior, the shoulder diameter is larger than 17.0 mm — estimated **19–21 mm** across the widest part of the exterior shoulder. Consistent with what is visible in catalog and Amazon product photos.

---

## 5. Fitting Face Geometry (External / Rear-Facing)

The external face of the PP1208W at the rear wall is the **push-fit collet entry face**:
- The collet is an annular ring visible at the fitting entry, approximately flush with or slightly recessed (0.5–1 mm) from the body end face
- The tube bore is 6.35 mm (1/4" OD tube passes through)
- The collet OD is approximately 10–11 mm (from quick-connect-collet-specs.md prior research)
- The exterior shoulder/flange bears against the outside of the rear wall and acts as the stop that prevents the fitting from pulling through inward

**Protrusion beyond panel surface:** The fitting protrudes approximately 18–20 mm proud of the exterior rear face. This protrusion is occupied by the fitting body and collet, which are integral to the push-fit function and cannot be recessed further. The fitting cannot be made flush with or recessed into the panel surface because the collet must be accessible to press when disconnecting tubing.

**Consequence for design:** The rear wall of the enclosure will have 5 fittings protruding ~18–20 mm from its exterior face. This sets the minimum standoff required between the enclosure rear and any cabinet wall or surface behind it. If the device is installed under a sink, the fittings will not contact the cabinet back panel as long as there is at least 25 mm of clearance behind the enclosure.

---

## 6. Tubing Bend Radius Behind the Panel (Interior Clearance)

After the fitting passes through the rear wall, tubing connects to the interior push-fit face. The interior protrusion of ~12–14 mm provides the tube entry depth. Beyond the fitting end on the interior side, the tubing must curve to route toward its destination inside the enclosure.

**Minimum bend radius for 1/4" OD LLDPE/hard poly tubing:** 32–41 mm (1.25–1.625 in.)

The JG LLDPE catalog tubing specification cites 1-1/4" (32 mm) as the standard minimum bend radius for 1/4" OD tubing. This is a manufacturer-published value for their own LLDPE tubing intended for use with their push-fit fittings. Stiffer tubing (e.g., semi-rigid polyethylene or nylon) will require a larger minimum bend radius, trending toward the 41 mm upper value.

**Clearance required behind the panel:** To allow a 90° bend routing the tubing from the rear wall port toward the interior, the tubing needs a quarter-circle of bend room. At 32 mm radius, a 90° bend sweeps through approximately 32 mm of depth from the fitting exit. Adding the interior fitting protrusion (12–14 mm) and the bend radius (32 mm minimum), the minimum depth from the interior panel face before the tube can complete a 90° turn is:

**12 mm (fitting body interior) + 32 mm (bend radius) ≈ 44 mm from the interior rear wall face**

This means tubing routed from the rear wall ports needs approximately 44 mm of clear interior depth behind the rear wall before it can make a turn. The enclosure is 220 mm deep, so there is ample space. No routing constraint from this geometry.

---

## 7. Port Spacing — Independent Operation

Each port requires a user to push a tube in (insert) or press the collet and pull (remove). The collet on a 1/4" fitting has an OD of approximately 10–11 mm, but the user's fingers approach the fitting from the exterior face, which also has the exterior shoulder (estimated 19–21 mm OD).

**Ergonomic clearance requirement:**
- To press a collet and pull tubing, the user uses one or two fingers against the fitting face while the other hand holds the tube.
- The finger contact zone is approximately 15–20 mm wide per fitting (a finger approaching the collet from the side).
- Minimum center-to-center spacing to allow independent finger access: **25–30 mm** between adjacent port centerlines.

This is derived from:
- 17.0 mm fitting body diameter in the panel hole
- ~2–4 mm of printed wall material between adjacent holes (minimum for structural integrity)
- Finger clearance for the user to press the collet on one fitting without contacting the adjacent fitting

**Design value: 30 mm center-to-center minimum** between adjacent port holes. This provides 13 mm of wall material between hole edges (30 mm spacing minus 17 mm hole diameter = 13 mm between edges), which is generous for a printed part and provides good structural integrity around each hole.

At 30 mm spacing with 5 ports, a row arrangement requires: **4 × 30 mm = 120 mm** of total span across the row. The enclosure rear wall is 220 mm wide (enclosure is 220 mm × 300 mm × 400 mm per the vision). A 120 mm row of ports easily fits within the 220 mm rear wall width with 50 mm of margin on each side.

---

## 8. Summary — Design Values for the Enclosure Rear Wall

| Parameter | Value | Source |
|-----------|-------|--------|
| Fitting part number | PP1208W-US | JG Catalog 2025 / JG product page |
| Panel hole diameter (nominal) | 17.0 mm (0.67 in.) | JG Catalog 2025 — confirmed official |
| Panel hole diameter (print target) | 17.2 mm | requirements.md: +0.2 mm for loose fit FDM |
| Max panel thickness | 15–16 mm | Google AI Overview, consistent with fitting geometry |
| Recommended wall thickness | 3.0–4.0 mm | Well within max; leaves full nut travel |
| Retention method | Threaded body + hex locking nut (supplied) | JG product page, Google AI Overview |
| Fitting overall length (end-to-end) | ~35 mm | Google AI Overview |
| Exterior protrusion from panel face | ~18–20 mm | Derived: 35 mm total minus wall and interior section |
| Interior protrusion into enclosure | ~12–14 mm | Derived: 35 mm total minus wall and exterior section |
| Minimum bend radius (1/4" hard poly tubing) | 32 mm (1-1/4 in.) | Google AI Overview citing Polyconn and JG data |
| Interior depth before 90° bend possible | ~44 mm from interior face | 12 mm protrusion + 32 mm bend radius |
| Min center-to-center port spacing | 30 mm | Ergonomic: finger access to collet between adjacent fittings |
| 5-port row total span at 30 mm pitch | 120 mm | 4 × 30 mm |
| Enclosure rear wall available width | 220 mm | vision.md |

---

## 9. Failure Modes and Concerns

**Over-tightening the locking nut on a thin printed wall:** At 3–4 mm wall thickness, overtightening the nut during assembly could crack the printed panel around the hole, especially in PETG or PLA with low interlaminar strength. Mitigation: use a metal or steel washer on the interior face between the nut and printed wall to distribute load, or design a recessed boss (raised ring) around each hole on the interior side to provide 3+ perimeters of printed wall.

**Hole-to-hole structural integrity:** At 30 mm center-to-center with 17.2 mm holes, there are 12.8 mm of solid wall between hole edges. This is approximately 16 perimeters at 0.8 mm wall thickness — more than adequate. However, if ports are aligned in a row, the wall section is a thin strip with 5 large holes. Print orientation matters: the rear wall should be printed such that the layer lines run horizontally across the port row, not vertically (which would create a stack of thin layers between holes).

**Fitting pull-out under tube tension:** At the rear wall, tubes connect to external plumbing which can exert pull forces if the user pulls on tubing during installation/removal. The locking nut is the only thing retaining the fitting in the panel. A correctly tightened nut on a 15 mm panel provides substantial clamping force. On a 3–4 mm panel, the nut engagement length on the body threads is longer (since the shoulder stops against a thinner wall), which is actually favorable — the nut has more thread length to grab.

**Collet accessibility on exterior face:** With 5 fittings spaced at 30 mm pitch, the outermost fittings are 60 mm from the centerline and 120 mm span total. This is easy to reach anywhere across the row with a hand. No accessibility concern.

**Note on the PI1208W (acetal gray) variant:** The PI range (acetal gray) has the same 0.67" (17.0 mm) mounting hole diameter per the catalog (PI1208S-US, page 21). Acetal has higher pressure rating (230 psi vs 150 psi) and is suitable for compressed air, but costs more and is not white. Since the application is water and flavoring at 150 psi max (already at the PP limit), PP1208W-US is the correct choice. The acetal variant is not needed.

---

## 10. Connection to the Design

**The enclosure rear wall requires:**
- 5 holes, each **17.2 mm diameter** (17.0 mm nominal + 0.2 mm FDM correction)
- Minimum **30 mm center-to-center spacing** between adjacent holes
- A raised boss (recessed on the exterior, raised on the interior) around each hole to reinforce the printed wall against nut clamping force — design boss to provide at least 3 perimeters (2.4 mm radial thickness) around the 17.0 mm hole, making each boss approximately 22 mm OD
- **3.0–4.0 mm wall thickness** at the hole locations (well within the 15–16 mm maximum panel thickness for the fitting)
- Approximately **20 mm of exterior protrusion** per fitting must be accounted for in clearance behind the enclosure (no cabinet surface within 25 mm of the rear wall exterior)
- **44 mm of unobstructed interior depth** behind the rear wall for tubing to make its first bend — the enclosure is 220 mm deep, so this is not a constraint

A row of 5 ports at 30 mm pitch spans 120 mm. Centered on the 220 mm wide rear wall, this leaves 50 mm of margin on each side — sufficient for the wall snap features, structural ribs, and the enclosure half-split line.

---

## Sources

- John Guest Fluid System Products Catalog 2025 (johnguest.com/sites/default/files/files/John-Guest-Fluid-System-Catalog-2025.pdf) — official; pages 12–13 (PP White Bulkhead Union table)
- John Guest US product page: johnguest.com/us/en/od-tube-fittings/polypropylene-white/bulkhead/bulkhead-union — official; confirmed mounting hole 0.67 in for PP1208W-US
- Google AI Overview (sourced from JG and distributors): overall length ~35 mm, max panel thickness ~15–16 mm, nut/thread description
- Polyconn and Ryan Herco data (via Google AI Overview): minimum bend radius 1.25–1.625 in (32–41 mm) for 1/4" OD LLDPE tubing
- Prior repo research: hardware/printed-parts/pump-cartridge/planning/research/quick-connect-collet-specs.md — collet OD ~10–11 mm, confirmed PP1208W hole 0.67 in

## Open Questions Requiring Physical Measurement

1. **Exterior protrusion exact value** — measure from exterior panel face to fitting end face on a physical PP1208W in a 3 mm test panel
2. **Locking nut hex size (across flats)** — measure with calipers; needed to design interior boss geometry so the nut can be tightened with a wrench if needed
3. **Body thread specification** — the thread form and pitch on the PP1208W body is not published; measure with thread gauges if boss geometry needs to mesh with body
4. **Boss reinforcement geometry** — test print a single hole with raised boss at 22 mm OD, 3 mm wall, and tighten a PP1208W nut to confirm no cracking
