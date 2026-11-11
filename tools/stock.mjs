#!/usr/bin/env node
// Stock commands plan and record physical activity through the shared ledger writer.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { readMaterialCatalog } from "../web/lib/material-catalog.js";
import { readMaterialStock } from "../web/lib/material-stock.js";
import {
  completionProposal,
  recordStockEvent,
  publishStockLedger,
} from "../web/lib/stock-operations.js";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), ".."),
  hardware = path.join(root, "hardware");
const [command, ...args] = process.argv.slice(2);
try {
  if (command === "plan") {
    const value = readMaterialCatalog(hardware);
    value.stock = readMaterialStock(hardware, value);
    const quantityIndex = args.indexOf("--quantity"),
      quantity = quantityIndex < 0 ? 1 : Number(args[quantityIndex + 1]);
    console.log(
      JSON.stringify(
        completionProposal(
          value,
          args[0],
          quantity,
          args.includes("--black") ? "black" : "white",
        ),
        null,
        2,
      ),
    );
  } else if (command === "record") {
    const result = recordStockEvent(
      hardware,
      JSON.parse(fs.readFileSync(path.resolve(args[0]), "utf8")),
    );
    if (args.includes("--publish"))
      Object.assign(result, await publishStockLedger(hardware, result.event));
    console.log(JSON.stringify(result, null, 2));
  } else if (command === "publish") {
    console.log(JSON.stringify(await publishStockLedger(hardware), null, 2));
  } else {
    console.log(
      "Use plan MATERIAL [--quantity QTY] [--black], record EVENT.json [--publish], or publish.",
    );
    process.exitCode = command ? 1 : 0;
  }
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
