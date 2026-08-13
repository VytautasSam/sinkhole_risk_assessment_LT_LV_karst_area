#!/usr/bin/env bash
set -euo pipefail

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/download_data.py --all
python scripts/verify_data.py

echo
echo 'Setup complete.'
echo 'Activate with: source .venv/bin/activate'
echo 'Then run: jupyter lab'
