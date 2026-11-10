# Video overlays

`hsm-marketing overlays INPUT SIDECAR OUTPUT` applies authored motion graphics
and sound cues to the edited picture. `hsm-marketing cut --overlays SIDECAR`
uses the same renderer. These commands run on demand through `tools/run`.

The sidecar is a JSON object with an `overlays` array, an optional `sounds`
array and an optional `default_font`. Entries draw in array order. Captions
supplied with `--captions` draw above the graphics. `--dry-run` prints the
assembled FFmpeg graph for inspection.

Every graphic has a `type`, a `t` pair containing its start and end in seconds,
and an optional `fade` duration. These times belong to the output picture,
including its freezes, title and dissolves. Coordinates and font sizes are in
output pixels. The command's help describes encoding options; the native source
owns the defaults.

| Type | Content and appearance |
| --- | --- |
| `text` | `text`, optional scalar `size`, `color`, `border` boolean and `position`. A newline starts another line. |
| `stamp` | `text`, optional scalar `size`, `color`, `bg`, `bg_alpha` and `position`. The background surrounds the text. |
| `lower_third` | `primary`, optional `secondary`, `primary_size`, `secondary_size` and `position`. |
| `hud` | `rows`, each a label/value pair; optional `row_size`, `label_col_w`, `label_color`, `value_color` and `position`. |
| `box` | `rect` containing x, y, width and height; optional `color` and `thickness`. |
| `pip` | `source` image path, optional width/height `size`, `position`, `border` color and `border_w`. Paths resolve beside the sidecar. |
| `magnifier` | `source_rect` and `dest_rect`, each containing x, y, width and height; optional `border` color and `border_w`. The inset follows the main picture. |
| `arrow` | `from` and `to` coordinate pairs, optional `color`, `thickness` and `arrowhead_size`. |
| `param` | `label`, `value`, optional `note`, `accent_color` and `position`. Native font outlines draw the parameter panel. |
| `title` | `text`, optional `subtitle`, `text_size`, `subtitle_size`, `accent_color` and `position`. Native font outlines draw the title panel. |

A position can be an x/y pair or an anchor: `top-left`, `top-center`,
`top-right`, `center`, `bottom-left`, `bottom-center` or `bottom-right`.
Parameter panels also accept `left-mid` and `right-mid`.

Each sound cue has a `file` path beside the sidecar and a start time `t` in
seconds. Optional `volume`, `fade_in` and `fade_out` control its gain and edges.
The main sound retains its gain; cues are mixed without automatic normalization
and end with the main picture.

The maintained implementation is
[`video/edit.rs`](../../tools/hsm/marketing/src/video/edit.rs). Brand and flavor
artwork use the same native drawing and font-outline support.
