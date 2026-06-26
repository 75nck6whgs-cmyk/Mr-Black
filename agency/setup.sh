#!/usr/bin/env bash
# One-command setup for Mr. Noble Agency system
set -e

echo "=== Mr. Noble Agency Setup ==="

# 1. Python venv
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  echo "✓ Created .venv"
fi
source .venv/bin/activate

# 2. Dependencies
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# 3. .env file
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "✓ Created .env — fill in your API keys"
else
  echo "✓ .env already exists"
fi

# 4. State directories
for d in leads diagnosed built filmed checked approved rejected sent; do
  mkdir -p "state/$d"
done
echo "✓ State directories ready"

echo ""
echo "Next steps:"
echo "  1. Edit .env and add your API keys"
echo "  2. Edit config.yaml — set your cities and agency name"
echo "  3. Run the pipeline:  python orchestrate.py"
echo "  4. Review leads:      python approve.py"
echo "  5. Send pitches:      python orchestrate.py pitcher"
echo "  6. Mobile UI:         python -m agents.mobile.app"
echo ""
echo "Revenue target: 47 clients × \$400 = \$18,800/month"
echo "Real cost: API tokens + subscriptions ≈ \$480/month"
