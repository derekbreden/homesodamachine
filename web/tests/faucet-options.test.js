import { test } from "node:test";
import assert from "node:assert/strict";
import { FAUCET_STYLES, FAUCET_FINISHES, faucetStyleFor, hasFaucetFinish, isFaucetFinishBody, showsInFaucetFinish } from "../contracts/faucet-options.js";
import { sourceFileFor } from "../contracts/component-sources.js";

const [sculpted, industrial] = FAUCET_STYLES;
const files = [...new Set(FAUCET_STYLES.flatMap((s) => [s.assembly, ...Object.values(s.parts)]))];

test("faucet styles name distinct assemblies and share the printable neck tip", () => {
  assert.deepEqual(FAUCET_STYLES.map((s) => s.label), ["Sculpted", "Industrial"]);
  assert.notEqual(sculpted.assembly, industrial.assembly);
  assert.equal(sculpted.parts.shell_tip, industrial.parts.shell_tip);
  assert.equal(faucetStyleFor(industrial.assembly), industrial);
  assert.equal(faucetStyleFor("manifold-layout/enclosure-assembly.step"), null);
  assert.deepEqual(FAUCET_FINISHES.map((f) => f.label), ["Black", "White"]);
});

test("part drilldown uses the owning faucet style, including the seated cover", () => {
  for (const style of FAUCET_STYLES) {
    for (const [name, part] of Object.entries(style.parts)) {
      assert.equal(sourceFileFor(name, files, style.assembly), part);
      assert.equal(sourceFileFor(`faucet/${name}`, files, style.assembly), part);
    }
  }
  assert.equal(sourceFileFor("shell_base", [], industrial.assembly), null);
  assert.equal(sourceFileFor("display-cover", files, "manifold-layout/enclosure-assembly.step"), null);
});

test("finish includes the faucet exterior, lever, dispense tubes and above-counter gasket", () => {
  for (const style of FAUCET_STYLES) {
    for (const name of ["shell_base", "shell_tip", "faucet-display-cover-seated", "above_counter_plate", "above_counter_gasket"]) {
      assert.ok(isFaucetFinishBody(style.assembly, name));
      assert.ok(hasFaucetFinish(style.parts[name]));
    }
    for (const name of ["lever", "soda_faucet_tube", "flavor_tube_pos_x", "flavor_tube_neg_x"]) {
      assert.ok(isFaucetFinishBody(style.assembly, name), name);
    }
    for (const name of ["westbrass", "faucet_display", "faucet_display_screen", "soda_umbilical_tube", "umbilical_sleeve", "under_counter_plate", "display-cover",
                        "flavor_umbilical_tube_pos_x", "flavor_umbilical_tube_neg_x", "flavor_union_pos_x", "flavor_tube_bridge_neg_x"]) {
      assert.equal(isFaucetFinishBody(style.assembly, name), false, name);
    }
  }
  assert.equal(isFaucetFinishBody("manifold-layout/enclosure-assembly.step", "shell_base"), false);
});

test("a White faucet shows its two flavor unions and a Black faucet its bridges, and neither the other's", () => {
  for (const style of FAUCET_STYLES) {
    for (const side of ["pos_x", "neg_x"]) {
      assert.equal(showsInFaucetFinish(style.assembly, `flavor_union_${side}`, "white"), true);
      assert.equal(showsInFaucetFinish(style.assembly, `flavor_union_${side}`, "black"), false);
      assert.equal(showsInFaucetFinish(style.assembly, `flavor_tube_bridge_${side}`, "black"), true);
      assert.equal(showsInFaucetFinish(style.assembly, `flavor_tube_bridge_${side}`, "white"), false);
      for (const finish of ["black", "white"]) {
        for (const name of [`flavor_tube_${side}`, `flavor_umbilical_tube_${side}`, "shell_base", "umbilical_sleeve"]) {
          assert.equal(showsInFaucetFinish(style.assembly, name, finish), true, `${name} ${finish}`);
        }
      }
    }
  }
  assert.equal(showsInFaucetFinish("manifold-layout/enclosure-assembly.step", "flavor_union_pos_x", "black"), true);
  assert.equal(showsInFaucetFinish(null, "flavor_tube_bridge_pos_x", "white"), true);
});
