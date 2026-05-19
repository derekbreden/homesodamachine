# Pepsi / Coca-Cola trademark usage and the "Home Soda Machine" mark: a brand-naming legal gap

**Author:** hourly agent, 2026-05-19
**Status:** recommendation only — not for direct execution
**Audience:** future agents, Derek
**Distinct from siblings 2026-05-18:** The six 2026-05-18 todos covered the post-sale customer experience (freight, CO2 supply, install consult, order/payment + FTC Mail Order Rule, per-unit portal, warranty/RMA). **This doc is about brand-name use itself — the legal posture of the marketing pitch "real Diet Mountain Dew on tap," the Pepsi/Coca-Cola brand bitmaps baked into the firmware, and the weakness of "Home Soda Machine" as the company's own mark.** No 2026-05-18 sibling touches Lanham Act trademark exposure, FTC endorsement-guide compliance, or USPTO registrability of the project's own brand assets.

---

## TL;DR

Five findings:

1. **The marketing message centers a registered third-party trademark.** [`marketing/target-market.md`](../../marketing/target-market.md) and [`marketing/video/concepts.md`](../../marketing/video/concepts.md) both put "Diet Mountain Dew pours from the faucet" at the top of the funnel. Diet Mountain Dew® is a registered PepsiCo trademark. The use is *nominative* — we are accurately describing what the customer pours from their own purchased PepsiCo concentrate — and is defensible under the *New Kids on the Block v. News America* nominative-fair-use test, but only if used carefully. **Today nothing in the repo names this doctrine or constrains the marketing copy accordingly.**

2. **The firmware ships Pepsi and Coca-Cola brand bitmaps as flavor logos.** [`firmware/src_config/main.cpp`](../../firmware/src_config/main.cpp) and [`firmware/src_display/main.cpp`](../../firmware/src_display/main.cpp) reference `flavor0_240` / `flavor1_240` / `flavor2_240` bitmaps with comments labeling them "Diet Wild Cherry Pepsi," "Diet Mountain Dew," and "Diet Coke." The 240×240 image data lives at [`firmware/src_config/images/flavor*_240.h`](../../firmware/src_config/images/) and [`firmware/src_display/flavor*_bitmap.h`](../../firmware/src_display/). **A bitmap of the Pepsi or Coca-Cola brand logo embedded in the product's display is a categorically harder trademark use than a marketing text reference — and the Diet Coke bitmap is present in firmware even though [`marketing/target-market.md`](../../marketing/target-market.md) does not list Diet Coke as a launch flavor.**

3. **The Steve Martin / *The Jerk* "He hates these cans" hook is being treated as free.** It is the marketing tagline in [`marketing/target-market.md`](../../marketing/target-market.md) Section "The market definition" and the closing card of the Tier-1 pour video in [`marketing/video/concepts.md`](../../marketing/video/concepts.md). The 1979 film *The Jerk* is owned by Universal. The line itself is a short cultural quotation (likely fair use as commentary), but the *Jerk* poster/clip/Steve Martin's likeness are not. **The line is probably fine; visual reuse of the film or Steve Martin imagery is not.**

4. **"Home Soda Machine" is descriptive-generic and almost certainly unregistrable on the USPTO Principal Register.** Three nouns describing the product literally. Trademark law treats "Home Soda Machine" the way it treats "Cold Soda Machine" or "Kitchen Beverage Maker" — fine as a common-law product descriptor, weak as a brand mark, unlikely to clear examination. The domain `homesodamachine.com` is similarly generic. **The "rings of trust" / artisan-founder positioning ([`target-market.md`](../../marketing/target-market.md) Section "The internal plan") rests heavily on the founder's *personal* brand, not a product brand — which is the correct positioning for a 50-unit run, but means the project should not be investing in defending the descriptive name as a trademark.**

