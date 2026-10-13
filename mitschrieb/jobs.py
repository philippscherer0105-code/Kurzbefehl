"""Ablage der Mitschriebe auf der Festplatte und Hintergrundverarbeitung."""

from __future__ import annotations

import json
import os
import queue
import threading
import traceback
from datetime import datetime
from pathlib import Path

from . import notes, transcribe

DATA_DIR = Path(os.environ.get("MITSCHRIEB_DATA", Path(__file__).resolve().parent.parent / "data"))

_lock = threading.Lock()
_live: dict[str, dict] = {}  # Laufzeitstatus: Fortschritt und gestreamter Text
_queue: "queue.Queue[str]" = queue.Queue()


def _dir(note_id: str) -> Path:
    path = (DATA_DIR / note_id).resolve()
    if path.parent != DATA_DIR.resolve():
        raise ValueError("Ungültige ID")
    return path


def _read_meta(note_id: str) -> dict:
    return json.loads((_dir(note_id) / "meta.json").read_text(encoding="utf-8"))


def _write_meta(note_id: str, meta: dict) -> None:
    (_dir(note_id) / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _update(note_id: str, **fields) -> None:
    with _lock:
        meta = _read_meta(note_id)
        meta.update(fields)
        _write_meta(note_id, meta)


def create(
    title: str,
    course: str,
    date: str,
    language: str,
    extra_instructions: str,
    audio: tuple[str, bytes] | None,
    transcript: str | None,
    slides_pdf: bytes | None,
) -> str:
    """Legt einen neuen Mitschrieb an und reiht ihn zur Verarbeitung ein."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    note_id = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    folder = _dir(note_id)
    folder.mkdir()

    meta = {
        "id": note_id,
        "title": title or "Vorlesung",
        "course": course,
        "date": date or datetime.now().strftime("%d.%m.%Y"),
        "language": language,
        "extra_instructions": extra_instructions,
        "created": datetime.now().isoformat(timespec="seconds"),
        "status": "wartet",
        "error": None,
        "audio_file": None,
        "has_slides": bool(slides_pdf),
    }
    if audio:
        filename, data = audio
        suffix = Path(filename).suffix.lower() or ".webm"
        meta["audio_file"] = f"aufnahme{suffix}"
        (folder / meta["audio_file"]).write_bytes(data)
    if transcript:
        (folder / "transkript.txt").write_text(transcript, encoding="utf-8")
    if slides_pdf:
        (folder / "folien.pdf").write_bytes(slides_pdf)
    _write_meta(note_id, meta)

    _queue.put(note_id)
    return note_id


def regenerate(note_id: str, extra_instructions: str | None = None) -> None:
    """Erstellt den Mitschrieb aus dem vorhandenen Transkript neu."""
    fields = {"status": "wartet", "error": None}
    if extra_instructions is not None:
        fields["extra_instructions"] = extra_instructions
    _update(note_id, **fields)
    _queue.put(note_id)


def _process(note_id: str) -> None:
    folder = _dir(note_id)
    meta = _read_meta(note_id)
    live = {"progress": 0.0, "text": ""}
    with _lock:
        _live[note_id] = live

    transcript_path = folder / "transkript.txt"
    if not transcript_path.exists():
        if not meta.get("audio_file"):
            raise RuntimeError("Weder Aufnahme noch Transkript vorhanden.")
        _update(note_id, status="transkribiert")

        def on_progress(value: float) -> None:
            live["progress"] = value

        text = transcribe.transcribe(
            str(folder / meta["audio_file"]), meta.get("language") or None, on_progress
        )
        if not text.strip():
            raise RuntimeError("In der Aufnahme wurde keine Sprache erkannt.")
        transcript_path.write_text(text, encoding="utf-8")

    _update(note_id, status="schreibt")
    live["progress"] = 0.0

    def on_text(chunk: str) -> None:
        live["text"] += chunk

    slides_path = folder / "folien.pdf"
    markdown = notes.generate_notes(
        transcript_path.read_text(encoding="utf-8"),
        title=meta.get("title", ""),
        course=meta.get("course", ""),
        date=meta.get("date", ""),
        slides_pdf=slides_path.read_bytes() if slides_path.exists() else None,
        extra_instructions=meta.get("extra_instructions", ""),
        on_text=on_text,
    )
    (folder / "mitschrieb.md").write_text(markdown, encoding="utf-8")
    _update(note_id, status="fertig")


def _worker() -> None:
    while True:
        note_id = _queue.get()
        try:
            _process(note_id)
        except Exception as exc:  # Fehler im Status anzeigen statt den Worker zu beenden
            traceback.print_exc()
            _update(note_id, status="fehler", error=str(exc))
        finally:
            with _lock:
                _live.pop(note_id, None)
            _queue.task_done()


def start_worker() -> None:
    threading.Thread(target=_worker, daemon=True).start()
    # Nach einem Neustart unterbrochene Aufträge erneut einreihen
    for meta in list_all():
        if meta["status"] in ("wartet", "transkribiert", "schreibt"):
            _queue.put(meta["id"])


def get(note_id: str) -> dict | None:
    try:
        meta = _read_meta(note_id)
    except (FileNotFoundError, ValueError):
        return None
    folder = _dir(note_id)
    with _lock:
        live = dict(_live.get(note_id, {}))
    meta["progress"] = live.get("progress", 0.0)
    md_path = folder / "mitschrieb.md"
    if meta["status"] == "fertig" and md_path.exists():
        meta["markdown"] = md_path.read_text(encoding="utf-8")
    else:
        meta["markdown"] = live.get("text", "")
    meta["has_transcript"] = (folder / "transkript.txt").exists()
    return meta


def file_path(note_id: str, name: str) -> Path | None:
    allowed = {"transkript.txt", "mitschrieb.md", "folien.pdf"}
    meta = get(note_id)
    if meta is None:
        return None
    if meta.get("audio_file"):
        allowed.add(meta["audio_file"])
    path = _dir(note_id) / name
    return path if name in allowed and path.exists() else None


def list_all() -> list[dict]:
    if not DATA_DIR.exists():
        return []
    result = []
    for folder in sorted(DATA_DIR.iterdir(), reverse=True):
        if (folder / "meta.json").exists():
            result.append(_read_meta(folder.name))
    return result


def delete(note_id: str) -> bool:
    import shutil

    folder = _dir(note_id)
    if not (folder / "meta.json").exists():
        return False
    shutil.rmtree(folder)
    return True
