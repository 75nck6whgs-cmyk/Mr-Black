require("dotenv").config();

function required(name) {
  const value = process.env[name];
  if (!value) throw new Error(`Missing required env var: ${name}`);
  return value;
}

module.exports = {
  wsUrl: process.env.XRPL_WS_URL || "wss://s.altnet.rippletest.net:51233",
  receivingSeed: required("RECEIVING_SEED"),
  mainAccountAddress: required("MAIN_ACCOUNT_ADDRESS"),
  sweepReserveBufferXrp: Number(process.env.SWEEP_RESERVE_BUFFER_XRP || "2"),
};
