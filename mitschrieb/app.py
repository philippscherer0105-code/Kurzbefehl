"""Web-Oberfläche: Vorlesung aufnehmen, verarbeiten lassen, Mitschrieb ansehen."""

from __future__ import annotations

import json
import os
from pathlib import Path

from flask import Flask, abort, jsonify, render_template, request, send_file

from . import jobs

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 1024  # 1 GB für lange Aufnahmen


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/mitschrieb/<note_id>")
def view(note_id: str):
    if jobs.get(note_id) is None:
        abort(404)
    return render_template("view.html", note_id=note_id)


@app.get("/mitschrieb/<note_id>/export.html")
def export(note_id: str):
    """Eigenständige HTML-Datei, die ohne den Server geöffnet werden kann."""
    meta = jobs.get(note_id)
    if meta is None or meta["status"] != "fertig":
        abort(404)
    html = render_template(
        "export.html",
        title=meta["title"],
        markdown_json=json.dumps(meta["markdown"]).replace("</", "<\\/"),
        render_js=(STATIC_DIR / "render.js").read_text(encoding="utf-8"),
        style_css=(STATIC_DIR / "style.css").read_text(encoding="utf-8"),
    )
    filename = f"{meta['date']} {meta['title']}.html".replace("/", "-")
    return html, 200, {
        "Content-Type": "text/html; charset=utf-8",
        "Content-Disposition": f"attachment; filename*=UTF-8''{_quote(filename)}",
    }


@app.get("/api/mitschriebe")
def list_notes():
    return jsonify(jobs.list_all())


@app.post("/api/mitschriebe")
def create_note():
    form = request.form
    audio_file = request.files.get("audio")
    transcript_file = request.files.get("transcript")
    slides_file = request.files.get("slides")

    audio = None
    if audio_file and audio_file.filename:
        audio = (audio_file.filename, audio_file.read())
    transcript = None
    if transcript_file and transcript_file.filename:
        transcript = transcript_file.read().decode("utf-8", errors="replace")
    if not audio and not transcript:
        return jsonify(error="Bitte eine Aufnahme, Audiodatei oder ein Transkript angeben."), 400
    slides = slides_file.read() if slides_file and slides_file.filename else None
    if slides and not slides.startswith(b"%PDF"):
        return jsonify(error="Die Folien müssen als PDF vorliegen."), 400

    note_id = jobs.create(
        title=form.get("title", "").strip(),
        course=form.get("course", "").strip(),
        date=form.get("date", "").strip(),
        language=form.get("language", "de").strip(),
        extra_instructions=form.get("extra", "").strip(),
        audio=audio,
        transcript=transcript,
        slides_pdf=slides,
    )
    return jsonify(id=note_id), 201


@app.get("/api/mitschriebe/<note_id>")
def get_note(note_id: str):
    meta = jobs.get(note_id)
    if meta is None:
        abort(404)
    return jsonify(meta)


@app.post("/api/mitschriebe/<note_id>/neu")
def regenerate_note(note_id: str):
    meta = jobs.get(note_id)
    if meta is None:
        abort(404)
    if not meta["has_transcript"]:
        return jsonify(error="Es liegt noch kein Transkript vor."), 400
    if meta["status"] in ("wartet", "transkribiert", "schreibt"):
        return jsonify(error="Wird bereits verarbeitet."), 409
    body = request.get_json(silent=True) or {}
    jobs.regenerate(note_id, body.get("extra"))
    return jsonify(ok=True)


@app.delete("/api/mitschriebe/<note_id>")
def delete_note(note_id: str):
    meta = jobs.get(note_id)
    if meta is None:
        abort(404)
    if meta["status"] in ("transkribiert", "schreibt"):
        return jsonify(error="Wird gerade verarbeitet."), 409
    jobs.delete(note_id)
    return jsonify(ok=True)


@app.get("/api/mitschriebe/<note_id>/dateien/<name>")
def download(note_id: str, name: str):
    path = jobs.file_path(note_id, name)
    if path is None:
        abort(404)
    return send_file(path, as_attachment=request.args.get("download") == "1")


def _quote(value: str) -> str:
    from urllib.parse import quote

    return quote(value)


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Hinweis: ANTHROPIC_API_KEY ist nicht gesetzt – die Mitschrieb-Erstellung wird fehlschlagen.")
    jobs.start_worker()
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    print(f"Mitschrieb läuft auf http://{'localhost' if host == '127.0.0.1' else host}:{port}")
    app.run(host=host, port=port, threaded=True)


if __name__ == "__main__":
    main()
