$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location "$Root\backend"
python -m venv .venv
. ".venv\Scripts\Activate.ps1"
pip install -r requirements.txt
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$Root\backend'; . .venv\Scripts\Activate.ps1; uvicorn nextusinger.main:app --reload --port 7860"
Set-Location "$Root\frontend"
npm install
npm run dev