5. **FTC Endorsement Guides (16 CFR Part 255) require disclosure of material connections — and the absence of a connection to PepsiCo is itself worth surfacing.** A 30-second video of "Diet Mountain Dew pouring from a home faucet" can readily be misread as an authorized partnership, a co-branded product, or a licensed sub-product. The FTC's Endorsement Guides do not technically require a non-endorsement disclaimer, but the same risk surface — consumer confusion about whether PepsiCo backs this — sits at the heart of a Lanham Act §43(a) **false-endorsement** claim, which is the most likely vector by which PepsiCo legal would land on this product.

This doc lays out the four named legal doctrines (Lanham Act §32, §43(a), nominative fair use, FTC endorsement guides), names where each one bites this project specifically, and recommends a concrete playbook: a one-page trademark policy in `business/`, a firmware-side change to neutralize the worst-case display bitmaps, and a marketing-copy guardrail document the founder can reference when writing the website and shooting video.

---

## What's actually unaddressed today

The repo's marketing documentation reads as if the legal status of the product's brand-name use is settled. It is not. Specifically:

- [`marketing/competitors/pepsi.md`](../../marketing/competitors/pepsi.md) covers PepsiCo as a competitor and supplier. The supply-chain risk section ("PepsiCo could notice our product and attempt to cut off supply (unlikely at current scale)") names the *commercial* risk but not the *legal* one. PepsiCo's first move on noticing this product is unlikely to be cutting off SodaStream concentrate at retail; it is much more likely to be a cease-and-desist over trademark use.
- [`marketing/target-market.md`](../../marketing/target-market.md) lines 23-27 and 246-254 commit the marketing to "He hates these cans!" — *The Jerk* reference — as the primary hook. No analysis of fair-use posture for the film reference.
- [`marketing/video/concepts.md`](../../marketing/video/concepts.md) Tier 1 specifies "Diet Mountain Dew pours into a glass with ice. Take a sip. End with 'He hates these cans' and a link." Two trademark uses + one film reference, no doctrinal posture.
- [`business/regulatory.md`](../../business/regulatory.md) covers EPA, UL, CPSC, SNAP, AIM. Says nothing about Lanham Act, FTC endorsement guides, or USPTO.
- [`business/incorporation.md`](../../business/incorporation.md) covers entity formation and federal income tax. Says nothing about brand-mark formation, trademark searches, or §43(a) exposure.
- The repo's own brand naming ("Home Soda Machine," `homesodamachine.com`) is treated as final without registrability analysis.

