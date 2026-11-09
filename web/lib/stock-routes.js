// The local stock workbench records completions, receipts and counts without exposing writes on the public site.
import path from "node:path";
import { fileURLToPath } from "node:url";
import { materialIndex } from "../contracts/materials.js";
import { readMaterialCatalog } from "./material-catalog.js";
import { readMaterialStock, stockMaterialUnit } from "./material-stock.js";
import {
  completionProposal,
  recordStockEvent,
  publishStockLedger,
  stockTarget,
} from "./stock-operations.js";

const repoRoot = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../..",
);
export function mountStockRoutes(app, { hardwareDir, enabled = false }) {
  if (!enabled) return;
  const local = (req, res, next) => {
    const address = req.socket.remoteAddress;
    if (!["127.0.0.1", "::1", "::ffff:127.0.0.1"].includes(address))
      return res.status(403).json({ error: "Record stock from this Mac" });
    if (req.get("Origin")) {
      try {
        if (new URL(req.get("Origin")).host !== req.get("Host"))
          return res
            .status(403)
            .json({ error: "Open the local workbench before recording stock" });
      } catch {
        return res.status(403).json({ error: "Invalid origin" });
      }
    }
    next();
  };
  function catalog() {
    const value = readMaterialCatalog(hardwareDir);
    value.stock = readMaterialStock(hardwareDir, value);
    return value;
  }
  app.get("/api/stock/entry", local, (req, res) => {
    try {
      const value = catalog(),
        quantity = req.query.quantity == null ? 1 : Number(req.query.quantity),
        finish = req.query.finish === "black" ? "black" : "white";
      const material = String(req.query.material || value.cost_root);
      const targets = [
        ...value.materials.map((item) => ({
          target: stockTarget(value, item.id, finish),
          label: item.description + " · " + item.id,
          unit: stockMaterialUnit(value, item.id),
          group: "Parts and assemblies",
        })),
        ...Object.values(value.stock.resources).map((item) => ({
          target: { resource: item.id },
          label: item.name,
          unit: item.unit,
          group: "Stock and supplies",
          available: item.available,
          incoming: item.incoming,
          estimated: item.estimated,
        })),
      ];
      for (const item of targets)
        if (item.target.resource) {
          const stock = value.stock.resources[item.target.resource];
          Object.assign(item, {
            unit: stock.unit,
            available: stock.available,
            incoming: stock.incoming,
            estimated: stock.estimated,
          });
        } else {
          const stock =
            value.stock.materials[
              item.target.material +
                (item.target.finish ? ":" + item.target.finish : "")
            ];
          item.available = stock?.available ?? null;
        }
      res.set("Cache-Control", "no-store").json({
        proposal:
          materialIndex(value).get(material)?.kind === "purchased"
            ? null
            : completionProposal(value, material, quantity, finish),
        selectedTarget: stockTarget(value, material, finish),
        targets,
      });
    } catch (error) {
      res.status(400).json({ error: error.message });
    }
  });
  app.post("/api/stock/events", local, async (req, res) => {
    let result;
    try {
      result = recordStockEvent(hardwareDir, req.body);
    } catch (error) {
      return res.status(400).json({ error: error.message });
    }
    if (path.resolve(hardwareDir) === path.join(repoRoot, "hardware")) {
      try {
        await publishStockLedger(hardwareDir, result.event);
        result.published = true;
      } catch (error) {
        result.published = false;
        result.publishError = "Saved locally; publication needs retrying.";
      }
    }
    res.status(201).json({ ...result, recorded: true });
  });
  app.post("/api/stock/publish", local, async (_req, res) => {
    try {
      res.json(await publishStockLedger(hardwareDir));
    } catch (error) {
      res.status(409).json({
        error:
          "The stock record is saved locally; publication could not finish.",
      });
    }
  });
}
