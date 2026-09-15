# Enclosure display studies

Four interactive visual directions for the 800 × 480 enclosure display. Each uses the same
uploaded picture on the enclosure and faucet. The studies cover Choose, Adjust, Fill, Prime,
Clean and Images, plus a three-screen companion app image setup preview.

[Persistent flavor selection](persistent-selection.md) contains four additional variations of
Control room with both flavor selectors and the large action target visible in every screen.

[Console Home](console-home.md) contains four Home and middle-column iterations with secondary
ratio controls, image selection and machine Settings access.

[Console completion](console-completion.md) compares three ways to finish a task, with Quiet's
resting layout, a larger Settings control and an eight-image picker.

[Console corner controls](console-corners.md) places Settings below the flavor choices and Done
at the top-right of every task.

[Console system status](console-system.md) gives machine settings the full pane beside the rail,
with the enclosure's side profile and unlabeled sensor indicators.

[`logo-first.html`](logo-first.html) is a self-contained conversation visualization fragment.
The controls above the device select the direction and screen. Selecting a drink on either
display changes the shared selection. Ratio adjustments belong to their own flavor; choosing
an image assigns it to the current flavor. The operation controls demonstrate local mock states.

## Directions

| Direction | Composition | What the view emphasizes |
| --- | --- | --- |
| Twin labels | Two equally sized portrait images, individual level and ratio readings, shared task buttons | Recognizing both drinks and choosing between them |
| Control room | A narrow image selector, large selected picture, and a group of direct controls | Keeping the drink visible while working with its settings and reservoir |
| Poster | A picture nearly as tall as the screen, a smaller alternate picture, and quiet controls | The strongest presence for the selected drink, including demonstrations and video |
| Index | Two horizontal image rows, with actions beside the selected row | Large action targets and a simple overview of both reservoirs |

Twin labels gives the two drinks equal visual weight. Poster puts most of that weight on the
selected drink. Control room preserves both selection and settings within one view. Index
spends more of the display on controls and less on the pictures. Those differences are the main
comparison; colors, type, and button treatment are independent design choices.

## The image as identity

The sample artwork combines actual Diet Mountain Dew and Pepsi marks with portrait backgrounds.
Each complete composition is a stand-in for a customer's uploaded picture. The same rectangle
appears on the faucet, in selection, beside adjustments and operations, and in the image picker.
The app preview shows choosing an image, composing its portrait, and seeing it on the faucet.

The supplied picture retains its proportions and full bounds in every view. Selection is shown
outside the picture, through a border, a marker, or nearby words. The artwork carries the drink's
name. Text identifies actions and machine state.

## Basis and scope

- The enclosure is a 4.3-inch, 800 × 480 capacitive touchscreen. The faucet is 172 × 320.
- Artwork is a 43:80 rectangle. The existing phone workflow supports choosing, framing and
  uploading pictures; both displays share the resulting image. Four factory and four customer
  image slots exist. The picker in this study shows the two demonstration uploads.
- Ratios range from 1:6 to 1:24. Each flavor starts at 1:20 in the study.
- Reservoir levels use four discrete segments. The example levels show three and two segments.
- Fill draws concentrate from the top funnel. Prime runs while held. Clean performs three
  water-in/water-out rounds with a visible Stop action during operation.
- The pictured operation progress is a selected mock state. These views contain no device
  connection. They cover the normal tasks and running operations; system status, pump service,
  fault recovery, boot and sleep are outside this visual set.
- Some concepts display artwork larger than the current stored renditions. A firmware
  implementation would need appropriate artwork renditions or scaling for those sizes.

Functional references: [enclosure display](../../firmware/src_front/README.md),
[shared artwork](../../firmware/README.md#a-users-own-pictures),
[faucet display](../../firmware/src_faucet/README.md), and
[protocol and ratio bounds](../../firmware/lib/proto_link/proto_msg.h).

Artwork sources: [PepsiCo Diet Dew package artwork](https://digitalassets.pepsico.com/m/642423311fca260c/original/00012000107351_L1.pdf)
and [PepsiCo Partners Pepsi brand](https://www.pepsicopartners.com/PEPSICO-BRANDS/PEPSI%C2%AE/c/brand_pepsi).

## Review checks

All 24 primary views have rendered screenshots. Browser checks cover screen bounds, image
loading, independent flavor ratios, shared selection, image assignment, and operation controls.
The views have been visually inspected for artwork clipping, text collisions and control size.