The gap is not theoretical: the firmware ships, today, with brand-logo bitmap files for PepsiCo and Coca-Cola products. Whoever produced those bitmaps either drew them from official brand assets (clear trademark use) or recreated them by hand (still trademark use of the mark's visual identity). The fact that this code path exists in `firmware/src_config/` — the WiFi/configurator firmware that talks to the customer's network and presumably the per-unit portal — means it ships on every unit.

---

## The four legal frames, in plain English

### Frame 1: Lanham Act §32 (15 U.S.C. §1114) — trademark infringement of registered marks

§32 makes it unlawful to use a registered mark "in commerce" in connection with goods or services in a way "likely to cause confusion, or to cause mistake, or to deceive."

Both **DIET MOUNTAIN DEW®** (USPTO Reg. No. 1,134,855 and others) and **DIET PEPSI®** are registered to PepsiCo. **DIET COKE®** is registered to The Coca-Cola Company. The "in commerce" element is met the moment we sell our product or run a paid ad. The whole §32 fight is about **likelihood of confusion** — the *Polaroid v. Polarad* / *AMF v. Sleekcraft* multi-factor test in the relevant Circuit.

**Where this bites:**

- A 30-second video captioned "Diet Mountain Dew on tap" without context can be (mis)read as a co-branded PepsiCo product. Consumer confusion about source = §32 exposure.
- A firmware-rendered Diet Mountain Dew logo on a 240×240 display embedded in the appliance's user interface is a much harder fact pattern than the marketing copy. It is the visual equivalent of co-branding. PepsiCo's quality-control argument ("we did not approve a Diet Mountain Dew display rendering at this resolution / color / animation") is straightforward.
- The Coca-Cola Diet Coke bitmap is *strictly worse*: we are not even selling a flavor of theirs, so we cannot raise the nominative-fair-use defense around accurately describing the customer's purchased product. The Diet Coke bitmap is just a Coca-Cola trademark used to seed a product UI — there is no commercial activity that requires it to be there.

### Frame 2: Lanham Act §43(a) (15 U.S.C. §1125(a)) — false endorsement / false association

§43(a) is broader than §32. It covers unregistered marks, false designations of origin, false endorsement, and false advertising. It is the statute under which a celebrity sues a company for using their image without permission, and the statute under which PepsiCo would most likely sue this project.

**Where this bites:**

- The "Diet Mountain Dew pours from the home faucet" video, even with no logo on screen, frames our appliance as the source of that flavor. A consumer can readily infer "this is a PepsiCo home product" without ever seeing a Pepsi logo. That inference is the §43(a) injury — *consumer is misled about whether PepsiCo endorses or partners with this product.*
- The Founder Edition plaque + `/u/NNN` per-unit URL ([`per-unit-portal-gap.md`](../2026-05-18/per-unit-portal-gap.md) sibling) is one more surface where brand-name use can create implied endorsement.

### Frame 3: Nominative fair use — *New Kids on the Block v. News America* and progeny

This is the project's actual defense, and it has teeth — but it has to be earned.

The Ninth Circuit's three-prong nominative-fair-use test ([*New Kids on the Block v. News America Publishing*, 971 F.2d 302 (9th Cir. 1992)](https://en.wikipedia.org/wiki/Nominative_use)):

1. **Necessity.** The product or service in question must be one not readily identifiable without use of the trademark. *(Met. There is no generic way to say "Diet Mountain Dew" — that is the name of the product PepsiCo sells. We cannot accurately describe what the customer is pouring without naming it.)*
2. **Minimum use.** Only so much of the mark may be used as is reasonably necessary to identify the product or service. *(Probably met for the **word mark** "Diet Mountain Dew." Almost certainly **not met** for the Diet Mountain Dew **logo** — color treatment, mountain-dew font, citrus-burst graphic — because the word mark alone identifies the product, the logo is extra.)*
3. **No implied endorsement.** The user must do nothing that would, in conjunction with the mark, suggest sponsorship or endorsement by the trademark holder. *(This is where the project is most exposed. Every video, every product surface, every web page that names "Diet Mountain Dew" without explicit non-endorsement framing edges toward implied endorsement.)*

The Third Circuit's parallel test from *Century 21 v. LendingTree*, 425 F.3d 211 (3d Cir. 2005), is similar but more demanding on prong 3 — it asks specifically about the **manner** of use. The Federal Circuit and Second Circuit treat nominative fair use as a factor inside the likelihood-of-confusion analysis rather than as a freestanding defense. **The defense is real but it is not automatic.**

The Supreme Court's *KP Permanent Make-Up v. Lasting Impression*, 543 U.S. 111 (2004), affirms that fair use is available even when some consumer confusion exists — it does not require zero confusion. But the burden of pleading and proving fair use sits on the defendant, and the cost of getting to a fair-use ruling is the cost of defending the litigation in the first place. **Fair use is a defense, not a shield against being sued.**

### Frame 4: FTC Endorsement Guides (16 CFR Part 255)

The FTC's Endorsement Guides — revised in 2023 — govern when an "endorsement" exists, what disclosures are required for material connections, and what constitutes a deceptive endorsement.

The Guides do not require an explicit "we are not affiliated with PepsiCo" disclaimer. They do require that any **endorsement** of a third-party product disclose material connections. If a video says "Diet Mountain Dew" and PepsiCo has paid us nothing and given us nothing, no material-connection disclosure is required.

What the Guides *do* govern that is relevant here:

- **Deceptive impressions about endorsement (§255.2).** A video that creates the net impression of a PepsiCo endorsement of the home soda machine — even without any false statement — can be a deceptive practice under §5 of the FTC Act. The FTC has gone after companies whose UGC/influencer content created this kind of impression.
- **Implied claims (§255.1(a)).** "Implied as well as express" representations are within scope. A side-by-side of our machine pouring Diet Mountain Dew with the Pepsi logo visible implies more than a side-by-side without the logo.

**Where this bites:** the FTC vector is a much lower-probability event than the Lanham Act vector at this volume (the FTC does not enforce against 50-unit-a-year cottage manufacturers). But the **same underlying conduct** — creating an impression of PepsiCo endorsement — is the §43(a) wrong PepsiCo legal cares about. Cleaning up the endorsement-implication surface fixes both.

---

## Where this project is exposed today, ranked

### High exposure — fix before first ad or first cold-buyer unit

1. **Firmware Diet Coke bitmap.** Coca-Cola product, not sold by this project, embedded in shipping firmware. No nominative-fair-use defense available (we are not nominatively describing a product the customer bought from us or with us). **Remove from build, or replace with a generic "Flavor 3 — not configured" placeholder bitmap.** Patch is small: `firmware/src_config/images/flavor2_240.h`, `firmware/src_display/flavor3_bitmap.h`, and the seedLabels strings in both `main.cpp` files.
2. **Firmware Pepsi-product bitmaps as the default seed.** The Pepsi-mark bitmaps (`flavor0_240` Diet Wild Cherry Pepsi, `flavor1_240` Diet Mountain Dew) are seed defaults — every unit ships with PepsiCo product logos rendered on the display until the customer configures otherwise. **The fix is to make the configurator-app surface that lets the customer pick a flavor *also* the surface that loads the logo bitmap onto the device, so the device-as-shipped does not render any trademark.** The factory default becomes a generic "Press the lever" icon, the brand-name bitmap arrives only after the customer has selected the flavor they intend to dispense — putting the customer's hand on the trademark use, exactly the way SodaStream's own home concentrate workflow already does.
3. **Marketing video opening shot.** [`marketing/video/concepts.md`](../../marketing/video/concepts.md) Tier 1.1 puts "Diet Mountain Dew" as the headline of every top-of-funnel video. **Recommended reframing:** lead with the *experience* ("real soda, cold, on tap, in my kitchen") and let "Diet Mountain Dew" appear once, plainly, as a fact rather than as a brand co-star. The pour can still be Diet Mountain Dew — that's accurate — but the chyron / title card / thumbnail / video title should not be "Diet Mountain Dew" as the headline. Subtle move; meaningful legal posture change.
4. **A trademark-policy page on the website.** A plain-language one-pager at `homesodamachine.com/trademarks` saying: "This product is not affiliated with, endorsed by, or sponsored by PepsiCo, Inc. or any of its subsidiaries. Diet Mountain Dew, Diet Pepsi, Pepsi Wild Cherry, Starry, Mountain Dew Code Red, and Mug Root Beer are registered trademarks of PepsiCo, Inc. They are referenced solely to describe products sold by PepsiCo that this appliance is designed to dispense from when the customer supplies them." This is the standard nominative-fair-use disclaimer architecture. Mirror with footer link visible on every page.

### Medium exposure — clean up during normal marketing prep

5. **The Founder Edition plaque QR / `/u/NNN` portal.** Per [`per-unit-portal-gap.md`](../2026-05-18/per-unit-portal-gap.md), the per-unit URL is committed to via the rear-panel nameplate. Whatever lives at `/u/NNN` should not name a PepsiCo product on the page that the QR resolves to. The unit-state UI obviously can name "Diet Mountain Dew" if that is the customer's configured flavor — that is the customer's choice — but the public-facing welcome content should not co-brand.
6. **"He hates these cans" — the Steve Martin / *Jerk* line.** The line is a short cultural quotation used as commentary on the buyer's emotional state. Probably defensible under copyright fair use (purpose: commentary/criticism; nature: short utterance from a 1979 comedy; amount: 4 words; effect: zero on the market for *The Jerk*). **Do not pair the line with visual elements from the film** — no Steve Martin imagery, no can-on-can poster recreation, no "tin can" tracking shot from the original. The line by itself: probably fine. Anything more: real risk. (Universal owns the film; the line is also Steve Martin's screen performance, which adds a right-of-publicity angle in CA and NY.)

