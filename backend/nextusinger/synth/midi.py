from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from ..models import Note, Project, TempoEvent, Track


def import_midi(path: str | Path, title: str | None = None) -> Project:
    """Import a simple MIDI file into one vocal track.

    Requires mido. Lyrics are initialized as "la" because standard MIDI often lacks lyric events.
    """
    import mido

    mid = mido.MidiFile(str(path))
    ticks_per_beat = mid.ticks_per_beat or 480
    bpm = 120.0
    notes: list[Note] = []
    active: dict[int, tuple[float, int]] = {}
    abs_ticks = 0

    for msg in mido.merge_tracks(mid.tracks):
        abs_ticks += msg.time
        beat = abs_ticks / ticks_per_beat
        if msg.type == "set_tempo":
            bpm = mido.tempo2bpm(msg.tempo)
        if msg.type == "note_on" and msg.velocity > 0:
            active[msg.note] = (beat, msg.velocity)
        elif msg.type in {"note_off", "note_on"} and getattr(msg, "note", None) in active:
            start, vel = active.pop(msg.note)
            dur = max(0.05, beat - start)
            notes.append(
                Note(
                    id=uuid4().hex,
                    start=round(start, 4),
                    duration=round(dur, 4),
                    midi=msg.note,
                    lyric="la",
                    velocity=max(0.2, min(1.4, vel / 96.0)),
                )
            )

    return Project(
        id=uuid4().hex,
        title=title or Path(path).stem,
        tempos=[TempoEvent(beat=0, bpm=bpm)],
        tracks=[Track(id=uuid4().hex, name="Imported MIDI Vocal", notes=notes)],
    )
