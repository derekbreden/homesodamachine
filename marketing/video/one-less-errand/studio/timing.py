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
    originals = {scene['id']: (round(scene['start']*fps), scene['frames']) for scene in story['scenes']}
    for scene in story['scenes']:
        selected = [beat for beat in beats if beat['after_scene'] == scene['id']]
        extra = sum(beat['frames'] for beat in selected)
        original_start, original_frames = originals[scene['id']]
        scene['start'] = (original_start+added)/fps
        scene['frames'] += extra
        scene['end'] = scene['start']+scene['frames']/fps
        if extra:
            scene['extra_frames'] = extra
            if scene['id'] in edit.get('extend_motion', []):
                scene['source_frames'] = scene['frames']
                scene['motion_duration'] = scene['frames']/fps
                preroll = edit.get('motion_preroll_frames', {}).get(scene['id'], 0)
                if preroll:
                    scene['motion_offset'] = -preroll/fps
                    scene['motion_duration'] -= preroll/fps
            elif scene['kind'] in ('can', 'studio') and not scene.get('hold'):
                scene['source_frames'] = original_frames
                scene['frame_holds'] = [
                    {'source_frame': beat.get('after_source_frame', original_frames-1), 'frames': beat['frames']}
                    for beat in selected]
        added += extra
    story['duration'] = (round(story['duration']*fps)+added)/fps
    for event in story['sound_events']:
        scene = next(scene for scene in story['scenes']
                     if originals[scene['id']][0] <= event['frame'] < sum(originals[scene['id']]))
        source_frame = event['frame']-originals[scene['id']][0]
        event['frame'] = round(scene['start']*fps)+source_frame+sum(
            hold['frames'] for hold in scene.get('frame_holds', []) if source_frame > hold['source_frame'])
    story['narration_pauses'] = beats
    story['type_timing'] = edit.get('type_timing', {})
    story['score'] = edit.get('score', {})
    if 'narration_pickup' in edit:
        story['narration_pickup'] = edit['narration_pickup']
    story['caption_source_onsets'] = edit.get('caption_source_onsets', [])
    story['separate_benefit_captions'] = edit.get('separate_benefit_captions', False)
    return story


def local_time(story, shot_id, source_time):
    scene = next(scene for scene in story['scenes'] if scene['id'] == shot_id)
    return source_time+sum(hold['frames']/story['fps'] for hold in scene.get('frame_holds', [])
                           if source_time*story['fps'] >= hold['source_frame']+1)