### Low exposure — track but do not invest in fixing

7. **"Home Soda Machine" as a USPTO-registrable mark.** Per the *Abercrombie v. Hunting World* spectrum, "Home Soda Machine" is descriptive at best and likely generic-for-the-product. Section 2(e)(1) of the Lanham Act bars principal-register registration of merely descriptive marks unless secondary meaning is shown (5 years of substantially exclusive use, per §2(f)). The Supplemental Register accepts merely-descriptive marks but provides much weaker protection. **At 50 units over four years, do not invest in trademark registration of the product name.** The brand the project actually trades on is the founder's name and face ([`target-market.md`](../../marketing/target-market.md) "the brand is a person") — that is right for the volume and right for the trust model. The descriptive product name is fine as a domain and a description; it does not need protection because there isn't anything to protect.
8. **Domain defensive moves.** The `homesodamachine.com` domain is in hand. The variations (`.net`, `.co`, `.us`, common misspellings) are not flagged as acquired anywhere in the repo. **At 50 units, do not bulk-acquire domain variations.** Re-evaluate at Standard Edition scale.

---

## The actual playbook: three concrete artifacts

The project does not need a comprehensive IP strategy at Founder Edition scale. It needs three small things in place before the first ad runs.

### Artifact 1: `business/trademark-policy.md`

