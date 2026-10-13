"""Lokale Transkription von Vorlesungsaufnahmen mit faster-whisper."""

from __future__ import annotations

import os
from typing import Callable

_MODEL = None


def _load_model():
    global _MODEL
    if _MODEL is None:
        from faster_whisper import WhisperModel

        size = os.environ.get("WHISPER_MODEL", "small")
        device = os.environ.get("WHISPER_DEVICE", "auto")
        compute_type = os.environ.get("WHISPER_COMPUTE_TYPE", "default")
        _MODEL = WhisperModel(size, device=device, compute_type=compute_type)
    return _MODEL


def _timestamp(seconds: float) -> str:
    seconds = int(seconds)
    return f"{seconds // 3600:d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"


def transcribe(
    audio_path: str,
    language: str | None = "de",
    on_progress: Callable[[float], None] | None = None,
) -> str:
    """Transkribiert eine Audiodatei und liefert Text mit Zeitmarken pro Absatz.

    on_progress wird mit einem Wert zwischen 0 und 1 aufgerufen.
    """
    model = _load_model()
    segments, info = model.transcribe(
        audio_path,
        language=language or None,
        vad_filter=True,
        beam_size=5,
    )

    lines: list[str] = []
    paragraph: list[str] = []
    paragraph_start = 0.0
    for segment in segments:
        if not paragraph:
            paragraph_start = segment.start
        paragraph.append(segment.text.strip())
        # Etwa jede Minute einen neuen Absatz mit Zeitmarke beginnen
        if segment.end - paragraph_start >= 60:
            lines.append(f"[{_timestamp(paragraph_start)}] " + " ".join(paragraph))
            paragraph = []
        if on_progress and info.duration:
            on_progress(min(segment.end / info.duration, 1.0))
    if paragraph:
        lines.append(f"[{_timestamp(paragraph_start)}] " + " ".join(paragraph))
    if on_progress:
        on_progress(1.0)
    return "\n\n".join(lines)
