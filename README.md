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

## Installation & Start

> **Wichtig:** Das Programm läuft auf **deinem eigenen Computer**. `localhost` bedeutet
> „dieser Computer“ – die Adresse funktioniert also erst, wenn du das Programm dort
> gestartet hast. Solange das Startfenster offen ist, läuft es.

**1. Python installieren** (einmalig, Version 3.10 oder neuer):
[python.org/downloads](https://www.python.org/downloads/).
Unter Windows beim Installieren unbedingt **„Add python.exe to PATH“** anhaken.

**2. Projekt herunterladen:** Auf GitHub auf **Code → Download ZIP** klicken und entpacken
(oder `git clone`).

**3. Starten per Doppelklick:**

| System | Datei |
|---|---|
| Windows | `start.bat` |
| macOS | `start.command` (beim ersten Mal: Rechtsklick → **Öffnen**, da die Datei nicht aus dem App Store stammt) |
| Linux | `start.sh` (im Terminal: `./start.sh`) |

Beim ersten Start werden alle Abhängigkeiten installiert (dauert ein paar Minuten).
Danach öffnet sich der Browser automatisch mit **http://localhost:8765**. Ist der Port
belegt, wird automatisch der nächste freie genommen – die richtige Adresse steht im
Startfenster.

**4. API-Schlüssel eintragen:** Beim ersten Öffnen fragt die Seite nach einem
[Anthropic-API-Schlüssel](https://console.anthropic.com/settings/keys). Er wird nur lokal
in `data/api_key.txt` gespeichert. (Alternativ: Umgebungsvariable `ANTHROPIC_API_KEY`.)

<details>
<summary>Manuell im Terminal starten</summary>

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m mitschrieb
```
</details>

### Wenn es nicht klappt

| Problem | Lösung |
|---|---|
| Browser zeigt „Seite nicht erreichbar“ | Das Startfenster muss offen bleiben. Adresse aus dem Startfenster verwenden. |
| „Python wurde nicht gefunden“ | Python installieren (siehe oben), unter Windows „Add to PATH“ anhaken, danach neu starten. |
| macOS: „kann nicht geöffnet werden“ | Rechtsklick auf `start.command` → Öffnen. Oder im Terminal: `chmod +x start.sh start.command`. |
| Mikrofon wird nicht freigegeben | Im Browser über das Schloss-Symbol in der Adressleiste das Mikrofon erlauben. Funktioniert nur unter `localhost`, nicht über die IP-Adresse. |
| Aufnahme am Handy | Mit einer Diktier-App aufnehmen und die Datei unter „… oder vorhandene Datei verwenden“ hochladen. |

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
| `HOST` / `PORT` | `127.0.0.1` / `8765` | Adresse des Webservers |
| `NO_BROWSER` | – | `1` = Browser nicht automatisch öffnen |

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
├── config.py        API-Schlüssel
├── jobs.py          Ablage + Hintergrundverarbeitung (Warteschlange)
├── transcribe.py    Spracherkennung mit faster-whisper
├── notes.py         Mitschrieb-Erstellung mit Claude (Prompt)
├── templates/       HTML-Seiten (Start, Ansicht, Export)
└── static/          Aufnahme (recorder.js), Darstellung (render.js), Stil
```

Wenn dir Aufbau oder Stil des Mitschriebs nicht gefallen, passe `SYSTEM_PROMPT` in
`mitschrieb/notes.py` an.
