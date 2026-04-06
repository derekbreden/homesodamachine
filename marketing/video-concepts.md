# Video Concepts

*Prioritized list of video content, ranked by shareability and product trust. Each concept includes an estimated length and the primary audience it reaches.*

---

## Tier 1: The videos that sell the machine

These build trust in the product and the person. They are the "wait, that's real?" moments.

### 1. The Pour (30 seconds)

The simplest and most important video. Turn the handle. Diet Mountain Dew pours into a glass with ice. Take a sip. That's it. No explanation, no setup, no context. The ordinariness is the message. End with "He hates these cans" and a link.

- **Audience:** Everyone. This is the top of the funnel.
- **Shareability:** Very high. The "wait, what?" factor carries it.
- **Trust signal:** The kitchen is real, the pour is real, the person is real.
- **Variants:** Do this with different flavors, different glasses, different times of day. This is a repeatable format — the Tuesday morning pour, the late-night pour, the "guests are over" pour.

### 2. The Full Story (3-5 minutes)

Derek, in his kitchen, telling the story. "I drink 3 diet sodas a day. I was tired of hauling cans. I tried SodaStream 15 years ago — it went flat. I tried to buy restaurant syrup — you need a business license. Then I found out Pepsi sells the real formula as SodaStream concentrate. So I built a machine."

Show the faucet. Show the pour. Show what's under the counter. Show the app. Show the display. Show the flavor switch. This is the trust-building video — the one that takes someone from "interesting" to "I believe this person and this product."

- **Audience:** Anyone who found you through a shorter video and wants to understand more.
- **Shareability:** Moderate — people share this with the specific friend they know drinks diet soda.
- **Trust signal:** Very high. Face, voice, kitchen, story, transparency.

### 3. The Install (2-3 minutes)

Real-time (sped up where boring) install of the system. Unbox. Connect to water line. Connect CO2. Plug in. Pour. Show the clock — start to first pour. The claim is "under an hour, no plumber." Prove it on camera.

- **Audience:** People in the decision phase. They've seen the pour, they believe it's real, now they need to believe they can do the install.
- **Shareability:** Moderate.
- **Trust signal:** Very high. This eliminates the biggest practical objection.

---

## Tier 2: The videos that build the audience

These are interesting on their own merits. They reach people who aren't looking for a soda machine but are interested in how things get built. Some percentage of those people drink diet soda. The soda machine is the backdrop, not the pitch.

### 4. The Live-Reload CAD Viewer (30-60 seconds)

The system you already identified. Tell an AI agent to make a CAD change. Browser updates in 3 seconds with the new 3D model. The CadQuery script changes → Python regenerates the STEP file → WebSocket pushes it → browser renders it. No manual export, no file opening, no refresh.

Show the terminal, the browser, and the result. Speed it up if the agent takes too long to respond. The "wow" is the feedback loop speed.

- **Audience:** Makers, 3D printing community, CadQuery users, anyone building physical things with code. Also: developers interested in AI-assisted workflows.
- **Shareability:** Very high in maker/dev communities. This is a tool video — people share tools.
- **Trust signal:** Indirect but strong. "This person built real infrastructure for their design process" = "this person is serious."
- **Where it lives in the repo:** `tools/step-viewer/` (server.js, run_redirected.py)

### 5. The AI Design Pipeline Failure (2-3 minutes)

The story of building an elaborate multi-agent pipeline to generate CAD parts autonomously — and tearing it down when it didn't work. Show the commit history. Show the frustrated commit messages ("WHY IS THIS SO HARD FOR THEM?"). Show the moment the pipeline was deleted. Show the commits that followed — precise, surgical, correct — once Derek learned CadQuery himself with the AI as teacher instead of designer.

The punchline: "AI can teach you CAD. AI can type your CAD. AI cannot design your CAD. It doesn't know what it's building."

- **Audience:** Huge. Anyone interested in AI capabilities and limitations. Makers. Developers. The "AI discourse" crowd. This is genuinely novel insight with evidence.
- **Shareability:** Very high. Contrarian takes with receipts get shared.
- **Trust signal:** Strong. Honesty about failure + the lesson learned + the recovery = credibility.
- **Where it's documented:** `how-ai-built-the-parts.md`, git log from March 30 2026

### 6. The Snap-Fit Testing (60-90 seconds)

Print three test pieces at different deflection values (0.3mm, 0.4mm, 0.5mm). Snap them together on camera. Try to pull them apart. Show which one works — moderate force to close, impossible to open with fingers. Then show the real pump case using the winning parameters.

- **Audience:** 3D printing community, mechanical design people, anyone who's tried to design snap fits.
- **Shareability:** High in printing communities. Empirical testing with real results.
- **Trust signal:** "This person tests before they commit. The product is engineered, not guessed."
- **Where it lives:** `hardware/printed-parts/case-snaps/`, `hardware/printed-parts/cadlib/snap.py`

### 7. The Logo Animation Pipeline (60-90 seconds)

One vector design that works as: the S3 screensaver (animated, looping), the iOS app loading screen (animated), the iOS splash/launch screen (static), and the iOS app icon (static). Show each context. Show the procedural SwiftUI animation (Canvas + TimelineView, bubble physics ported from the ESP32 Python frame generator). Show the consistency — same design, same colors, same physics, four contexts.

- **Audience:** iOS developers, designers, anyone interested in brand consistency across platforms.
- **Shareability:** Moderate-high. Multi-platform design consistency is satisfying to see.
- **Trust signal:** Strong. "This person cares about polish across every surface" = "this is a real product."
- **Where it lives:** `ios/SodaMachine/SodaMachine/Views/GlassAnimationView.swift`, `src_config/` (screensaver frames), app icon assets

