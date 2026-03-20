#!/bin/bash
# Daily restaurant research and commit script with live availability checking

set -e

REPO_DIR="/root/.openclaw/workspace/seattle-dinner-finder"
DATE=$(date +%Y-%m-%d)
RAW_DATA_FILE="$REPO_DIR/data/$DATE-raw.json"
DATA_FILE="$REPO_DIR/data/$DATE.json"
SCRAPER_DIR="$REPO_DIR/scraper"

# GitHub token should be set as environment variable
GITHUB_TOKEN="${GITHUB_TOKEN:-}"

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Error: GITHUB_TOKEN environment variable not set"
    exit 1
fi

echo "🔍 Researching restaurants for $DATE..."

# Check if scrapling is installed
if ! python3 -c "import scrapling" 2>/dev/null; then
    echo "📦 Installing scrapling..."
    python3 -m pip install -q scrapling
fi

# Run the batch availability checker
echo "🌐 Checking live availability on OpenTable, Resy, Tock..."
cd "$SCRAPER_DIR"
python3 batch_check.py --date "$DATE" --party-size 2 --output "$RAW_DATA_FILE"

# Convert to site format
echo "🔄 Converting to site format..."
python3 convert_format.py --input "$RAW_DATA_FILE" --output "$DATA_FILE"

echo "✅ Research complete"

# Commit and push to GitHub
cd "$REPO_DIR"

# Configure git
git config user.name "OpenClaw Bot"
git config user.email "bot@openclaw.local"

# Add the data file
git add "data/$DATE.json"
git add "data/$DATE-raw.json"

# Commit if there are changes
if git diff --cached --quiet; then
    echo "📋 No changes to commit"
else
    git commit -m "Add restaurant data for $DATE with live availability"
    
    # Push using the token
    git push "https://mango-codes:${GITHUB_TOKEN}@github.com/mango-codes/seattle-dinner-finder.git" main
    echo "🚀 Pushed to GitHub!"
fi

echo "✅ Done! Site will update automatically."
