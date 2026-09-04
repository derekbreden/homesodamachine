# Quick Start visual variations

This study applies alternate field colors, paper colors, center lockups, and step-number systems
to the canonical 19 x 13 inch Quick Start without changing its six action panels or scene
geometry.

`preview.png` shows the six composed directions. `number-preview.png` holds C1's Purpose First
lockup and F5 Warm Stone colors fixed while comparing eight step-number systems. The complete
review PDF carries each study independently, then presents the composed directions and strongest
number treatments at full sheet size.

## Render

```sh
tools/cad-venv/bin/python hardware/quickstart/studies/visual-variations/_build.py
```

The builder reads `hardware/quickstart/quick-start.html` and `style.css`, creates temporary study
pages under `tmp/pdfs/`, and writes the review PDF to `output/pdf/`.
