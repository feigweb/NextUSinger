from __future__ import annotations

from ..models import Project, Track


def project_to_score_json(project: Project, track: Track) -> dict:
    """Convert a NextUSinger track into a neutral DiffSinger-style score payload.

    Real DiffSinger forks vary in exact CLI and preprocessing formats. This neutral JSON keeps
    enough musical information for adapters to map into MIDI-A/B, OpenUTAU, or custom inference
    scripts.
    """
    bpm = project.default_bpm
    notes = []
    for note in track.notes:
        notes.append(
            {
                "id": note.id,
                "onset_beats": note.start,
                "duration_beats": note.duration,
                "onset_seconds": note.start * 60.0 / bpm,
                "duration_seconds": note.duration * 60.0 / bpm,
                "midi": note.midi,
                "lyric": note.lyric,
                "phonemes": note.phonemes,
                "velocity": note.velocity,
                "controls": {
                    "tension": note.tension,
                    "breathiness": note.breathiness,
                    "energy": note.energy,
                    "gender": note.gender,
                },
            }
        )
    return {
        "schema_version": "nextusinger.score.v1",
        "project_id": project.id,
        "title": project.title,
        "track_id": track.id,
        "track_name": track.name,
        "sample_rate": project.sample_rate,
        "tempo": bpm,
        "tempos": [t.model_dump() for t in project.tempos],
        "notes": notes,
        "pitch": [p.model_dump() for p in track.pitch],
    }
