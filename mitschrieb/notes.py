"""Erzeugt aus einem Vorlesungstranskript einen strukturierten Mitschrieb mit Claude."""

from __future__ import annotations

import base64
import os
from typing import Callable

import anthropic

MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-5-5")

SYSTEM_PROMPT = """\
Du bist ein sehr guter Studierender, der aus dem Transkript einer Vorlesung einen \
übersichtlichen, prüfungstauglichen Mitschrieb erstellt. Das Transkript stammt aus \
automatischer Spracherkennung: Es enthält Füllwörter, Wiederholungen und \
Erkennungsfehler (vor allem bei Fachbegriffen, Namen und Formeln). Korrigiere solche \
Fehler aus dem Kontext stillschweigend; wo du dir bei einer inhaltlich wichtigen \
Stelle unsicher bist, markiere sie mit „(unsicher)“. Erfinde keine Inhalte, die in der \
Vorlesung nicht vorkamen – Ergänzungen zum Verständnis kennzeichnest du als \
„Ergänzung:“.

Ausgabe: ausschließlich ein Markdown-Dokument (kein umschließender Codeblock), in der \
Sprache der Vorlesung, mit diesem Aufbau:

1. `# Titel` der Vorlesung, darunter eine Zeile mit Fach/Datum, falls bekannt.
2. `## Auf einen Blick` – 3–6 Stichpunkte mit den wichtigsten Aussagen.
3. `## Gliederung` – nummerierte Liste der Themenblöcke, jeweils mit Zeitmarke aus dem \
Transkript (z. B. „(0:12:30)“).
4. Für jeden Themenblock ein `##`-Abschnitt mit `###`-Unterabschnitten. Schreibe \
knapp und strukturiert (Stichpunkte, kurze Absätze), nicht als Fließtext-Nacherzählung.
5. `## Wichtige Begriffe` – Tabelle `| Begriff | Bedeutung |`.
6. `## Prüfungsrelevant` – was der/die Dozierende betont hat („das kommt dran“, \
Wiederholungen, Hinweise auf Übungen/Klausur) plus 3–5 Verständnisfragen zum Selbsttest.
7. `## Offene Punkte` – nur falls es unklare Stellen, Verweise auf Folien/Literatur \
oder Hausaufgaben gab.

Visualisierung – setze sie gezielt dort ein, wo sie das Verständnis wirklich \
verbessert (typisch 2–5 Grafiken und mehrere Tabellen pro Vorlesung):
- Tabellen (GitHub-Markdown) für Vergleiche, Eigenschaften, Vor-/Nachteile, \
Fallunterscheidungen, Zahlenwerte.
- Diagramme als ```mermaid-Codeblöcke: `flowchart` für Abläufe, Algorithmen und \
Ursache-Wirkung; `mindmap` für den Themenüberblick (eine direkt nach „Auf einen \
Blick“); `sequenceDiagram` für Interaktionen; `classDiagram`/`erDiagram` für \
Strukturen; `timeline` für historische Entwicklungen; `pie` oder `xychart-beta` \
für Zahlen, die tatsächlich genannt wurden.
- Mermaid-Regeln, damit die Diagramme fehlerfrei rendern: Knoten-IDs nur aus \
Buchstaben/Ziffern (A, B1, …); Beschriftungen mit Sonderzeichen, Umlauten, Klammern \
oder Leerzeichen in doppelte Anführungszeichen setzen, z. B. `A["Eingabe (x, y)"]`; \
keine Formeln oder Markdown in Diagrammen; in `mindmap` keine Klammern in \
Beschriftungen.
- Formeln in LaTeX: inline `$...$`, abgesetzt `$$...$$` auf eigenen Zeilen.
- Merksätze und Definitionen als Zitatblock, beginnend mit `> **Merke:**` bzw. \
`> **Definition:**`.
"""


class NotesError(RuntimeError):
    pass


def generate_notes(
    transcript: str,
    title: str = "",
    course: str = "",
    date: str = "",
    slides_pdf: bytes | None = None,
    extra_instructions: str = "",
    on_text: Callable[[str], None] | None = None,
) -> str:
    """Erstellt den Mitschrieb als Markdown. on_text erhält die Textstücke beim Streamen."""
    client = anthropic.Anthropic()

    meta = "\n".join(
        f"{label}: {value}"
        for label, value in (("Titel", title), ("Fach", course), ("Datum", date))
        if value
    )
    prompt = ""
    if meta:
        prompt += f"Angaben zur Vorlesung:\n{meta}\n\n"
    if slides_pdf:
        prompt += (
            "Die Vorlesungsfolien sind als PDF beigefügt. Nutze sie, um Fachbegriffe, "
            "Formeln und Struktur korrekt wiederzugeben; maßgeblich ist aber, was in der "
            "Vorlesung gesagt wurde.\n\n"
        )
    if extra_instructions:
        prompt += f"Zusätzliche Wünsche: {extra_instructions}\n\n"
    prompt += f"<transkript>\n{transcript}\n</transkript>\n\nErstelle jetzt den Mitschrieb."

    content: list[dict] = []
    if slides_pdf:
        content.append(
            {
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": base64.standard_b64encode(slides_pdf).decode(),
                },
            }
        )
    content.append({"type": "text", "text": prompt})

    with client.beta.messages.stream(
        model=MODEL,
        max_tokens=64000,
        system=SYSTEM_PROMPT,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        messages=[{"role": "user", "content": content}],
        # Bei einer fälschlichen Ablehnung durch Sicherheitsfilter automatisch
        # auf ein anderes Modell ausweichen.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    ) as stream:
        for text in stream.text_stream:
            if on_text:
                on_text(text)
        message = stream.get_final_message()

    if message.stop_reason == "refusal":
        raise NotesError("Die Anfrage wurde vom Modell abgelehnt.")
    markdown = "".join(block.text for block in message.content if block.type == "text")
    if message.stop_reason == "max_tokens":
        markdown += "\n\n> **Hinweis:** Der Mitschrieb wurde wegen Längenbegrenzung abgeschnitten.\n"
    return markdown.strip() + "\n"
