param([string]$Token = "")

Set-Location (git rev-parse --show-toplevel)

# Set token for this process (optional)
if ($Token -and $Token.Trim().Length -gt 0) {
  $env:NOTEOPS_TOKEN = $Token
}
python -m venv .venv_noteops | Out-Null
. .\.venv_noteops\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r tools/noteops/requirements.txt

python tools/noteops/app.py
