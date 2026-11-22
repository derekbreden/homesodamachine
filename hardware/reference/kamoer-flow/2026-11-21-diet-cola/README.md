# Diet Cola on the Kamoer pump bench

The USB camera measures how much undiluted SodaStream Diet Cola moves between a graduated OXO cup and a rectangular dish. The cup’s printed marks set the volume scale. Each test links a pump command to an observed change in the liquid level. [Run summary](flow-summary.json) · [Run table](dose-results.csv)

## What the camera measured

The side camera resolves smaller changes by matching the same section of the liquid surface in consecutive images and registering both views to the cup’s printing. The precision study tests that method on quiet images, reflective glass and small motor-drive settings. Its working threshold applies to changes near the measured fill. The cup’s manufacturing accuracy is unknown. [Precision and motor-drive results](camera-precision.json) · [Annotated native image](camera-precision.png)

The camera measures the combined volume of each pulse train. Dividing by its completed gate count gives the mean volume per pulse for that train. The full-cycle rate includes the pause that would follow its final pulse in continuous use. Separate controller logs give the actual gate timing. [Optical pulse volumes](pulse-cup/measurements.csv) · [Marked contact lines](pulse-cup/contacts.jpg) · [Full-flow pulse measurements](pulse-optical-check.json) · [Controller timing audit](pulse-timing-audit.json) · [Dose and load figure](measured-dosing.png)

The initial wet runs and lower-fill runs measure transfer through each assembled open hose. The dry-start commands also drew syrup into empty tubing, with little visible change in the receiving dish. The first steep view uses the hand-set starting level and the first direct side reading as its volume anchors. Derek confirmed the amount in the cup stayed the same when the camera moved. [Initial trials](trials.csv) · [Cup calibration](cup-calibration.json) · [Receiving dish](receiving-dish.json) · [Continuous runs](side-optical.csv) · [Matched fill bands](fill-band-optical.json)

## Released outlet tube

The single-shot series follows each head from short isolated starts through sustained flow. Full-resolution stills bracket each small shot. Idle comparisons in the same sequence set the threshold for detecting motion in that run. The videos record the cup through each start, stop and settling period. The refill surface overshoots its resting level. The reported doses use the later settled frames. [Individual doses and idle controls](native-single-shots.png) · [Native single-shot measurements](native-single-shots.csv) · [Native image method and pixel evidence](native-single-shots.json) · [Camera and command times](released/native-command-events.jsonl) · [Surface timing](dynamic-timing-check.json)

A separate comparison divides equal motor on-time into trains of different pulse lengths. Each schedule has the same total period when its final pause is included. Controller acknowledgements give the duration of every gate. Shorter, more frequent pulses moved more syrup than the longest pulses on each head in the matched comparisons. The trial table includes signed optical changes, readings from nearby parts of the glass and the difference between post-stop windows. [Measured dose curves](released/dose-curves.png) · [Trial readings](released/trials.csv) · [Independent pulse comparison](independent-segmentation-check.json) · [Measurement method and recording index](released/summary.json) · [Cup videos, original frame times and controller receipts](released/recordings)

## Rig and scale

Derek cut all the tubes to the same length. Both channels initially drew from the measuring cup. A is the left head as seen from the sink and carried both bend guides on its dish-side tube. B is the right head. Its plain tube moved when the controller drove B. Derek exchanged B’s loose ends between the vessels. B then returned syrup to the cup while A withdrew it. The motors ran forward. The as-built comparison includes differences between the heads and their flow paths. [Rig identification](setup.json) · [Setup photograph](setup/photo-3.jpg) · [Channel identification](video/pilot-b.mp4) · [Return check](frames/return-check-view.jpg)

The iPhone recorded the Smart Weigh display. The cup, liquid and forces from the pumps and hoses all contributed to its reading. Even a stable display can include a sustained pull on the cup. Signed differences in grams describe the supported load. Every reported volume comes from the liquid surface and the cup markings. [Display readings and time series](scale/measurements.json) · [LCD pairs](scale/return-rig.csv)

Derek removed A’s guides after the guided runs. Its tube had already been bent. Releasing the clips gives an observation of that tube in its released state. A measurement of what forming the bends changes would need a straight reading on the same tube before forming. An installed faucet pour also includes valves and moving water. [Rig configurations](setup.json)

The bench image provides short, timed motor-drive commands. The readback matched the original application sectors after restoration, and the appliance reported idle with its valves closed. [Controller transcripts](controller) · [Image verification](controller/restored-image.json) · [Restored appliance status](controller/restored-status.log) · [Final single-shot controller log](controller/released-native-shots.log)
