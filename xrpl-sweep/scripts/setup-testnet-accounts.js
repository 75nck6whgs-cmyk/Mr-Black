// One-time helper: generates and faucet-funds a receiving + main account pair
// on XRPL Testnet, and turns on RequireDestinationTag for the receiving
// account so untagged payments are rejected instead of silently unattributed.
//
// Usage: node scripts/setup-testnet-accounts.js
// Prints the values to paste into .env. Testnet funds only, not real money.

const { Client } = require("xrpl");

const WS_URL = "wss://s.altnet.rippletest.net:51233";

async function main() {
  const client = new Client(WS_URL);
  await client.connect();

  console.log("Funding receiving account via faucet...");
  const { wallet: receiving } = await client.fundWallet();

  console.log("Funding main account via faucet...");
  const { wallet: main } = await client.fundWallet();

  console.log("Setting RequireDestinationTag on receiving account...");
  const prepared = await client.autofill({
    TransactionType: "AccountSet",
    Account: receiving.address,
    SetFlag: 1, // asfRequireDest
  });
  const signed = receiving.sign(prepared);
  const result = await client.submitAndWait(signed.tx_blob);
  console.log("AccountSet result:", result.result.meta.TransactionResult);

  await client.disconnect();

  console.log("\n=== Paste into xrpl-sweep/.env ===");
  console.log(`XRPL_WS_URL=${WS_URL}`);
  console.log(`RECEIVING_SEED=${receiving.seed}`);
  console.log(`MAIN_ACCOUNT_ADDRESS=${main.address}`);
  console.log("\n=== Keep for your own records (Testnet only) ===");
  console.log(`Receiving address: ${receiving.address}`);
  console.log(`Main address:      ${main.address}`);
  console.log(`Main seed:         ${main.seed}  (not needed by the watcher — it never signs)`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
