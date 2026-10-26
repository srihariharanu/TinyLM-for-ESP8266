. "$PSScriptRoot/environment.ps1"
foreach ($script in @('prepare_focused.py','train_gru.py','export_gru.py')) {
    & $Python -B (Join-Path $PSScriptRoot $script)
    if ($LASTEXITCODE -ne 0) { throw "$script failed" }
}
& "$PSScriptRoot/build-firmware.ps1"
