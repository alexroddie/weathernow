#!/bin/bash
set -e

# Change to your working directory
cd /var/services/homes/alex/scripts/weathernow/

# 1. Housekeeping: Delete historic logs older than 30 days
if [ -d "logs" ]; then
    find ./logs -name "error_*.txt" -type f -mtime +30 -delete
fi

# 2. Clear out the previous "current" error file.
# This ensures that if the script fails before Python can write a new 
# error file, we don't accidentally email you an old one.
rm -f python_error.txt

# 3. Execute the Python Build.
# We redirect output to build_log.txt to keep successful runs silent.
if ! /usr/local/bin/python3 build.py > build_log.txt 2>&1; then
    echo "WEATHER NOW: SCRIPT FAILURE DETECTED"
    echo "------------------------------------"
    
    # Check if Python caught the error and wrote a clean message
    if [ -f "python_error.txt" ]; then
        echo "PYTHON FAULT:"
        cat python_error.txt
    else
        # If no python_error.txt exists, the failure happened at 
        # a system level (e.g., Python itself crashed or couldn't start).
        echo "SYSTEM/SHELL FAULT:"
        cat build_log.txt
    fi
    
    echo "------------------------------------"
    exit 1 # Exit with 1 so Synology sends the email
fi

# 4. Proceed with the Git push (Cache-Busting & Zero-Bloat)
git add index.html README.md Readme.html update.sh build.py

# We MUST commit and force-push every 15 minutes to update GitHub's "Last-Modified" header.
# If we don't, TRMNL serves a cached screenshot and the JS time-slicing freezes.
# --allow-empty ensures the commit proceeds even if the Open-Meteo JSON is identical byte-for-byte.
git commit --amend --allow-empty -m "Automated build from Synology: $(date +'%Y-%m-%d %H:%M')"

git push origin main --force