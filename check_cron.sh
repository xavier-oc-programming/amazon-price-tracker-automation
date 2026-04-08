#!/bin/bash
# Checks whether the Amazon price tracker cron job is active.

if crontab -l 2>/dev/null | grep -q "advanced/main.py"; then
    echo "Cron job is ACTIVE."
    echo ""
    echo "Schedule:"
    crontab -l 2>/dev/null | grep "advanced/main.py"
    echo ""
    echo "The tracker runs daily at 08:00. Output is written to tracker.log."

    PROJECT="$(cd "$(dirname "$0")" && pwd)"
    LOGFILE="$PROJECT/tracker.log"
    if [ -f "$LOGFILE" ]; then
        echo ""
        echo "Last 5 log entries:"
        echo "---"
        tail -5 "$LOGFILE"
    else
        echo ""
        echo "No log file yet — tracker has not run since cron was installed."
    fi
else
    echo "Cron job is NOT active."
    echo ""
    echo "To schedule it: select option 3 from the menu."
fi
