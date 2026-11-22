# Forecasting an unfamiliar lever movement

A guest can taste a drink, ease the lever back, top off a glass or pause partway through filling it. This experiment asks whether the same model for a pump can predict the concentrate in any of those servings before the motor starts. Each forecast begins at the level the camera sees. Pump A withdraws syrup from the graduated cup. Pump B returns it from the dish.

![Individual concentrate errors for each pump and reserved lever movement](results/unseen-pours.png)

## Read a serving

Each row of the serving record has a photographed starting level, a predicted finishing level and a photographed finish for each sightline. Error is the concentrate delivered minus the concentrate predicted. A positive error means the pump moved extra syrup in its direction of flow. The practical acceptance band includes an absolute allowance for small pours. The stricter percentage-only result is reported alongside it. [Every reserved serving](results/attempts.csv) · [Coverage and bias by lever movement](results/by-program.csv) · [Overall score and comparison with the earlier pulse-width model](results/scores.json)

## What held up

The refill head met both acceptance criteria on every reserved movement. The withdrawal head passed the taste, changing-opening and glass-size programs. Every uninterrupted full glass and every glass with a slower middle also landed inside the stricter percentage band on each sightline. The earlier pulse-width-only model systematically underpredicted the larger pours. The frozen model reduced the mean absolute error on each head and each sightline. [Scores by lever movement](results/by-program.csv) · [Residuals by acquisition block](results/by-block.csv)

The matched restart test met its equivalence limit for pump B on both sightlines. The primary reading showed almost identical average doses for its uninterrupted and resumed glasses. On pump A, a resumed glass delivered less syrup on average. The uncertainty interval crossed the registered limit, leaving the size of A’s restart correction unresolved. The matched brief taste and uninterrupted glass also show how much concentrate the extra pulses delivered on average. Their starting levels differ because each pour was centered within the cup's readable band. [Matched differences by block and sightline](results/contrasts.json)

## Where the model broke down

Pump A delivered extra syrup on the low, steady top-off. In this program every pulse falls below the model's width threshold and every gap falls below its restart threshold. The model therefore uses its short-pulse rate, the count correction and a single start. The observed excess rules out that combined prediction for this head. Pulse width, ordinary pause length and pulse count also differ from the training top-offs, which limits attribution to any individual term. Both camera stripes saw the same repeated excess. Pump B met the accuracy criteria on the same top-off program. [Top-off repeats and errors](results/attempts.csv) · [Cup movement between commands](results/stationary.csv)

## What was tested

The training data come from previous open-hose pours of undiluted SodaStream Diet Cola. Each head has its own relationship between its delivered dose and the time its motor is on, the number of pulses, the time spent above a pulse-width threshold, and starts after a long rest. Programs that produced the same ordered motor commands were grouped during fitting and held out together in the historical model checks. The fit uses the primary clear-glass sightline. [Training pours](historical-doses.csv) · [Unique training motor schedules](historical-gates.json) · [Historical checks](fit-diagnostics.json) · [Coefficients and formula](model.json)

The reserved programs span a brief taste, a low top-off, a changing opening, an uninterrupted full glass, a release and restart, and a full glass with a slower middle. They include several flavor ratio settings. Every ordered motor schedule and burst count was absent from the training set. The glass with a slower middle recombines familiar pulse widths and gaps. The closeness of single positioning pulses to the brief taste limits what can be said about the novelty of that individual pulse. [Test order, expected motor intervals and rejection rules](design.json)

The controller ran its installed pour firmware. The laptop supplied the sequence of water-meter signals. The controller selected the valve outputs and drove the physical pumps at full power. The syrup traveled through the bench hoses. The water volume shown in the tables is calculated from the supplied signals. The open-hose results cover concentrate delivery within the observed cup-level band. The installed faucet ratio also depends on water delivery and the installed syrup path. [Meter driver](acquisition/meter.py) · [Firmware policy replay](acquisition/policy_trace.cpp)

