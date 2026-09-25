# Production slice reviews

Each manifest binds its own geometry receipt, exact native archive and support review. An archive whose receipt no longer matches the files it names is not the current geometry.

Visible top/bottom rounds at 0.08 mm print without support contacts. Every pending archive
needs that check on the actual support paths, including unlabelled slivers; a passed layer-band
review does not establish support exclusion. Derek's
[tee-carrier observations](../../../tee-carrier/physical-acceptance.json) provisionally accept
the v14 lower surface with no observed spaghetti failure and a slight concavity. Six walls
alone with the original wall-first order is the preferred next recipe and remains untested.

| Job | Printer | State | Evidence |
| --- | --- | --- | --- |
| back-bottom | Mark2 | reviewed, not sent; uniform 0.24 mm, no band at the handhold rounds; back-bottom changed after it | [2026-09-21-enclosure-back-bottom-mark2-v2](2026-09-21-enclosure-back-bottom-mark2-v2/manifest.json) |
| back-top | H2C | printing on H2C since 09-22; sliced from the 09-21 inputs, uniform 0.24 mm; back-top changed after it | [2026-09-21-enclosure-back-top-h2c-v2](2026-09-21-enclosure-back-top-h2c-v2/manifest.json) |
| front-bottom | Mark2 | printed 09-21; before the carrier windows notched the seam rail | [2026-09-21-enclosure-front-bottom-mark2-v2](2026-09-21-enclosure-front-bottom-mark2-v2/manifest.json) |
| front-top | H2C | printed 09-21; supports trapped behind the skirt-pocket surrounds | [2026-09-21-enclosure-front-top-h2c-v4](2026-09-21-enclosure-front-top-h2c-v4/manifest.json) |
| front-top | Mark2 | superseded: 34 mm skirt pockets | [2026-09-22-enclosure-front-top-mark2-v6](2026-09-22-enclosure-front-top-mark2-v6/manifest.json) |
| front-top | Mark2 | superseded: pulled top curve | [2026-09-22-enclosure-front-top-mark2-v7](2026-09-22-enclosure-front-top-mark2-v7/manifest.json) |
| front-top | Mark2 | superseded: before the storey cavities and the carrier windows | [2026-09-22-enclosure-front-top-mark2-v8](2026-09-22-enclosure-front-top-mark2-v8/manifest.json) |
| display-cover | Mark2 | superseded: 34 mm skirts | [2026-09-22-display-cover-mark2-v1](2026-09-22-display-cover-mark2-v1/manifest.json) |
| display-cover | Mark2 | superseded: face up, skirts on the bed | [2026-09-22-display-cover-mark2-v2](2026-09-22-display-cover-mark2-v2/manifest.json) |
| display-cover | Mark2 | printed face down; flat when removed or seated upside down, bows when its snaps engage | [2026-09-22-display-cover-mark2-v3](2026-09-22-display-cover-mark2-v3/manifest.json) |
| display-cover | Mark2 | printed; 34 mm skirts, fits only the front-top printed 09-21 | [2026-09-22-display-cover-mark2-v4](2026-09-22-display-cover-mark2-v4/manifest.json) |
| display-cover | Mark2 | prepared, not sent; original perimeter, snaps inset 0.3 mm each; 23 min 51 sec | [2026-09-24-display-cover-mark2-v5](2026-09-24-display-cover-mark2-v5/manifest.json) |
| display-cover and both window covers | Mark2 | printing since 09-25, task 1281656339; inset display snaps and existing window covers; 41 min 57 sec; window covers unsupported | [2026-09-24-display-cover-window-covers-mark2-v6](2026-09-24-display-cover-window-covers-mark2-v6/README.md) |
| foam-cap-lid-top | Mark2 | superseded mount geometry | [2026-09-21-g-ganen-foam-cap-lid-top-mark2-v1](2026-09-21-g-ganen-foam-cap-lid-top-mark2-v1/manifest.json) |
| foam-cap-lid-top | Mark2 | reviewed, not sent | [2026-09-21-g-ganen-foam-cap-lid-top-mark2-v2](2026-09-21-g-ganen-foam-cap-lid-top-mark2-v2/manifest.json) |
| foam-cap-top | H2C | superseded mount geometry | [2026-09-21-g-ganen-foam-cap-top-h2c-v2](2026-09-21-g-ganen-foam-cap-top-h2c-v2/manifest.json) |
| foam-cap-top | Mark2 | superseded mount geometry | [2026-09-21-g-ganen-foam-cap-top-mark2-v1](2026-09-21-g-ganen-foam-cap-top-mark2-v1/manifest.json) |
| foam-cap-top | Mark2 | reviewed, not sent | [2026-09-21-g-ganen-foam-cap-top-mark2-v2](2026-09-21-g-ganen-foam-cap-top-mark2-v2/manifest.json) |
| pump-cartridge | H2C | reviewed, not sent; the cartridge changed after it (hand-pocket floor) | [2026-09-23-pump-cartridge-cap-h2c-v2](2026-09-23-pump-cartridge-cap-h2c-v2/manifest.json) |
| tee-carrier | H2C | superseded by v2, the same plate with both window covers on its bed | [2026-09-23-tee-carrier-plate-h2c-v1](2026-09-23-tee-carrier-plate-h2c-v1/manifest.json) |
| front-top | Mark2 | reviewed, not sent; front-top changed after it (window-cover posts, audit fixes) | [2026-09-23-enclosure-front-top-mark2-v9](2026-09-23-enclosure-front-top-mark2-v9/manifest.json) |
| front-bottom | H2C | reviewed, not sent; front-bottom changed after it (audit fixes) | [2026-09-23-enclosure-front-bottom-h2c-v3](2026-09-23-enclosure-front-bottom-h2c-v3/manifest.json) |
| front-top | Mark2 | superseded by v12: front-top goes to H2C | [2026-09-23-enclosure-front-top-mark2-v11](2026-09-23-enclosure-front-top-mark2-v11/manifest.json) |
| front-bottom | H2C | not to send: its 0.08 band covers only 32.65–37.85 mm of the R6 handhold rounds, which span 29.25–41.25 mm | [2026-09-23-enclosure-front-bottom-h2c-v5](2026-09-23-enclosure-front-bottom-h2c-v5/manifest.json) |
| front-bottom | H2C | running since 09-24, task 1279923918; complete 0.08 mm handhold rounds and flute run-outs; six walls through downward curves only; original order and speeds; rounded faces unsupported | [2026-09-24-enclosure-front-bottom-h2c-v7](2026-09-24-enclosure-front-bottom-h2c-v7/manifest.json) |
| back-bottom | Mark2 | not to send: its 0.08 band covers only 32.65–37.85 mm of the R6 handhold rounds, which span 29.25–41.25 mm | [2026-09-23-enclosure-back-bottom-mark2-v3](2026-09-23-enclosure-back-bottom-mark2-v3/manifest.json) |
| pump-cartridge | H2C | superseded by v4: the cartridge and cap go to Mark2 | [2026-09-23-pump-cartridge-cap-h2c-v3](2026-09-23-pump-cartridge-cap-h2c-v3/manifest.json) |
| back-top | H2C | not to send: the first layer is 0.20 mm, and the 0.08 band covers only 0–2.6 mm of the R6 roof edges, which span 0–6 mm from the bed | [2026-09-23-enclosure-back-top-h2c-v5](2026-09-23-enclosure-back-top-h2c-v5/manifest.json) |
| back-top | H2C | prepared, not sent; v7 blocks support on both visible roof rounds, preserves complete 0.08 mm layers and the 40 functional support interfaces; see the scoped review | [2026-09-24-enclosure-back-top-h2c-v7](2026-09-24-enclosure-back-top-h2c-v7/manifest.json) |
| tee-carrier | H2C | superseded by v3: the carrier goes to Mark2 | [2026-09-23-tee-carrier-plate-h2c-v2](2026-09-23-tee-carrier-plate-h2c-v2/manifest.json) |
| front-top | H2C | cancelled 09-23 at layer 51/1326: its 0.08 band covers the R18 roof arc, but only the last part of the R6 roof side and corner curves | [2026-09-23-enclosure-front-top-h2c-v12](2026-09-23-enclosure-front-top-h2c-v12/manifest.json) |
| front-top | H2C | printing since 09-23, task 1277245499; emitted 0.08 mm wall layers cover the complete R6 roof side and corner curves and R18 roof arc | [2026-09-23-enclosure-front-top-h2c-v13](2026-09-23-enclosure-front-top-h2c-v13/manifest.json) |
| tee-carrier | Mark2 | not to send: its 0.08 bands cover 2.6 mm of each R6, not the whole curve | [2026-09-23-tee-carrier-plate-mark2-v3](2026-09-23-tee-carrier-plate-mark2-v3/manifest.json) |
| tee-carrier | Mark2 | superseded: its 0.08 mm layers cover both R6 ends, but the plate STL has the old fluted face | [2026-09-23-tee-carrier-plate-mark2-v4](2026-09-23-tee-carrier-plate-mark2-v4/manifest.json) |
| tee-carrier | Mark2 | superseded by v6; the smooth plate's visible aft and fore R6 ends are complete, while eight hidden tee troughs have 0.24 mm layers above 6.1 mm | [2026-09-23-tee-carrier-plate-mark2-v5](2026-09-23-tee-carrier-plate-mark2-v5/manifest.json) |
| tee-carrier | Mark2 | rejected by Mark2 as invalid 3MF; smooth carrier and both covers, 0.08 mm across the end rounds and hidden troughs | [2026-09-23-tee-carrier-plate-mark2-v6](2026-09-23-tee-carrier-plate-mark2-v6/manifest.json) |
| pump-cartridge | Mark2 | not to send: its 0.08 bands cover 2.6 mm either side of each grip opening's level, not the whole curves | [2026-09-23-pump-cartridge-cap-mark2-v4](2026-09-23-pump-cartridge-cap-mark2-v4/manifest.json) |
| pump-cartridge | Mark2 | not sent; complete 0.08 mm grip-round bands, cap at 0.24 mm; requires the visible-round support-exclusion check before sending | [2026-09-23-pump-cartridge-cap-mark2-v6](2026-09-23-pump-cartridge-cap-mark2-v6/manifest.json) |
| pump-cartridge | Mark2 | printing since 09-24, task 1279835918; complete 0.08 mm grip rounds, six walls only in upper grip band, original order and speeds; rounded surfaces unsupported, flat ceilings and cap seats supported | [2026-09-24-pump-cartridge-cap-mark2-v8](2026-09-24-pump-cartridge-cap-mark2-v8/manifest.json) |
| bulkhead rings | Mark2 | printed 09-23 at 0.20 mm; Derek rejected the surface finish | [2026-09-23-bulkhead-rings-tap-flavor-mark2-v1](2026-09-23-bulkhead-rings-tap-flavor-mark2-v1/manifest.json) |
| bulkhead rings | Mark2 | printed 09-23, task 1277283660; 0.08 mm improved the face-up lettering, but Derek found it less sharp than the face-down nameplate | [2026-09-23-bulkhead-rings-tap-flavor-mark2-v2](2026-09-23-bulkhead-rings-tap-flavor-mark2-v2/manifest.json) |
| bulkhead rings | Mark2 | printing since 09-24, task 1277448913; lettered faces down, all 25 layers at 0.08 mm, Mark2 +0.04 mm requested Z trim and the same black/white hotend assignments | [2026-09-23-bulkhead-rings-tap-flavor-mark2-v3](2026-09-23-bulkhead-rings-tap-flavor-mark2-v3/manifest.json) |
| bulkhead rings | Mark2 | printing on Mark2 since 09-24; face down on the nameplate's settings (0.20 first layer, 0.24) | [2026-09-24-bulkhead-rings-tap-flavor-mark2-v4](2026-09-24-bulkhead-rings-tap-flavor-mark2-v4/manifest.json) |
| tee-carrier | Mark2 | completed, task 1277634817; carrier only, 0.24 mm base and 0.08 mm through the exposed end rounds including the first layer; +0.04 mm requested Z trim | [2026-09-24-tee-carrier-plate-mark2-v10](2026-09-24-tee-carrier-plate-mark2-v10/manifest.json) |
| tee-carrier | Mark2 | completed, task 1277839952; supports disabled; clean upper curve, localized lower-curve curling around layers 20–30 | [2026-09-24-tee-carrier-plate-mark2-v11](2026-09-24-tee-carrier-plate-mark2-v11/manifest.json) |
| tee-carrier | Mark2 | completed; physical result rejected, task 1278660260; fan-off trial has inward edge retreat, unsupported strands and eventual recovery from the interior | [2026-09-24-tee-carrier-plate-mark2-v12](2026-09-24-tee-carrier-plate-mark2-v12/manifest.json) |
| tee-carrier | Mark2 | stopped by Derek after renewed edge failure, task 1279237907; failures lie between infill contacts; actual failure layer unknown | [2026-09-24-tee-carrier-plate-mark2-v13](2026-09-24-tee-carrier-plate-mark2-v13/manifest.json) |
| tee-carrier | Mark2 | completed, task 1279390313; provisional lower-curve acceptance: no observed spaghetti failure, residual slight concavity; six walls at Z 0–6.1 mm and infill first | [2026-09-24-tee-carrier-plate-mark2-v14](2026-09-24-tee-carrier-plate-mark2-v14/manifest.json) |
| tee-carrier | Mark2 | prepared, not sent; six walls only at Z 0–6.1 mm, original wall-first order, speeds and 15% overlap; physical result untested | [2026-09-24-tee-carrier-plate-mark2-v15](2026-09-24-tee-carrier-plate-mark2-v15/manifest.json) |

The two current Mark2 mounting plates use the shared 7 mm G Ganen feet and corrected screw stations. The shell archives retain their complete native/support reviews; back-top additionally has a native-equivalence proof for its numerical mesh variation. Physical support cleanup and assembled fit are observations from the full enclosure trial.