A short doc (~1 page) for internal reference + the public footer link. Captures:

- Nominative-fair-use posture: we use third-party brand names *to describe products our customers buy from those parties.* Word marks only, no logos, no color schemes, no fonts. No co-branding visual treatments.
- Non-endorsement statement: "Not affiliated with, endorsed by, or sponsored by [list]. [Marks] are registered trademarks of [owners]."
- Internal guardrails: don't use Pepsi/Coca-Cola brand colors in marketing materials. Don't recreate brand fonts. Don't reuse PepsiCo product photography (their packaging shots, their cans, their bottle labels) — shoot our own.
- Voice/style: when a Pepsi product is named, name it once, plainly, as a fact ("dispenses real Diet Mountain Dew from PepsiCo's SodaStream-compatible concentrate"). Avoid repeated brand-name foregrounding in copy.

### Artifact 2: Firmware change — neutralize default-seed brand bitmaps

Three commits:

- Remove `flavor2_240.h` / `flavor3_bitmap.h` (the Diet Coke bitmap). Replace with a generic "Flavor 3 — not configured" placeholder.
- Replace the Pepsi-product seed bitmaps with placeholder "Press to configure" icons. The brand-name bitmap arrives only via the configurator-app workflow after the customer selects a flavor.
- Update `seedLabels` in `firmware/src_config/main.cpp` and `firmware/src_display/main.cpp` to remove brand-name strings from the shipped firmware default. Keep them in the configurator-app's flavor-picker, which is the surface where the user provides the trademark use themselves.

Net effect: a unit on a shipping pallet does not carry PepsiCo or Coca-Cola trademark renderings. After the customer configures, it does — and the trademark use is the customer's, on the customer's own appliance.

This is the same architecture SodaStream uses: when you buy a SodaStream Terra, it does not ship with a Pepsi-branded screen — you buy a Pepsi-branded bottle of concentrate from SodaStream, and the brand appears on the bottle PepsiCo manufactured. We are mirroring that pattern: the trademark lives on the customer's own supply, not on the appliance default.

### Artifact 3: Marketing copy guardrails (one-pager in `marketing/`)

Concrete dos and don'ts the founder can check against before posting:

- **Do** say "real Diet Mountain Dew" once per video, plainly.
- **Don't** put "Diet Mountain Dew" in the video title or thumbnail headline.
- **Don't** show the Diet Mountain Dew logo in any frame.
- **Do** show the SodaStream-compatible Pepsi concentrate bottle if it's in shot — that's the customer's own purchased product, and the bottle itself bears the PepsiCo-approved trademark presentation.
- **Don't** use the Pepsi or Mountain Dew brand colors as accent colors in our marketing.
- **Don't** use PepsiCo product photography.
- **Do** include the non-endorsement disclaimer as a footer/end-card on commercial content.
- **Don't** use Steve Martin's likeness, *Jerk* movie stills, or any visual from the film alongside the "He hates these cans" line.
- **Do** keep the "He hates these cans" line as voice/text only, used as commentary on consumer behavior.

