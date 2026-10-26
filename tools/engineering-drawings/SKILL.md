---
name: engineering-drawings
description: Create or revise dimensioned mechanical part drawings from CAD and fabrication requirements, with separate source, annotation, and visual layout reviews. Use for manufacturing drawings, not illustrative diagrams or assembly instructions.
---

# Engineering drawings

Deliver a vector drawing of the requested part state, with source-backed
requirements and readable annotations. Use the PDF skill for PDF authoring and
rendering. The reviews below belong to the requested drawing task; they add no
commit hooks, build checks, or checks on unrelated edits.

## Define the finished part

Read the part's geometry source, fabrication procedure, material specification,
and applicable drawing instructions before choosing views. Identify whether the
request is for a blank, a machined part, or an assembly. Include secondary
operations in that state: tapping, blind drilling, edge preparation, and similar
features that a cut file or simplified CAD model may omit.

Keep a short working inventory of features and their authoritative sources.
Reuse source parameters rather than restating dimensions in another generator.
Distinguish thread designations from pilot diameters, drill-tip depth from
full-diameter depth, and actual requirements from conventional representations.
Use published standards or primary technical references when a convention is
uncertain; do not invent a convention to make a drawing fit.

Choose units, precision, datums, and tolerances deliberately. Do not infer a
manufacturing tolerance from CAD precision or copy one from a reference drawing.
Identify missing acceptance criteria specifically and preserve the drawing's
review status when those requirements remain unresolved.

## Compose and generate

Choose the smallest useful set of views that describes the finished part.
Generate outlines and sections from the model or source-defined analytical
geometry. Use sections and enlarged details where they resolve internal shape or
small-feature depth. Keep the coordinate origin tied to identifiable geometry.

Reserve room for dimensions and notes before placing the views. Reuse established
primitives for text, arrowheads, leaders, dimensions, hatching, and title blocks.
Keep manufacturing geometry separate from annotation placement. A conventional
thread graphic does not replace its finished-thread callout.

For a side-attached leader, place the shoulder beside the first text line at
mid-height, with a visible gap and correct left/right text alignment. Direct a
hole leader radially to the intended circle edge. Choose a clear face target
rather than crowding a corner that already carries a dimension.

Judge the complete route as well as its individual pieces. With a left-hand
label and a simple inclined leader, the text endpoint, knee, and target should
progress toward the right; reverse that arrangement for a right-hand label.
Move the label or select another legitimate point on the same face when a route
unnecessarily doubles back. Extra bends need a clearance or communication
purpose. Do not apply these leader rules to dimension lines or cutting-plane
arrows, which have different meanings.

## Verify geometry and requirements

Do this separately from visual review, before presenting a new drawing. Trace
each finished feature to its source, check its location and size, and check the
view and section directions. Account for the required material, thickness,
threads, blind/through conditions, and edge preparation. Avoid competing
controlling dimensions. Mark derived reference dimensions appropriately.

Identify which requirements belong to the component drawing and which belong to
its assembly. A rendered picture, a valid PDF, or a plausible-looking section is
not evidence of dimensional or manufacturing completeness.

## Review the rendered drawing twice

Render the full sheet and enlarged crops of every annotation cluster. Make a
short temporary inventory of callouts, dimensions, section markers, tables,
and notes, using the generator's own groups where available. Map that inventory
to crops so neither review depends on remembering which items were inspected.
Include neighboring geometry and annotations in each crop; isolated text is
insufficient for routing review. Expand a crop that clips the label or relevant
neighboring lines before judging that annotation.

**First visual review: annotation consistency.** Visit every inventory item.
Check text attachment and alignment, arrowhead placement, symbol and line use,
units and precision, feature identifiers, and the link between each cutting
plane and its section. Distinguish intentional drafting conventions from errors.
Use enlarged crops to inspect small details and the full sheet to judge type
size and hierarchy at the stated print size.

**Second visual review: routing and composition.** Follow each leader from the
label to its feature. Check directness, unnecessary reversals, tiny jogs,
ambiguous targets, and crowding. Inspect its interaction with neighboring
leaders, dimension lines, extension lines, arrowheads, and text. Separate
necessary crossings of a part outline from avoidable crossings of annotations.
Check witness-line origins, section hatching, text clearance, and overall view
spacing. A route that clears every bounding box can still need simplification.

Correct the findings together where practical, then regenerate and inspect the
changed clusters with their neighbors. Inspect the sheet overview again if the
layout changed. For a narrow revision, revisit the affected checks and regions;
repeat source verification only if dimensions, geometry, or requirements changed.
Use images from the current PDF, not a previous revision's render.

Stop when known drafting defects have been resolved and the latest changed
regions have been inspected. Report specific unresolved requirements and what
was actually checked; do not equate two reviews with a guarantee of correctness.
Do not ask the user to perform routine annotation cleanup as an approval step.

## Review rendering helper

`scripts/render_review.py` renders an overview of each selected page and named
detail crops with Poppler. It also records which PDF produced the images.
It does not assess drawing quality; inspect the resulting images.

Region arguments are `PAGE,NAME,X0,Y0,X1,Y1` in points, measured from the
bottom-left of the displayed page's crop box after rotation. Include context
around the annotation, not only the letters. Invoke this helper during drawing
review, not from a general build or commit path.

Example from the Home Soda Machine repository root:

```sh
python3 tools/engineering-drawings/scripts/render_review.py \
  hardware/cut-parts/carbonation/endcaps-circular/endcap-circular-2hole-drawing.pdf \
  --output-dir /tmp/endcap-review \
  --region 1,port-callout,325,465,660,625 \
  --region 1,register-callout,235,325,660,455 \
  --region 1,port-section,35,155,635,292 \
  --region 1,register-section,750,500,1180,745
```

Those crops illustrate the command; a complete new-sheet review also covers the
other inventory items, including tables, notes, and section markers.

For the Home Soda Machine part family, use
`hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_drawing.py`
and its current PDF as a worked example of the finish and source linkage.
Reuse its drafting patterns, not its dimensions, tolerances, material, sheet
size, or approval status. Keep a new drawing beside its part source and retain
the project's existing export and publishing conventions.

For publication on the materials page, follow the engineering-drawing document
entry and PDF publication metadata described in `hardware/ledger/materials.md`.
The material record drives the featured drawing action and 3D/Drawing switch.
