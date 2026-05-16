from __future__ import annotations

import re

from ..models import PhonemeRequest, PhonemeResponse

PINYIN_HINTS = {
    "你": "n i",
    "我": "w o",
    "他": "t a",
    "她": "t a",
    "爱": "ai",
    "的": "d e",
    "了": "l e",
    "风": "f eng",
    "光": "g uang",
    "梦": "m eng",
    "海": "h ai",
    "星": "x ing",
}


def draft_phonemes(req: PhonemeRequest) -> PhonemeResponse:
    lyrics = re.sub(r"\s+", " ", req.lyrics.strip())
    phonemes: list[str] = []
    for ch in lyrics:
        if ch.isspace():
            continue
        if ch in PINYIN_HINTS:
            phonemes.extend(PINYIN_HINTS[ch].split())
        elif "a" <= ch.lower() <= "z":
            phonemes.append(ch.lower())
        elif ch in "，。,.!?！？":
            phonemes.append("pau")
        else:
            phonemes.append("la")
    return PhonemeResponse(phonemes=phonemes, normalized_lyrics=lyrics)
