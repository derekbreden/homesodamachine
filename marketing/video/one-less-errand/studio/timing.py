"""Read the picture clock and apply an optional processing-beat edit."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_story(timing_path: Path | None = None):
    story = json.loads((HERE/'story.json').read_text())
    if timing_path is None:
        return story
    edit = json.loads(timing_path.read_text())
    beats = edit['beats']
    fps = story['fps']
    added = 0
    boundaries = []
    for scene in story['scenes']:
        extra = sum(beat['frames'] for beat in beats if beat['after_scene'] == scene['id'])
        original_end = round(scene['end']*fps)
        scene['start'] += added/fps
        scene['frames'] += extra
        scene['end'] = scene['start']+scene['frames']/fps
        if extra:
            scene['extra_frames'] = extra
            boundaries.append((original_end, extra))
        added += extra
    story['duration'] = (round(story['duration']*fps)+added)/fps
    for event in story['sound_events']:
        event['frame'] += sum(extra for boundary, extra in boundaries if event['frame'] >= boundary)
    story['narration_pauses'] = beats
    story['type_timing'] = edit.get('type_timing', {})
    story['score'] = edit.get('score', {})
    return story
