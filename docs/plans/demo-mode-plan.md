---
name: Demo mode implementation
description: DONE — iOS demo mode for Apple review (no hardware needed), commits c265607 + 7e91abe
type: project
---

# Demo Mode — DONE

Completed 2026-03-14 (commits c265607, 7e91abe).

## What it does

Demo mode lets Apple reviewers (and anyone without hardware) explore the full iOS app UI. Entry via "Try Demo Mode" button on scan screen; exit via "Exit Demo" in settings.

## Key decisions

- **Entry:** Small gray "Try Demo Mode" button on scan screen, visible in all pre-connected states
- **Images:** 3 programmatically generated placeholder images (colored circles with text labels) — no bundled assets
- **Simulated operations:** Upload (animated progress over ~2s), delete (instant with index adjustment), factory reset (restores demo defaults)
- **Exit:** "Exit Demo" button on settings page; resumes BLE scanning. Not persisted — app relaunch returns to scan screen.
- **Minimal View changes:** Only ScanView (entry button) and SettingsPageView (exit button) know about `demoMode`. All other views work identically via BLEManager properties.
- **`send()` naturally no-ops** in demo mode since `rxCharacteristic` is nil.
