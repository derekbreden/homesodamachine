# SolidCraft workflow study

This study exercises native SolidCraft features, parameter edits, GUI editing and manufacturing exports on standalone demonstration parts.

Open [`native-plate.sc`](native-plate.sc) or [`native-case.sc`](native-case.sc) in SolidCraft. Click **Parameters** in the Model toolbar to edit the favorites. The History strip exposes the features that construct each part.

The plate has a rounded outline, mounting holes and an engraved text parameter. Its starting blank uses the rear nameplate's envelope from [`rear_wall.rs`](../../../printed-parts/enclosure/enclosure/numbers/rear_wall.rs). Hole offsets follow its dimensions. It is a workflow example; production artwork, mounting details and the receiver belong to the production nameplate.

The enclosure coupon has a shelled rounded body, a continuous upper round, mounting bosses with blind holes and a cable opening. Its dimensions, wall stock, corner radius and boss height are parameters. The bosses use native cylinder and hole features. Each corner boss follows its adjacent walls.

[`gui-edited-case.sc`](gui-edited-case.sc) holds the enclosure edited through the running app. [`gui-edited-case.json`](gui-edited-case.json) is the same editable design exported as plain JSON; the headless engine rebuilds it from its parameters and features. This JSON is a design document, while the `commands` lists in the creation examples are command scripts.

## Commands

The creation examples use the commands exposed by the installed app's registry. Run them from the repository root:

```sh
python3 tools/run.py -- solidcraft-cli run hardware/manifold-layout/studies/solidcraft-workflow/native-plate.json --save output/solidcraft-demo/plate.sc --out output/solidcraft-demo/plate.step --out output/solidcraft-demo/plate.stl
python3 tools/run.py -- solidcraft-cli run hardware/manifold-layout/studies/solidcraft-workflow/native-case.json --save output/solidcraft-demo/case.sc --out output/solidcraft-demo/case.step --out output/solidcraft-demo/case.stl
```

The output folder must exist. The edit examples apply parameter changes to a saved design:

```sh
python3 tools/run.py -- solidcraft-cli run hardware/manifold-layout/studies/solidcraft-workflow/edit-case.json --in hardware/manifold-layout/studies/solidcraft-workflow/native-case.sc --save output/solidcraft-demo/edited-case.sc --out output/solidcraft-demo/edited-case.stl
```

In the app, File → Save keeps an editable native design; File → Export can write STEP, STL or the plain JSON design. Agents can inspect and change the same parameters and features through the command engine or MCP.

## Evaluation

[`evaluation.json`](evaluation.json) identifies the tested release, input and output hashes, timings, exported-solid checks and observed limits. Timings distinguish command execution from a request to the running GUI. These examples establish a native editing and export workflow; they do not establish whole-enclosure compatibility or a speed comparison with the production build.

The tested release refuses feature patterns of its plastic-boss feature and command-script export of component designs. Plain JSON design export and headless rebuilding work. The production quadrant STEP tested here contains triangulated surfaces and is refused by this release's STEP importer as having no solids.

SolidCraft's [architecture](https://github.com/tangency-labs/solidcraft/blob/main/docs/architecture.md) describes its shared command engine and incremental document. Its [roadmap](https://github.com/tangency-labs/solidcraft/blob/main/ROADMAP.md) tracks the modeling kernel and assembly work. The [plugin document](https://github.com/tangency-labs/solidcraft/blob/main/docs/plugins.md) is a design for custom parametric features; the study uses the existing native commands.
