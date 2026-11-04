"""Selected PET-GF cooling values used when preparing current print projects.

This changes configuration; it performs no check and submits no printer job.
Historical native archives retain the commands that produced their evidence.
"""
import json
from _scalar_provider import call as _rust_shared

VALUES = dict(_rust_shared('cooling.values'))


def apply(settings):
    """Apply the selected values to PET-GF filament slots, retaining other materials."""
    updates = _rust_shared('cooling.apply',settings=settings)['updates']
    for key,change in updates:
        settings[key] = change['to']
    return {key:change for key,change in updates}


def apply_members(members):
    """Update project and embedded filament presets; return changed member settings."""
    changes = {}
    for name in _rust_shared('cooling.member_names',names=list(members)):
        settings = json.loads(members[name])
        changed = apply(settings)
        if changed:
            members[name] = (json.dumps(settings,indent=2) + '\n').encode()
            changes[name] = changed
    return changes
