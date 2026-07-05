const fs = require("fs");
const path = require("path");

const DATA_DIR = path.join(__dirname, "..", "data");
const PROCESSED_FILE = path.join(DATA_DIR, "processed.json");
const SWEEP_LOG = path.join(DATA_DIR, "sweeps.log");

function ensureDataDir() {
  if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
  if (!fs.existsSync(PROCESSED_FILE)) fs.writeFileSync(PROCESSED_FILE, "[]");
}

function loadProcessed() {
  ensureDataDir();
  return new Set(JSON.parse(fs.readFileSync(PROCESSED_FILE, "utf8")));
}

function markProcessed(txHash, processedSet) {
  processedSet.add(txHash);
  fs.writeFileSync(PROCESSED_FILE, JSON.stringify([...processedSet], null, 2));
}

function appendSweepLog(entry) {
  ensureDataDir();
  fs.appendFileSync(SWEEP_LOG, JSON.stringify({ at: new Date().toISOString(), ...entry }) + "\n");
}

module.exports = { loadProcessed, markProcessed, appendSweepLog };
