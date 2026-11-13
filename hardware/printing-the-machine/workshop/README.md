# Workshop of "Printing the Machine"

The generator that drew the book's first pages, the brief its chapter writers worked from, and the
research they started from. The book's pages are the HTML files one folder up, and they are edited
directly. Nothing here is needed to bind the book.

- `AUTHORING.md`: the brief. Voice, scope, facts and the kit.
- `bookkit.py`, `svgkit.py`, `proj.py`: pages, photographs, model pictures and bound settings;
  drawings; callouts placed on a model picture.
- `build.py`, `measure.mjs`, `check.py`, `publish.py`: build a chapter or the whole book; size each
  picture to its page and scale an overfull page to fit; check every quote and evidence link against
  the repository; copy the result into `hardware/printing-the-machine/`.
- `chapters/`: one Python module per chapter. A page is a function.
- `dig/`: research reports by area, and Derek's remarks on printing with the commit that carries
  each. These are leads. Every fact was checked against the record before a page used it, and the
  reports contain errors.

The scripts take the repository root to be three folders above them, as when this folder sits at
`.cache/runs/<name>/` in a checkout. There, `python3 build.py all` draws the book.
