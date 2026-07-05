const { run } = require("./watcher");

run().catch((err) => {
  console.error("[watcher] fatal error:", err);
  process.exit(1);
});
