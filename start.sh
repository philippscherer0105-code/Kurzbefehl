#!/usr/bin/env bash
# Startet den Vorlesungs-Mitschrieb (macOS/Linux). Beim ersten Start wird alles installiert.
cd "$(dirname "$0")" || exit 1

PY=""
for cmd in python3 python; do
  if command -v "$cmd" >/dev/null 2>&1 && "$cmd" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    PY="$cmd"; break
  fi
done
if [ -z "$PY" ]; then
  echo "Python 3.10 oder neuer wurde nicht gefunden."
  echo "Bitte installieren: https://www.python.org/downloads/"
  read -r -p "Enter zum Schließen ..." _; exit 1
fi

if [ ! -x .venv/bin/python ]; then
  echo "Erster Start: richte Umgebung ein ..."
  "$PY" -m venv .venv || { read -r -p "Fehler. Enter zum Schließen ..." _; exit 1; }
fi
if [ ! -f .venv/.installiert ] || [ requirements.txt -nt .venv/.installiert ]; then
  echo "Installiere Abhängigkeiten (kann ein paar Minuten dauern) ..."
  .venv/bin/python -m pip install --upgrade pip >/dev/null
  .venv/bin/python -m pip install -r requirements.txt || { read -r -p "Installation fehlgeschlagen. Enter zum Schließen ..." _; exit 1; }
  touch .venv/.installiert
fi

.venv/bin/python -m mitschrieb
