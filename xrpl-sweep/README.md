# XRPL sweep service

Watches a receiving XRP account and automatically forwards incoming payments
to a main (treasury) account, keeping the receiving account's reserve intact.
This is an always-on Node process — it does not run on GitHub Pages and needs
its own host (see "Hosting" below).

Runs on plain XRP mainnet or Testnet, not Xahau/Hooks — see the design
discussion this came out of for why.

## How it works

- `src/watcher.js` subscribes to the receiving account over the XRPL
  websocket and reacts to each validated incoming `Payment`.
- `src/sweep.js` figures out how much can safely be swept (balance minus the
  network's required reserve, minus a configurable safety buffer, minus fee
  headroom) and submits a `Payment` to the main account for that amount.
- `src/state.js` tracks processed transaction hashes so a restart never
  double-sweeps, and appends every sweep to `data/sweeps.log` for
  reconciliation (pair the destination tag on the incoming payment with the
  sweep it triggered).

## Setup (Testnet first — do not skip this)

1. `npm install`
2. `node scripts/setup-testnet-accounts.js` — generates and faucet-funds a
   receiving + main account pair on Testnet, turns on `RequireDestinationTag`
   on the receiving account, and prints the values to paste into `.env`.
3. `cp .env.example .env` and fill in the printed values.
4. `npm start` — leave it running.
5. From a wallet/tool of your own, send a Testnet payment to the receiving
   address **with a destination tag** (required, since step 2 turned that
   flag on). Watch the process log the incoming payment and the sweep.
6. Check `data/sweeps.log` — each line pairs the incoming hash, the tag, and
   the sweep hash.

Only after this works reliably on Testnet should the same accounts/process be
recreated on mainnet with real funds.

## Important: this has not been run end-to-end yet

I wrote and unit-tested the reserve/buffer arithmetic (`scripts/test-sweep-math.js`,
using a mocked client), but **I could not run the live Testnet flow above**
from the sandbox this was built in — its network policy explicitly blocks
WebSocket connections and non-443 ports, which is exactly what XRPL requires.
That means the `account_info` / `server_state` / `subscribe` calls in
`src/sweep.js` and `src/watcher.js` are based on documented XRPL/xrpl.js
behavior but have not been exercised against a real server. Run the Testnet
setup above from an environment with normal network access before trusting
this with real money, and watch for the transaction-stream event shape in
particular (`extractPaymentTx` in `watcher.js` handles two known shapes, but
confirm against your rippled server's actual API version).

## Configuration (`.env`)

| Var | Meaning |
|---|---|
| `XRPL_WS_URL` | Testnet: `wss://s.altnet.rippletest.net:51233`. Mainnet: `wss://xrplcluster.com` (or your own node). |
| `RECEIVING_SEED` | Secret seed of the receiving account. Only this process should ever hold it. |
| `MAIN_ACCOUNT_ADDRESS` | Address only — this process never holds the main account's key. |
| `SWEEP_RESERVE_BUFFER_XRP` | Extra XRP left behind above the network reserve, as a safety margin. |

## Hosting

Needs an always-on process (holds an open websocket subscription), so a
serverless function won't work — a small VPS or a background-worker platform
(Fly.io, Render, etc.) is the right shape. Whatever host you pick, treat
`RECEIVING_SEED` as the most sensitive value in this whole project: anyone
with it can drain the receiving account.
