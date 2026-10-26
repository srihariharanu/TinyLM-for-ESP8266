@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 goto usepython
py -3 -B flash.py --setup
goto finished
:usepython
python -B flash.py --setup
:finished
if errorlevel 1 echo Flashing did not complete. Read the message above and README.md.
pause
