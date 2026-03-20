#!/bin/bash
# Daily restaurant research and commit script

set -e

REPO_DIR="/root/.openclaw/workspace/seattle-dinner-finder"
DATE=$(date +%Y-%m-%d)
DATA_FILE="$REPO_DIR/data/$DATE.json"

# GitHub token should be set as environment variable
GITHUB_TOKEN="${GITHUB_TOKEN:-}"

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Error: GITHUB_TOKEN environment variable not set"
    exit 1
fi

echo "🔍 Researching restaurants for $DATE..."

# TODO: This will be replaced with actual OpenClaw API call
# For now, create sample data
cat > "$DATA_FILE" << 'EOF'
[
  {
    "name": "Revel",
    "neighborhood": "Fremont",
    "cuisine": "Korean Fusion",
    "price": "$$",
    "vibes": ["🎉 Lively", "🔥 Open Kitchen", "🍜 Shareable"],
    "address": "401 N 36th St",
    "phone": "(206) 547-2040",
    "reservationUrl": "https://www.opentable.com/r/revel-seattle",
    "availability": "available",
    "whyFun": "A quintessential Seattle spot with a massive open kitchen. Chef Rachel Yang's creative Korean comfort food is perfect for sharing, and the energy is always buzzing."
  }
]
EOF

echo "✅ Research complete"

# Commit and push to GitHub
cd "$REPO_DIR"

# Configure git
git config user.name "OpenClaw Bot"
git config user.email "bot@openclaw.local"

# Add the data file
git add "data/$DATE.json"

# Commit if there are changes
if git diff --cached --quiet; then
    echo "📋 No changes to commit"
else
    git commit -m "Add restaurant data for $DATE"
    
    # Push using the token
    git push "https://mango-codes:${GITHUB_TOKEN}@github.com/mango-codes/seattle-dinner-finder.git" main
    echo "🚀 Pushed to GitHub!"
fi

echo "✅ Done! Site will update automatically."
