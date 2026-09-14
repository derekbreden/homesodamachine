# Quick Start visual variations

This study applies alternate field colors, paper colors, center lockups, and step-number systems
to the canonical 19 x 13 inch Quick Start without changing its six action panels or scene
geometry.

`preview.png` shows the six composed directions. `number-preview.png` holds C1's Purpose First
lockup and F5 Warm Stone colors fixed while comparing eight step-number systems. The complete
review PDF carries each study independently, then presents the composed directions and strongest
number treatments at full sheet size.

## THIS DOCUMENT IS NOT A STEP OF THE BUILD. LEAVE IT THAT WAY.

It was drawn once, by hand, against the sheet as it stood that day, and committed. No bazel
target builds it, no `graph.json` entry names it, no publish or derive lane touches it. Wiring
it in would put forty browser renders on every nightly derive and rewrite a comparison that was
read once, each time the sheet moves.

What stands as it stands:

- The script lives under `tools/` — [`build.py`](/tools/quickstart-visual-variations/build.py)
  writes the variant pages, renders them and binds the review PDF. `tools/bazel/trace_inputs.py`
  names `tools/` in `ELSEWHERE`.
- It keeps no `note_read` / `note_write` bookkeeping.
- `preview.png`, `number-preview.png` and `output/pdf/quick-start-visual-variations.pdf` are in
  the git index. `tools/cad-artifacts/pack.py`'s `NOT_BUNDLED_DIRS` names
  `hardware/quickstart/studies`.
- Its working pages go under `tmp/pdfs/` and are removed when it finishes.

## Rebuilding it

```sh
tools/cad-venv/bin/python tools/quickstart-visual-variations/build.py
```

The builder reads `hardware/quickstart/quick-start.html` and `style.css`, creates temporary study
pages under `tmp/pdfs/`, and writes the review PDF to `output/pdf/`. Rebuilding redraws the
comparison against the sheet as it stands now.
