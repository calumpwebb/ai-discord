#!/bin/bash
# OpenCode Monitor Wrapper Script

# Navigate to the OpenCode Monitor directory
cd "$(dirname "$0")/ocmonitor-share" || exit 1

# Activate virtual environment
source venv/bin/activate || exit 1

# Run OpenCode Monitor with all arguments passed to this script
python3 run_ocmonitor.py "$@"