@echo off
rem Startet den Vorlesungs-Mitschrieb (Windows). Beim ersten Start wird alles installiert.
chcp 65001 >nul
cd /d "%~dp0"

set "PY="
where py >nul 2>nul && py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul && set "PY=py -3"
if not defined PY (
  where python >nul 2>nul && python -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul && set "PY=python"
)
if not defined PY (
  echo Python 3.10 oder neuer wurde nicht gefunden.
  echo Bitte installieren: https://www.python.org/downloads/
  echo Wichtig: Beim Installieren "Add python.exe to PATH" anhaken.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Erster Start: richte Umgebung ein ...
  %PY% -m venv .venv || (pause & exit /b 1)
)
if not exist ".venv\.installiert" (
  echo Installiere Abhaengigkeiten ^(kann ein paar Minuten dauern^) ...
  ".venv\Scripts\python.exe" -m pip install --upgrade pip >nul
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt || (echo Installation fehlgeschlagen. & pause & exit /b 1)
  echo ok> ".venv\.installiert"
)

".venv\Scripts\python.exe" -m mitschrieb
pause
