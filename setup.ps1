$ErrorActionPreference = 'Stop'

python -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/download_data.py --all
python scripts/verify_data.py

Write-Host ''
Write-Host 'Setup complete.'
Write-Host 'Activate with: .\.venv\Scripts\Activate.ps1'
Write-Host 'Then run: jupyter lab'
