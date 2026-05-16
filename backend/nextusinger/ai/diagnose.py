from __future__ import annotations

from ..models import DiagnoseRequest, DiagnoseResponse


def diagnose_project(req: DiagnoseRequest) -> DiagnoseResponse:
    issues: list[str] = []
    suggestions: list[str] = []
    project = req.project
    if not project.tracks:
        issues.append("工程没有音轨。")
        suggestions.append("新建一个 Vocal Track，并添加音符。")
    for track in project.tracks:
        if not track.notes:
            issues.append(f"音轨 {track.name} 没有音符。")
        last_end = -1.0
        for note in sorted(track.notes, key=lambda n: n.start):
            if note.start < last_end - 1e-6:
                issues.append(f"音轨 {track.name} 中音符 {note.id} 与前一个音符重叠。")
            if not note.lyric.strip():
                issues.append(f"音符 {note.id} 缺少歌词。")
            if note.duration < 0.1:
                suggestions.append(f"音符 {note.id} 很短，可能需要合并或改为辅音/气口。")
            last_end = max(last_end, note.start + note.duration)
    if project.default_bpm < 60 or project.default_bpm > 200:
        suggestions.append("BPM 较极端，请确认导入 MIDI 的 tempo 是否正确。")
    if not issues:
        suggestions.append("未发现阻塞问题，可以尝试渲染或使用 AI 调音。")
    return DiagnoseResponse(issues=issues, suggestions=suggestions)
