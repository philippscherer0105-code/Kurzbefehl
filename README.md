# 🎓 Vorlesungs-Mitschrieb

Nimm eine Vorlesung im Browser auf – daraus entsteht automatisch ein übersichtlicher
Mitschrieb mit Gliederung, **Diagrammen**, **Tabellen**, Formeln, Merksätzen, Begriffsliste
und prüfungsrelevanten Punkten.

**Ablauf:** Aufnahme im Browser → lokale Spracherkennung mit Whisper → Claude schreibt den
strukturierten Mitschrieb (live mitlesbar) → Export als PDF, HTML oder Markdown.

## Funktionen

- **Aufnahme direkt im Browser** mit Pause/Fortsetzen, Pegelanzeige und Timer.
  Der Bildschirm bleibt während der Aufnahme an, und die Aufnahme wird alle 10 Sekunden
  im Browser gesichert – stürzt der Tab ab, lässt sie sich wiederherstellen.
- Alternativ **vorhandene Audio-/Videodatei** (mp3, m4a, wav, mp4 …) oder ein fertiges
  **Transkript** (.txt) hochladen.
- **Folien als PDF** optional beifügen – damit werden Fachbegriffe und Formeln korrekt.
- **Mitschrieb** mit:
  - „Auf einen Blick“-Zusammenfassung und Mindmap
  - Gliederung mit Zeitmarken
  - Ablauf-, Struktur-, Sequenz- und Zeitstrahl-Diagrammen (Mermaid) sowie Balken-/Kreisdiagrammen
  - Vergleichs- und Begriffstabellen
  - Formeln (LaTeX/KaTeX), hervorgehobene Merksätze und Definitionen
  - Prüfungsrelevantes + Verständnisfragen zum Selbsttest
- Export: **Drucken/PDF**, eigenständige **HTML-Datei**, **Markdown** (z. B. für Obsidian/Notion).
- Mitschrieb mit anderen Wünschen **neu erstellen**, ohne erneut zu transkribieren.

## Installation

Voraussetzungen: Python 3.10+ und ein [Anthropic-API-Schlüssel](https://console.anthropic.com/).

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Starten

```bash
export ANTHROPIC_API_KEY="sk-ant-..."   # Windows (PowerShell): $env:ANTHROPIC_API_KEY="sk-ant-..."
python -m mitschrieb
```

Dann im Browser **http://localhost:5000** öffnen.

> Das Mikrofon funktioniert im Browser nur über `localhost` oder HTTPS. Wenn du mit dem
> Handy aufnehmen willst, nimm dort mit einer Diktier-App auf und lade die Datei hoch –
> oder stelle den Server per HTTPS bereit (`HOST=0.0.0.0` plus Reverse-Proxy/Tunnel).

Beim ersten Transkribieren lädt Whisper das Sprachmodell herunter (einmalig, ca. 500 MB
für `small`). Die Spracherkennung läuft komplett lokal; nur das Transkript (und ggf. die
Folien) werden zur Mitschrieb-Erstellung an die Claude-API gesendet.

## Einstellungen (Umgebungsvariablen)

| Variable | Standard | Bedeutung |
|---|---|---|
| `ANTHROPIC_API_KEY` | – | API-Schlüssel für Claude (erforderlich) |
| `CLAUDE_MODEL` | `claude-opus-5-5` | Modell für den Mitschrieb |
| `WHISPER_MODEL` | `small` | `tiny`, `base`, `small`, `medium`, `large-v3`, `turbo` – größer = genauer, aber langsamer |
| `WHISPER_DEVICE` | `auto` | `cpu` oder `cuda` (NVIDIA-GPU) |
| `WHISPER_COMPUTE_TYPE` | `default` | z. B. `int8` für schnellere CPU-Verarbeitung |
| `MITSCHRIEB_DATA` | `./data` | Ablageort für Aufnahmen, Transkripte und Mitschriebe |
| `HOST` / `PORT` | `127.0.0.1` / `5000` | Adresse des Webservers |

**Richtwerte:** Eine 90-minütige Vorlesung braucht mit `small` auf einem aktuellen Laptop
(CPU) grob 15–30 Minuten zur Transkription, mit GPU nur wenige Minuten. Die Erstellung
des Mitschriebs dauert danach einige Minuten.

## Ablage

Jeder Mitschrieb liegt in `data/<id>/`:

```
data/20261013-101500-123456/
├── meta.json        Titel, Fach, Datum, Status
├── aufnahme.webm    Originalaufnahme
├── folien.pdf       (optional)
├── transkript.txt   Transkript mit Zeitmarken
└── mitschrieb.md    Der fertige Mitschrieb
```

## Projektstruktur

```
mitschrieb/
├── app.py           Flask-Webserver und API
├── jobs.py          Ablage + Hintergrundverarbeitung (Warteschlange)
├── transcribe.py    Spracherkennung mit faster-whisper
├── notes.py         Mitschrieb-Erstellung mit Claude (Prompt)
├── templates/       HTML-Seiten (Start, Ansicht, Export)
└── static/          Aufnahme (recorder.js), Darstellung (render.js), Stil
```

Wenn dir Aufbau oder Stil des Mitschriebs nicht gefallen, passe `SYSTEM_PROMPT` in
`mitschrieb/notes.py` an.
