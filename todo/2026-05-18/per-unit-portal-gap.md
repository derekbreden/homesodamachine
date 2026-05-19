# Per-unit portal: the QR code commits to a URL that has no destination

**Author:** hourly agent, 2026-05-18
**Status:** recommendation only — not for direct execution
**Audience:** future agents, Derek
**Siblings today:**
- [co2-supply-ownership-gap.md](co2-supply-ownership-gap.md) — post-delivery consumable supply (CO2)
- [firmware-manifold-gap.md](firmware-manifold-gap.md) — pre-delivery firmware/hardware build readiness

This todo is distinct from both: it is the **customer-facing software service** that the physical plaque commits us to, with no implementation and no specification today.

## TL;DR

[printed-parts/enclosure/nameplate/README.md](../../hardware/printed-parts/enclosure/nameplate/README.md) describes a plaque physically bonded to every Founder Edition unit that carries a QR code rendered against `homesodamachine.com/u/NNN` (zero-padded, `001`..`050`). The plaque is laser-engraved or two-color-inlay 3D-printed — once shipped, the URL is **permanent** on the artifact.

The nameplate doc explicitly defers what that URL resolves to:

> Per-unit QR code + serialization. ... What that URL resolves to is a future customer-portal decision — the QR is the binding, and the destination can evolve without changing the physical plaque.
> — [nameplate/README.md:13](../../hardware/printed-parts/enclosure/nameplate/README.md)

That is correct in principle. It is also a Ring 1 readiness gap, because:

1. **There is no `/u/:n` route in the web service today.** [web/server.js:251–258](../../web/server.js) mounts viewer, blog, push, notifications, firebase-config, landing, viewer-pages, settings. Nothing handles `/u/NNN`. The first customer who scans their plaque QR today gets the Express 404 page.
2. **There is no design for what the page shows.** No spec, no template, no fixture data. The plaque is being generated against a URL we have not staffed.
3. **There is no decision on what unit-portal data is public vs. private.** `/u/003` is guessable (the run is 001..050). Without a policy, the URL leaks whatever it shows to anyone who iterates the namespace — which today is "nothing," which is also a problem.
4. **There is no long-term domain commitment plan.** The plaque outlives any single year of registrar fees. `homesodamachine.com` becoming a parked / squatter / unrelated page in 2031 would brick the QR on units 001–050 forever, and there is nothing in the repo today acknowledging that.

The plaque is currently held up on multiple other open items (signature workflow, mounting interface, generator script — see [nameplate/README.md "Open items"](../../hardware/printed-parts/enclosure/nameplate/README.md)). So no live plaque has shipped yet, and there is time to fix this — but the order of operations matters: **the URL contract must be decided before the first plaque prints**, because the QR data is what locks it in.

## Why this matters at Founder Edition specifically

[target-market.md:256–262](../../marketing/target-market.md):

> At Founder Edition scale, the answer to "is this a real product?" is not a brand — it's Derek. His face, his kitchen, his story. ... The first 50 buyers are buying from a person they've come to trust, not from a company.

The plaque is the **first moment after delivery** that translates the founder-as-brand promise into something the customer can touch and verify. The flow Derek presumably wants:

1. Customer's unit arrives. The shipping email (per [finish-pack-ship.md:140](../../hardware/assembly/finish-pack-ship.md)) was sent personally from `derek@homesodamachine.com` with the rear-panel photo of the unit's plaque.
2. Customer unboxes, sees the signed plaque, scans the QR with their phone.
3. They land on a page that says, in effect: *"This is unit 003 of 050. I built this on March 14, 2026, on the bench in Lincoln. I tested it for 72 hours of burn-in (here are the readings). Here's a 90-second video of me explaining what to do in the first hour. Here's how to text me if anything is off. Thank you."*

If step 3 is a 404 (or the landing page, or something generic), the trust the plaque was building is reversed in the moment the customer first tries to claim it.

This is not a hypothetical — it is what the trust-gap section of target-market.md explicitly bets on. The QR is one of two physical artifacts that survive the unboxing (the other is the appliance itself). It deserves to land somewhere worth the scan.

## What's already locked in by upstream docs

Useful constraints to design against rather than re-litigate:

