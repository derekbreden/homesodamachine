# Lillium faucet and short-outlet pours · 25 November 2026

The white countertop faucet delivered about **44 mL/s (2.62 L/min, 0.69 US gal/min)** across three pours. At that rate a 12 US fl oz glass of water fills in **8.1 s**, and a 16 US fl oz glass in **10.8 s**. A fourth pour from the short outlet at the Lillium was faster. All four used the same OXO two-cup measure.

## What reached the cup

| Path and clip | Derek's settled reading | Water equivalent | Phone stop | Flow interval in clip | Pour time | L/min | Seconds per 12 US fl oz |
|---|---:|---:|---:|---:|---:|---:|---:|
| White faucet · C031 | 1⅔ cups | 394 mL | 11.06 s | 22.92–31.93 s | 9.0 s | 2.63 | 8.1 |
| White faucet · C033, first | 1¾ cups | 414 mL | 11.29 s | 18.55–28.26 s | 9.7 s | 2.56 | 8.3 |
| White faucet · C033, second | 1⅞ cups | 444 mL | 11.21 s | 70.07–80.01 s | 9.9 s | 2.68 | 8.0 |
| Short outlet · C034 | about 2 cups | about 473 mL | — | 8.54–16.95 s | about 8.4 s | about 3.4 | about 6.3 |

The cup's two-cup mark is 16 US fl oz. The volume conversions use 236.588 mL per US cup. The faucet times run from the first visible jet through the end of the main stream, as it narrows to drips. The phone includes reaching for the lever and returning to stop the clock. The three cups total about 1,252 mL over 28.66 s of flow, or **1.48 US fl oz/s**. Using the 33.56 s on the phone would give 2.24 L/min.

For the short outlet, the jet appears at 8.54 s. Its sound falls sharply around 16.95 s while the hand turns the valve in foam. The outlet is visibly clear by 18.18 s. Counting that entire tail gives 9.64 s, **2.94 L/min** and **7.2 s per 12 US fl oz**. The two end cues put the short outlet about **12–29% higher in flow** than the faucet, saving **0.9–1.8 s per glass**. This was a single draw about 17 minutes after the last faucet pour, with a different outlet valve and height.

The camera looks down into a handheld cup. Tilt, perspective and foam limit the settled readings. The frame times locate the events more precisely than the graduations locate the volumes. For scale, moving a reading by ⅛ cup moves it by 30 mL, or about 0.18 L/min on a ten-second pour. The spread between faucet trials is smaller than that example. [Settled levels in all four pours](cup-levels.jpg)

## What was plumbed

Derek traces the long path from a tee at the Lillium through countertop tubing and an inline meter to the white faucet. The short pour uses a blue-handled valve near the source. The two routes give an end-to-end comparison. Assigning a pressure drop to the meter, the tubing or the faucet requires a flowing-pressure reading or a test that changes one component at a time. [Plumbing, meter label and short outlet](plumbing.jpg)

