from nextusinger.ai.tuning import auto_tune, generate_harmony
from nextusinger.models import HarmonyRequest, Note, TuneRequest


def test_auto_tune_points():
    notes = [Note(id="n1", start=0, duration=1, midi=60, lyric="你")]
    resp = auto_tune(TuneRequest(notes=notes))
    assert len(resp.pitch) > 3
    assert resp.pitch[0].beat == 0


def test_harmony():
    notes = [Note(id="n1", start=0, duration=1, midi=60, lyric="你")]
    resp = generate_harmony(HarmonyRequest(notes=notes, interval="fifth_up"))
    assert resp.notes[0].midi == 67
