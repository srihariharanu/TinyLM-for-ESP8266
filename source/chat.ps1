param([Parameter(Mandatory=$true)][string]$Port, [switch]$Test)
. "$PSScriptRoot/environment.ps1"
$arguments = @('-B', "$PSScriptRoot/serial_console.py", '--port', $Port)
if ($Test) { $arguments += '--test' }
& $Python @arguments
if ($LASTEXITCODE -ne 0) { throw 'Console failed' }