### 8. Three Microcontrollers, One System (2-3 minutes)

Lay out the three boards on a table. Explain what each one does and why they're separate. ESP32: brain, pump control, flow sensing, image storage, config authority. RP2040: tiny round display showing the active flavor's real logo. ESP32-S3: rotary touchscreen for settings, BLE bridge to iOS. Show them communicating over UART with HDLC. Show what happens when you flip the flavor switch — the round display changes, the S3 updates, the pump reconfigures — all in under a second.

- **Audience:** Embedded systems people, electronics hobbyists, anyone who appreciates hardware architecture.
- **Shareability:** Moderate-high. Multi-MCU architectures are inherently interesting to the right crowd.
- **Trust signal:** Strong. "This is not an Arduino with a servo. This is a real embedded system."

### 9. The Duty-Cycling Pump Algorithm (60-90 seconds)

Visualize how the pump adapts to water flow in real-time. At slow pour: short pulses, long gaps (8% duty). At full pour: longer pulses, shorter gaps (40% duty). Show the flow meter readings, the pump cycling, and the resulting soda — consistent flavor whether you pour slow or fast.

- **Audience:** Control systems nerds, embedded engineers, makers.
- **Shareability:** Moderate. Niche but satisfying to the right audience.
- **Trust signal:** "The flavor ratio is actively controlled, not approximate."

### 10. The Business License Wall (60-90 seconds)

Short, punchy storytelling. "I wanted restaurant syrup. Pepsi said no — business license required. The internet said lie on the application. I said no. Then I found out Pepsi sells the actual formulation as SodaStream concentrate to home consumers. No license. Same product."

- **Audience:** Broad. Anyone who's run into a gatekeeping problem and found a creative workaround. Home soda explorers. SodaStream owners who didn't know this existed.
- **Shareability:** High. Underdog-finds-loophole stories get shared.
- **Trust signal:** Integrity. "I took the hard path instead of the dishonest one."

---

## Tier 3: Supporting content (make when the audience exists)

### 11. The iOS App Demo Mode

The app works without hardware — built for App Store review. Show the demo mode: fake stats, simulated clean cycles, generated gradient images. Everything functional with no Bluetooth connection. Then connect to real hardware and show the transition.

- **Audience:** iOS developers, app reviewers.
- **Trust signal:** Product completeness.

### 12. The BLE Image Upload Pipeline

Upload a custom flavor photo from your iPhone. Watch it get processed into three formats (PNG, RGB565 240×240, RGB565 128×115), chunked over BLE, CRC-verified, and appear on both displays in under a minute. All local, no cloud, no account.

- **Audience:** iOS/BLE developers, privacy-conscious tech people.
- **Trust signal:** Technical depth + privacy-respecting architecture.

### 13. The Statistics System

Show the iOS app charts: last 24 hours (hourly), last 30 days (daily), hour-of-day average. Show live updates — pour a glass and watch the chart update in real-time. The DS3231 RTC means data survives power loss. "My machine knows I drink more Diet Mountain Dew on Saturdays."

- **Audience:** Data nerds, quantified-self people.
- **Trust signal:** "This machine knows things about your habits."

### 14. The Off-the-Shelf Parts Documentation

Show the measurement protocol: caliper photos of the Kamoer pump, John Guest couplers, Beduan solenoids. Cross-referenced with datasheets. Corrections to manufacturer specs noted. "If you're designing around commercial parts, this is how you get the dimensions right."

- **Audience:** Mechanical design people, makers integrating commercial hardware.
- **Shareability:** Moderate — useful reference content.

### 15. The Clean Cycle

Trigger a clean cycle from the iOS app. Watch the solenoids fire, water flush through the lines, air purge. Three rounds, fully automated. "When you change flavors, the machine cleans itself."

- **Audience:** Anyone considering the product. Answers the "how do you maintain it?" question.
- **Trust signal:** Maintenance is solved, not deferred.

### 16. Material Exploration: PLA to PETG to ABS

Show the progression of printing the same part in different materials. Drying process, material differences, why PETG for internals, why ABS might be needed for heat resistance near the compressor. Show the snap-fit behavior changing between materials (different deflection values for PLA vs PETG).

- **Audience:** 3D printing community.
- **Shareability:** Moderate. Material comparison content does well in printing communities.

---

## Production notes

### The sequence: Tier 2 → Tier 1 → Tier 3

**Tier 2 starts now.** These videos are about the build process, and they're most valuable *while the build is happening*. A live-reload CAD viewer demo posted during active development has an authenticity that a retrospective never matches. Build-in-public content has a shelf life — make it while it's fresh. The AI pipeline failure story and the live-reload CAD viewer are the highest-value Tier 2 pieces — they reach large, active communities (AI discourse, 3D printing) with genuinely novel content.

**Tier 1 waits for the self-contained prototype.** The pour video, the full story, and the install video are the sales funnel. They need to show the product someone can actually buy — not the current Lillium-backed system that's going to change. The pour video is stronger when it pours from the finished appliance. The install video requires a finished unit to install. These should exist before the first sale, but not before the product is ready to sell.

**Tier 3 comes when people start asking.** "How does the app work?" "How do you clean it?" These answer specific questions from people already interested.

**Every Tier 2 and Tier 3 video should have the soda machine visible in the background or mentioned in passing.** The machine is always the context. Never the pitch, but always present. The audience built during Tier 2 is the audience that sees the Tier 1 videos when they drop.
