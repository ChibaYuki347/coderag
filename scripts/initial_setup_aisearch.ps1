#!/usr/bin/env pwsh

./scripts/load_python_env.ps1

$venvPythonPath = "./.venv/scripts/python.exe"
if (Test-Path -Path "/usr") {
  # fallback to Linux venv path
  $venvPythonPath = "./.venv/bin/python"
}

Write-Host 'Running "initial_setup_aisearch.py"'

Start-Process -FilePath $venvPythonPath "scripts/initial_setup_aisearch.py" -Wait -NoNewWindow

Write-Host 'set azd variables'