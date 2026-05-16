from __future__ import annotations

from pathlib import Path

import numpy as np

from ..models import Project, Track, VoicebankManifest
from .audio import midi_to_hz, soft_limiter, write_wav

VOWEL_FORMANTS = {
    "a": (800, 1150),
    "i": (350, 2500),
    "u": (325, 900),
    "e": (500, 1700),
    "o": (450, 800),
}


def _lyric_vowel(lyric: str) -> str:
    lyric = lyric.lower()
    for key in VOWEL_FORMANTS:
        if key in lyric:
            return key
    if any(ch in lyric for ch in "啊呀哈啦吗"):
        return "a"
    if any(ch in lyric for ch in "衣一你里"):
        return "i"
    if any(ch in lyric for ch in "乌无路都"):
        return "u"
    return "a"


def _adsr(n: int, sr: int) -> np.ndarray:
    attack = max(1, int(0.025 * sr))
    release = max(1, int(0.06 * sr))
    env = np.ones(n)
    env[: min(attack, n)] = np.linspace(0.0, 1.0, min(attack, n))
    env[max(0, n - release) :] *= np.linspace(1.0, 0.0, min(release, n))
    return env


def _formant_layer(t: np.ndarray, base: float, lyric: str) -> np.ndarray:
    vowel = _lyric_vowel(lyric)
    f1, f2 = VOWEL_FORMANTS[vowel]
    # very cheap vowel-like layer: not a real vocoder, only for mock preview
    return 0.12 * np.sin(2 * np.pi * f1 * t) + 0.06 * np.sin(2 * np.pi * f2 * t)


def render_mock(project: Project, track: Track, output_path: Path, voicebank: VoicebankManifest | None = None) -> tuple[Path, float]:
    sr = project.sample_rate or (voicebank.sample_rate if voicebank else 44100) or 44100
    bpm = project.default_bpm
    beats_to_seconds = 60.0 / bpm
    last_beat = max((n.start + n.duration for n in track.notes), default=4.0)
    length = int((last_beat * beats_to_seconds + 0.5) * sr)
    audio = np.zeros(length, dtype=np.float32)

    for note in track.notes:
        start = int(note.start * beats_to_seconds * sr)
        dur = max(1, int(note.duration * beats_to_seconds * sr))
        end = min(length, start + dur)
        if start >= length:
            continue
        t = np.arange(end - start, dtype=np.float32) / sr
        freq = midi_to_hz(note.midi)
        vibrato = 1.0 + 0.0035 * np.sin(2 * np.pi * 5.4 * t)
        phase = np.cumsum(freq * vibrato) / sr
        sawish = (
            0.48 * np.sin(2 * np.pi * phase)
            + 0.18 * np.sin(2 * np.pi * phase * 2)
            + 0.08 * np.sin(2 * np.pi * phase * 3)
        )
        breath = 0.02 * np.random.default_rng(abs(hash(note.id)) % (2**32)).normal(size=t.shape)
        vowel = _formant_layer(t, freq, note.lyric)
        env = _adsr(len(t), sr)
        audio[start:end] += (sawish + vowel + breath) * env * 0.22 * note.velocity

    audio = soft_limiter(audio)
    write_wav(output_path, audio, sr)
    return output_path, len(audio) / sr
