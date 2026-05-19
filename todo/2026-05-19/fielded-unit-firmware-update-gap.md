# Fielded-unit firmware-update gap

*Hourly-todo-filler agent, 2026-05-19. Focused recommendation; not a commitment.*

---

## Summary

Founder Edition is 50 units, hand-built over ~4 years, expected to live in customers' kitchens for 10 years. The firmware running each unit is non-trivial — three MCUs (ESP32-DevKitC main, ESP32-S3 config display, RP2040 round display), ~3.8k lines just in [`firmware/src/main.cpp`](firmware/src/main.cpp), with safety-critical setpoints (compressor min-off-time, freeze-protect cutoff, refill interlock during dispense) that we will absolutely revise as field data comes in.

There is no plan for getting updated firmware onto a shipped unit. [`hardware/assembly/firmware-and-commissioning.md`](hardware/assembly/firmware-and-commissioning.md) explicitly punts:

> Not in scope: … the over-the-air firmware-update flow (not in scope for first-unit shipping).

The partition tables can't even do safe A/B OTA today — [`firmware/partitions_esp32.csv`](firmware/partitions_esp32.csv) and [`firmware/partitions_s3.csv`](firmware/partitions_s3.csv) both define an `otadata` partition and an `app0` (`ota_0`) slot, but no `ota_1`. ESP-IDF / Arduino OTA refuses to write without a second slot, because rollback is impossible. No WiFi, MQTT, HTTPS, ArduinoOTA, esp_https_ota, or signing-key infrastructure exists anywhere under [`firmware/`](firmware/). The web service ([`web/server.js`](web/server.js), [`web/lib/`](web/lib/)) handles push notifications, the marketing site, and the build-log viewer; no firmware-manifest, no per-unit version pinning, no rollout cohort.

This is a real gap. The Founder Edition story — "hand-built by Derek, I will personally support your unit" — collapses the moment a bug ships and the only remediation is "fly out and reflash three USB ports under the customer's sink, two of which are buried behind valves, and one of which requires disconnecting a UART JST to even enumerate." That's the literal Step 5 of [`firmware-and-commissioning.md`](hardware/assembly/firmware-and-commissioning.md): the RP2040 won't enter BOOTSEL while the ESP32 UART is connected.

---

## Why this is worth addressing now, not after first ship

A bug discovered in unit #001 after delivery affects every unit shipped so far. With a 4-year run at ~12 units/year, the cumulative count of in-field units grows linearly — but the cumulative *firmware bugs the field will encounter* grows roughly as time × units, which is quadratic. The window where "I'll just drive to their house" is workable is the first 3–5 units. By unit #15 it's a real expense. By unit #50 it's untenable and we're either bricking customer trust or replicating a fleet-management capability under pressure.

The Founder Edition is also when the safety-critical firmware logic is youngest and most likely to need revision. Freeze-protect cutoff, compressor min-off-time, refill-during-dispense interlock, MQ-6 hydrocarbon-sensor response, backflow drip-pan moisture alarm — these are described in [`hardware/future.md`](hardware/future.md) and will get tuned as units accumulate operating hours. Tuning isn't a future *want*; it's a structural feature of the product's first 4 years. We need a path to ship those tunings without a service truck.

There is a separate, weaker form of "ship updates" already implied by the architecture: an iOS/Android app at install handles WiFi credentials, cloud pairing, and per-customer ratio tuning ([`firmware-and-commissioning.md`](hardware/assembly/firmware-and-commissioning.md) §Scope). That gets configuration onto the unit. It does not get *firmware* onto the unit.

---

## Where the gaps actually are

### 1. Partition tables don't support safe OTA

[`firmware/partitions_esp32.csv`](firmware/partitions_esp32.csv) and [`firmware/partitions_s3.csv`](firmware/partitions_s3.csv) both have:

```
otadata,  data, ota
app0,     app,  ota_0
spiffs,   data, spiffs
```

A working OTA partition table requires `app0 (ota_0)` *and* `app1 (ota_1)`, both sized to hold a full firmware image, plus the otadata. The current layouts give the entire post-otadata flash to a single app slot plus LittleFS. We get more LittleFS room and more app size — at the cost of being unable to atomically swap firmware. ESP-IDF refuses to write into a non-existent partition; ArduinoOTA throws on init.

