#!/bin/bash
# Removes the Amazon price tracker cron job.

if ! crontab -l 2>/dev/null | grep -q "advanced/main.py"; then
    echo "No cron job found — nothing to remove."
    exit 0
fi

crontab -l 2>/dev/null | grep -v "advanced/main.py" | crontab -

if crontab -l 2>/dev/null | grep -q "advanced/main.py"; then
    echo ""
    echo "ERROR: Could not remove cron job."
    echo "macOS may be blocking access. Fix:"
    echo "  System Settings → Privacy & Security → Full Disk Access → enable Terminal"
    echo "Then try again."
    exit 1
else
    echo "Cron job removed. The tracker will no longer run automatically."
fi
