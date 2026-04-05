# How This Got Built

*This is the story of how a home soda machine came to exist — from a failed SodaStream experiment 15 years ago to a working appliance dispensing real Diet Mountain Dew from a kitchen faucet. It was written by Claude based on a conversation with Derek, the sole developer, in April 2026.*

---

## The SodaStream cycle

About 15 years ago, Derek bought a SodaStream. Like most people, he used it wrong at first — carbonating room temperature water, opening the cap too casually. The CO2 escaped before he finished the bottle.

He learned the tricks. Chill the water first. Minimize the time the cap is open. It got better, but it still went flat before he was done. That's not a user error — it's physics. Warm water cannot hold dissolved CO2 the way cold water can, and once you open the bottle, you're fighting a losing battle against equilibrium. He gave up and went back to cans.

This is not an unusual story. SodaStream had enormous initial sales. Very few people stuck with it.

## Fifteen years later

About two years ago, Derek started casually looking into the state of home carbonation again. YouTube surfaced a hack: use flexible bottles and squeeze the air out before resealing. This actually works — eliminating the headspace keeps the CO2 in solution. He tried it with 2-liter bottles. It was not fun. He tried smaller bottles. Even less fun. He declined.

He started researching what it would take to get a real setup — the kind restaurants use. Bag-in-box syrup, a carbonator, CO2 tank, the works. He found kits. He was ready to buy.

Then he tried to actually order the syrup.

## The business license problem

Pepsi and Coca-Cola will not sell bag-in-box syrup to home consumers. You need a business license. Their distribution network is set up for commercial accounts, and they have no interest in selling individual bags to someone's house.

This is the wall that stops most people. The workarounds suggested to Derek — by AI assistants and by people on the internet — included starting a shell catering business with no customers, or simply lying on the application. Both approaches would probably work. People do it.

Derek wouldn't. If the supplier doesn't want to sell to him when he's being honest, and the only path forward is deception, he'd rather find another way. There are plenty of stories online about people losing their supplier connection. He wasn't interested in being one of those stories.

## Another way

Here's what most people don't know: Pepsi sells their own brand formulations as SodaStream-compatible concentrate. Diet Mountain Dew syrup made by Pepsi *is* Diet Mountain Dew — the same formulation, sold to home consumers at a 1:20 ratio, sweetened with sucralose. No business license required.

The missing piece was a way to dispense it that didn't involve squeezing bottles.

Derek bought a Lillium under-counter cold water carbonator from China. It arrived in under two weeks. The Lillium solves the fundamental problem — it carbonates cold water under pressure in a sealed system, dispensed through a faucet. The water never goes flat because it's never exposed to air until it hits your glass.

Within a week of the Lillium arriving, an ESP32 was driving a Kamoer peristaltic pump, injecting SodaStream concentrate into the cold carbonated water stream as it flowed from the faucet. The first pump he chose — based on extensive AI-assisted research — turned out to be too small. The second one worked.

Turn the handle, soda comes out. The result is indistinguishable from the canned product, with equal or better carbonation and temperature.

## Building the system

What started as one pump and one flavor grew quickly:

- A toggle switch (a KRAUS air switch, safe for wet countertops) to select between two flavors.
- A Waveshare RP2040 round LCD, mounted flush next to the switch, showing the active flavor's real logo.
- Solenoid valves to keep the concentrate lines primed between uses — no waiting, no air in the lines.
- Flow-meter feedback driving a duty-cycling pump controller that scales concentrate delivery to water flow rate.

Then the scope expanded from "working prototype" toward "product someone could actually use":

- A Meshnology ESP32-S3 rotary touchscreen display for the enclosure — originally just for adjusting flavor ratios, but it grew to handle factory reset, clean cycles, pump priming after flavor changes, and a screensaver animation.
- An iOS companion app over BLE, because users need to upload their own flavor photos, and doing that locally (no cloud, no account) meant Bluetooth. The app grew to include usage statistics, clean cycle control, and a demo mode for App Store review.
- A clean cycle system — solenoid valves that fill the flavor bladders with tap water, flush them through the dispense line, then air-purge. Three cycles, fully automated from the app or the S3 display.
- A statistics system backed by a DS3231 RTC, tracking per-flavor usage in hourly buckets that survive power loss.

The firmware runs across three microcontrollers (ESP32, RP2040, ESP32-S3) communicating over UART using TinyProto HDLC. The ESP32 is the single source of truth for configuration and images, pushing them to the display boards at boot and on change. The entire system — including the iOS app — is described in detail in the README.

## 3D printing and the AI design wall

Two to three weeks before this was written, Derek ordered a Bambu H2C and started exploring whether AI could bypass the need to learn mechanical CAD.

The idea was appealing: describe a part in plain language, have AI generate a CadQuery script, validate the output, print it. He built an elaborate multi-agent pipeline — an orchestrator launching an engineering manager, writing specs, generating scripts, running validation checks. The pipeline went through many iterations. Rubrics, grounding rules, path continuity probes, scoping principles.

It worked for simple parts. Flat plates with holes. Rectangles with cutouts.

It failed the moment parts needed to relate to each other in physical space. The AI could produce valid CadQuery that passed every validation check — but it couldn't understand that two lips forming a channel need a gap where another panel slides through. It would add features by pattern-matching ("rails = good") without understanding why each rail exists. A coupler tray split — conceptually simple, cut a plate in half through the hole centers — took multiple painful attempts.

The full analysis of this failure is in [how-ai-built-the-parts.md](how-ai-built-the-parts.md). The short version: no amount of pipeline scaffolding, rubrics, or validation checks can substitute for spatial understanding. The AI doesn't know what it's building.

Derek tore down the pipeline and learned CadQuery himself. The AI taught him the principles — what a workplane is, how lofts work, what fillets do to edge topology. Then he directed the AI to implement specific geometry based on his understanding. The commits went from "AI produces a part from a spec" to surgical, precise changes: "widen to 170mm, shift features +15mm, move strut bores outward."

The AI is simultaneously the teacher and the typist, but it cannot be the designer. It can explain to a human why a snap fit needs a specific deflection angle, but it cannot look at a STEP file and see that two parts don't fit together. This is a genuinely strange gap — and probably the most useful thing in this repository for anyone trying to use AI for physical design work.

## Where it is now

The system dispenses two flavors of real Pepsi-made soda from a kitchen faucet, on demand, ice cold and fully carbonated. The firmware, iOS app, and display interfaces are feature-complete for the current phase. Clean cycles work in software; the plumbing for them is next.

The current hardware work is the pump case — a custom 3D-printed enclosure that molds tightly around the Kamoer peristaltic pump. This is the user-replaceable unit: when the silicone pump tubing wears out, the user swaps the entire cased pump. Two halves snap together and lock — the snap fit geometry was just validated on the printer with test pieces at multiple deflection values. One candidate met the goal: snaps together with moderate force, impossible to pull apart with fingers alone.

The longer-term vision described in `hardware/future.md` — a self-contained appliance with its own carbonator, refrigeration, and insulated cold core — is designed but hasn't started. The current system depends on the Lillium for carbonation and chilling. The future system would do both internally, from tap water, powered by a single 12V DC supply.

This is one person building a consumer product with AI assistance, documented publicly as it happens. The repository is the complete record — firmware, iOS app, 3D-printed part designs, off-the-shelf part measurements, and the full git history of every iteration, dead end, and lesson learned along the way.