This is a one-time partition-layout decision with material implications:
- Main ESP32 is on `esp32dev` (4 MB flash). Two ~1.5 MB app slots + otadata + a smaller LittleFS (currently 3.5 MB; would shrink to ~0.5–1 MB) is feasible if we move the embedded `factory_manifest.json` and image store off LittleFS and back into the firmware binary, *or* if we accept a smaller LittleFS. The image store is the constraint — `RP2040_IMAGE_BYTES = 128 × 115 × 2 = 29440` per flavor, plus the S3 images — fits in 0.5 MB.
- ESP32-S3 is on `esp32-s3-devkitc1-n8r8` (8 MB flash, 8 MB PSRAM). Plenty of room for dual 2 MB app slots and a 3 MB LittleFS.
- RP2040 has no built-in OTA. It has a 2 MB flash, a 1.5 MB filesystem allocation, and is reflashed via USB or via an ESP32-acting-as-host SWD/UART pathway. There's no analogue of `otadata`.

**Recommendation:** before unit #003 ships, lock in dual-slot partition tables for both ESP32s, and write a one-page decision doc on the RP2040 update path (options enumerated below in §3).

### 2. No transport, no signing, no manifest

No WiFi credentials provisioning, no HTTPS client, no MQTT, no certificate pinning, no manifest endpoint, no image-signing key in any state — committed, gitignored, or in a password manager.

For 50 units at $7,500 with safety-critical firmware controlling a 90 PSI vessel and a 120 VAC compressor, unsigned OTA is not acceptable. A compromised image — or just a botched build — that opens the dispense valve, energizes the compressor with no minimum off-time, or disables freeze-protect, has physical-world consequences. ESP32 Secure Boot + Flash Encryption is the textbook answer but it is a one-way door (efuses, key burning, no recovery). The lower bar is *signed manifests + signed images verified in software at boot*, which is reversible and still raises the bar materially above "anyone who phishes a Cloudflare token can push code to 50 kitchens."

**Recommendation:** specify, before first OTA-capable unit ships:
- Signing key location, custody, rotation policy. Today there is no signing key. Generate one offline, store in 1Password + a paper backup in a fireproof box, do not commit the private key, do not store it on the build host.
- Manifest format: signed JSON with `firmware_version`, `image_sha256`, `image_url`, `min_compatible_hw_revision`, `cohort` (canary / standard / pinned), `release_notes_url`, `signed_at`, `signed_by`.
- Manifest endpoint: under `homesodamachine.com/fw/manifest.json` (or per-MCU: `/fw/esp32_main.json`, `/fw/esp32_s3.json`, `/fw/rp2040.json`). Served by the existing Express app, no new infrastructure.
- Verification at the device: SHA-256 of the downloaded image, ed25519 verify of the manifest, refuse to write the inactive slot if either fails, refuse to switch to the new slot at boot if the new slot's image hash doesn't match the manifest.

### 3. Three MCUs, three different update mechanisms

The product has three independently-flashable MCUs ([`platformio.ini`](platformio.ini) envs `esp32dev`, `rp2040_display`, `esp32s3_config`). An OTA story has to cover all three:

- **ESP32-DevKitC main controller.** Has WiFi (once provisioned), has flash space for dual slots if we trim LittleFS. Standard `esp_https_ota` pattern works. This is the easy one.

- **ESP32-S3 config display.** Has WiFi, has a USB-CDC port that BLE/NimBLE already uses for the iOS app pairing flow. Two paths: (a) it does its own OTA over WiFi pulled from the same manifest endpoint, or (b) the main ESP32 acts as host and pushes the image to the S3 over the existing UART link. Option (a) is simpler if both MCUs are on the customer's WiFi, but doubles the WiFi-credential propagation surface. Option (b) keeps the S3 off-network and treats the main ESP32 as the single network endpoint — better security posture, more firmware to write.

- **RP2040 round display.** No built-in WiFi, no native OTA. Updated today via USB-BOOTSEL after disconnecting the UART JST ([`firmware-and-commissioning.md`](hardware/assembly/firmware-and-commissioning.md) §5). Options:
  - **Picotool over UART from ESP32 main.** RP2040 supports `picoboot` USB and `picotool` host-mode reflash, but does *not* expose a UART bootloader by default. Would require a custom bootloader pinned in the RP2040's flash that listens on UART for a firmware blob from the ESP32 main and writes it. Non-trivial to get right, especially on power-fail mid-write.
  - **Hardware solution: SWD link from ESP32 main to RP2040.** Add two GPIO lines (SWCLK, SWDIO), wire to the RP2040 SWD pads. The ESP32 main bit-bangs SWD and reflashes the RP2040 from a binary held in its own LittleFS. Requires a board respin or a small flying-lead retrofit on existing units. Cleanest long-term answer.
  - **Punt the RP2040.** The round display is logos + flavor indication; its firmware is the least-likely-to-change of the three. Accept that an RP2040 update requires a service visit (or shipping a USB stick to the customer with a how-to video) and design accordingly.

