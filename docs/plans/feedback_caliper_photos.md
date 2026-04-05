---
name: Caliper photo readings are unreliable
description: Vision model cannot reliably read caliper displays - ask the user instead of guessing
type: feedback
---

Do not trust caliper readings extracted from photos by the vision model. The readings are inconsistent — sometimes close, sometimes off by a digit, sometimes the measurement subject itself is misidentified.

**Why:** Photos 15/16 of the Kamoer pump were misread: photo 15 was labeled as motor diameter when it measured bracket-to-barb-edge, and photo 16's 35.73mm was misread as 35.13mm. The user had to correct both the values and what was being measured.

**How to apply:** When caliper photos exist and measurements are needed, ask the user to read the values rather than relying on vision extraction. Flag readings as "needs user verification" rather than guessing confidence levels.
