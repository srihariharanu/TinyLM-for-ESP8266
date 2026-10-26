param([switch]$Cuda)
. "$PSScriptRoot/environment.ps1"
if (-not (Test-Path -LiteralPath "$PSScriptRoot/.venv/Scripts/python.exe")) {
    & $Python -B -m venv "$PSScriptRoot/.venv"
    if ($LASTEXITCODE -ne 0) { throw 'Environment creation failed. Install Python 3.12.' }
}
$Python = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if ($Cuda) {
    & $Python -B -m pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cu124
    if ($LASTEXITCODE -ne 0) { throw 'CUDA PyTorch installation failed' }
}
& $Python -B -m pip install -r "$PSScriptRoot/requirements.txt"
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
Write-Host 'Python ready. Install Arduino CLI and core 3.0.2 as described in docs/DEVELOPMENT.md.'
