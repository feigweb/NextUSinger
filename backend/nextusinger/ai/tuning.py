from __future__ import annotations

import math

from ..models import HarmonyRequest, HarmonyResponse, Note, PitchPoint, TuneRequest, TuneResponse

INTERVALS = {
    "third_up": 4,
    "third_down": -3,
    "fifth_up": 7,
    "octave_down": -12,
}


def auto_tune(req: TuneRequest) -> TuneResponse:
    points: list[PitchPoint] = []
    strength = req.strength
    vibrato_depth = {"stable": 12, "natural": 28, "expressive": 45}[req.style] * strength
    comments: list[str] = []

    for note in req.notes:
        attack = min(0.18, note.duration * 0.25)
        points.append(PitchPoint(beat=note.start, cents=-35 * strength))
        points.append(PitchPoint(beat=note.start + attack, cents=0))
        steps = max(2, int(note.duration * 4))
        for i in range(steps):
            frac = i / max(1, steps - 1)
            beat = note.start + note.duration * frac
            cents = math.sin(frac * math.tau * max(1.0, note.duration * 1.5)) * vibrato_depth
            if frac < 0.25:
                cents *= frac / 0.25
            points.append(PitchPoint(beat=round(beat, 4), cents=round(cents, 2)))
        points.append(PitchPoint(beat=note.start + note.duration, cents=-18 * strength))

    comments.append(f"已生成 {req.style} 风格 pitch curve，强度 {strength:.2f}。")
    comments.append("真实人声细节建议接入 RMVPE/F0 extractor 或已训练 variance model。")
    return TuneResponse(pitch=sorted(points, key=lambda p: p.beat), comments=comments)


def generate_harmony(req: HarmonyRequest) -> HarmonyResponse:
    interval = INTERVALS[req.interval]
    notes: list[Note] = []
    for n in req.notes:
        clone = n.model_copy(deep=True)
        clone.id = f"harmony-{n.id}"
        clone.midi = max(0, min(127, clone.midi + interval))
        clone.velocity = max(0.1, min(1.0, clone.velocity * 0.82))
        notes.append(clone)
    return HarmonyResponse(notes=notes)
