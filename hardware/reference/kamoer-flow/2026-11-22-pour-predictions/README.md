# Predicting concentrate delivery during a pour

This record tests whether the Home Soda Machine can start from a photographed cup level and predict where the concentrate will finish when someone opens, varies or releases the lever. Each trial retains its starting photograph, forecast, controller receipt and settled result. The figures show individual servings and misses.

| Question | Observations |
| --- | --- |
| After calibrating a particular lever program, how closely does the same head repeat it? | [Predictions and measured servings](results/repeat/recipe-predictions.png) · [Starting levels, predicted finishes and actual finishes](results/repeat/attempts.csv) · [Coverage and bias](results/repeat/scores.json) |
| Can motor pulse widths alone predict a new lever movement? | [Reserved programs](results/fresh/pour-predictions.png) · [Results by program and pump](results/fresh/by-scenario.csv) |
| What changes when the lever briefly closes and reopens? | [Surface movement recorded through the interruption](camera/release-reopen.png) · [Original dose test](results/original/scores.json) · [Same pairs reread on clear glass](results/original/release-clear-glass.json) |
| Does starting higher in the cup affect the same dose? | [Paired high-minus-low differences](results/fill/fill-level-effect.png) · [Starting and ending volumes on each sightline](results/fill/attempts.csv) · [Paired intervals](results/fill/scores.json) · [Forecasts calibrated at each fill](results/fill/level-forecast.json) |
| How precisely can this camera read the syrup? | [Photographs of the two contacts](optical-calibration/photos/clear-pour-examples.jpg) · [Photographed cup markings](optical-calibration/photos/forecast-graduations.jpg) · [Agreement on the same pours](optical-calibration/photos/same-pour-optical-agreement.png) |

## What held up

After calibration with a pair of servings on each head, the same lever program predicted subsequent concentrate doses for a partial-flow top-off, a short richer pour, a pour that finished at full flow and a glass at a sustained near-full opening. Every head and program met its registered coverage and bias limits on both sightlines. The [individual endpoint predictions](results/repeat/attempts.csv) can be read as a starting cup level, an expected finish and the finish the camera actually saw. [Observed errors across servings](results/repeat/overall.json)

Briefly releasing and reopening the lever during a pour triggered the controller’s cooldown. At the same simulated water volume the controller delivered fewer motor bursts, and the measured concentrate dose fell in every matched pair on both clear-glass sightlines. The two sightlines also captured the lag after the final meter input on a pour that finished at full flow. [Paired concentrate doses](results/original/release-clear-glass.json) · [Timed camera observations](camera/README.md)

A model based on individual pulse widths underpredicted a sustained glass at an intermediate lever opening on both pumps. The error was visible in native pixels as well as in the calibrated volumes. At equal simulated water volume, the full-opening and slower-opening comparison depended on head and optical method. [Reserved waveform results](results/fresh/by-scenario.csv) · [Equal-water comparison](results/original/scores.json)

The withdrawal pump’s five-burst dose was smaller at the higher fill in every matched pair on each sightline. The refill pump showed nearly unchanged native pixel displacement across fills. The conversion from pixels to volume varies locally with the cup’s geometry, and the two independently fitted sightlines gave different equivalence decisions on that pump. Calibrating separate doses by fill put every reserved serving within the practical tolerance, but its improvement over a pooled calibration fell short of the registered threshold. [High and low fills](results/fill/scores.json) · [Reserved fill forecasts](results/fill/level-forecast.json)

## Reading a prediction

A took concentrate out of the OXO cup and B returned it from the rectangular dish. Subtract A’s predicted dose from the photographed start or add B’s. The controller ran the installed pour firmware. USB supplied the meter readings that a faucet would produce. The controller selected the dispense path and drove the real motors at full power. Both pumps moved undiluted SodaStream Diet Cola. All water volumes are calculated from the programmed meter inputs. The experiment measured concentrate through the bench hoses. The installed flavor-line lift, valves and umbilical and the water delivered by a faucet need a separate measurement.

