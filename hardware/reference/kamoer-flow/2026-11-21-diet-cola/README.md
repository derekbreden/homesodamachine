# Diet Cola on the Kamoer pump bench

The pumps transfer undiluted SodaStream Diet Cola between a graduated OXO cup and a rectangular glass dish. The [run summary](flow-summary.json) groups the results by head, tubing, direction and drive setting. The [weighed doses](dose-results.csv) give each measured load change, pulse count and controller time.

## Rig

Derek filled the cup to its one-cup line. All cut tubes are the same length. Both pumps started dry, and both initially drew from the cup. Channel A carries both bend guides on the dish-side tube and has a yellow-lettered tube in the cup. Channel B has a plain cup tube. The setup photographs trace the tubing. The plain tube moves when the controller first drives B. [Setup and channel identification](setup.json) · [Rig photograph](setup/photo-3.jpg) · [Channel B video](video/pilot-b.mp4)

Derek exchanged the straight pump’s free ends between the vessels. B then returned concentrate from the dish to the cup while A withdrew concentrate. The first return raised both the visible cup level and the indicated mass. The firmware drives the motors forward throughout the series. [Return check](frames/return-check-view.jpg) · [Scale startup during the return](scale/return-setup.json)

## Reading the measurements

The cup camera records the near liquid surface against the front graduations. For the initial steep camera angle, the starting fill and the first side reading fix the volume scale. Derek confirmed that the cup held the same amount throughout the camera move. The calibration compares alternate readings of the surface and a separate rise in the receiving dish. The practical optical allowances cover the choice of meniscus and interpolation. The cup’s manufacturing tolerance is unknown. [Initial trials](trials.csv) · [Cup calibration](cup-calibration.json) · [Receiving dish](receiving-dish.json) · [Side readings](side-optical.csv)

The iPhone records the Smart Weigh display under the measuring cup. A positive difference adds load to the cup, and a negative difference removes it. Each difference uses its own before and after readings within one scale power interval. The sign, the elapsed run time and the separate level readings identify transfer direction. The LCD’s drift, settling and power-off are visible in the scale record. Immersed tubes can transmit load to the scale. The relation between indicated mass and optically inferred volume applies to this rig. [Scale record](scale/measurements.json) · [Paired scale readings](scale/return-rig.csv)

The first runs include syrup taken into the dry tubing. The receiving dish shows little level change during those commands. The wet runs describe transfer through the assembled open hoses. The mean per pulse comes from weighing an entire train. The full-cycle rate includes the pause that would follow the final pulse in steady operation. The PCB reports its gate time separately. [Controller transcripts](controller) · [Cup images](frames)

The initial comparison changes the head and tubing together. Exchanging B’s free ends also changes which vessel supplies it. The open-hose measurements do not establish the syrup-to-water ratio at the installed faucet.
