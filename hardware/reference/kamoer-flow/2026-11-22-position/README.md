# Predicting syrup level on the pump bench

With the tube ends restored and the electrical connections swapped, a command on channel A draws Diet Cola concentrate out of the graduated cup. B returns it from the rectangular dish. The controller pulsed each channel separately. The camera saw the liquid move in the corresponding direction across the cup and stay still during the idle check. The labels throughout this record identify the PCB outputs. [Before-and-after photographs](optics/post-reset/reset-direction.jpg) · [Measurements from the direction check](optics/post-reset/reset-direction.csv) · [Original board replies](logs/rewired-a.jsonl)

## Moving from a known level to a requested level

Each channel's direction check supplied a single estimate of movement per second. With those estimates frozen, the controller read the starting level, chose a motor time and recorded its prediction before applying power. It visited the same set of destinations in different trials. At each destination it either waited or used the camera to make one correction if the miss exceeded the stated tolerance. Every first shot and late endpoint has a score. [Predicted and observed destinations](analysis/position_validation.png) · [Frozen destinations and policy assignments](rewired-design.json) · [Target, motor time and miss for every attempt](analysis/position_trials.csv) · [Scores, local delivery rates and optical scale](analysis/position_scores.json)

A clear strip at the front of the cup supplied the steering coordinate. A second strip of glass supplied an independent test of the prediction. It used different pixels and estimated the brightness crossing with a different method. The held-out strip gave larger errors. Changes in the printed marks reveal cup motion. Different parts of the curved surface show different apparent travel. The kitchen cup supplies a local volume estimate, with the conversion from each set of marks retained separately. After the last test, B returned the liquid to its photographed starting level. Both the control strip and the independent strip located the settled surface within one pixel of their own reference. The fluctuating scale carries some of the tube and pump load. All reported doses and destination scores in this record come from the camera. [Independent optical scores and idle drift](optics/post-reset/reset-summary.json) · [Independent observations per target](optics/post-reset/reset-targets.csv) · [Final return and parked controller](logs/return-to-reference.jsonl)

## Continuous drive and spaced pulses

The pulse experiment holds total motor-on time fixed on each head. Every block compares continuous drive with short pulses separated by different pauses. The controller returns the cup to a comparable initial level before each schedule and records its prediction, switch times, settled optical movement and both printed-scale estimates. A delivered more with short pauses than with long pauses in every matched block, including on the independent image strip. B varied across blocks and showed both orderings. The raw journals distinguish completed schedules from interrupted attempts. [Prespecified pulse schedules and order](rewired-pauses.json) · [Dose by pulse spacing](analysis/equal-time-doses.png) · [Individual doses and actual off-times](analysis/equal-time-trials.csv) · [Differences within matched blocks](analysis/equal-time-results.json) · [Held-out optical check](optics/post-reset/reset-pulse-summary.json)

## Earlier overnight observations

The wider cup view and its original calibration cover isolated shots, repeated durations, rest, and an interrupted pause sweep. Across the isolated shots, the previous evening's calibration consistently predicted more syrup than the camera observed. Fitting the first overnight block gave closer predictions on the following blocks. Derek reported a fallen pump, returned the tube ends to their original vessels and switched electrical connections. The camera records the handling interval. The time of the fall and its contribution to the earlier rates remain unknown. The transition journal contributes no earlier flow or precision estimate. The restored configuration uses its own optical reference and rates. [Earlier width forecasts and outcomes](analysis/forecast_validation.png) · [Scores and exclusions](analysis/forecast_scores.json) · [Transition images measured under the earlier reference](optics/transition)

The two tubes on each pump are equal in cut length. The earlier clip-removal comparison concerns the effect of external support on a tube that had already been bent. These trials leave the isolated effect of bending a fresh tube open. [Earlier pump, routing and dose measurements](https://github.com/derekbreden/homesodamachine/tree/30f0c9078f5905d1041d60111efb0b832e3c554e/hardware/reference/kamoer-flow/2026-11-21-diet-cola)

## Replaying the measurements

The camera tests measure idle drift, the effect of white balance and focus on the apparent level, the time from a motor command to visible movement, and how long the surface takes to settle. In the stationary autofocus test the apparent liquid line moved, and reapplying the fixed focus value also left a visible offset. The destination trials kept the stream open with focus and image controls fixed. Each fresh setup needs its own optical reference. The saved readback confirms the original camera settings after closure. [Camera measurements, motion traces and replay](camera/stream/README.md)

The lossless luma crops show the liquid. The contemporaneous color tiles show the printed graduations. Their individual camera timestamps and hashes are in the frame index. The optical analysis can be rerun on the photographs without operating the pumps. The experimental acquisition source is kept alongside the data. [Image index](frames/index.json) · [Optical methods and replay commands](optics/README.md) · [Motor commands and observations](logs) · [Acquisition source](acquisition)

From this directory, the following commands replay the dated trials with Python, NumPy, SciPy and Pillow. Output paths can point to any writable directory. Matplotlib is used for the optional plots.

```sh
python analysis/replay_endpoints.py .
python optics/audit_reset.py . --output /tmp/pump-reset-replay
python analysis/score_forecasts.py logs --local local-gap-forecast.json --out /tmp/pump-width-replay
python analysis/score_positions.py logs --design rewired-design.json --responses camera/position-responses --out /tmp/pump-position-replay
python analysis/read_equal_time.py . --out /tmp/pump-pulse-replay --plot
```
