#!/usr/bin/env bash
# Installs system crontab entries for Mr. Noble Agency.
# Run once: bash cron_setup.sh
# Removes itself cleanly if re-run.

set -e
AGENCY_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$AGENCY_DIR/.venv/bin/python3"
LOG="$AGENCY_DIR/cron.log"

# Remove any existing Mr. Noble entries
crontab -l 2>/dev/null | grep -v "mr-noble" > /tmp/crontab_clean || true

# Add new entries
cat >> /tmp/crontab_clean << EOF

# mr-noble: morning pipeline (scout → checker)
0 6 * * * cd $AGENCY_DIR && $PYTHON orchestrate.py all >> $LOG 2>&1

# mr-noble: send approved leads
0 7 * * * cd $AGENCY_DIR && $PYTHON orchestrate.py pitcher >> $LOG 2>&1

# mr-noble: evening follow-up
0 18 * * * cd $AGENCY_DIR && $PYTHON orchestrate.py followup && $PYTHON orchestrate.py pitcher >> $LOG 2>&1
EOF

crontab /tmp/crontab_clean
rm /tmp/crontab_clean

echo "✓ Crontab installed:"
crontab -l | grep "mr-noble" -A1
echo ""
echo "Log file: $LOG"
echo "To remove: crontab -e (delete the mr-noble lines)"
