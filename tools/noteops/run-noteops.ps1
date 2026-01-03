Set-Location (git rev-parse --show-toplevel)

python -m venv .venv_noteops | Out-Null
. .\.venv_noteops\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r tools/noteops/requirements.txt

python tools/noteops/app.py