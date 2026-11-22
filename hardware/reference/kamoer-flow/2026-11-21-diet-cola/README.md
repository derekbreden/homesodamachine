# Diet Cola on the Kamoer pump bench

The Kamoer heads transfer SodaStream Diet Cola concentrate between the OXO measuring cup and a rectangular glass dish. Derek set the cup at its one-cup mark and confirmed that all the cut tubes share the same length. The pumps started dry.

Channel A carries both bend guides on the dish-side tube. The cup-side tube on that head has yellow lettering. Channel B has straight runs and a plain tube in the cup. The setup photographs trace the paths. The pilot video shows the plain tube moving with the command to B. [Setup photograph](setup/photo-3.jpg) · [Channel B video](video/pilot-b.mp4)

## Cup measurements

The measured volumes, PCB times, pulse doses and optical reading allowances are in the [run table](trials.csv). The [cup calibration](cup-calibration.json) locates the liquid relative to both sets of printed marks in each frame. The [independent dish readings](receiving-dish.json) show whether the receiving level rose.

Each timed command runs one motor at full drive. The controller acknowledges the start and reports the elapsed time on completion. The camera records the settled liquid level after each command or pulse train. The rectangular dish supplies a separate check on delivery while the lines fill. [Controller transcripts](controller) · [Cup and dish images](frames)

The wet continuous runs measure the delivery of each assembled channel. The burst runs use the same commanded interval on both channels, which makes the wet continuous and pulsed delivery comparable at a known motor-on time. The cycle-average rate includes the scheduled pause after each pulse. The mean dose per pulse comes from the total withdrawal across the train. These are timed motor commands on open hoses. The installed faucet, dispense valves, water flow and syrup-to-water ratio require a pour through the appliance.

Pump identity and routing vary together in this arrangement. The difference between channels includes both contributions. The firmware configuration and the original pump connections appear in the controller record. [Initial state](controller/identify.log)

The wet continuous withdrawals overlap within the optical reading allowances. The lowest pulse-train endpoint falls below the last printed graduation. The resting pair gives an optical drift check at that same low level.
