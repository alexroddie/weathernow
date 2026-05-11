#!/bin/bash
set -e

# Change to your working directory
cd /var/services/homes/alex/scripts/weathernow/

# SET YOUR VERIFIED GIT PATH
GIT_PATH="/volume1/@appstore/Git/bin/git"

# 1. Housekeeping: Delete historic logs older than 30 days
if [ -d "logs" ]; then
    find ./logs -name "error_*.txt" -type f -mtime +30 -delete
fi

# 2. Clear out previous error logs.
rm -f python_error.txt
rm -f git_error.txt

# 3. Execute the Python Build.
if ! python3 build.py > build_log.txt 2>&1; then
    echo "WEATHER NOW: PYTHON SCRIPT FAILURE"
    echo "------------------------------------"
    if [ -f "python_error.txt" ]; then cat python_error.txt; else cat build_log.txt; fi
    echo "------------------------------------"
    exit 1
fi

# 4. Proceed with the Git push using the verified path.
if ! $GIT_PATH add index.html README.md Readme.html update.sh build.py > git_error.txt 2>&1; then
    echo "GIT ADD FAILED"; cat git_error.txt; exit 1
fi

if ! $GIT_PATH commit --amend --allow-empty -m "Automated build from Synology: $(date +'%Y-%m-%d %H:%M')" > git_error.txt 2>&1; then
    echo "GIT COMMIT FAILED"; cat git_error.txt; exit 1
fi

if ! $GIT_PATH push origin main --force > git_error.txt 2>&1; then
    echo "GIT PUSH FAILED"; cat git_error.txt; exit 1
fi