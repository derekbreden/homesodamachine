# Manual shop guides

`hsm-manual-guides` authors the requested shop book, fixture or illustration from
typed source and current owning dimensions. These commands run on demand outside
the normal build.

```sh
tools/run -- cargo build --manifest-path tools/hsm/Cargo.toml --release --locked -j 2 -p hsm-manual-guides
hsm-manual-guides list
tools/run hsm-manual-guides bind tube-insertion-guide
tools/run hsm-manual-guides build faucet-assembly-guide
tools/run hsm-manual-guides markings refrigerant-warning
tools/run --cad -- hsm-manual-guides art tube-insertion-guide --list
```

`bind` renders and joins authored HTML leaves. `--reuse-leaves` uses their current
leaf PDFs, and `--pages` selects the leaves to render before joining the complete
book. `author magnetic-float-guide` fills the editable HTML templates from current
design and fabrication inputs.

`build` draws mold, refrigeration, faucet, water-inlet jet and PGFUN books through
`hsm-pages`. Their maintained content lives beside the book as typed page records
or owning Markdown procedures. `art` reads current component or retained print
meshes and draws only the selected operation pictures. `--scenes` selects names;
`--output` keeps a requested comparison outside the current deliverable.

The PGFUN book accepts `--reuse-art`. Its `--inputs DIR` option reads the retained
fixture inputs for a geometry comparison; the selected files are recorded in the
source receipt. `qa gun-positioner-guide` performs the requested release-binding
review and calls the installed native peripheral verifier.

`fixture tube-insertion` regenerates that fixture's printable solids and named
assembly. `fixture donor-hold-down` regenerates its separately scoped TPU hand pad
and contact view. `review tube-insertion` measures the travel and factory pad backing on
request. The physical acceptance record retains its own scope.

`markings refrigerant-warning` draws the maintained warning SVGs and full-size PDF
proof from Helvetica Bold outlines and the owning W021 artwork. It reads the Mac's
system Helvetica collection; `--inputs FILE` selects an explicit collection.
