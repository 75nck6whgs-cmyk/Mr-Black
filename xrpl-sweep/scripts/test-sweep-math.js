// Offline check of the reserve/buffer arithmetic in src/sweep.js, using a
// fake client instead of a live XRPL connection (this sandbox's network
// policy blocks the WebSocket connections XRPL needs — see README).
const assert = require("assert");
const { getSweepableDrops } = require("../src/sweep");

function fakeClient({ balanceXrp, ownerCount, reserveBaseXrp, reserveIncXrp }) {
  return {
    request: async ({ command }) => {
      if (command === "account_info") {
        return {
          result: {
            account_data: {
              Balance: String(BigInt(Math.round(balanceXrp * 1e6))),
              OwnerCount: ownerCount,
            },
          },
        };
      }
      if (command === "server_state") {
        return {
          result: {
            state: {
              validated_ledger: {
                reserve_base_xrp: reserveBaseXrp,
                reserve_inc_xrp: reserveIncXrp,
              },
            },
          },
        };
      }
      throw new Error(`unexpected command ${command}`);
    },
  };
}

async function main() {
  // 100 XRP balance, 10 XRP base reserve, 0 owned objects, 2 XRP buffer
  // -> sweepable should be 100 - 10 - 2 = 88 XRP minus fee headroom (50 drops)
  const client1 = fakeClient({ balanceXrp: 100, ownerCount: 0, reserveBaseXrp: 10, reserveIncXrp: 2 });
  const drops1 = await getSweepableDrops(client1, "rFAKE", 2);
  assert.strictEqual(drops1, 88_000_000n - 50n, "basic sweep amount");
  console.log("PASS: basic sweep amount ->", drops1.toString(), "drops");

  // Balance right at reserve + buffer -> nothing sweepable
  const client2 = fakeClient({ balanceXrp: 12, ownerCount: 0, reserveBaseXrp: 10, reserveIncXrp: 2 });
  const drops2 = await getSweepableDrops(client2, "rFAKE", 2);
  assert.strictEqual(drops2, 0n, "at-reserve balance sweeps nothing");
  console.log("PASS: at-reserve balance ->", drops2.toString(), "drops");

  // Owned objects increase required reserve
  const client3 = fakeClient({ balanceXrp: 100, ownerCount: 3, reserveBaseXrp: 10, reserveIncXrp: 2 });
  const drops3 = await getSweepableDrops(client3, "rFAKE", 2);
  // required reserve = 10 + 3*2 = 16, buffer 2 -> sweepable = 100-16-2=82 minus fee headroom
  assert.strictEqual(drops3, 82_000_000n - 50n, "owner count raises required reserve");
  console.log("PASS: owner count raises reserve ->", drops3.toString(), "drops");

  console.log("\nAll sweep-math checks passed.");
}

main().catch((err) => {
  console.error("FAIL:", err.message);
  process.exit(1);
});
