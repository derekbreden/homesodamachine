# Kitchen Edition enclosure shell

A six-walled PETG box, 3 mm walls, sized live to the bounding box of
[`../enclosure-contents-assembly/enclosure-contents-assembly.step`](../enclosure-contents-assembly/).
No penetrations modelled (no faucet hole, no AC inlet, no BiB adapter, no
condenser grilles, no funnel hole, no display pocket) — just the closed shell
that proves the contents fit a single-piece print inside the H2C left-nozzle
build envelope.

The production enclosure with all penetrations, panel splits, mounting bosses,
and door cutouts lives at [`../printed-parts/enclosure/`](../printed-parts/enclosure/).
This study is the bounding-box check that hands the production design its
maximum outer envelope.

## Regenerate

```
tools/cad-venv/bin/python hardware/enclosure/enclosure.py
```

→ `enclosure.step`. Wall thickness and interior clearance are at the top of
`enclosure.py`. Prints whether the outer envelope fits the H2C bed.
