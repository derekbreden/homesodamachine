# Clear PETG reservoir: flow 1.05 and 30% overlap

The current recipe uses **five requested Arachne wall loops**, **1.05 filament
flow**, **30% Infill/Wall overlap** and **265/270 °C** first/subsequent nozzle
temperatures through Mark1's right **0.8 mm Standard** nozzle. Mark1 task
**1365626370** identifies the intentionally partially printed left article.
Derek reports a **one-hour water hold** on October 23, 2026.
[Physical result](../../prints/2026-10-22-mark1-flow105-overlap30-right08-z000/physical-result/physical-result.json).
[Launch and startup](../../prints/2026-10-22-mark1-flow105-overlap30-right08-z000/README.md).
The result supports the current recipe for the tested portion; exact print
height, water head and cap/gasket assembly sealing are unspecified.

The broad floor and cap faces use **100% zig-zag fill**, with three bottom
shell layers and three top layers / 0.8 mm minimum top thickness. The modeled
floor remains 3 mm. No brim, zero added user Z trim and ironing Off are selected.
Stock Textured PEI compensation is `G29.1 Z-0.02`.

## Wall count

Both complete body/cap plates were sliced with counts **2, 3, 4 and 5** at the
selected flow, temperature, overlap and layer heights. Counts 2–4 retain infill
in the ordinary curved-corner walls. Count **5** has only inner/outer wall
features throughout both ordinary body-wall bands, **12 < Z < 175 mm**. This
band excludes the lower rod boss, floor and upper insert-boss transitions.
The straight 3 mm wall alone does not determine the count for the thicker
curved corners. Broad floor/cap areas and locally thicker bosses retain solid fill.
[Complete counts, feature samples and G-code hashes](wall-count-review.json).

Five is the lowest tested count that achieves the requested wall construction.
The native feature labels establish planned paths; they do not establish
physical fusion or water holding. [Native review of both complete plates](native-review.json)
confirms the right nozzle, zero added trim, no ironing, empty plate-warning
fields, 833 layers, at least 70.5 mm full-bead bed-edge inset and seven bed-rooted
support bodies per plate. Plate 1 estimates **5 h 42 min, 444.28 g**.

## Layer heights and defaults

| Setting | Verified value |
| --- | --- |
| Current ordinary / first layer | 0.24 / 0.30 mm |
| Installed H2C 0.8 Balanced Quality preset | 0.24 mm |
| Installed H2C 0.8 Balanced Quality and Strength presets | 0.32 mm |
| Installed H2C 0.8 Standard preset | 0.40 mm |
| First layer in those stock presets | 0.40 mm |
| Machine-profile custom layer range | 0.16–0.56 mm |
| Stock preset wall generator | Classic |
| Stock Infill/Wall overlap | 15% |
| Recovered May wall generator / transition threshold | Arachne / 10° |

[Installed files, inheritance and source hashes](installed-presets.json) bind
these values to Bambu Studio **02.08.02.61**. Custom machine limits are distinct
from supplied process presets. The recovered May recipe's 0.18 mm layer height
belonged to its 0.6 mm nozzle; the recent 0.8 mm reservoir prints use 0.24 mm.

**10° is the Arachne transition parameter's default** in [Bambu's source](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/PrintConfig.cpp#L6395).
The recovered May project selects Arachne; the installed stock H2C 0.8 process
profiles inherit Classic. The current recipe retains May's Arachne selection
with its default threshold. [Exact recipe changes and Derek's request](adaptation.json).
