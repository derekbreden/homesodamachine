# Console system status

[`console-system.html`](console-system.html) opens on System status. Machine pages occupy the
full 696-pixel pane beside the left rail. Their header contains the page title and Done;
they have no large flavor image or flavor action tabs. The left rail and Done retain their
positions on every page.

System status shows the enclosure viewed along X, front on the left. The silhouette, cold core,
reservoir pockets, carbonator and ten sensor positions use the geometry in the enclosure
firmware's [`buildStatusDiagram`](../../firmware/src_front/main.cpp). The profile is 462 × 361 mm
with a 61.87 mm facet. The diagram contains no words or per-sensor labels.

The eight reservoir indicators and two carbonator indicators use the firmware's state mapping:
closed switches are filled discs, open switches are rings.
Two illustrative snapshots and an unavailable-reading state are available in the review controls.
The unavailable state clears the discs and shows one message below the diagram.

Pump service opens a machine-wide page for drying the lines. Settings returns to the diagram;
Done returns to the resting screen. Selecting a flavor in the left rail opens its controls.
Changing the faucet selection leaves the current machine page open. These interactions and
sensor readings are local mock states.

The flavor pages retain the [Console corner controls](console-corners.md), including their
persistent images, Quiet resting layout and eight-image picker. Browser review covers diagram
geometry, indicator states, page scope, navigation, fixed Done and Settings positions, and
operation controls.
