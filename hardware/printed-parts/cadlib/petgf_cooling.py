"""Selected PET-GF cooling values used when preparing current print projects.

This changes configuration; it performs no check and submits no printer job.
Historical native archives retain the commands that produced their evidence.
"""
import json


VALUES = {
    'fan_min_speed': '0',
    'fan_max_speed': '0',
    'additional_cooling_fan_speed': '0',
    'first_x_layer_fan_speed': '0',
    'first_x_layer_part_fan_speed': '0',
    'enable_overhang_bridge_fan': '1',
    'overhang_fan_speed': '70',
    'overhang_fan_threshold': '50%',
    'reduce_fan_stop_start_freq': '0',
    'pre_start_fan_time': '0',
}


def apply(settings):
    """Apply the selected values to PET-GF filament slots, retaining other materials."""
    identities = settings.get('filament_settings_id', [])
    if not identities:
        identities = [settings.get('name', '')]
    if isinstance(identities, str):
        identities = [identities]
    indices = [i for i, name in enumerate(identities)
               if 'pet-gf' in name.lower() or 'petgf' in name.lower()]
    changes = {}
    for key, value in VALUES.items():
        if not indices:
            break
        old = settings.get(key)
        new = list(old) if isinstance(old, list) else [str(old or '0')] * len(identities)
        for i in indices:
            while i >= len(new):
                new.append(new[-1] if new else '0')
            new[i] = value
        if new != old:
            changes[key] = {'from': old, 'to': new}
            settings[key] = new
    return changes


def apply_members(members):
    """Update project and embedded filament presets; return changed member settings."""
    changes = {}
    for name in list(members):
        if name == 'Metadata/project_settings.config' or (
                name.startswith('Metadata/filament_settings_') and name.endswith('.config')):
            settings = json.loads(members[name])
            changed = apply(settings)
            if changed:
                members[name] = (json.dumps(settings, indent=2) + '\n').encode()
                changes[name] = changed
    return changes
