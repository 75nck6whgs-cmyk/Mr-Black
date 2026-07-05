const { xrpToDrops } = require("xrpl");

// Extra headroom (in drops) held back on top of the reserve/buffer so the
// autofilled network fee never pushes the receiving account below reserve.
const FEE_HEADROOM_DROPS = 50n;

async function getSweepableDrops(client, address, bufferXrp) {
  const [accountInfo, serverState] = await Promise.all([
    client.request({ command: "account_info", account: address, ledger_index: "validated" }),
    client.request({ command: "server_state" }),
  ]);

  const balanceDrops = BigInt(accountInfo.result.account_data.Balance);
  const ownerCount = BigInt(accountInfo.result.account_data.OwnerCount || 0);
  const { reserve_base_xrp, reserve_inc_xrp } = serverState.result.state.validated_ledger;
  const requiredReserveDrops = BigInt(xrpToDrops(reserve_base_xrp)) + ownerCount * BigInt(xrpToDrops(reserve_inc_xrp));
  const bufferDrops = BigInt(xrpToDrops(bufferXrp));

  const sweepable = balanceDrops - requiredReserveDrops - bufferDrops - FEE_HEADROOM_DROPS;
  return sweepable > 0n ? sweepable : 0n;
}

async function sweep(client, wallet, mainAccountAddress, bufferXrp) {
  const sweepableDrops = await getSweepableDrops(client, wallet.address, bufferXrp);
  if (sweepableDrops <= 0n) return null;

  const prepared = await client.autofill({
    TransactionType: "Payment",
    Account: wallet.address,
    Destination: mainAccountAddress,
    Amount: sweepableDrops.toString(),
  });
  const signed = wallet.sign(prepared);
  const result = await client.submitAndWait(signed.tx_blob);

  return {
    engineResult: result.result.meta.TransactionResult,
    hash: result.result.hash,
    amountDrops: sweepableDrops.toString(),
  };
}

module.exports = { getSweepableDrops, sweep };
