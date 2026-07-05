const { Client, Wallet } = require("xrpl");
const config = require("./config");
const { loadProcessed, markProcessed, appendSweepLog } = require("./state");
const { sweep } = require("./sweep");

function extractPaymentTx(event) {
  // rippred's `transaction` stream nests fields under tx_json on newer API
  // versions, and flat on older ones. Support both.
  const tx = event.tx_json || event.transaction || event;
  const meta = event.meta || event.meta_blob;
  return { tx, meta, validated: event.validated };
}

async function run() {
  const wallet = Wallet.fromSeed(config.receivingSeed);
  const processed = loadProcessed();

  const client = new Client(config.wsUrl);
  await client.connect();
  console.log(`[watcher] connected to ${config.wsUrl}`);
  console.log(`[watcher] watching receiving account ${wallet.address}`);
  console.log(`[watcher] sweeping to main account ${config.mainAccountAddress}`);

  await client.request({ command: "subscribe", accounts: [wallet.address] });

  client.on("transaction", async (event) => {
    try {
      const { tx, meta, validated } = extractPaymentTx(event);
      if (!validated) return;
      if (tx.TransactionType !== "Payment") return;
      if (tx.Destination !== wallet.address) return;
      if (meta.TransactionResult !== "tesSUCCESS") return;

      const hash = tx.hash || event.hash;
      if (!hash || processed.has(hash)) return;

      console.log(`[watcher] incoming payment ${hash} from ${tx.Account} (tag ${tx.DestinationTag ?? "none"})`);
      markProcessed(hash, processed);

      const result = await sweep(client, wallet, config.mainAccountAddress, config.sweepReserveBufferXrp);
      if (!result) {
        console.log("[watcher] nothing sweepable after reserve/buffer, skipping");
        appendSweepLog({ incomingHash: hash, swept: false });
        return;
      }

      console.log(`[watcher] swept ${result.amountDrops} drops -> ${result.hash} (${result.engineResult})`);
      appendSweepLog({
        incomingHash: hash,
        sourceTag: tx.DestinationTag ?? null,
        sweepHash: result.hash,
        amountDrops: result.amountDrops,
        engineResult: result.engineResult,
        swept: true,
      });
    } catch (err) {
      console.error("[watcher] error handling transaction event:", err);
    }
  });

  process.on("SIGINT", async () => {
    console.log("\n[watcher] shutting down");
    await client.disconnect();
    process.exit(0);
  });
}

module.exports = { run };
