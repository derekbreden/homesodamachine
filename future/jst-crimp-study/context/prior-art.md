# Prior art

What already exists, at every price and scale, for each step of making an XH
cable end: separate the conductors, strip, feed and place the contact, crimp,
insert into the housing, inspect. Explorers start here instead of rediscovering
it. XH-specific dimensions and forces belong to [`xh-facts.md`](xh-facts.md);
this file covers machines, mechanisms and methods.

**How to read an entry.** Name, the mechanism in a sentence or two, cost or
source where known, and the link. Links marked **[mfr]** are manufacturer
documents; **[source]** is any other published source. Anything I infer is
marked **[estimate]** or **[assumption]**. Prices were observed 2026-09-28 on
non-Amazon pages. Amazon candidates are listed in
[`sourcing-requests.md`](sourcing-requests.md) for the Prime-confirmation pass.

**Kinds within each step:** maker / open-source builds; small-shop commercial;
industrial mechanisms worth borrowing; research; hand tools.

---

## Start here: four things that already do most of the job, slowly or cheaply

These four between them sketch a one-conductor-at-a-time ribbon machine.

- **JCW-2TE flat ribbon cable crimping machine.** A bench press that crimps
  side-feed terminals onto a pre-split, pre-stripped ribbon **one conductor at a
  time**. The operator clamps the ribbon once, a screw slide translates it
  sideways by the conductor pitch, and a "wire fork" guides each conductor
  exactly over the terminal before the foot pedal fires the crimp. Pitch, pin
  count and transfer speed are set on a touchscreen. 20 kN. Price not listed.
  [source](https://www.jcw-wirestripping.com/jcw-2te-flat-ribbon-cable-crimping-machine.html)
  TE's FFC termination machine does the same for flat flexible cable and can
  skip positions (J2's empty cavity 3 is a skip).
  [mfr](https://www.te.com/en/products/application-tooling/flat-flexible-cable-processing-machine.html)
- **Molex US 4,074,424 (1978), crimping and wire lead insertion machine.** The
  operator lays a stripped lead into an uncrimped terminal at the crimp
  station. The press crimps, grippers take the terminated lead to an
  **adjacent insertion station** and push it into a housing cavity, and a
  housing feed indexes the next cavity. A strip feed advances terminals one at
  a time. [source](https://patents.google.com/patent/US4074424A/en)
- **Sogang University, "Automated Terminal-to-Housing Assembly System for Flat
  Ribbon Cable Harness" (arXiv, Aug 2026).** A 3D-printed mechanism driven by
  12 Robotis Dynamixel XM430 servos on an OpenCR board inserts pre-crimped
  terminals of a 6-conductor #26 flat ribbon into 2.5 mm and 2.0 mm pitch
  6-way housings, with **no vision and no force sensing**. Curved guide
  channels passively fan the terminals to housing pitch. The housing then
  "leans and slides" on a hole edge, oscillates ±26.4° at 0.625 Hz
  ("weaving") while the cable advances, and a rack-and-pinion clamp locks it.
  Optical fibre sensors detect terminal presence. 67 of 80 trials succeeded
  end to end. Insertion itself succeeded 98%; most failures came in
  transferring the floppy cable. 33 s per cycle at half speed.
  [source](https://arxiv.org/html/2608.06996)
- **Kurabo Kurassem-WH.** A robot with 3D vision picks one wire from a bundle,
  measures the direction of its tip, **sets the wire into an ordinary terminal
  crimping machine**, then inserts the crimped contact into a connector. About
  10 s per wire. The press is stock; the robot is the operator.
  [mfr](https://www.kurabo.co.jp/el/world/en/kurasense/products/kurassemwh.html)

---

## 0. Whole-procedure machines (cut, strip, crimp, insert)

### Small-shop and industrial commercial

- **Chinese fully automatic crimp-and-insert machines** (Kingsing, Sanao, JMK
  JM-800, Juhai). They cut, strip, crimp and insert into single- or double-row
  housings at 1.25–3.96 mm pitch, AWG 30–18, about 1200 pieces/h, with a 2 t
  press, two-channel crimp force monitoring, CCD vision, and "housing insertion
  force detection". Quote only.
  [Kingsing](https://www.kingsing.com/product/1177.html) ·
  [Sanao](https://www.sanaomachine.com/product/Automatic-Terminal-Crimping-and-Housing-Insertion-Machine.html) ·
  [Juhai](https://juhaimachine.en.made-in-china.com/product/RAnrGJLbUgpY/China-Auto-Terminal-Crimping-and-Housing-Insertion-Machine.html)
- **Fully automatic two-end cut/strip/crimp for JST XH (no insertion).**
  Eastontech lists **US$3,500–4,500**, MOQ 1, AWG 30–18, 3800 pieces/h, taking
  "universal or mini-style applicators" (applicators may be extra).
  [source](https://ew-wirestripping.en.made-in-china.com/product/wFBfCSivKOhP/China-Eastontech-Fully-Automatic-Wire-Cutting-Stripping-Both-Ends-Jst-Xh-Terminal-Crimping-Machine-Double-Ends-Press.html)
  An AliExpress listing titled for JST VH/XH/SM/SH/PH carries about US$11,142
  in its title (page not readable).
  [source](https://www.aliexpress.com/item/1005001961961782.html)
- **JAM (Japan Automatic Machine).** Fully automatic machines that strip,
  crimp, insert and test, and **semi-automatic "manually loaded" machines for
  stripping, crimping and insertion**, a class between bench press and
  full automation.
  [mfr](https://www.jam-net.co.jp/eng/product/crimping/)
- **Komax Zeta 633/656.** Wire processing for control cabinets. With the
  Zeta 656 block loader, the insertion head pushes processed wire ends into
  spring-clamp terminal blocks, and a pull test confirms each one locked.
  [source](https://connectorsupplier.com/control-panel-manufacturing-gets-automated-komas-zeta-111213/) ·
  [mfr](https://www.komaxgroup.com/en-us/products/wire-processing/higher-automation-platforms/harness-manufacturing)
- **Cellios intRAC (Fraunhofer IPA spin-out, with TE and MVTec).** Robot cell
  that cuts and strips, crimps with a semi-automatic crimp tool, and inserts
  MQS contacts into housings. Two 2D cameras measure where the crimp sits in
  the gripper **after every handling**, because "the position of the crimp in
  the gripper changes with every handling operation". A force-torque sensor
  regulates insertion force. 0.1 mm insertion accuracy. The prototype is
  slower than a person; the production version is due mid-2027.
  [source](https://www.roboticstomorrow.com/story/2026/09/with-precision-and-clear-vision-robots-work-autonomously-in-wire-harness-manufacturing/27141/) ·
  [source](https://interaktiv.ipa.fraunhofer.de/start-ups/filigrane-kabelmontage-mit-robotern/)

### Research

- **University of Tennessee.** A UR10e with custom grippers picked terminated
  wire ends from a staging area and pinned them into connectors: 47 wires, 7
  connectors. Proof of concept. The team's conclusion: harnesses "need to be
  designed for automation from the start".
  [source](https://www.assemblymag.com/articles/99868-volunteer-engineers-tackle-wire-harness-automation)
- **Molex US 4,718,167, semi-automatic harness fabricating apparatus.** The
  operator loads a connector into a nest and feeds conductors into entry
  ports. A microswitch fires termination; tapered insertion blades push the
  terminals fully into their cavities; a **spring-biased pawl and ratchet
  indexes the connector one position**.
  [source](https://patents.google.com/patent/US4718167A/en)

---

## 1. Separate and fan the conductors

### Maker / open source

- **Pull-apart by hand (zip cord).** Zip cord is made to separate by pulling
  the conductors apart from the tip. Whether BNTECHGO silicone ribbon tears
  cleanly this way is untested (shared context, Open item 5).
  [source](https://en.wikipedia.org/wiki/Zip-cord)
- No open-source ribbon splitter or fan-out jig turned up.

### Small-shop commercial

- **Automatic ribbon cut / split / strip machines.** Chinese makers sell
  bench machines that feed ribbon with rollers or belts, split between
  conductors, cut to length and strip both ends. Three split methods appear:
  - **cylinder punching** (a die punches out the web between conductors; for
    many-pin and webbed cable);
  - **cylinder "scribing" or slide cutting** (a knife slides along the web for
    a set split length; for few-pin cable);
  - **electric punching** (the same punch driven by a motor, no air).

  Belt feed rather than roller feed prevents slip on wide ribbon. Up to 20 or
  25 mm width, 16–20 pins, split length 1–200 mm, 1000–5000 pieces/h. Quote
  only.
  [Kingsing](https://www.kingsing.com/product/697.html) ·
  [HongHao HH-420](https://wireharnessor.com/product/hh-420-computerized-splitting-cutting-and-stripping-machine-for-flat-ribbon-cable/) ·
  [JCW-CS12](https://www.jcw-wirestripping.com/jcw-cs12-automatic-flat-ribbon-cable-slitting-and-stripping-machine.html) ·
  [WIREPRO SF-SE4](https://www.wireproauto.com/product/sf-se4-flat-ribbion-cable-automatic-cutting-slitting-stripping-machine/)
- **Hand ribbon separators** (for example Flat Cable Solutions SL-3 "Slitz-It")
  split large flat cables into smaller counts; the site did not resolve on
  2026-09-28.
  [source](https://flatcablesolutions.com/product/sl-3-slitz-it-flat-ribbon-cable-separator/)

### Industrial mechanisms worth borrowing

- **Interlaced toothed jaws (US 4,179,964).** Two opposed combs whose teeth are
  channel-shaped cradles one conductor wide, spaced at conductor pitch. As the
  jaws close, the teeth interlace, **shear the web between side faces of
  alternate teeth, and push neighbouring conductors apart**. The action is a
  lever through a roller bearing.
  [source](https://patents.google.com/patent/US4179964A/en)
- **Scalloped meshing cutters with a convex blade (US 4,046,045, ITT, 1977).**
  Concave scallops sit over each round conductor to stabilise it. One cutter is
  curved along the cable length, so the shear starts at a point and progresses,
  which lowers the force and avoids jacket damage.
  [source](https://patents.google.com/patent/US4046045A/en)
- **Wire fork** (JCW-2TE, above). A fork guides one conductor at a time over the
  terminal while the rest of the ribbon stays clamped.
- **Passive curved fan-out channels** (Sogang, above). Curved guide paths,
  derived from a geometric model, take conductors from ribbon pitch to housing
  pitch with no actuator.

---

## 2. Strip

### Maker / open source

- **ProjectsWithRed auto wire stripper/cutter.** ESP32, three NEMA 17
  steppers. A 3D-printer extruder feeds the wire, and two steppers drive the
  cut and strip blades on threaded rods. OLED plus encoder. Aimed at
  solid-core prototyping wire.
  [GitHub](https://github.com/ProjectsWithRed/auto-wire-stripper-cutter) ·
  [Hackaday 2025](https://hackaday.com/2025/06/03/building-an-automatic-wire-stripper-and-cutter/)
  A fork on an Arduino Pro Mini also exists.
  [GitHub](https://github.com/Tozzi89/auto-wire-stripper-cutter-arduino)
- **Mr Innovative / sandy9159 wire prep machine.** A stepper feeds wire through
  a tube into the jaws of an ordinary hand stripper closed by a second
  stepper. A **hobby servo bends the guide tube** to aim the wire at the
  cutting notch or the stripping notch. A partial close **nicks** the
  insulation and the person pulls the slug. Arduino Nano, Nextion HMI.
  [Hackaday](https://hackaday.com/2020/12/09/this-automated-wire-prep-machine-cuts-and-strips-the-wire/) ·
  [GitHub](https://github.com/sandy9159/DIY-Wire-cutting-and-stripper-Machine-Arduino-project)
- **bstrip.** Open-source cut/strip machine: all 3D-printed structure,
  brushless motors on moteus controllers, an off-the-shelf V-blade cutter.
  18–30 AWG; tested mostly on 26 AWG. The blade depth must be tuned against
  conductor damage.
  [Hackaday.io](https://hackaday.io/project/176211-bstrip-wire-cutstrip)
- **"Automated Wire Cutter" for hardware startups.** A BOM under $300 with a $5
  hardware-store cutter. The author's stated plan: cut, then strip, then
  "crimping might be a secondary machine". No crimping stage was published.
  [Hackaday.io](https://hackaday.io/project/9364-automated-wire-cutter)

### Small-shop commercial

- **Schleuniger RotaryStrip 2400.** Rotary stripper, 36–10 AWG. The **wire tip
  touching a trigger sensor starts the cycle**. Incision diameter is
  programmable in 0.01 mm steps, strip length 0.1–34 mm. It pulls the slug
  partly or fully, with **controlled twisting of the strands** (26–13 AWG). No
  mechanical change between wire sizes. 1 s cycle. Rated for PVC, PUR,
  rubber, PTFE, Kapton.
  [mfr datasheet](https://www.schleuniger.com/fileadmin/schleuniger.com/products/strip/wire-stripping/rotarystrip-2400/datasheets/RotaryStrip_2400_DS_EN_A4.pdf)
- **Schleuniger UniStrip 2015** (pneumatic, discrete wires and small cables to
  3.2 mm) and **EcoStrip 9380** (entry cut-and-strip, 36–8 AWG). Both trade
  used on eBay and CAE.
  [mfr](https://www.schleuniger.com/en-us/products/strip/wire-stripping/unistrip-2015/) ·
  [mfr](https://www.schleuniger.com/en-us/products/cut-strip/ecostrip-9380/) ·
  [used market](https://caeonline.com/buy/machine-tools/schleuniger)
- **Chinese sensor-triggered bench strippers** (for example WIREPRO SP-2015E:
  AWG 32–11, 20 mm maximum strip). vevor.com lists electric strippers from
  $128.99 and "computer" cut-strip machines from $1,099; most of those target
  larger cable.
  [WIREPRO](https://www.wireproauto.com/product/high-accuracy-electrical-wire-stripper-machine/) ·
  [VEVOR search](https://www.vevor.com/s/benchtop-automatic-wire-stripping-machine)
- **Thermal strippers.**
  - Hakko FT-802: tweezer-style heated blades; strips AWG 38 without nicks.
    [mfr](https://www.hakko.com/english/products/hakko_ft802.html)
  - Eraser BTS1: bench unit, elements up to 1400 °F, adjustable strip-length
    stop, built-in fume extraction.
    [mfr](https://www.eraser.com/products/wire-cable-strippers/thermal-wire-strippers/bts1-thermal-wire-stripper/)
  - Used Teledyne Stripall units are cheap on eBay.
    [Hackaday](https://hackaday.com/2016/08/09/hot-wire-strippers-are-probably-the-best-tool-you-arent-using/)
  - **Silicone caveat.** Silicone is a thermoset and does not melt; it degrades
    above about 300 °C.
    [source](https://rysilicone.com/silicone-melting-temperature/)
    A claim repeated in search summaries says a hot blade turns silicone to an
    insulating ash layer and works only on walls of 0.7 mm or less. I could
    not find its original source, so it is **unverified**.
- **Laser stripping.**
  - **CO₂ (10.6 µm) is selective.** Every polymer absorbs it and metals reflect
    it, so the process is self-limiting at the conductor. The usual method
    burns a 360° ring and then pulls the slug. Flatbed, rotary-optic and
    galvo-scanner versions exist.
    [source](https://wiringharnessnews.com/basics-of-laser-wire-stripping/) ·
    [source](https://www.assemblymag.com/articles/92934-lasers-remove-polymer-wire-insulation-quickly-precisely)
  - Silicone under CO₂ leaves **silica ash** that air assist has to clear.
    [source](https://laseracc.com/can-a-co2-laser-cut-silicone.html)
  - The bench's XLaserlab fiber laser is near-infrared, the band that "cuts
    within metals" rather than stopping at them.
    [source](https://wiringharnessnews.com/basics-of-laser-wire-stripping/)
    **[assumption]** It would not strip selectively.

### Industrial mechanisms worth borrowing

- **Three stripping geometries.**
  - **V-blade (die) stripping:** two V-notched blades close to a set diameter,
    then the clamp pulls the slug. Most cut-strip machines work this way, and
    bstrip uses it.
  - **Rotary stripping:** the blades rotate around the wire, carried by a
    rotating cage, to cut a ring before the pull.
    [source](https://patents.google.com/patent/EP1867022B1)
  - **Orbiting ("planetary") blades:** the blades orbit the wire axis, driven
    by a rod on an inclined axis. Used on coax.
    [source](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/6588302)

  Rotary and orbiting cuts load soft insulation around the circumference
  rather than squeezing it from two sides. **[assumption]** That may matter
  for silicone that tears.
- **Blade-to-conductor contact detection** (Schleuniger/Komax SmartDetect, ACD).
  The stripping blades are electrically isolated. When a blade touches copper,
  an AC signal coupled through the wire changes, so every nick is flagged.
  Separate zones are monitored during incision and during pull-off.
  [source](https://wiringharnessnews.com/article/defect-free-wire-cutting-and-stripping/) ·
  [GE patent US 3,645,156](https://www.freepatentsonline.com/3645156.html)
- **Trigger-by-touch.** Stripping starts when the wire tip reaches a sensor
  (RotaryStrip). The tip position is the reference.

### Hand tools with mechanisms worth borrowing

- **Self-adjusting stripper (Klein 11061/11063 family).** One squeeze makes
  gripping jaws clamp ahead of the cutter; the jaws then **move away from the
  cutters while a cam progressively closes them**, which cuts and pulls in one
  stroke. An adjustable stop sets strip length.
  [mfr](https://www.kleintools.com/catalog/combination-cutting-tools/wire-stripper-and-cutter-self-adjusting) ·
  [mechanism patent US 3,942,397](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/3942397)

---

## 3. Feed and place the contact

### How the industry locates a chain contact (industrial mechanism)

The applicator is the prior art for "place the metal bit on the end of the
cable". Its parts:

- **Carrier strip and reel.** Chain terminals such as **SXH** come joined on a
  carrier strip, 8000 to a reel. Loose-piece **BXH** is the same contact cut
  free.
  [DigiKey](https://www.digikey.com/en/products/detail/jst-sales-america-inc/SXH-001T-P0-6/527371) ·
  [JST catalog](https://www.jst-mfg.com/product/pdf/eng/eCRIMPING_MACHINES_AND_TOOLS.pdf) [mfr]
- **Side feed vs end feed.**
  - **Side-feed** strip: the contacts stand crosswise on the carrier and the
    feed pawl **engages a hole in the carrier strip**.
  - **End-feed** strip: the contacts run nose to tail and the pawl **pushes on
    the terminal's own wings**.

  JST's applicator for the side-feed XH chain on the AP-K2N press is
  **MKS-L**; MK-L is its end-feed sibling.
  [WERI manual, §5.2](https://www.we-online.com/components/products/datasheet/600662403.pdf) [mfr] ·
  [JST catalog](https://www.jst-mfg.com/product/pdf/eng/eCRIMPING_MACHINES_AND_TOOLS.pdf) [mfr]
- **The feed cycle.**
  - A **feed pawl (finger)** advances one pitch per stroke.
  - A **stock drag** (spring brake) holds the strip so it cannot slide back.
  - **Strip guides** constrain it sideways.
  - A **hold-down** on the ram pins the terminal to the anvil during the crimp
    and cut-off.
  - A **floating shear**, pushed down by a shear depressor on the ram, cuts the
    terminal from the carrier.
  [TE 408-32162](https://www.te.com/commerce/DocumentDelivery/DDEController?Action=showdoc&DocId=Specification+Or+Standard%7F408-32162%7FB%7Fpdf%7FEnglish%7FENG_SS_408-32162_B.pdf%7F2217002-2) [mfr]
- **Pre-feed vs post-feed.** In a **pre-feed** applicator, "the lead terminal is
  over the anvil when the machine is at rest": the next contact already waits
  in the die for a wire. A post-feed cam advances it on the upstroke instead.
  On the WERI mini-applicator the change is a cam position.
  [TE 408-32162](https://www.te.com/commerce/DocumentDelivery/DDEController?Action=showdoc&DocId=Specification+Or+Standard%7F408-32162%7FB%7Fpdf%7FEnglish%7FENG_SS_408-32162_B.pdf%7F2217002-2) ·
  [WERI manual §7](https://www.we-online.com/components/products/datasheet/600662403.pdf) [mfr]
- **What sets position.**
  - A **pitch screw** on the pawl sets feed length.
  - A **crimping-axis screw** aligns the terminal to the punches.
  - A **terminal slide and wedge** set bellmouth and cut-off tab.
  - The operator's **wire stop** plus the strip length set where the
    insulation lands.

  Mecal's troubleshooting notes add three rules:
  - the pawl "should never come out of the hole in the carrier strip" on its
    return;
  - it must push from the hole's centre;
  - the terminal should float only 0.003–0.005 in. as it approaches the anvil.

  [WERI §6](https://www.we-online.com/components/products/datasheet/600662403.pdf) ·
  [Mecal](https://www.mecalbystarn.com/2019/04/23/primer-in-diagnosing-crimp-applicator-issues/) ·
  [Molex Quality Crimp Handbook](https://media.digikey.com/pdf/data%20sheets/molex%20pdfs/quality%20crimp%20handbook.pdf) [mfr]
- **Mechanical vs pneumatic feed.** The mini-applicator feed is a cam driven by
  the ram stroke, with no separate actuator. Some applicators use an air
  cylinder to feed; TE's G II through-splice and Chinese "pneumatic side-feed"
  applicators are examples.
  [WERI §4](https://www.we-online.com/components/products/datasheet/600662403.pdf) ·
  [Kingsing](https://www.kingsing.com/product/428.html)
- **Mini-applicator interface standard.**
  - **135.8 mm shut height** at bottom dead centre.
  - **T-shank coupling** to the ram.
  - Clamped base plate.
  - **30 or 40 mm stroke.**

  A WERI mini-applicator weighs 4.0 kg and measures 155 × 150 × 110 mm
  (side feed). Any press built to this interface drives any such applicator.
  [WERI](https://www.we-online.com/components/products/datasheet/600662403.pdf) ·
  [Molex Mini-Mac](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/applicationtoolingspecificationpdf/607/60713/ATS-011182170-001.pdf) [mfr]
- **Würth WR-WTB 2.50 mm mini-applicator 600 646 401**, for Würth 646 x01 137 22
  contacts (AWG 28–22), sold through Würth's distribution. **Whether WR-WTB
  2.50 mm intermates with JST XH is not confirmed here.**
  [WERI manual](https://www.we-online.com/components/products/datasheet/600662403.pdf) ·
  [contact](https://www.we-online.com/en/components/products/WTB_2_50_FEMALE_CRIMP_CONTACT_646X0113722) [mfr]

### Loose-piece feeding (small-shop and industrial)

- **Vibratory bowl loose-terminal crimpers.** A bowl orients and feeds loose
  terminals to a single-terminal die; operators reach about 3000–4000
  pieces/h, the same as chain. Quote only.
  [Yuanhan](https://www.yuanhanequip.com/product/crimping-machine-with-feeding-bowl-zdp.html) ·
  [JCW-CST02](https://www.jcw-wirestripping.com/jcw-cst02-vib-automatic-vibrate-bowl-feeding-loose-piece-terminal-crimp-machine.html)
- **Tri-Star automatic contact crimpers (aerospace machined contacts).**
  - **TAC X:** vibratory bowl, **wire-triggered**; a wire funnel prevents
    bird-caging; up to 1800 crimps/h.
  - **CR-36 handheld:** preloaded cartridge of 36 contacts.
  - **CrimpXpress:** **loads loose contacts into an ordinary hand crimp tool
    in under 2 s**.

  [mfr](https://tri-star-technologies.com/product-category/automated-crimpers/) ·
  [CrimpXpress](https://tri-star-technologies.com/product/crimpxpress-5/)
- **Boeing US 5,702,030, rotating-arm contact feeder.** A scoop on an arm
  turning at **about 4 rpm** lifts contacts from a bowl onto an inclined chute
  between orienting rails. An air-driven shuttle gate releases one contact at
  a time into a drop tube to the crimp tool. A slow singulator.
  [source](https://patents.google.com/patent/US5702030A/en)

### Maker / open source

- **OpenPnP strip handling.**
  - **ReferenceStripFeeder:** a cut piece of tape is stuck to the bed, and
    vision finds the **sprocket holes** to locate each part.
  - **Drag feeder:** the head drags the tape forward.
  - **BlindsFeeder:** a printed cut-tape holder whose cover the nozzle opens.

  Carrier-strip holes play the same role as tape sprocket holes.
  [OpenPnP wiki](https://github.com/openpnp/openpnp/wiki/ReferenceStripFeeder) ·
  [feeders](https://github.com/openpnp/openpnp/wiki/Setup-and-Calibration_Feeders)
- **Opulo LumenPnP.** Open-source gantry pick-and-place with top and bottom
  cameras; **a vacuum sensor on each nozzle confirms a pick**. **$1,995.**
  [mfr](https://www.opulo.io/products/lumenpnp) ·
  [GitHub](https://github.com/opulo-inc/lumenpnp)
- **3D-printed vibratory bowl feeder** (Andrzej Laczewski). ABS link arms act
  as springs, and a hand-wound electromagnet driven by a sine wave twists the
  bowl so tiny SMD parts climb a spiral ramp. Printable variants are on Cults,
  Thingiverse and similar sites.
  [Hackaday](https://hackaday.com/2018/07/22/a-3d-printed-bowl-feeder-for-tiny-smd-parts/) ·
  [Cults MKII](https://cults3d.com/en/3d-model/tool/vibrating-bowl-feeder-mkii)

### Hand tools with mechanisms worth borrowing

- **JST WC-110** (for SXH-001T-P0.6; J.S.T. UK).
  - **Flap locator and wire stop.**
  - Three cavities (22, 24, 26/28 AWG).
  - A full-cycle ratchet that will not open until the dies bottom.

  Procedure: close lightly until the contact is held, check it sits centred
  in the profile, feed the wire to the stop, then crimp.
  [RS](https://int.rsdelivers.com/product/jst/wc-110/jst-wc-hand-ratcheting-crimp-tool-for-sxh/6880912) ·
  [manual](https://www.manualslib.com/manual/3011682/Jst-Wc-Series.html) ·
  [DigiKey](https://www.digikey.com/en/products/detail/jst-sales-america-inc/WC-110/527372)
  JST's catalog also lists the **YRS-110** and **YC-110R/YC-111R** hand tools
  for SXH-001T-P0.6. JST calls its hand tools prototype and repair tools with
  fixed dies and no crimp-height adjustment.
  [JST catalog](https://www.jst-mfg.com/product/pdf/eng/eCRIMPING_MACHINES_AND_TOOLS.pdf) [mfr]
- **Molex 63819-series tools.** Pivot the locator open and lift the wire-stop
  blade. Seat the terminal until it stops. Push the stripped wire through to
  the stop, then crimp.
  [mfr](https://www.manualslib.com/manual/2335533/Molex-63819-3800.html?page=3)
- **Weidmüller Stripax Plus 2.5.** Ferrules sit in a **magazine in the handle
  and are transported automatically to the crimp die**. Cut, strip and crimp
  happen in one squeeze without regripping. A hand tool that feeds its own
  consumable.
  [mfr](https://www.weidmuller.com/en/company/press/trade_press_news/stripax_plus_2_5_launch.jsp) ·
  [flyer](https://assets.dam.weidmueller.com/assets/api/e09397f7-e647-4460-84e6-9a35ffacef0f/Original/Fl_Stripax_Plus.pdf)

---

## 4. Crimp

### Small-shop commercial

- **JST AP-K2N** (the semi-automatic press for SXH chain with MKS-L
  applicator). 14.7 kN (1.5 t), about 90 kg, 100 VAC. **$12,500** at TLC
  Electronics with a **116-day** manufacturer lead time. The sister AP-K5B has
  a 400 W motor at 1:11 reduction, 30 mm stroke and 0.44 s cycle.
  [TLC](https://tlcelectronics.com/tlc-4910.html) ·
  [JST catalog](https://www.jst-mfg.com/product/pdf/eng/eCRIMPING_MACHINES_AND_TOOLS.pdf) [mfr] ·
  [applicator DS SXH001-06/MKS-L](https://www.jst.co.uk/productSeries.php?pid=11327)
- **ETCO Mighty-T** bench press.
  - Cast-iron frame, 40 mm stroke, 4,450 lbf.
  - Footswitch, reel arm.
  - Takes standard mini-applicators.
  - **$2,950**; ETCO's "Mighty-Mini" applicator from **$1,850** plus tooling.

  [source](https://www.etco.com/wire-crimping-press-complete-with-terminal-applicator/)
- **Chinese 1.5–2 t "mute" presses.** Vendors describe a frequency-conversion
  motor drive with "electronic precision positioning", quieter than
  traditional presses. They take OTP-style horizontal (side-feed) or vertical
  (end-feed) molds, or a single-terminal mold.
  - WIREPRO TU-N02: 2 t, 30 mm stroke, 750 W, 55 kg; page shows "$201", which
    I take as a placeholder **[assumption]**.
  - Zonesun lists a semi-automatic terminal crimping machine at **$2,079** and
    an industrial one at **$950**.
  - An eBay OTP applicator for XH appeared in search results at about
    **US$155 plus about $91 shipping**.
  [Sanao](https://www.sanaoequipment.com/1-5t-2t-mute-terminal-crimping-machine-product/) ·
  [WIREPRO](https://www.wireproauto.com/product/tu-n02-1-5t-2t-3t-semi-automatic-terminal-crimping-machine/) ·
  [Zonesun](https://www.zonesun.com/collections/terminal-crimping-machines) ·
  [eBay applicator](https://www.ebay.de/itm/405412063260)
- **Komax benchtop.**
  - UniCrimp 208: 33 kN, rear- and side-feed banded terminals.
  - **StripCrimp 208:** strips 0.5–15 mm and crimps 30–10 AWG in one machine,
    with crimp force monitoring (CFM).
  - Delta 220/240/260: programmable, CFM, automatic crimp height on the
    240/260, stripping unit.
  - Uni-M mini-applicators.

  [mfr](https://www.komaxgroup.com/en-us/products/wire-processing/semi-automation-machines/wire-crimping)
- **TE 91085-2 manual arbor frame.** A bench frame driven by a hand lever, or
  pneumatically by foot switch, that accepts TE hand-tool die assemblies.
  Hand-tool dies in a press frame. Newark, DigiKey, and used on eBay.
  [Newark](https://www.newark.com/amp-te-connectivity/91085-2/manual-arbor-frame-assembly/dp/95F1374)

### Motorised and pneumatic "hand-tool" crimpers (small-shop)

- **Rennsteig eForce.** 12 V electromechanical (no hydraulics) crimper that
  accepts every Rennsteig PEW12 **interchangeable die set and locator**; Rennsteig
  offers 400+ die sets and customs. It has a start button and a quick-stop
  against over-crimping. Quote.
  [mfr](https://www.rennsteig.us/index.php/products/crimping-tools/73-rennsteig-system-tools/1467-eforce-battery-powered-crimping-tool) ·
  [system tool](https://www.rennsteig.us/products/crimping-tools/rennsteig-system-tools/1466-crimp-system-tools-hand-crimp-tool)
- **Phoenix Contact CF 500.** Compact electric bench crimper with quick-change
  dies, for lugs, sleeves and ferrules. Phoenix sells the CF 3000 as an
  "automatic stripping and crimping device".
  [mfr](https://www.phoenixcontact.com/en-us/products/crimping-machine-cf-500-230v-1208348) ·
  [mfr](https://www.phoenixcontact.com/en-us/products/crimping-machine-cf-3000-25-1205477)
- **Pneumatic crimpers with die sets.**
  - VEVOR AM-10: 1.3 t, 10 die sets, **$209.90** on vevor.com; for insulated
    terminals and ferrules.
  - DMC HX33: open-frame bench tool with a **foot pedal** that takes standard
    "Y" dies.
  [VEVOR](https://www.vevor.com/pneumatic-crimping-tool-c_10824/vevor-pneumatic-crimping-tool-am-10-air-powered-wire-terminal-crimping-machine-crimping-up-to-16mm2-pneumatic-crimper-plier-machine-with-10-sets-of-dies-for-many-kinds-of-terminals-p_010790984965) ·
  [DMC](https://dmctools.com/hx33)

### Industrial mechanisms worth borrowing

- **Two arrangements of crimp and wire.**
  - **Wire to a fixed press:** a person, a swivel arm or a robot brings the
    stripped end into a contact already waiting on the anvil. Examples: bench
    presses; Komax Alpha 550's servo swivel arm
    ([mfr](https://www.komaxgroup.com/en/products/crimp-to-crimp/alpha-550-g2));
    Kurabo's robot feeding a stock press (Start here).
  - **Crimp head to a fixed wire:** hand tools, battery crimpers, the Tri-Star
    CR-36 handheld, crimping on a harness board.

  The trade names for these vary; the two arrangements are what the sources
  show.
- **The crimp itself.** The punch rolls the open-barrel wings into the strands
  against the anvil. A separate insulation crimp gives strain relief. Molex's
  guidelines:
  - bellmouth 1–2× material thickness;
  - cut-off tab 1.0–1.5× thickness;
  - a visible conductor brush past the barrel;
  - the insulation edge centred in the transition;
  - **conductor crimp height** as the process variable, checked every 250–500
    parts.

  [Molex Quality Crimp Handbook](https://media.digikey.com/pdf/data%20sheets/molex%20pdfs/quality%20crimp%20handbook.pdf) [mfr]
- **Two-step crimp** (Engineer PA-09 and JST YC/YRS). The wire barrel and
  insulation barrel are crimped in **separate strokes**, each with its own
  force and die. PA-09 advice: set the barrel's rear edge 0.1–0.2 mm proud of
  the die edge to form a bellmouth.
  [source](https://www.experimental-engineering.co.uk/2017/10/09/quick-tool-review-engineer-pa-09-crimping-pliers/) ·
  [mfr](https://www.engineertools-jp.com/product-page/pa-09-connector-crimping-pliers) ·
  [JST catalog note (2)](https://www.jst-mfg.com/product/pdf/eng/eCRIMPING_MACHINES_AND_TOOLS.pdf)
- **Crimp force monitoring** is covered under §6 Inspect.

### Maker / open source

- **None found.** I searched Hackaday, Hackaday.io, GitHub, Instructables and
  Reddit for automated or motorised crimping of JST or Dupont contacts and
  found no published build. Maker prior art stops at cut and strip. Useful
  maker writing on the tools themselves:
  - "Crimping Tools And The Cost Of Being Cheap" and "Confessions Of A
    Crimpoholic" (Hackaday);
  - "Crimp my style", a teardown of the IWISS IWS-3220M, whose jaws are four
    pieces of EDM-cut steel.
  [Hackaday](https://hackaday.com/2022/02/07/crimping-tools-and-the-cost-of-being-cheap/) ·
  [Hackaday](https://hackaday.com/2022/04/04/confessions-of-a-crimpoholic/) ·
  [Hackaday.io](https://hackaday.io/project/176110/log/202683-crimp-my-style)

---

## 5. Insert the contact into the housing

### Industrial mechanisms worth borrowing

- **Grip near the contact, push, then pull back (Siemens US 5,315,756).** A
  **centering gripper** of nested inner and outer form-fitting parts encloses
  the contact precisely. A separate insertion gripper holds the wire. The
  module drives the contact into the cavity **to an adjustable limit stop**,
  then the wire gripper retracts with an **adjustable tensile force**. If the
  contact is not held, the assembly is rejected.
  [source](https://patents.google.com/patent/US5315756A/en)
- **Slide-along jaws that push from behind the crimp (Molex US 4,936,011).**
  Long jaws hold the wire lightly enough to **slide along it** toward the
  terminal. A proximity sensor detects arrival at the terminal's rear. The
  jaws then clamp hard, with their tips against the terminal's back, and push
  it home through a terminal guide. Optional probes push-test through the
  housing's front or pull-test.
  [source](https://patents.google.com/patent/US4936011A/en)
- **Guide arms plus press arm (Sumitomo US 5,109,602).** Spring-closed guide
  arms and a pivoting press arm hold the terminal straight while a wire chuck
  thrusts it into the cavity. The housing sits on an indexing rotary member.
  [source](https://patents.google.com/patent/US5109602A/en)
- **Vision, then force, then pull-back (Boeing US 11,374,374).**
  - Two cameras on the end effector see the contact tip and the target hole
    together, and a corrective transform aligns them.
  - The robot advances until it touches the connector face, then a set
    distance further.
  - **Low insertion force means the contact found the hole.**
  - Seating is confirmed when the **pull force reaches the test value before
    the gripper has moved the pull distance**.
  [source](https://patents.google.com/patent/US11374374B2/en)
- **Light-guided manual insertion (Yazaki US 5,590,457).** An optical fibre on
  an XY stage **lights the next cavity from under the housing**. The inserted
  terminal breaks the beam, which confirms it and moves the light to the next
  cavity. Pin order without a sample harness.
  [source](https://patents.google.com/patent/US5590457A/en)
- **Insertion tools.** JST lists insertion tools for some series and says they
  help "especially when thin wires are used"; **none is listed for XH**. The XH
  extraction tool listed in JST's catalog row for SXH is XJ-06.
  [JST catalog](https://www.jst-mfg.com/product/pdf/eng/eCRIMPING_MACHINES_AND_TOOLS.pdf) [mfr]

### Research

- **Vibration-assisted fitting of crimp contacts** (Warnecke, Frankenhauser,
  Gweon and Cho, *Robotica*, 1988). A robot with a vibrating tool fits
  irregular, flexible crimp contacts into connectors. The paper names "the
  flexibility of the wires and the irregularity of the contact shapes" as the
  obstacles.
  [source](https://www.cambridge.org/core/journals/robotica/article/abs/fitting-of-crimp-contacts-to-connectors-using-industrial-robots-supported-by-vibrating-tools/050FA563CC4DAD47446A042C6B9D63F9)
- **Sogang flat-ribbon terminal-to-housing** (see Start here). The "weaving"
  oscillation is a modern cousin of vibration-assisted insertion.
- **University of Bologna / Campania, Palli and Pirozzi group.**
  - De Gregorio et al., *IEEE T-ASE* 2019: wire-terminal insertion with vision
    plus custom tactile fingers.
  - REMODEL, 2023: sensorized fingers for wire-harness manipulation.
  - Caporali et al., *IEEE/ASME T-Mech* 2026: stereo cameras and sensorized
    parallel-jaw fingers for DLO manipulation and **pin insertion** in connector
    assembly.
  [2019](https://cris.unibo.it/retrieve/handle/11585/685703/e1dcb339-ea37-7715-e053-1705fe0a6cc9/PP%20Integration_of_Robotic_Vision_and.pdf) ·
  [2023](https://ieeexplore.ieee.org/document/10284109/) ·
  [2026, bibliographic record only](https://sciprofiles.com/profile/247056)
- **"Towards Automated Connector Assembly: Wire Insertion Combining Tactile and
  Vision Sensors"** (IEEE Xplore record; abstract not retrieved).
  [source](https://ieeexplore.ieee.org/document/11175819/)
- **Structured compliance instead of sensing.**
  - Hartisch and Haninger 2023: 3D-printed fin-ray fingers with a 14–36
    directional stiffness ratio give a remote centre of compliance and
    self-align connectors within a 7.5 mm tolerance window.
    [arXiv](https://arxiv.org/abs/2307.15589)
  - *Biomimetics* 2025: a compliant tactile finger with a rigid "fingernail"
    for connector insertion.
    [source](https://pmc.ncbi.nlm.nih.gov/articles/PMC12383613/)

---

## 6. Inspect and verify

### Industrial mechanisms worth borrowing

- **Crimp force monitoring (CFM).**
  - **Sensors:** a strain sensor on the press frame (cheapest), or a piezo ring
    in the ram or base plate (more sensitive for small wire).
  - **Teach-in:** it learns from 1–6 verified good crimps.
  - **Comparison:** each curve's area and shape against a band of about ±4%.
  - **Limit:** detection depends on "headroom", the force difference between
    crimping with and without wire. In a 7-strand wire one strand is about
    6.7% of the force, which is detectable. In a 19-strand wire it is about
    2.5%, which is not.

  [Assembly Magazine](https://www.assemblymag.com/articles/86473-crimp-force-monitoring)
  Retrofit monitors cover 0.14–6 mm² (AWG 26–10) and flag missing strands, the
  wrong gauge, a missing contact, poor stripping and the wrong depth
  ([Zoller + Fröhlich CK 01](https://www.zofre.de/en/wire-processing/measurement-devices/crimp-force-monitoring-ck-01)).
  **[assumption]** 22 AWG with about 60 strands puts one strand under 2% of
  the force, so CFM here would catch gross faults (no wire, insulation in the
  crimp, no contact) but not a single missing strand.
- **Crimp height measurement.**
  - Method: a point spindle in the bottom radius and a flat blade across the
    top, **centred, away from the bellmouth**.
  - Benchtop gauges: Schleuniger CHM, with a spring-loaded point for
    repeatable force; Komax 341, which stops production on a mismatch; Komax
    MicroHeight 10.
  [Molex micrometer](https://www.content.molex.com/dxdam/literature/987650-6593%20A4.pdf) ·
  [Schleuniger](https://www.schleuniger.com/en/products/quality-assurance/crimp-height-measurement/) ·
  [Komax 341](https://www.komaxgroup.com/en-us/products/quality-tools/komax-341)
- **Camera inspection of the wire end** (Komax Q1250). A digital camera under
  **dome lighting**, with colour recognition, checks for insulation in the
  crimp, the conductor brush length, and stray or crimped-in strands.
  [source](https://www.komaxgroup.com/en/products/testing-and-quality-tools/cable-and-harness-quality-tools/integrated-quality-monitoring)
- **Pull test.** UL 486A minimum pull-out for **22 AWG is 8 lbf (35.6 N)**,
  pulled at 25.4 mm/min with the insulation crimp loosened.
  [Molex Quality Crimp Handbook](https://media.digikey.com/pdf/data%20sheets/molex%20pdfs/quality%20crimp%20handbook.pdf) [mfr]
- **Four-wire milliohm test.** Resolves about 1 mΩ. It **cannot** see a tight
  crimp with insulation caught in it.
  [source](https://www.camiresearch.com/Campaigns/Web-Articles/4-wire-testing.html) ·
  [source](https://wiringharnessnews.com/electrically-checking-crimps/)
- **Ultrasonic crimp verification (NASA Langley).** Transducers built into
  the jaws of a crimp tool send ultrasound through the crimp as it closes.
  Transmission rises once wire and barrel are in intimate contact. It detects
  under-crimping, missing strands, incomplete insertion, insulation left on
  and the wrong gauge.
  [NTRS](https://ntrs.nasa.gov/api/citations/20100011289/downloads/20100011289.pdf)
- **Cross-section.** Pot the crimp in epoxy, cut, grind with 120–1200 grit SiC,
  polish, then image strand compaction and symmetry.
  [source](https://wiringharnessnews.com/developments-in-cross-section-analysis/) ·
  [source](https://www.cs-technologies.com/CrossSectioning_Epoxy.html)

### Research

- **Deep-learning optical inspection of crimps.** Nguyen, Meiners, Schmidt and
  Franke (FAU), EDPC 2020.
  [source](https://cris.fau.de/publications/255226992/)
  Also TCQI-YOLOv5, 98.3% mAP including shallow insulation crimps.
  [source](https://pmc.ncbi.nlm.nih.gov/articles/PMC12736603/)
  Roboflow and Overview.ai publish crimp-inspection walkthroughs.
  [Roboflow](https://roboflow.com/ai/terminal-crimp-inspection) ·
  [Overview.ai](https://www.overview.ai/resources/walkthroughs/crimp-barrel-visual-inspection/)
- **Systematic review of computer vision in robotized wire harness assembly**
  (2023).
  [arXiv](https://arxiv.org/pdf/2309.13744)

### Maker / open source

- **Arduino harness testers.** Learn a known-good cable, then check opens,
  shorts and miswires pin by pin. Examples: Arduwire (32 points, expandable to
  64) and Hackaday.io "Cable harness tester".
  [Hackaday.io](https://hackaday.io/project/28428-cable-harness-tester) ·
  [cable-tester.com](https://www.cable-tester.com/diy-cable-tester/)
- **DIY pull tester.** A load cell and HX711 on an Arduino. The HX711 samples
  at 10 Hz by default and 80 Hz after a pad change.
  [SparkFun](https://learn.sparkfun.com/tutorials/load-cell-amplifier-hx711-breakout-hookup-guide/all)

---

## 7. Robots and learning, across steps

- **SO-100 / SO-101 (LeRobot).** Open-source, 3D-printable 6-DOF arms on
  Feetech STS3215 serial servos. Servo kits cost **$220–240**, printed parts
  about $35 or self-printed. They are trained by teleoperated imitation
  learning. No published cable or contact insertion demo found.
  [CNX](https://www.cnx-software.com/2025/05/02/so-arm101-open-source-dual-robotic-arm-kit-works-with-hugging-faces-lerobot/) ·
  [docs](https://huggingface.co/docs/lerobot/so101) ·
  [GitHub](https://github.com/TheRobotStudio/SO-ARM100)
- **ALOHA** (Stanford and collaborators). Bimanual teleoperation for under
  $20k. It threads zip ties; ACT learned several fine tasks at 80–90% success
  from about 10 minutes of demonstrations.
  [project](https://tonyzhaozh.github.io/aloha/)
- **Behavioral cloning for connector assembly** (Kernbach et al., 2026). A
  UR5e with force-torque sensing and a fixed camera, trained on up to 300
  SpaceMouse demonstrations, mated five connector geometries at over 90%
  success.
  [arXiv](https://arxiv.org/pdf/2602.22100)
- **FFC insertion with tactile memory** (arXiv 2025). A 3D tactile sensing
  module plus Bayesian reliability estimation detects 0.5 mm misalignment with
  97.9% accuracy.
  [arXiv](https://arxiv.org/abs/2502.12514)
- **Deformable linear object (DLO) surveys.** Caporali et al., *IJRR* 2026;
  wire-harness-specific review, *RAS* 2026; general survey, arXiv 2023.
  [IJRR](https://journals.sagepub.com/doi/10.1177/02783649261432253) ·
  [RAS](https://www.sciencedirect.com/science/article/abs/pii/S0921889026000485) ·
  [arXiv](https://arxiv.org/html/2312.10419v1)
- **Earlier harness robots.**
  - Jiang et al. (Tohoku), IROS 2010: three PA10 arms fixing a harness to a
    car panel.
    [source](https://vigir.missouri.edu/~gdesouza/Research/Conference_CDs/IEEE_IROS_2010/data/papers/1057.pdf)
  - Navas-Reascos et al., 2022: cobot harness review, finding few cobot
    applications.
    [source](https://research.chalmers.se/publication/531070/file/531070_Fulltext.pdf)
  - Eureka Robotics: 3D camera plus force-controlled connector mating.
    [source](https://eurekarobotics.com/applications/force-controlled-connector-insertion)

---

## Adjacent routes that exist

- **Pre-crimped XH leads.** JST sells 22 AWG XH socket-to-socket jumper leads
  (ASXHSXH22K51 to K305, 2 to 12 in.) through DigiKey. They are discrete black
  wires, not ribbon.
  [DigiKey](https://www.digikey.com/en/products/detail/jst-sales-america-inc/ASXHSXH22K305/6684932)
- **Used industrial equipment.** Schleuniger, Komax, TE and ETCO machines
  trade used on eBay and CAE, which shortens lead time compared with new
  quotes.
  [CAE](https://caeonline.com/buy/machine-tools/schleuniger) ·
  [eBay Schleuniger](https://www.ebay.com/b/Schleuniger-Wire-Stripping-Machines/181855/bn_7116643171)

---

## What surprised me, and what transfers

What surprised me most is that the industry has already built the
one-conductor ribbon machine: the JCW-2TE clamps the ribbon once, steps it
sideways at conductor pitch, and a wire fork presents each conductor to a
pre-fed contact. The only terminal-to-housing machine made from printed parts
and hobby servos is also for flat ribbon at 2.5 mm pitch. That Sogang
prototype inserted reliably (98%) and failed mostly while moving the floppy
cable. Meanwhile no maker project automates the crimp itself; published maker
work stops at cut and strip.

Two facts reframe what matters. First, crimp force monitoring cannot see a
single missing strand in fine-stranded 22 AWG, so a slow machine's natural
checks carry more weight: crimp height, a camera under dome light, a pull-back
test and a milliohm test. Second, the mini-applicator standard (135.8 mm shut
height, T-shank, 30–40 mm stroke, cam-driven pawl) packages "place the contact
and crimp it" into a roughly 4 kg module that needs only a vertical ram
stroke. Its pre-feed cam leaves the next contact sitting in the die at rest,
waiting for a wire. Whether a slow actuator through leverage can supply the
needed force depends on the XH crimp force, which is in the facts pass.

These mechanisms seem most transferable to a very slow, one-conductor-at-a-time
machine:
- the carrier strip with pawl, drag and hold-down, located by the strip's own
  holes;
- clamp-and-index at ribbon pitch, with a fork for each conductor;
- a manipulator presenting the wire to a fixed press (Kurabo);
- crimp, then transfer to an adjacent insertion station (Molex 1978);
- slide-along jaws that push from behind the crimp;
- a seating check that passes when force arrives before distance;
- a light under the housing to show the next cavity;
- vibration or oscillation during insertion;
- electrically isolated stripping blades that report a nick;
- a slow rotating-scoop singulator for loose BXH contacts.