- **URL shape is fixed:** `https://homesodamachine.com/u/NNN` where `NNN` is the zero-padded unit number — [nameplate/README.md:13,39,56](../../hardware/printed-parts/enclosure/nameplate/README.md). Not `/units/`, not `/serial/`, not with a path token. The QR encodes exactly this and the printed text under it shows exactly this.
- **Serial format is fixed:** `SFI1-FE-NNN` — [nameplate/README.md:33–35](../../hardware/printed-parts/enclosure/nameplate/README.md), [finish-pack-ship.md:66](../../hardware/assembly/finish-pack-ship.md). The `SFI1` is the model, `FE` is Founder Edition, `NNN` is the unit number. The serial is on the plaque text; the URL only carries the unit number.
- **There is a per-serial archive directory:** `logs/<serial>/` with sub-folders `burn-in/`, `finish/`, etc. — [finish-pack-ship.md:9,98,100](../../hardware/assembly/finish-pack-ship.md). This is the local-only record today, and [finish-pack-ship.md:100](../../hardware/assembly/finish-pack-ship.md) flags the open question: *whether this archive ships with the appliance, QR-links into the cloud, or stays at the factory* is unresolved.
- **No customer accounts, no auth, no sessions:** [web/README.md:152](../../web/README.md). The site identifies a "user" only by FCM push token on devices that opted in. Any portal design has to live inside this model or extend it consciously.
- **The plaque QR cannot be revoked or rotated.** This is the single most important fact. Whatever scheme is chosen must survive the entire service life of unit 001.

## Specific gaps, sized for follow-up tickets

### U1 — Decide the URL semantics: public, tokened, or owner-bound (doc-only, do first)

The choice between three patterns has to be made before any plaque is printed:

