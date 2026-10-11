# Production slice reviews

Each manifest binds its own geometry receipt, exact native archive and support review. An archive whose receipt no longer matches the files it names is not the current geometry.

Expanding print-down show rounds use the additive chamfer/taper at 0.24 mm with
six local walls. Inward/top show rounds use 0.08 mm. Both exclude support contacts.
Every pending archive needs that check on the actual support paths, including unlabelled
slivers; a passed layer-band review does not establish support exclusion. The
[tee-carrier physical record](../../../tee-carrier/physical-acceptance.json) qualifies
the chamfer/taper surface on job 1292379739. Sliding fit and each other part require
their own physical checks.

| Job | Printer | State | Evidence |
| --- | --- | --- | --- |
| Face-up raised CO2 ring, red body, white letters | Mark2 | completed, task 1307189764, after a refusal during the red load; right-nozzle correction on red; 13 min 36 sec | [2026-10-04-bulkhead-co2-raised-mark2-v1](2026-10-04-bulkhead-co2-raised-mark2-v1/README.md) |
| Face-up raised SODA ring, blue body, white letters | Mark2 | completed, task 1307088867; right-nozzle correction on blue; 13 min 58 sec | [2026-10-04-bulkhead-soda-raised-mark2-v1](2026-10-04-bulkhead-soda-raised-mark2-v1/README.md) |
| Current back-top, PRV chase crown | Mark2 | Native paths and accessible supports reviewed; retained ground-round terminal approximation; not submitted; 26 h 8 min 54 sec | [2026-10-03-enclosure-back-top-current-mark2-v9](2026-10-03-enclosure-back-top-current-mark2-v9/README.md) |
| Current front-top, centred expanded funnel interface | H2C | Native archive and accessible supports reviewed; accepted task 1305315362; 25 h 44 min 45 sec | [2026-10-03-enclosure-front-top-current-h2c-v17](2026-10-03-enclosure-front-top-current-h2c-v17/README.md) |
| Tee carrier, 1.00 mm upper / 0.25 mm lower clearance | Mark2 | accepted sliding and reduced tilt, task 1297480230; existing front-top; 1 h 45 min 40 sec | [2026-09-30-tee-low-force050-mark2-v16](2026-09-30-tee-low-force050-mark2-v16/README.md) |
| Display receiver; 0.30 mm body X and 0.60 mm wing-thickness clearance | H2C | accepted fit and shake retention with residual bow, task 1297296218; 2 h 49 min 41 sec | [2026-09-30-display-x030-receiver-h2c-v5](2026-09-30-display-x030-receiver-h2c-v5/README.md) |
| Nameplate receiver; 0.15 mm body X and 0.45 mm wing Y clearance | Mark2 | completed, task 1297285813; fit accepted with existing flat nameplate | [2026-09-30-nameplate-x015-y045-receiver-mark2-v10](2026-09-30-nameplate-x015-y045-receiver-mark2-v10/README.md) |
| Nameplate receiver, 0.35 mm body X clearance per side | Mark2 | completed, task 1296373726; lateral X movement present; bow persists throughout movement; wings feel tight in Y | [2026-09-30-nameplate-body-x035-receiver-mark2-v8](2026-09-30-nameplate-body-x035-receiver-mark2-v8/README.md) |
| Display receiver, wing-thickness and full-depth body relief | H2C | completed, task 1295323504; still bowing; further main-body X clearance requested | [2026-09-30-display-relief-receiver-h2c-v3](2026-09-30-display-relief-receiver-h2c-v3/README.md) |
| Face-up raised TAP and two FLAVOR collars | Mark2 | completed, task 1295298484; finish and excellent, clear lettering accepted | [2026-09-30-bulkhead-raised-mark2-v2](2026-09-30-bulkhead-raised-mark2-v2/README.md) |
| Nameplate receiver, 0.30 mm Y gap | Mark2 | completed, task 1295207560; provisionally accepted with remaining bow; body-X trial requested | [2026-09-29-nameplate-y030-receiver-mark2-v7](2026-09-29-nameplate-y030-receiver-mark2-v7/README.md) |
| Display receiver, open wing pockets | H2C | completed, task 1295044165; bowing when engaged; inverted fit checks only partial seating depth | [2026-09-29-display-open-wing-receiver-h2c-v2](2026-09-29-display-open-wing-receiver-h2c-v2/README.md) |
| Flat nameplate and standard receiver | Mark2 | completed, task 1294806669; bowing with apparent body X clearance; wing-slot fit under evaluation | [2026-09-29-nameplate-flat-standard-mark2-v5](2026-09-29-nameplate-flat-standard-mark2-v5/README.md) |
| Face-up display cover and receiver | H2C | completed, task 1294550319; receiver supports trapped beneath wing pockets; cover retained for revised receiver | [2026-09-29-display-flat-wings-h2c-v1](2026-09-29-display-flat-wings-h2c-v1/README.md) |
| back-top | H2C | printing on H2C since 09-22; sliced from the 09-21 inputs, uniform 0.24 mm; back-top changed after it | [2026-09-21-enclosure-back-top-h2c-v2](2026-09-21-enclosure-back-top-h2c-v2/manifest.json) |
| display-cover | Mark2 | printed; 34 mm skirts, fits only the front-top printed 09-21 | [2026-09-22-display-cover-mark2-v4](2026-09-22-display-cover-mark2-v4/manifest.json) |
| display-cover reach trial | Mark2 | completed; shake retention failed, popped out intact, task 1289413482; +0.5 mm hook reach, 0.9 mm leaf inset; about 24 minutes | [2026-09-27-display-cover-reach-mark2-v11](2026-09-27-display-cover-reach-mark2-v11/README.md) |
| display-cover reach trial | H2C | completed; physical fit not yet assessed, task 1289418578; +1 mm hook reach, 0.9 mm leaf inset; about 24 minutes | [2026-09-27-display-cover-reach-h2c-v1](2026-09-27-display-cover-reach-h2c-v1/README.md) |
| display-cover retention trial | Mark2 | completed, task 1289548468; shake test passes; very small bow when engaged; 3.6 mm hooks, 75 mm leaves | [2026-09-28-display-cover-retention-mark2-v12](2026-09-28-display-cover-retention-mark2-v12/README.md) |
| display receiver retention trial | H2C | completed, task 1289537122; no remaining HMS; matching receiver passes shake test with cover; retained for arm-reach trials | [2026-09-28-display-receiver-retention-h2c-v2](2026-09-28-display-receiver-retention-h2c-v2/README.md) |
| display-cover reach 0.75 mm | H2C | completed, task `1291079562`; selected fit: clean snap, no noticeable bow, shake test passes; same receiver | [2026-09-28-display-cover-retention-reach-h2c-v2](2026-09-28-display-cover-retention-reach-h2c-v2/README.md) |
| display receiver trial | Mark2 | completed, task 1282488338; full-width coupon for the existing 1.2 mm-inset cover, revised catches and flex lanes; 2 h 42 min | [2026-09-25-display-receiver-trial-mark2-v1](2026-09-25-display-receiver-trial-mark2-v1/README.md) |
| foam-cap-lid-top | Mark2 | reviewed, not sent | [2026-09-21-g-ganen-foam-cap-lid-top-mark2-v2](2026-09-21-g-ganen-foam-cap-lid-top-mark2-v2/manifest.json) |
| front-bottom | H2C | completed, task 1279923918; complete 0.08 mm handhold rounds and flute run-outs; six walls through downward curves only; original order and speeds; rounded faces unsupported | [2026-09-24-enclosure-front-bottom-h2c-v7](2026-09-24-enclosure-front-bottom-h2c-v7/manifest.json) |
| front-top | H2C | printing since 09-23, task 1277245499; emitted 0.08 mm wall layers cover the complete R6 roof side and corner curves and R18 roof arc | [2026-09-23-enclosure-front-top-h2c-v13](2026-09-23-enclosure-front-top-h2c-v13/manifest.json) |
| pump-cartridge | Mark2 | printing since 09-24, task 1279835918; complete 0.08 mm grip rounds, six walls only in upper grip band, original order and speeds; rounded surfaces unsupported, flat ceilings and cap seats supported | [2026-09-24-pump-cartridge-cap-mark2-v8](2026-09-24-pump-cartridge-cap-mark2-v8/manifest.json) |
| tee-carrier | Mark2 | completed; physical result rejected, task 1278660260; fan-off trial has inward edge retreat, unsupported strands and eventual recovery from the interior | [2026-09-24-tee-carrier-plate-mark2-v12](2026-09-24-tee-carrier-plate-mark2-v12/manifest.json) |
| tee-carrier | Mark2 | stopped by Derek after renewed edge failure, task 1279237907; failures lie between infill contacts; actual failure layer unknown | [2026-09-24-tee-carrier-plate-mark2-v13](2026-09-24-tee-carrier-plate-mark2-v13/manifest.json) |
| tee-carrier | Mark2 | prepared, not sent; six walls only at Z 0–6.1 mm, original wall-first order, speeds and 15% overlap; physical result untested | [2026-09-24-tee-carrier-plate-mark2-v15](2026-09-24-tee-carrier-plate-mark2-v15/manifest.json) |

Reviews retired from this folder, and their rows here, are in git at aab7f24fec.

The two current Mark2 mounting plates use the shared 7 mm G Ganen feet and corrected screw stations. The shell archives retain their complete native/support reviews; back-top additionally has a native-equivalence proof for its numerical mesh variation. Physical support cleanup and assembled fit are observations from the full enclosure trial.
