# Console completion

[`console-completion.html`](console-completion.html) compares three ways to finish a task and
return to the resting “On tap.” screen. All use Quiet's colors, resting layout and image picker
spacing. Both flavor selectors and the large selected image stay in fixed positions on every
screen, with “✓ Selected” below the large image.

| Iteration | Finishing a task | Navigation while working |
| --- | --- | --- |
| Done beside the action | Done beside the primary control or in the image picker footer | Fill, Prime, Clean and Settings stay available |
| Task header | Done at the left of a header naming the current task | Settings stays in its corner; Done reveals the action tabs |
| Close beside the flavor | Close above the large selected image | Fill, Prime, Clean and Settings stay available |

The resting screen has no navigation destination of its own. The Settings button occupies an
80-pixel-wide cell at the right of the action bar, with a 36-pixel gear. Done and Close return
from every task to the resting screen. During an operation the Stop control remains available;
completion and navigation controls are disabled until the operation stops.

Done beside the action is the recommended direction. It pairs task completion with the task
controls and keeps direct access to the three main actions. Task header provides a consistent
place for Done across every task. Close preserves the full action pane and uses the space above
the selected image for completion.

## Image selection

The image picker contains eight images, four at a time. The first page shows the four sample
customer uploads, followed by the four factory defaults. Previous and Next controls retain their
positions. The footer shows “Your images · 1–4 of 8” or “Defaults · 5–8 of 8” and disables the
unavailable direction at each end.

Choosing an image immediately updates the selected flavor's thumbnail, large image and faucet
preview. A checkmark identifies the assigned image. The picker stays open for review until Done
or Close is selected. Image assignments and ratio values are independent for each flavor.

The customer images use the artwork described in the [logo studies](README.md#the-image-as-identity).
The default portraits are decoded from the compiled RGB565 arrays in
[`flavor0_card.h`](../../firmware/src_front/images/flavor0_card.h),
[`flavor1_card.h`](../../firmware/src_front/images/flavor1_card.h),
[`flavor2_card.h`](../../firmware/src_front/images/flavor2_card.h) and
[`flavor3_card.h`](../../firmware/src_front/images/flavor3_card.h). Their 129 × 240 pixels match
the firmware arrays when converted back to RGB565.

## Scope and review

Fill, Prime and Clean use the Console task bodies. Prime runs while held; releasing the control
stops it. Settings contains illustrative system status and pump service states. Operation progress
is simulated locally. The study covers interaction and layout; it has no device connection.

Browser review covers all 24 combinations of the three iterations and eight screens, plus both
image pages and running operations. Checks cover stable image positions, control bounds, gear
size, image assignment, ratio independence, completion, Settings access and operation controls.