- **Public** — `/u/003` returns the same page to everyone. Public-ish info only (model, build month, founder's general greeting, install-guide pointers, "this is a real unit" attestation). No customer name, no telemetry, no support thread.
- **Token-in-URL** — `/u/003?k=xxxxxxxx` where `k` is a per-unit secret generated at print time and embedded in the QR data. The plaque's *visible* text still reads `homesodamachine.com/u/003`, but the QR payload includes the token. A bare `/u/003` (typed in, or scanned from a photo) gets the public page; the full URL with the token gets the owner page.
- **Owner-bound by first-scan** — `/u/003` is public until the first FCM token registers against it through the page itself, then that token "owns" the unit. Simpler than token-in-URL, but vulnerable to a stranger scanning the plaque in a Reddit photo before the actual buyer plugs it in.

**Recommendation: token-in-URL with public fallback.** The plaque QR already encodes opaque data — the human-readable URL is on the plaque face, the QR can carry a longer string. A 32-bit token per unit is plenty (4 billion values, 50 units, collision probability is negligible). A bare `/u/003` typed by hand returns the public attestation page; a scanned QR carries the customer to their owner page in the same URL family. The plaque visible text is unchanged.

This decision affects the [generator](../../hardware/printed-parts/enclosure/nameplate/README.md) (`generate_step_cadquery.py` would need a per-unit token list as input), the [finish-pack-ship](../../hardware/assembly/finish-pack-ship.md) bench (the bench operator confirms the QR scans to the same token recorded in the per-serial archive), and the web route handler. Decide once, document, move on.

Estimated effort: ~2 hours of writing + decision capture.

### U2 — Build the public `/u/:n` route

Minimum-viable content for the public page (anyone, no auth, no token):

- **Identity attestation.** "This is unit 003 of 050 — Home Soda Machine SFI-1, Founder Edition." Confirms the plaque matches a real run.
- **Build provenance.** Build month (not exact date — privacy hedge), signature presence ("hand-signed by Derek B"), burn-in pass attestation. Pulled from the per-serial archive (see U4).
- **Founder voice.** One paragraph from Derek written in first person. Same paragraph for every unit at Ring 1 — personalization comes through the owner page (U3), not here. This is the "yes, a person built this" page for anyone in the world, including the customer's spouse looking over their shoulder.
- **Pointers.** Install guide, support contact (`derek@homesodamachine.com` + phone), one-line "if this is your unit, scan the QR on the plaque with your phone to see your unit's data."
- **No telemetry, no PII, no order info.** Anything sensitive lives behind the token (U3).

Implementation: new `lib/units.js` with `mountUnitRoutes(app, { unitsDir })`, mounted in `server.js` per the [web/README.md "Where things go"](../../web/README.md) pattern. Unit data lives as JSON or markdown under `web/data/units/NNN.json` (or under `logs/<serial>/` and read by the server — there's a coupling question to settle, see U4).

Add to `tests/smoke.test.js` so a 404 regression on `/u/003` blocks deploys, since unlike the rest of the site, this is a contract with the customer's physical hardware.

Estimated effort: ~1 day, including a basic template that visually matches the rest of the site.

### U3 — Owner page (token-gated)

This is where it gets interesting. With a per-unit token (U1), the owner page can show:

- **Customer's name and address on file**, with the message "if this is wrong, here's how to fix it" — Ring 1 customers will care that the unit recognizes them.
- **The unit's photo at ship-time** ([finish-pack-ship.md:91–98](../../hardware/assembly/finish-pack-ship.md) already specifies that this photo gets archived under `logs/<serial>/finish/`). The customer sees "this is what your unit looked like when it left the bench."
- **Burn-in readings.** Per-serial test logs ([finish-pack-ship.md:9](../../hardware/assembly/finish-pack-ship.md)). "Your unit ran 72 hours, here's the temperature curve, here's the pour count, here's why we shipped it."
- **A personal note from Derek**, written per-unit at finish-pack-ship time. Three or four sentences. This is what "hand-built" means in writing form.
- **Future doorways.** "Order a refill kit" (ties to the [CO2 sibling todo's C5/C6](co2-supply-ownership-gap.md)), "current CO2 level" (ties to [CO2 todo's C3](co2-supply-ownership-gap.md)), "log a support ticket," "your unit's telemetry" — none of which need to *work* at Ring 1, but the page is where they will live, so the layout should leave room.

This page is also where the FCM push token can be registered as "owner of unit 003" — the bridge between "physically holds this plaque" and "gets notifications about this unit."

Estimated effort: ~2 days for a Ring 1 version with placeholder doorways. The placeholders are deliberate — they tell the customer what's coming without overcommitting.

### U4 — Resolve the `logs/<serial>/` ↔ `web/` coupling

[finish-pack-ship.md:100](../../hardware/assembly/finish-pack-ship.md) explicitly leaves this open:

> Whether the per-serial archive ships with the appliance (USB stick in the box, QR-linked cloud archive at `homesodamachine.com/u/NNN`, both), stays at the factory only, or some split is an Open item.

The /u/NNN page is exactly the resolution mechanism for that open item — if the cloud archive exists, this is where it lives. But the coupling has a direction question:

- **Push from logs/** — finish-pack-ship bench publishes a curated subset of `logs/<serial>/` into `web/data/units/NNN/` at ship time. Pro: factory-controlled, version-able in git. Con: needs a publish step the bench operator can't forget.
- **Pull from logs/** — `lib/units.js` reads `logs/<serial>/` directly at request time. Pro: nothing to forget. Con: ties prod-web to a directory whose schema is currently undocumented, exposes accidentally-saved sensitive data if someone drops a debug file in the wrong place.

Recommendation: **push, with a manifest**. A `logs/<serial>/portal.json` written at the finish-pack-ship bench is the only file the web service reads. Everything else under `logs/<serial>/` stays factory-only. The bench step is one new line in [finish-pack-ship.md](../../hardware/assembly/finish-pack-ship.md) — "generate portal.json from the run log." The web side reads exactly that one file per unit and renders against its schema. Decoupled, auditable, and there's a clear "what does the customer see" file the founder can review before ship.

This is the part of U2/U3 that should be designed first because it determines the data contract everything downstream renders against.

### U5 — The forever-URL problem: domain ownership and the redirect plan

The plaque is a 5-year-DOT-recertifiable, multi-decade artifact. The QR is a 10-second photo away from being decoded at any point in that life. The URL has to keep working.

Things that should exist in the repo today and don't:

- **A multi-year domain registration commitment.** Renew `homesodamachine.com` to the maximum the registrar allows (typically 10 years at most), then set up annual auto-renew with two paid contacts. The marginal cost is ~$15/year and the failure mode is catastrophic and irreversible.
- **A registrar-level lock + transfer-lock.** Standard. Document who has access to the registrar account, and where that recovery email lives.
- **A documented succession plan in case Derek is unavailable.** The Founder Edition story is explicitly that "the brand is a person." The URL is a 50-unit contract that survives the person. A bus-factor doc — even a one-pager — naming who keeps the domain alive and what they do with the site if the founder steps away, is a real Founder Edition deliverable, not a vanity exercise. (This is sensitive enough that the doc might live outside the public repo, but its *existence* should be flagged.)
- **A redirect fallback at the QR level.** If the canonical domain ever has to change, the QR is locked to `homesodamachine.com/u/NNN`. The mitigation is that *whoever owns `homesodamachine.com` next* points it at the successor. This is a property of the domain registration, not of the page design — but it's worth being explicit about.

Out of scope for the immediate Ring 1 build but absolutely in scope before the first plaque prints.

### U6 — Privacy: what the URL must NOT leak

`/u/003` is guessable. A scraper can iterate 001 through 050 trivially. The public page (U2) is fine — it's designed for that. But:

- The **token-bound owner page** (U3) leaks if there's any side-channel that confirms a token without showing it (e.g., a `404` on a bad token vs. `200` with a "no owner registered" page). All three responses must be indistinguishable in size/timing/structure to a casual scraper. This is solvable with a uniform "unit page" template that conditionally hides the owner pane.
- The **per-serial photo** archived at finish-pack-ship time could accidentally include workspace details (faces, addresses, other-unit serials). The bench procedure should specify "rear-panel framing only, no incidental capture" — a one-line addition to [finish-pack-ship.md "5. Photograph"](../../hardware/assembly/finish-pack-ship.md) closes this.
- The **customer's name** should never appear on the public page — only the owner page. Same goes for shipping city/state.
- The **telemetry curve** is mostly innocuous but reveals when the household is awake / dispensing / out of town. The owner page is the right surface; embedding it in the public page would be a privacy hole.

Estimated effort: ~half a day of doc work + a 2-hour timing-attack check on the route handler.

### U7 — App store / push integration with the owner page

The iOS / Android apps and FCM push infrastructure ([lib/push.js](../../web/lib/push.js), [web/README.md:152](../../web/README.md)) already use a token-bound identity model. The owner page is the natural place to bind "this FCM token owns unit 003" — scan the QR with your phone (FCM token in browser context), tap "this is my unit," done.

That's also how the [CO2 sibling's C3 monitoring](co2-supply-ownership-gap.md) notification path resolves: the pressure-drop event needs to know *who to notify*, and the answer is "the FCM tokens registered against the unit's owner page." Without this, the monitoring work has no audience.

Out of scope for the first /u/NNN landing, but the architectural decision in U1 (token-in-URL) is what makes it tractable later.

## Migration plan / order of operations

Same shape as the [CO2 sibling](co2-supply-ownership-gap.md) — order matters, don't bundle:

1. **U1 + U5 today.** Document the URL-scheme decision and the domain-lifetime commitment. Both are doc + admin work, no code, but they have to land before generator changes or first plaque print. ~half a day.
2. **U4 next.** Design the `logs/<serial>/portal.json` contract. This is the spec that U2 and U3 render against. ~1 day with a worked example.
3. **U2 before the first plaque prints.** Public route. Skipping this means the first scanned QR is a 404, which is the failure mode this whole todo is preventing. ~1 day.
4. **U3 before unit #1 ships.** Owner page with placeholders for what's not built yet. The customer scans on day one; the page can be honest about "this section will populate when the CO2 sensor goes live in firmware vN." ~2 days.
5. **U6 (privacy review)** runs in parallel with U2/U3, not after. Easier to bake in than retrofit.
6. **U7 (push binding)** lands when the CO2 monitoring lands, not before. The "no audience" problem doesn't exist until there's something to notify about.

## Out of scope for this todo

- **The visual design** of the unit page. Layout, typography, hero photo treatment. The recommendation here is structural and content-level; making it look right is a separate, video-first design task that probably wants the founder's hands on it directly.
- **The Standard Edition variant.** [nameplate/README.md:15](../../hardware/printed-parts/enclosure/nameplate/README.md) defers Standard to a later revision. The URL contract probably differs ("unit 137 of an open run" is a different story than "unit 003 of 050"). Revisit when Founder Edition is committed-out.
- **Whether the plaque itself should change.** The Founder Edition QR is what it is. If a future audit of the plaque ever happens (signature workflow, mounting, etc.), the URL contract laid out here is the input, not an output to revisit.
- **App / iOS-side unit binding UX.** The Android port roadmap is in [docs/android-port-roadmap.md](../../docs/android-port-roadmap.md); the iOS app is separate. How an app deep-links a unit-scan into the owner page is a future ticket; the URL family designed in U1 is the substrate it builds on.
- **Telemetry storage architecture.** The CO2 sibling flags this as out of scope too. The owner page surfaces telemetry but does not define it.

## Suggested next concrete step

Write **U1** as a 1-page decision doc captured in `hardware/printed-parts/enclosure/nameplate/README.md` (extending the existing "Per-unit generation (planned)" section). It is the smallest artifact that unblocks the most: it gives the CadQuery generator the per-unit input shape it needs, it gives the finish-pack-ship bench an extra archive line, and it gives the web service a contract to implement against. Everything else in this todo cascades from it.
