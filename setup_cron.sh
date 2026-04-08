#!/bin/bash
# Sets up a daily cron job to run the Amazon price tracker at 08:00.
# Run once from the project root: bash setup_cron.sh

PROJECT="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$(which python3)"
LOGFILE="$PROJECT/tracker.log"
CRON_CMD="0 8 * * * cd \"$PROJECT\" && \"$PYTHON\" advanced/main.py >> \"$LOGFILE\" 2>&1"

echo "Project : $PROJECT"
echo "Python  : $PYTHON"
echo "Log     : $LOGFILE"
echo ""

# Check .env exists
if [ ! -f "$PROJECT/.env" ]; then
    echo "ERROR: .env not found."
    echo "Copy .env.example to .env and fill in your Gmail credentials first:"
    echo "  cp .env.example .env"
    exit 1
fi

# Check packages
if ! "$PYTHON" -c "import requests, bs4, dotenv" 2>/dev/null; then
    echo "ERROR: Missing packages. Run:"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Check if cron job already installed
if crontab -l 2>/dev/null | grep -q "day47-amazon-price-tracker\|amazon-price-tracker"; then
    echo "Cron job already installed:"
    crontab -l 2>/dev/null | grep "amazon\|price.tracker"
    echo ""
    echo "Nothing to do. To remove it: crontab -e"
    exit 0
fi

# Install cron job
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

if crontab -l 2>/dev/null | grep -q "advanced/main.py"; then
    echo "Cron job installed successfully."
    echo "The tracker will run daily at 08:00. Output goes to tracker.log."
    echo ""
    echo "To remove it later: crontab -e  (delete the line and save)"
else
    echo ""
    echo "ERROR: crontab write failed."
    echo "macOS may be blocking access. Fix:"
    echo "  System Settings → Privacy & Security → Full Disk Access → enable Terminal"
    echo "Then run this script again."
    exit 1
fi
