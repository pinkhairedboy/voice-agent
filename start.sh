#!/bin/bash

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

if [ ! -d "venv" ]; then
    echo "Error: venv not found. Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

source venv/bin/activate

if ! python -c "import rumps" 2>/dev/null; then
    echo "Error: Dependencies not installed. Run: pip install -r requirements.txt"
    exit 1
fi

python app/main.py
