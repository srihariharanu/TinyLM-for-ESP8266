$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
foreach ($name in @('tmp','cache','logs','build')) { New-Item -ItemType Directory -Path (Join-Path $PSScriptRoot $name) -Force | Out-Null }
$env:TEMP = Join-Path $PSScriptRoot 'tmp'
$env:TMP = $env:TEMP
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PIP_CACHE_DIR = Join-Path $PSScriptRoot 'cache/pip'
$env:TORCH_HOME = Join-Path $PSScriptRoot 'cache/torch'
$env:CUDA_CACHE_PATH = Join-Path $PSScriptRoot 'cache/cuda'
$env:HF_HOME = Join-Path $PSScriptRoot 'cache/huggingface'
$env:ARDUINO_DIRECTORIES_DATA = Join-Path $PSScriptRoot '.arduino/data'
$env:ARDUINO_DIRECTORIES_DOWNLOADS = Join-Path $PSScriptRoot '.arduino/downloads'
$env:ARDUINO_DIRECTORIES_USER = Join-Path $PSScriptRoot '.arduino/user'
$env:PLAYWRIGHT_BROWSERS_PATH = Join-Path $PSScriptRoot '.playwright'
$Python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $Python)) { $Python = (Get-Command python -ErrorAction Stop).Source }
