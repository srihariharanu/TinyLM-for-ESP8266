@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 goto usepython
py -3 -B flash.py
goto finished
:usepython
python -B flash.py
:finished
if errorlevel 1 echo Flashing did not complete. Read the message above and README.md.
pause
