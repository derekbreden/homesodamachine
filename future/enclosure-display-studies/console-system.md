# Console system status

[`console-system.html`](console-system.html) opens on Fill. Machine pages occupy the
full 696-pixel pane beside the left rail. Their header contains the page title and Done;
they have no large flavor image or flavor action tabs. The left rail and Done retain their
positions across pages. Done is absent while Fill or Clean is running.

System status shows the enclosure viewed along X, front on the left. The silhouette, cold core,
reservoir pockets, carbonator and ten sensor positions use the geometry in the enclosure
firmware's [`buildStatusDiagram`](../../firmware/src_front/main.cpp). The profile is 462 × 361 mm
with a 61.87 mm facet. The diagram contains no words or per-sensor labels.

The eight reservoir indicators and two carbonator indicators use the firmware's state mapping:
closed switches are filled discs, open switches are rings.
Two illustrative snapshots and an unavailable-reading state are available in the review controls.
The unavailable state clears the discs and shows one message below the diagram.

Pump service opens a machine-wide page for drying the lines. Settings returns to the diagram.
Done, either flavor choice, the rail's empty space, and the whole large-image area dismiss the
focused task and return to the resting screen. Tapping the already-selected flavor also dismisses
the task. During Fill or Clean, the running action locks the screen: only Stop filling or
Stop cleaning is available. Done is hidden, and flavor choices, background dismissal,
Settings and action navigation are disabled. Stop leaves the current task open and restores
normal navigation. Other dismissals cancel a running operation before applying a new flavor
selection.

Changing the faucet selection returns flavor tasks to the resting screen and leaves machine
pages open. Image assignments and ratio adjustments persist when a task is dismissed. These
interactions and sensor readings are local mock states.

The flavor pages retain the [Console corner controls](console-corners.md), including their
persistent images, Quiet resting layout and eight-image picker. Browser review covers diagram
geometry, indicator states, page scope, navigation, fixed Done and Settings positions, and
operation controls.