The Lillium display reads **E4** during C032, between the first and second faucet pours. Lilium describes E4 as a protection warning that can appear when inlet flow or refill cannot keep up. The cause and the source state during each timed pour are unknown. Drink temperature, flowing pressure and dissolved CO₂ were unmeasured. For context, the maker suggests about 35 mL/s (2.1 L/min) as a starting point for sparkling water on its system. Both filmed outlets exceeded that rate. [Lilium's E4 guidance](https://liliumfaucet.com/blogs/news/what-should-i-do-if-my-liliumfaucet-sparkling-water-dispenser-shows-an-e4-error-causes-and-solutions) · [Lilium's sparkling flow guidance](https://liliumfaucet.com/blogs/news/how-to-set-up-an-under-sink-sparkling-water-dispenser-co%E2%82%82-pressure-water-flow-troubleshooting)

## What this changes for the model and the pour

- **Glass time.** At revision `935547eae2`, the default `repo-tools model` forecast for its specified Lillium-fed plumbing was 3.2 L/min (middle 80% of draws, 2.9–3.7) and 6.6 s per 12 US fl oz (5.8–7.3). The filmed faucet took about 1.5 s longer per glass than that median. Its tubing lengths, source pressure and valve opening are unmeasured. Use 8.1 s for this faucet. The integrated machine with its own carbonator still needs a timed, weighed pour. [Model and assumed route](../../../../future/model.md#4-seconds-to-fill-a-12-oz-glass) · [Calculation at the time of the trial](https://github.com/derekbreden/homesodamachine/blob/935547eae2a667d4781696478b8e62bb5838084d/tools/hsm/repo-tools/src/model.rs)
- **Meter calibration.** The C032 nameplate reads **FL-S402B**, **0.3–10 L/min**, **F = 23 × Q**. With frequency in Hz and flow in L/min, that is **1,380 pulses/L** or **0.725 mL/pulse**. The model assumes 35–39 Hz per L/min for its specified meter, and DIGITEN's product page for a 0.3–10 L/min meter gives 36. At the pooled faucet rate, the filmed label predicts **60 Hz, or 3.0 pulses per 50 ms**. Using 38 predicts **100 Hz, or 5.0 pulses** for the same water. Six pulses per window would take 5.22 L/min with the filmed label. The clips contain no electrical pulse count. [Filmed nameplate](plumbing.jpg) · [DIGITEN's published specification](https://www.digiten.shop/products/digiten-1-4-quick-connect-0-3-10l-min-water-hall-effect-flow-sensor-meter) · [Model inputs](../../../../tools/hsm/repo-tools/src/model.rs)
- **Concentrate demand.** At 1 part concentrate to 20 parts water, this faucet needs about **131 mL/min of concentrate** while water flows. The 250 mL water test takes about **5.7 s** and calls for **12.5 mL** of concentrate. A **finished** 12 US fl oz drink calls for **338 mL water and 16.9 mL concentrate**. At the 1:20 setting a steady three-count input commands **110 ms on / 480 ms off** (19% duty). Five counts command **170 / 360 ms** (32%), and six command **200 / 300 ms** (40%). The open-hose tests measured each head's response to those commands. Determining the installed mix takes the actual water count and concentrate delivered through the faucet path. [Pour policy](../../../../firmware/lib/machine_policy/pour_policy.cpp) · [Open-hose dosing evidence](https://github.com/derekbreden/homesodamachine/tree/cffe141025fa0fd353335083c6159bead7591ace/hardware/reference/kamoer-flow/2026-11-22-unseen-pours)

The earlier pump experiment used **2,280 pulses/L** to assign water volumes to simulated meter signals. For example, its three-count, 2.7 s program represents 162 pulses. At the registered factor that is **71 mL** of water. At the filmed label factor it would represent **117 mL**. The photographed concentrate amounts still measure what each head delivered for that command. The water quantities and ratios inferred from those amounts depend on the meter fitted to the faucet. [Pump experiment's registered water factor and program](https://github.com/derekbreden/homesodamachine/blob/bc26987f18f42e863b6e2af7df3dad5da07d3eb7/hardware/reference/kamoer-flow/2026-11-22-pour-predictions/preregistration.json)

## Next measurement

The first calibration needs one weighed water-only catch through the pictured meter, with the Lillium display and actual flow time recorded. The appliance console's `status` reports total flow pulses since boot. Subtract its before reading from its after reading and divide by collected litres to get pulses/L. A catch of about 250 g of water should give roughly **345 pulses** at the label factor, **540** at 36 or **570** at 38. This one observation distinguishes the factors. Pair a subsequent water catch with a separate concentrate catch on each channel to check the installed ratio. A repeat of the outlet comparison at a common source state and height would narrow the hydraulic result. [Console counter](../../../../firmware/src_appliance/main.cpp) · [Installed ratio test](../../../../future/model.md#test-1-the-ratio)

Two other uses of the factor deserve separate checks. The model accepts `--set meter_hz_per_lpm=23` for its pulse and dose predictions, but its `SHAPE_FLOW` and `SHAPE_PUMP` summary fields still use the default range. The dry-gas sweep also uses 2,280 pulses/L. Applying a liquid label or a water calibration to gas would require a gas measurement. [Model calculation](../../../../tools/hsm/repo-tools/src/model.rs) · [Dry-gas sweep](../../../../firmware/lib/machine_policy/sweep_policy.h)

## Source recordings

Times are seconds from the start of each original Canon movie, at 30,000/1,001 frames/s. The selected zero-based frame pairs are C031 687–957, C033 556–847 and 2100–2398, and C034 256–508 (545 for the later endpoint). The hash identifies the original even if it moves off the Desktop.

| Original movie | Evidence | SHA-256 |
|---|---|---|
| `A_0001C031A261125_211344C6_CANON.MP4` | First faucet pour and settled level | `f0386c7df99c706604f6194c2ab5b8fba1308736907aa23c7947c043ffa2045d` |
| `A_0001C032A261125_2115453J_CANON.MP4` | Plumbing tour, meter face at 13.31 s, display at 36.50 s | `5ec83e62f974d343e678d33116222e6a4075410d970eb31ff0fe53a60e634b6e` |
| `A_0001C033A261125_2117210N_CANON.MP4` | Second and third faucet pours and settled levels | `0396d95a1eaf54834904431d5f37544ed37d6d4a51f4d205b1d2e719d6e58d91` |
| `A_0001C034A261125_2135133R_CANON.MP4` | Short-outlet pour, valve closure and settled level | `16fc988639e598e2f57f8b53dfadcad7423eab00985151d0e9dfbf81136728f9` |
