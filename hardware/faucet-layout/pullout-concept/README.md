# Pull-out Sculpted faucet concept

The curved front of the Sculpted faucet pulls out with its display and dispense
face. Its keyed magnetic seat stands at the crown. Docked, the base lever commands
dispensing; undocked, the display offers flavor selection and hold-to-pour control.
A presence sensor in the seat selects the mode. The fluids stay connected while
the head moves, and their outlets remain separate at the dispense face.

The study imports the current faucet's lower shell, lever, tip and display. A
fuller neck and grip surround a smooth sliding-bundle passage. An electronic
dispense arrangement and a hollow mount serve the moving bundle;
the lever stands in its familiar position as an electrical input. The soda path
requires a dispensing shutoff in the removable head, close to the outlet, so the
moving hose remains pressurized between pours. The published geometry leaves that
valve unplaced and does not establish the head's required size or internal layout.

[Derek's observation of the working fixed faucet](physical-context.json) records
a quick stop of the main flow followed by fast and then slow outlet dripping
after releasing the lever. The pull-out design must control the much longer
downstream water volume. Closing only the enclosure end leaves the hose open to
the nozzle; pressure falls and dissolved carbon dioxide can leave solution,
driving afterflow and reducing carbonation in retained water. The
[gas-solubility reference](https://openstax.org/books/chemistry-2e/pages/11-3-solubility)
explains the pressure dependence; the expected hose behavior is a design inference,
not a measured pull-out result.

Below the counter, the bundle hangs freely with a return weight and connects to
the enclosure. Its low return bend forms the hanging loop. Pulling out the head
raises the loop and return weight. The enclosure connection supplies the fixed
anchor; the bracket in the illustration is not required for that arrangement.
The study keeps the loop's path length in balance with the exposed hose. The
weight, dock retention and travel are study parameters, not qualified hardware.

## Recommended hose construction

Make the bundle from separately stocked tubing, a flexible signal cable and a
continuous black protective sleeve. Keep the drink paths separate through the
head. Use flexible beverage tubing through the moving section, with stationary
transitions below the counter. The braid protects and gathers the lines; it is
not a pressure boundary. The drain and display conductors share the bundle.

- Soda: Accuflex Bev-Flex reinforced beverage hose, [sold by the foot at Parts
  Town](https://www.partstown.com/p/lancer/lan172-04102-77), or the blue-trace
  [stock coil at Installation Parts Supply](https://installationpartssupply.com/172-04122-77.html).
  [Accuflex's specification](https://www.accuflex.eu/wp-content/uploads/Bev-Flex-172-series.pdf)
  owns its dimensions, working pressure and bend radius.
- Flavor: [Tygon beverage tubing at U.S.
  Plastic](https://www.usplastic.com/catalog/item.aspx?catid=864&itemid=74410).
  The soft tube is for the pumped flavor path. Its diameter is close to the current
  flavor bore, and its pressure limit belongs to this line's design.
- Outer sleeve: [Techflex Flexo PET, black, by the foot at
  PacRad](https://www.pacrad.com/techflex-expandable-sleeving-pet3-4black.html).

Each linked shop listed the selected item in stock when this study was prepared.
The pages show actual product photos. The recommendation identifies prototype
stock; it makes no production-life or assembled-bundle qualification claim.
Insulation, the flexible cable and outlet shutoffs still need selection. The
drawn bundle is an envelope: its finished diameter and cold bending resistance
need a physical sample before committing to the neck or grip.

## Views

The published models use the normal Parts viewer:

- [Docked](https://homesodamachine.com/parts#step:faucet-layout%2Fpullout-concept%2Fdocked-above-counter.step)
- [Pulled out](https://homesodamachine.com/parts#step:faucet-layout%2Fpullout-concept%2Fpulled-out-above-counter.step)
- [Under the counter](https://homesodamachine.com/parts#step:faucet-layout%2Fpullout-concept%2Fpulled-out.step)
- [Handheld head](https://homesodamachine.com/parts#step:faucet-layout%2Fpullout-concept%2Fhandheld-detail.step)

![Docked](docked.png)

![Pulled out](pulled-out.png)

![Moving hose loop](under-counter.png)

![Handheld head and display](handheld-detail.png)

## Generate

`concept.rs` creates this visualization without changing the production faucet.
It is an explicit sandbox example outside the normal print build.

`render.json` fixes the comparison cameras and lights the display graphics. Its
under-counter picture makes the countertop translucent to expose the weight and
fixed anchor.

Run from the repository root:

```sh
tools/run -- cargo run --release --locked -j2 --manifest-path tools/hsm/Cargo.toml \
  -p hsm-sandbox --example faucet-pullout-concept -- hardware/faucet-layout/pullout-concept
tools/run -- hsm render --jobs hardware/faucet-layout/pullout-concept/render.json
hsm-publish --root .
```

This is an appearance and motion study. It is not a printable assembly, a
verified valve design or implemented faucet firmware.
