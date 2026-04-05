---
name: Back-as-default in S3 sub-menus
description: S3 rotary encoder sub-menus must always default to "Back" as the first/highlighted item
type: feedback
---

In S3 sub-menus, "Back" must always be the first item and the default selection.

**Why:** The most common accidental input is a double-tap — one tap enters the sub-menu, the second tap acts on whatever is highlighted. If "Back" is default, a double-tap is a harmless no-op (enter then exit). If an action item is default, a double-tap puts the user one confirmation away from triggering something they didn't intend, in a screen they don't recognize.

**How to apply:** Any new sub-menu on the S3 config display should list "Back" first at index 0, with the selection index initialized to 0. This matches the existing settings menu pattern.
