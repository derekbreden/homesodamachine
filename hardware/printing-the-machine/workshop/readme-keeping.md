## Keeping the book

- **Pages** are the `NN-title.html` files here, numbered in reading order. Text is plain HTML; drawings are inline SVG, each with a
  title and a description. `style.css` holds every style.
- **Numbers.** A current setting appears in a page as `{{source:/json/pointer}}` and is filled from its owning file when the book is
  bound. [`guide-inputs.json`](guide-inputs.json) names the sources. A number from a dated trial is typed, with its date.
- **Pictures.** [`art/manifest.json`](art/manifest.json) lists each photograph with the file and Git revision it was copied from, and
  each model picture with the render job that drew it.
- **Binding.** `tools/run hsm-manual-guides bind printing-the-machine` draws every page, stops on any whose content overflows, and
  writes `printing-the-machine.pdf` here and in `output/pdf/`.
- **Adding a page.** Start from one print: its date, printer, plastic, plate and nozzle, and a photograph. Say what happened, the rule
  it taught and how far that has been tested. Put it in its plastic's part and link the record.
