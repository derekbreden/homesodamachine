# Changes

Each directory here records one change to the enclosure's geometry: a before and an after
picture from one camera, marked where the change is, with a line on what changed and why. The
site shows them newest first at [homesodamachine.com/changes](https://homesodamachine.com/changes),
reached from Latest in the site's navigation, and tapping one opens its detail.

## What gets an entry

A change that moves geometry inside the integrated machine: a printed part, a dock, a tube
route, the layout, anything
[`enclosure-assembly.step`](../hardware/manifold-layout/enclosure_assembly.py) contains. One
entry per change, however many commits it took. A rebuild that moves bytes and no visible shape
gets none.

## Recording a change

[`tools/changes/change.mjs`](../tools/changes/change.mjs) does the drawing; its header has every
option.

1. **Before you rebuild anything**, set the current geometry aside:

       node tools/changes/change.mjs snapshot

   It copies the machine's viewer payload out of the tree in under a second and prints where
   it put it. That copy is the only "before" there will be: the tree is rebuilt in place, and
   the site's store drops geometry the pointer file stops naming within the hour.
   `--model <path under hardware/>` sets aside another model as well, such as the enclosure's
   own `printed-parts/enclosure/enclosure/enclosure.step`.

2. Make the change, build it and publish it as usual. The tree's rebuilt payload is the after.

3. See what moved:

       node tools/changes/change.mjs changed --before <stash>

   It lists the solids whose surfaces moved, groups them into regions, and prints, for each, a
   camera that frames it and the `render` line that draws it. It reports everything that moved
   since the snapshot, other sessions' work included; draw your own.

4. Draw the view that shows it, once for each region worth showing:

       node tools/changes/change.mjs render changes/<id> --view <name> --before <stash> \
         --caption "..." --only <solids> --cam x,y,z --target x,y,z --up 0,0,1 --span mm \
         --mark "x,y,z,r:label"

   It writes `<name>-before.webp`, `<name>-after.webp` and the view's line in `views.json`.
   The first view is the one the feed shows.

5. Write `entry.md`, look at both pictures, delete the stash, and commit the directory:

       git add changes/<id> && git commit -- changes/<id>

Recording follows the change and never holds it up. When it cannot be done (no snapshot was
taken, the machine is short of memory), say so in your report and leave it.

## Choosing the view

The entries here are the examples, and what reads best is still being worked out; this section
changes when something reads better.

- The change is the subject of the frame: a frame a centimetre or two across for a slot or a
  skin, the neighbours in frame for a part that moved.
- `--only` draws just the parts named, so nothing stands in front of what changed. It comes
  first.
- `--section` cuts the parts open, for a change inside one: a passage, a bore, a wall's
  thickness.
- The pictures are opaque. `--xray` draws every part translucent, the hardest view to read; it
  is for a change hiding parts and a section both fail to show.
- The camera looks from where the difference shows: down onto the face a slot opens on, square
  to the plane of a bend, along a gap.
- A mark is a labelled ring on a point of the geometry, read off `changed` or the payload,
  never off the picture.
- A pair that looks the same at phone size shows nothing.

## Entry format

`changes/<id>/`, where `<id>` is the change commit's date and local time and a few words:
`2026-10-20-2154-hinge-bore-slots`.

`entry.md` is written by hand:

    ---
    title: M5 hinge passages run on as slots through the 45° knuckle faces
    lede: One or two plain sentences under the picture.
    date: 2026-10-20T21:54:57-05:00
    commit: 074738cb6936f20c1171bbbf671f4baadcccbd7f
    model: printed-parts/enclosure/enclosure/enclosure.step
    ---
    The detail: what changed, why, and Derek's words where they asked for it.

- `title` is the line on the card; `lede` sits under it, two lines at most.
- `date` is the change commit's, `git log -1 --format=%cI <commit>`; the feed sorts on it,
  newest first, and prints it as written.
- `commit` is the change commit, or several separated by spaces; each links to GitHub.
- `model` is the path under `hardware/` that "Open in 3D" opens.
- The body is the detail the entry opens to, in the subset `/updates` reads: `## ` headings,
  paragraphs, `- ` bullets, `**bold**`, `[text](href)`.

`views.json` and the images are the render tool's. Each view is a before and an after of one
size from one camera, WebP, named by `before` and `after`, with its `width`, `height`, an
optional `caption`, and optional `marks` (`x`, `y`, `r`, `label` in image pixels, from the top
left) drawn over both. The rest of each view records what was drawn: the camera, the section,
the parts shown and highlighted, and the geometry each picture came from.

Nothing else is kept: no meshes, STEPs or payloads.

## On the site

[`web/lib/changes.js`](../web/lib/changes.js) reads every directory here that holds an
`entry.md`. A view shows when both its images are in the directory; an entry without one is a
card of text. Committing an entry does not deploy the site: the page fetches what main holds
and its clone lacks when it is next opened.
