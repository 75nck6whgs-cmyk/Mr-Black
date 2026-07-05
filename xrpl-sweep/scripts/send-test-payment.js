// Convenience script for proving the watcher works: funds a brand-new
// throwaway Testnet wallet and sends it a payment (with a destination tag,
// since the receiving account requires one) to the receiving account in
// your .env. Run this in a second terminal while `npm start` is running in
// the first, and watch the watcher's logs react.
//
// Usage: node scripts/send-test-payment.js [amountXrp] [destinationTag]

require("dotenv").config();
const { Client, Wallet } = require("xrpl");

async function main() {
  const amountXrp = process.argv[2] || "5";
  const destinationTag = Number(process.argv[3] || "12345");

  const receivingAddress = Wallet.fromSeed(process.env.RECEIVING_SEED).address;
  const wsUrl = process.env.XRPL_WS_URL || "wss://s.altnet.rippletest.net:51233";

  const client = new Client(wsUrl);
  await client.connect();

  console.log("Funding a throwaway test-payer wallet...");
  const { wallet: payer } = await client.fundWallet();

  console.log(`Sending ${amountXrp} XRP to ${receivingAddress} (tag ${destinationTag})...`);
  const prepared = await client.autofill({
    TransactionType: "Payment",
    Account: payer.address,
    Destination: receivingAddress,
    DestinationTag: destinationTag,
    Amount: String(Number(amountXrp) * 1_000_000),
  });
  const signed = payer.sign(prepared);
  const result = await client.submitAndWait(signed.tx_blob);

  console.log("Result:", result.result.meta.TransactionResult);
  console.log("Hash:  ", result.result.hash);
  await client.disconnect();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
