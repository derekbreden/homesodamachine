# Bounded inlet and pump contact review

The current C14 reference has **0.0 mm³ native overlap** with the exported back-top at its production seated pose. The printed pocket is native-identical to the physically accepted profile at nominal, 0.15 mm slipped and 3.15 mm outer offsets, each through its 5 mm depth. Derek has physically accepted this station with the inlet and mating C13 connector. Its rim seats at Y463.05; the rear boundary carries the station aft by 4.3 mm without altering its profile, bore or screw pitch.

The twelve Kamoer component-to-cartridge/cap readings have no positive intersection. The G Ganen rigid body has no cap intersection; 722.156848 mm³ of unloaded rubber-foot contact falls inside the four exact foot masks, with 0.00005475 mm³ outside-mask numerical residue. The retained pump clears all four shell inputs. These pump readings use the production mesh-overlap query and native bounding-box rejection; they do not quantify clamp force or rubber compression. Each input and source digest is in the JSON.

[The review](review.json) links the [seated C14 proof](c14-frozen-reference-check.json), [printed-pocket equality](c14-pocket-preservation.json), and [pump readings](pump-contact-check.json). The four classifier regression cases independently retain failures for rigid interference, outside-mask material and an incorrect bearing plane.

This review covers the recorded parts and poses. It is not a complete assembly scorecard, new full insertion proof, or physical enclosure acceptance. Shell input hashes in the pump report are explicit because later shell regeneration can replace those artifacts.

The retained read-only scripts preserve the exact probe code and original temporary output paths. Run the pocket-preservation script before the seated C14 script with the repository CadQuery Python. No script exports production geometry.