**Recommendation:** before unit #003 ships, write a one-pager — call it `hardware/assembly/firmware-update-architecture.md` — that picks one path per MCU and locks it in. Punting the RP2040 is acceptable if it's an explicit decision with a documented mean-time-to-firmware-change for that MCU. Drift-by-default is what bites us in year 3.

### 4. Update orchestration across the three MCUs

Even with the per-MCU mechanism solved, *ordering* matters:

- Main ESP32 controls compressor and valves. An interruption mid-update that leaves the main MCU in a half-state is the worst case — could leave the compressor stuck on, or freeze-protect disabled. Update the main MCU only when the compressor has been off for ≥3 minutes (the existing min-off-time), all valves are confirmed closed, the carbonator is not in a refill cycle, and the user isn't actively dispensing. A "safe-to-update" precondition check, run on the device, that holds the update until the unit is genuinely idle.
- Config display and round display can update almost any time, but should not update while the main MCU is updating (the UART link goes down during the main MCU's reboot).
- The firmware updates of the three MCUs are not independent — the main ESP32 talks to the S3 via WiFi/BLE-paired-app and to the RP2040 via UART. Version compatibility between MCUs (proto_msg, proto_link in [`firmware/src/main.cpp`](firmware/src/main.cpp:8)) needs an explicit compatibility matrix, or every update is a coordinated three-image release.

**Recommendation:** the manifest format should include a `min_compatible_versions` map keyed by MCU, so the device refuses an upgrade that would orphan one of its peers.

### 5. Telemetry / "is the field broken?"

No way to learn — short of a customer phone call — that a unit's firmware is misbehaving. The reed-switch level-sensor architecture, the DS18B20 freeze-protect probe, the MQ-6 hydrocarbon sensor, the backflow drip-pan moisture sensor, and the audible alarm logic in [`hardware/future.md`](hardware/future.md) all log locally. If a unit's compressor is short-cycling, we won't know until the customer notices an electricity-bill spike or the unit fails. With 50 units in 50 kitchens and a one-person factory, latent-defect discovery is the bottleneck on iteration.

The web service already has push-notification plumbing ([`web/lib/push.js`](web/lib/push.js)) for the dev-log feed. Reusing the same Express server to accept a small periodic device telemetry POST — boot count, last 24h compressor runtime, last 24h dispense count, current firmware version per MCU, any alarm flags — costs little and creates the dataset that tells us *when to push* a firmware update and to *which units*.

**Recommendation:** a `/api/units/:serial/heartbeat` endpoint accepting a small signed JSON blob once an hour from each unit. Stored in the existing pg pool (which already has the `subscribers` table). The founder gets a dashboard at `homesodamachine.com/fleet` of all 50 units. This is one afternoon of Express work and pays back the first time a customer says "it just hums sometimes" and we can look at their cycle data without asking them to describe it.

### 6. Rollback and bricking

Currently zero rollback support — there's only one app slot. Even with dual-slot OTA, the boot logic has to handle "new image boots once, hangs, watchdog reboots, fall back to old slot." ESP-IDF supports this natively (`esp_ota_mark_app_valid_cancel_rollback`) but it has to be wired in: the firmware must, after some minimum runtime where it's exercised the safety-critical paths, explicitly mark itself as good, otherwise the next reboot reverts.

The "minimum runtime where it's exercised the safety-critical paths" is non-trivial to define. A unit that doesn't dispense for 6 hours after an update isn't exercising the safety paths. A unit that the customer is on vacation from for 2 weeks would revert. Probably the right pattern is: mark good after N successful reboots *or* after the first successful dispense + compressor cycle + freeze-protect transition, whichever comes first.

**Recommendation:** the boot-validation gate is a first-class design problem, not an afterthought. Spec it before the first OTA-capable build.

### 7. User-visible UX during update

The unit lives under a sink. The customer doesn't see it during normal use. If an update is happening, the *only* user-visible surface is the RP2040 round display above the counter (currently shows the active flavor logo). The ESP32-S3 config display is on the cabinet door interior — only seen when the customer opens the cabinet.

A bad outcome: customer turns the handle mid-update, nothing happens, customer doesn't know why. A good outcome: round display briefly shows "updating," dispense is blocked with a brief and obvious indication on the round display, post-update the round display goes back to the flavor logo.

**Recommendation:** define the in-update visual state for both displays before any OTA ships. Include this in the round-display image set so it's not a runtime composite.

### 8. Safety-critical update changes need a heavier gate

Most firmware changes are minor — image tweaks, log strings, UI polish, dispense-pulse-counting bug fixes. A small fraction will change a setpoint that has real-world consequences: freeze-protect cutoff, compressor min-off-time, refill interlock, PRV pressure check, MQ-6 alarm threshold. Those changes should require a heavier process — second pair of eyes, dry-run on a bench unit for at least one full diurnal cycle, staged rollout (push to one canary unit first, then 10%, then 100%), and explicit release-note flagging.

**Recommendation:** the manifest schema includes a `safety_class` field — `cosmetic` / `functional` / `safety-critical`. The device respects the rollout cohort embedded in the manifest. Today, with 50 units, this can be a literal hand-edited JSON file with explicit serial-number allow-lists per release; tooling can grow if the unit count grows.

---

## What to do, in priority order

1. **Decide if OTA is in or out for the first 10 units.** "Out" is a defensible answer — ring 1 in the rings-of-trust model is 10 units to friends-and-family, and for those 10 a service-truck reflash is fine. The decision should be explicit, written down, and revisited before ring 2.

2. **If OTA is in: fix the partition tables before any unit ships.** This is reversible *for unit #001 today* and irreversible *for any unit already in a customer's kitchen*. The partition layout is baked into the factory firmware image at flash time. A unit shipped with a single-slot partition table cannot be retrofitted to dual-slot over the air — by definition. Decide now or accept never.

3. **Specify the firmware-update architecture in one page.** Pick the per-MCU mechanism, pick the signing scheme, pick the manifest schema, pick the rollback policy, pick the UX. Land it as `hardware/assembly/firmware-update-architecture.md` referencing [`firmware-and-commissioning.md`](hardware/assembly/firmware-and-commissioning.md).

4. **Add a heartbeat endpoint to the web service and a heartbeat sender to the ESP32 main.** This is the single highest-leverage piece of work in this whole gap. It doesn't require deciding OTA architecture; it works even if OTA stays out forever. It tells the founder what's happening in customer kitchens. One afternoon of work.

5. **Document the manual reflash procedure for the first 10 units explicitly.** Even with no OTA, the founder needs a procedure for "I'm at the customer's house, I need to reflash" — including the USB cables, the UART disconnect, the order of operations, and a sanity-check script. Right now this lives in [`firmware-and-commissioning.md`](hardware/assembly/firmware-and-commissioning.md) but as a *factory* procedure, not a *field* procedure. The two have different prerequisites (the field version assumes water and CO2 are connected, the factory version doesn't).

---

## What I considered and decided not to recommend

- **ESP32 Secure Boot + Flash Encryption.** Right answer at scale, wrong answer at 50 units. The efuse-burning step is irreversible per-MCU. If we burn keys on unit #003 and then learn at unit #007 that the key custody process has a flaw, units #003–#006 are stuck with the bad key. Signed manifests + software signature verification is the appropriate trust level for Founder Edition and stays appropriate well into Standard Edition.

- **MQTT or a "real" fleet-management tool (Balena, Memfault).** Useful at hundreds of units. Overkill at 50. Plain HTTPS POST to an Express endpoint with the existing pg pool is right-sized. Revisit at Standard Edition.

- **Tying firmware updates to the per-unit portal (`/u/NNN`).** Tempting — the portal already exists in concept. But the per-unit portal is a *customer-facing* surface, and firmware-update orchestration is an *engineering* surface. Keeping them separate avoids leaking implementation detail to a marketing artifact.

- **Sidecar update via SD card.** Some appliances ship updates as files on a USB stick. The cabinet location and the three-MCU split make this strictly worse than WiFi OTA. Ruled out.

---

## Acceptance criteria, if someone picks this up

A reader of this todo, in priority order:

1. Adds a "firmware update strategy" line to [`hardware/assembly/firmware-and-commissioning.md`](hardware/assembly/firmware-and-commissioning.md) §Scope §"Not in scope" that points either to a written decision ("out for first N units, revisit at unit N+1") or to a new `hardware/assembly/firmware-update-architecture.md`.

2. If OTA is in: lands a dual-slot partition table in [`firmware/partitions_esp32.csv`](firmware/partitions_esp32.csv) and [`firmware/partitions_s3.csv`](firmware/partitions_s3.csv), tests that the existing main.cpp + LittleFS image store still fits, and commits the new layout with a comment pointing back to this decision.

3. Stands up the heartbeat endpoint regardless of OTA decision. Smallest possible scope: one POST endpoint, one DB table, one push notification rule for "no heartbeat in 24h."

4. Writes the field-reflash procedure as a peer to [`firmware-and-commissioning.md`](hardware/assembly/firmware-and-commissioning.md), capturing the under-sink reality (cable lengths, UART JST access, photo of where the USB ports physically are with the back panel attached).

None of these need to happen this week. All of them need to happen before the unit count in customer kitchens exceeds the founder's bandwidth for service visits — which, given solo build capacity of ~12 units/year, is somewhere between unit #5 and unit #15.