The operator reported that the tubes were cut to equal lengths, the guides had been removed from a tube that had already been bent, and the electrical connections had been exchanged after the rig shifted. The [qualification photographs and commands](logs/qualifications.jsonl) establish the transfer directions for this setup. The earlier dry motor motion contributes no liquid-delivery data. Pump identity, tubing history and transfer direction stayed paired throughout these runs. Neither the effect of creating a fresh bend nor the result of reversing an individual pump can be inferred from the A–B difference.

## Testing the hypotheses

The [initial design](preregistration.json) defines the training runs, randomized serving order and miss criterion. A [replay of the firmware policy](policy_trace.cpp) predicts the sequence of motor bursts. The [pulse-width model](frozen-model.json) estimates delivery per burst from training pours on each head and interpolates between the trained widths. The original serving series scores this forecast against the right-hand cup ruler, an independent reading of the other print column and a separate displacement forecast in native image pixels. [Original scores](results/original/scores.json)

The [graduation experiment](graduation-design.json) follows the foreground liquid across the end of each printed mark and locates that crossing on clear glass at two positions. The lowering sweep located the lower and middle marks. Glare obscured the upper mark while lowering. The [registered fallback](reserved-native-and-fallback.json) uses an earlier rising crossing there. A separate rising sweep checks the resulting scale. At the upper mark this tests same-direction repeatability. Both sightlines share the cup and its graduations. Local agreement measures repeatability of a transfer. An offset between the cup’s two printed one-cup marks illustrates the limit on an absolute reading from this angle. The photographs retain the glare and false-edge cases. The kitchen scale carries variable load from the hoses and motor and supplies no values to these forecasts. [Calibration and stationary checks](optical-calibration/stationary-check.json) · [Optical audit](optical-calibration/geometry-results/summary.json)

The [reserved lever programs](fresh-programs.json) test the [graduation-based pulse-width forecasts](geometry-model.json) on new waveforms. The [known-recipe test](repeat-design.json) separately asks whether measuring the **same** program on a head can predict later servings. Only the first pair for each head and program sets the arithmetic mean. Each subsequent serving tests both models on the same command and photographs. Later blocks from the reserved series count once in the physical total. The additional repeat blocks follow the cup-level experiment. [Frozen recipe forecasts](repeat-model.json) · [Prediction chronology](chronology.json)

The [fill-level test](fill-design.json) compares identical bursts in randomized high/low pairs. The controller gave the test head the same conditioning pulse and rest before each pour. The calibrated midpoints give the actual separation. Each pair changes both vessels’ fill levels and the tubing immersion together. A difference measures sensitivity of this complete setup. The registered equivalence margin and paired intervals decide whether the two mean doses can be treated alike on this bench. A [separate prospective check](level-forecast.json) uses the first matched blocks to learn a different dose at each fill, freezes those predictions, and compares them with a pooled calibration on the untouched final pairs.

## Reproducing the readings

The [optical replay](optical-calibration/README.md) reconstructs the settled glass contacts from the archived camera pixels. The [camera timing replay](camera/README.md) aligns motion during a pour with the timestamped motor and meter events. The [final return photographs](optical-calibration/photos/return-edge-selection.jpg) identify a bright reflection selected by the broad positioning reader and the foreground contact selected by the qualified volume reader. The [controller journals](logs/) include the pre-command forecasts, input transitions, burst counts, elapsed times and final state. The [volume command and its readback](logs/volume.jsonl) document the saved mute setting.

From this directory, the following commands reproduce the repeat and fill tables from those records. Python uses SciPy for the paired interval. Matplotlib and NumPy render the figures.

```sh
python3 analysis/score_repeat.py logs/fresh.jsonl logs/repeat.jsonl repeat-model.json geometry-model.json /tmp/kamoer-repeat
python3 analysis/plot_repeat.py /tmp/kamoer-repeat/attempts.csv /tmp/kamoer-repeat/recipe-predictions.png
python3 analysis/score_fill.py logs/fill.jsonl /tmp/kamoer-fill
python3 analysis/plot_fill.py /tmp/kamoer-fill/scores.json /tmp/kamoer-fill/fill-level-effect.png
python3 analysis/level_forecast.py score logs/fill.jsonl level-forecast.json /tmp/kamoer-fill/level-forecast.json
```
