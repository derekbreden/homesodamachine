import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { DIM, JOINT, CAP_TOP, WIRE_GUIDE_END, WIRE_TIP, GRIP_BASE, posePoint } from "../public/js/weld-position/pose.js";

const near = (a, b) => assert.ok(Math.abs(a - b) < 1e-9, `${a} ≠ ${b}`);
const distance = (a, b) => Math.hypot(...a.map((v, i) => v - b[i]));

test("the unrolled barrel and wire both approach along the tangent in plan", () => {
  for (const p of [[0, 0, 0], [0, 0, DIM.gunLength], WIRE_GUIDE_END, WIRE_TIP]) {
    near(posePoint(p, 0)[0], JOINT[0]);
  }
  assert.ok(posePoint([0, 0, DIM.gunLength], 0)[1] < posePoint([0, 0, 0], 0)[1]);
  assert.ok(posePoint(WIRE_GUIDE_END, 0)[1] < JOINT[1]);
});

test("roll fixes the laser dot, grip base and straight wire approach", () => {
  for (const roll of [0, 15, 35, 60, 80]) {
    posePoint(WIRE_TIP, roll).forEach((v, i) => near(v, JOINT[i]));
    for (const p of [GRIP_BASE, WIRE_GUIDE_END]) {
      posePoint(p, roll).forEach((v, i) => near(v, posePoint(p, 0)[i]));
      near(posePoint(p, roll)[0], JOINT[0]);
    }
    if (roll > 0) {
      assert.ok(posePoint([0, 0, 0], roll)[0] < JOINT[0]);
      assert.ok(posePoint([0, 0, 0], roll)[2] > CAP_TOP);
    }
  }
});

test("the hole-axis rotation fixes the dot and raises the tangent approach", () => {
  for (const roll of [0, 35, 80]) {
    const reference = posePoint(GRIP_BASE, roll);
    for (const holeRoll of [-60, -25, 0, 25, 60]) {
      posePoint(WIRE_TIP, roll, holeRoll).forEach((v, i) => near(v, JOINT[i]));
      const base = posePoint(GRIP_BASE, roll, holeRoll);
      near(base[0], JOINT[0]);
      near(distance(base, JOINT), distance(reference, JOINT));
      if (holeRoll > 0) assert.ok(base[2] > reference[2]);
      if (holeRoll < 0) assert.ok(base[2] < reference[2]);
    }
    // A quarter-turn around the cap diameter exchanges height and tangent
    // distance, with the dot's elevation as the origin and no radial travel.
    const quarterTurn = posePoint(GRIP_BASE, roll, 90);
    near(quarterTurn[0], reference[0]);
    near(quarterTurn[1], reference[2] - CAP_TOP);
    near(quarterTurn[2], CAP_TOP - reference[1]);
  }
});

test("grip-axis roll keeps the selected base and wire line fixed at every hole-axis tilt", () => {
  for (const holeRoll of [-60, 0, 30, 60]) {
    for (const roll of [0, 35, 80]) {
      for (const p of [GRIP_BASE, WIRE_GUIDE_END, WIRE_TIP]) {
        const actual = posePoint(p, roll, holeRoll), reference = posePoint(p, 0, holeRoll);
        actual.forEach((v, i) => near(v, reference[i]));
        near(actual[0], JOINT[0]);
      }
    }
  }
});

test("gun, guide and wire undergo one rigid rotation without a reflection", () => {
  const points = [[0, 0, 0], GRIP_BASE, WIRE_GUIDE_END, WIRE_TIP];
  for (const roll of [0, 35, 80]) for (const holeRoll of [-60, 0, 60]) {
    for (const a of points) for (const b of points) near(distance(a, b), distance(posePoint(a, roll, holeRoll), posePoint(b, roll, holeRoll)));
    const origin = posePoint([0, 0, 0], roll, holeRoll);
    const [a, b, c] = [[1, 0, 0], [0, 1, 0], [0, 0, 1]].map(p => posePoint(p, roll, holeRoll).map((v, i) => v - origin[i]));
    near(a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0]), 1);
  }
});

test("tube and cap dimensions agree with the fabrication sources", () => {
  const repo = fileURLToPath(new URL("../../", import.meta.url));
  const actual = JSON.parse(execFileSync("python3", ["-c", `
import ast, json, runpy
from pathlib import Path
root = Path(${JSON.stringify(repo)})
interface = runpy.run_path(str(root / 'hardware/printed-parts/fixtures/weld-rotator/_rotator_interface.py'))
cap = ast.parse((root / 'hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_dxf.py').read_text())
values = {}
for node in cap.body:
    if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
        for target in node.targets:
            if isinstance(target, ast.Name): values[target.id] = node.value.value
print(json.dumps(dict(
    tubeOd=interface['TUBE_OD'], tubeWall=interface['TUBE_WALL'],
    tubeHeight=interface['TUBE_LENGTH'], capRecess=interface['ENDCAP_RECESS'],
    capDiameter=values['disc_diameter']*25.4, capThickness=values['disc_thickness']*25.4,
    portDiameter=values['hole_diameter']*25.4, portOffset=values['hole_spacing']*25.4/2,
)))
`], { encoding: "utf8" }));
  for (const [key, value] of Object.entries(actual)) near(DIM[key], value);
});
