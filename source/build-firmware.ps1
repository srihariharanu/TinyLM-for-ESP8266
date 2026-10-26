. "$PSScriptRoot/environment.ps1"
& $Python -B "$PSScriptRoot/build_web.py"
if ($LASTEXITCODE -ne 0) { throw 'Web generation failed' }
& arduino-cli compile --fqbn 'esp8266:esp8266:generic:xtal=160,FlashMode=dout,eesz=4M1M' --build-path "$PSScriptRoot/build/objects" --output-dir "$PSScriptRoot/build/export" "$PSScriptRoot/firmware/RecurrentLM"
if ($LASTEXITCODE -ne 0) { throw 'Firmware compilation failed' }
Write-Host 'Build ready in build/export. Packaged product firmware has not been replaced.'