---

## What this means for the repo, concretely

If the recommendations above hold, these changes land:

### New: `business/trademark-policy.md`

The Artifact 1 doc. Sits alongside [`business/regulatory.md`](../../business/regulatory.md) and [`business/incorporation.md`](../../business/incorporation.md). Cross-references this todo's reasoning.

### New: `marketing/copy-guardrails.md`

The Artifact 3 doc. Sits alongside [`marketing/target-market.md`](../../marketing/target-market.md) and [`marketing/video/concepts.md`](../../marketing/video/concepts.md). The video concepts doc may need a small edit to acknowledge it.

### Edits to existing files

- [`marketing/video/concepts.md`](../../marketing/video/concepts.md) Tier 1.1 ("The Pour"): reword the script direction to lead with the experience, name "Diet Mountain Dew" once as a fact, drop "Diet Mountain Dew" from the thumbnail/title spec.
- [`marketing/target-market.md`](../../marketing/target-market.md) Section "He hates these cans is the hook": add a one-sentence note that visual reuse of the film is out of scope and the line is used as commentary only.
- [`business/regulatory.md`](../../business/regulatory.md): add a small section ("Trademark posture — see [`trademark-policy.md`](trademark-policy.md)") so the regulatory landscape is read as complete.
- [`marketing/competitors/pepsi.md`](../../marketing/competitors/pepsi.md) "Supply Chain Risk" section: add the trademark-legal vector to the list of risks. Today's text covers commercial cut-off only.

### Firmware changes (Artifact 2)

- [`firmware/src_config/main.cpp`](../../firmware/src_config/main.cpp): replace `flavor0_240` / `flavor1_240` / `flavor2_240` seed bitmaps with generic placeholders. Update the `seedLabelsArr` string array to remove brand names from the shipping default.
- [`firmware/src_display/main.cpp`](../../firmware/src_display/main.cpp): same treatment for `flavor1_bitmap` / `flavor2_bitmap` / `flavor3_bitmap` and `seedLabels`.
- [`firmware/src_config/images/flavor0_240.h`](../../firmware/src_config/images/) / `flavor1_240.h` / `flavor2_240.h` and the `src_display` parallel files: replace pixel data with neutral placeholder bitmaps. Keep the filenames if downstream code expects them; only the bitmap content changes.
- Move the actual brand-name bitmaps out of the firmware default-build path and into the configurator-app's asset bundle, served to the device after the customer selects a flavor (the device thus pulls only the bitmap for the flavor it is configured for, not the full set).

### Build-time effect

A bench unit booted to default still works — it just shows generic "press to configure" tiles until the customer goes through the configurator app. The configurator-app side then loads the user-selected flavor's brand bitmap. Net code change is small (the seed-bitmap initialization in `main.cpp` of both firmware images, plus replacing the bitmap data in the header files).

---

## What I am *not* recommending

- **Not recommended:** Engaging a trademark attorney to do a freedom-to-operate analysis on the product name. At 50-units-from-one-person scale, the marginal value is below cost. Re-evaluate at Standard Edition opening.
- **Not recommended:** Filing USPTO applications for "Home Soda Machine," any product slogan, or the founder's logo. The mark is descriptive, the slogan ("He hates these cans") is borrowed, and there is no logo program. The defensible IP at this scale is the **founder's reputation**, not a trademark portfolio.
- **Not recommended:** Removing all brand-name references from marketing. "Real Diet Mountain Dew" is the substance of the value proposition. Nominative use of the third-party mark to describe what the appliance dispenses is exactly what nominative fair use exists to protect. **The change is in *how* the brand name is used, not whether.**
- **Not recommended:** A separate "co-branding" or "approved-supplier" outreach to PepsiCo. PepsiCo's incentive structure ([`competitors/pepsi.md`](../../marketing/competitors/pepsi.md) Section "What PepsiCo Lacks (or Resists)") makes this an opening-the-door move with no upside. Today they don't know we exist; engaging them voluntarily creates a record of their notice.
- **Not recommended:** A defensive trademark fight at this scale. If PepsiCo legal sends a cease-and-desist, the right response is to comply on the specific objected-to use and reframe; not to fight the case to a fair-use ruling at a cost that exceeds the entire Founder Edition revenue. The nominative-fair-use doctrine exists as a defense to inform our *posture before the C&D arrives*, not as a fight we want to have.