The study reserved the serving order and criteria in Git, then committed every numerical dose forecast before the first wet command. Each physical repeat has its own endpoint forecast, written to the journal after its starting photograph and before the meter command. The paired commands move syrup in opposite directions. Program order was randomized within each block. Each head led equally often for each program. Positioning commands bring the cup near the registered midpoint for each program and are logged separately. [Design registration](https://github.com/derekbreden/homesodamachine/commit/cd4b81349d685eb61ad615c59f2408cad7ca8e2d) · [Numerical freeze](https://github.com/derekbreden/homesodamachine/commit/0bc951783366815b7d9e5d1566ea9ec3bc3965ac) · [Exact forecasts](forecasts.json) · [Command and photograph journal](logs/validation.jsonl)

The uninterrupted and resumed glasses have identical motor-on widths and burst counts. The resumed program extends one gap. Their programmed water volumes differ. The matched comparison asks whether the change in concentrate agrees with the model's restart correction. The taste and uninterrupted glass provide a second comparison at the same pulse width, measuring the additional concentrate per extra burst. Each comparison pairs servings within the same head and block. [Paired results and uncertainty](results/contrasts.json)

## How the cup was read

A single fixed-control USB camera stream supplied the starting and finishing photographs. The reader locates the liquid edge on clear glass at two positions and uses the previously frozen calibration against the cup's printed marks. In the tables, `near` is the primary image stripe (`x990`) and `far` is the stripe farther right (`x1986`). Each position predicts and scores its own endpoint. The camera record preserves the native pixels used by both readers, their timestamps, the printed-mark alignment and the original and restored controls. Both views share the same cup and graduations. A discrepancy between its two printed cup scales limits the accuracy of absolute volume. The kitchen scale carries variable force from the tubing and contributes no observations to this experiment. [Camera evidence and replay](camera/README.md) · [Cup calibration](optics/geometry-used.json) · [Photograph reader](optics/read_levels.py)

The controller reported the head, first motor-on and motor-off durations, selected valves, number of bursts, and elapsed time through valve closure. The remaining motor intervals come from replaying the firmware policy. Replaying the recorded meter-command times checks whether the transmitted programs produce the complete motor schedules used by the model. The optical endpoint data measure the transfer over the complete pour. Short stationary pairs compare adjacent photographs during which the laptop issued no movement command. Those differences include any residual settling. [Per-serving electrical acknowledgements and endpoints](results/attempts.csv) · [Replay of transmitted meter commands](results/policy-replay.json) · [Stationary differences](results/stationary.csv) · [Initial and returned bench state](results/bench-state.json)

The original flavor and both ratios were restored. The final controller readback reports idle pumps, closed valves and muted volume. The far-right reading at return differed from the first cold-stream photograph by about as much as it moved during the stationary warm-up. Both final readings agree closely with the separate warmed-up reference. The archive includes the original and final levels and the control readback after the camera closed. [Returned cup and board settings](results/bench-state.json) · [Stationary camera repeat](camera/reference/readiness-repeat.json) · [Camera shutdown and restoration](camera/reference/closure.json)

## Reproduce the results

From this directory in a checkout with repository history, run the following with Python, NumPy, SciPy, Pillow, Matplotlib and a C++ compiler. The scorer reads the complete logged sequence and verifies the frozen inputs. The optical replay independently recovers both readings from archived sensor pixels.

```sh
python3 analysis/score.py
python3 analysis/replay_meter.py
python3 analysis/plot_unseen.py
(cd camera && python3 verify_evidence.py .)
```

To rebuild the historical fit into a separate directory, use `python3 analysis/dose_model.py fit --out /tmp/unseen-pour-fit` from this checkout. The predictor accepts `predict --model model.json --head A --gates` followed by the JSON list of motor start times and widths from a program in the design. [Fitter and predictor](analysis/dose_model.py) · [Original training archive](https://github.com/derekbreden/homesodamachine/tree/bc26987f18f42e863b6e2af7df3dad5da07d3eb7/hardware/reference/kamoer-flow/2026-11-22-pour-predictions)
