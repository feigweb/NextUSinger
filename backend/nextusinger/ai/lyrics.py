from __future__ import annotations

from ..models import LyricsRequest, LyricsResponse

MOOD_WORDS = {
    "清新": ["风", "光", "窗", "海", "星"],
    "热血": ["火", "梦", "跑", "山", "光"],
    "伤感": ["雨", "夜", "影", "旧", "海"],
    "未来": ["银", "轨", "电", "云", "光"],
}


def generate_lyrics(req: LyricsRequest) -> LyricsResponse:
    seeds = MOOD_WORDS.get(req.mood, MOOD_WORDS["清新"])
    prompt = req.prompt.strip("，。,. ") or "新的旋律"
    lines: list[str] = []
    for i in range(max(1, min(req.bars, 16))):
        a = seeds[i % len(seeds)]
        b = seeds[(i + 2) % len(seeds)]
        if req.language.lower().startswith("zh"):
            line = f"把{prompt}唱进{a}里，让{b}替我回应你"
        else:
            line = f"I sing {prompt} into the {a}, and let the {b} answer me"
        lines.append(line)
    return LyricsResponse(lines=lines, tips=["规则版歌词助手已启用；可在 ai/provider.py 中接入 LLM。"])