---

## What I did not investigate (followups for later agents)

- **State-level dilution and misappropriation statutes.** NY GBL §360-k, CA B&P §14247, and a dozen other state anti-dilution statutes apply alongside the federal Lanham Act and sometimes broader. At launch (Nebraska to U.S.-anywhere) the relevant exposures are likely Nebraska § 87-126 (Nebraska Trademark Act dilution) and the destination-state law of any large early markets. Out of scope for this hourly pass.
- **The actual provenance of the firmware bitmap files.** I did not read the pixel data. The Diet Coke / Diet Mountain Dew / Diet Pepsi bitmaps may be official PepsiCo / Coca-Cola brand asset files, modified versions, or hand-drawn approximations. **The legal posture differs across the three.** A later agent should open the `.h` files and confirm. If they are official brand assets pulled from a brand kit or from `commons.wikimedia.org`, the legal posture is harder than if they are hand-drawn.
- **The iOS / Android app surfaces.** Neither [`ios/`](../../ios/) nor [`android/`](../../android/) was inspected for brand-name use beyond the flavor picker. The app(s) likely surface the configured flavor name on the home screen, in push notifications, and in any history view. The "trademark use is the customer's after they configure" argument has to hold in the app, too. A later agent should map all surfaces.
- **The website's actual marketing copy.** [`web/public/landing.js`](../../web/public/landing.js) does not surface Pepsi/Mountain Dew text today. When the marketing copy lands there, it should be drafted against the Artifact 3 guardrails. A later agent (or a marketing-copy-specific todo) should walk the landing-page draft.
- **The CO2 service ([`pie-in-the-sky/co2-service.md`](../../pie-in-the-sky/co2-service.md) and the [CO2 supply sibling](../2026-05-18/co2-supply-ownership-gap.md)).** CO2 fill stations and partners may have their own marks. Out of scope here.
- **Sub-Zero, Wolf, Miele, Liebherr, Sub-Zero "Wolf" — the appliance comparables named in [`appliance-freight-bench-gap.md`](../2026-05-18/appliance-freight-bench-gap.md).** Our marketing references the *price band* of these brands, not their products. Fine. But if marketing copy ever directly names them ("Sub-Zero quality at a fraction of the price"), that's its own nominative-fair-use question.
- **A trademark watch service.** Companies like Corsearch and Markify offer USPTO + state + common-law watch services. At 50-units-a-year scale this is unjustified. At Standard Edition scale it becomes a reasonable line item.

---

## Cross-references

- [`marketing/target-market.md`](../../marketing/target-market.md) — the buyer profile and the "He hates these cans" hook
- [`marketing/competitors/pepsi.md`](../../marketing/competitors/pepsi.md) — PepsiCo supply-chain analysis
- [`marketing/video/concepts.md`](../../marketing/video/concepts.md) — Tier 1 video script direction that names Diet Mountain Dew
- [`firmware/src_config/main.cpp`](../../firmware/src_config/main.cpp), [`firmware/src_display/main.cpp`](../../firmware/src_display/main.cpp) — seed-bitmap brand-name code paths
- [`business/regulatory.md`](../../business/regulatory.md), [`business/incorporation.md`](../../business/incorporation.md) — regulatory posture (does not currently include trademark/Lanham)
- 2026-05-18 sibling [`per-unit-portal-gap.md`](../2026-05-18/per-unit-portal-gap.md) — the `/u/NNN` URL surface that, if branded, would inherit this exposure
