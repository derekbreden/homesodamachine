# Big Blue

Big Blue is the enclosure display design exploration for the Home Soda Machine.
[`big-blue.html`](big-blue.html) contains the self-contained interactive preview of the
800 × 480 display, with a companion faucet preview. It opens on Fill.

## Flavor controls

Two flavor images stay in the left rail. Flavor pages show a large copy of the selected image
with “✓ Selected” below it. The same complete portrait appears on the faucet. Fill, Prime and
Clean occupy the top navigation; Settings sits at the bottom left, and Done sits at the top right.

The resting “On tap.” screen shows the reservoir reading and links to Change image and Ratio.
The ratio is shown only when opened. Each flavor has its own ratio and image assignment.
The image picker shows four customer uploads followed by four factory defaults, four at a time,
with Previous, Next and position feedback.

Done, either flavor choice, the rail's empty space, and the whole large-image area dismiss the
focused task and return to On tap. Tapping the already-selected flavor also dismisses the task.
Image and ratio changes persist. Changing the faucet selection returns flavor tasks to On tap
and leaves machine pages open.

While Fill or Clean runs, only Stop filling or Stop cleaning is available. Done is hidden;
flavor choices, background dismissal, Settings and task navigation are disabled. Stop keeps
the current task open and restores normal navigation. Prime runs while held. Other dismissals
cancel a running operation before applying a new flavor selection.

## Machine settings

Machine pages occupy the full 696-pixel area beside the left rail. Their header contains the
page title and Done, with no large flavor image or flavor action tabs.

System status shows the enclosure viewed along X, front on the left, using the silhouette,
cold core, reservoir pockets, carbonator and ten sensor positions from the enclosure firmware's
[`buildStatusDiagram`](../../firmware/src_front/main.cpp). The profile is 462 × 361 mm with a
61.87 mm facet. The drawing contains no words or per-sensor labels. Closed switches are filled
discs; open switches are rings. The review controls offer two sensor snapshots and an
unavailable-reading state, which clears the discs and displays a message below the drawing.

Pump service opens a page for drying the lines. Settings returns to the diagram; Done returns
to On tap. Selecting either flavor in the left rail also returns to that flavor's resting screen.

## Artwork and scope

The four sample uploads combine actual Diet Mountain Dew and Pepsi marks with portrait
backgrounds. The factory portraits are decoded from the compiled RGB565 arrays in
[`flavor0_card.h`](../../firmware/src_front/images/flavor0_card.h),
[`flavor1_card.h`](../../firmware/src_front/images/flavor1_card.h),
[`flavor2_card.h`](../../firmware/src_front/images/flavor2_card.h) and
[`flavor3_card.h`](../../firmware/src_front/images/flavor3_card.h).

Artwork sources: [PepsiCo Diet Dew package artwork](https://digitalassets.pepsico.com/m/642423311fca260c/original/00012000107351_L1.pdf)
and [PepsiCo Partners Pepsi brand](https://www.pepsicopartners.com/PEPSICO-BRANDS/PEPSI%C2%AE/c/brand_pepsi).

Ratios range from 1:6 to 1:24 and start at 1:20. Reservoir readings use four discrete segments.
All operations and sensor readings are local mock states; the preview has no device connection.
The review controls also provide a faucet preview toggle and a Done/Close label choice.

Functional references: [enclosure display](../../firmware/src_front/README.md),
[shared artwork](../../firmware/README.md#a-users-own-pictures),
[faucet display](../../firmware/src_faucet/README.md), and
[protocol and ratio bounds](../../firmware/lib/proto_link/proto_msg.h).

Browser review covers the eight screens, stable image positions, image paging and assignment,
independent ratios, background dismissal, machine status geometry, and operation controls.
