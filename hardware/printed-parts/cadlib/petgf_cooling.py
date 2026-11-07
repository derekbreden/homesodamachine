"""Prepare localized PET-GF cooling and bridge-foundation paths for current prints.

This prepares configuration and toolpaths; it submits no printer job.
Completed print archives retain the commands that produced their evidence.
"""
import copy
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import shlex
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from _scalar_provider import call as _rust_shared

VALUES = dict(_rust_shared('cooling.values'))


def apply(settings, *, project=True):
    """Apply the selected values to PET-GF filament slots, retaining other materials."""
    command = shlex.join([sys.executable, str(Path(__file__).resolve())]) if project else None
    updates = _rust_shared('cooling.apply', settings=settings, post_process_command=command)['updates']
    for key,change in updates:
        settings[key] = change['to']
    return {key:change for key,change in updates}


def apply_members(members):
    """Update project and embedded filament presets; return changed member settings."""
    changes = {}
    for name in _rust_shared('cooling.member_names',names=list(members)):
        settings = json.loads(members[name])
        changed = apply(settings, project=name == 'Metadata/project_settings.config')
        if changed:
            members[name] = (json.dumps(settings,indent=2) + '\n').encode()
            changes[name] = changed
    return changes


def _digest(path, algorithm='sha256'):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, algorithm).hexdigest()


def cli_project(project, directory):
    """Keep the GUI project intact and omit its cooling hook from the CLI input copy.

    CLI callers apply the same cooling stage to the emitted archive themselves.
    """
    project = Path(project)
    with zipfile.ZipFile(project) as source:
        member = 'Metadata/project_settings.config'
        settings = json.loads(source.read(member))
        scripts = settings.get('post_process', [])
        if not scripts:
            return project
        for script in scripts:
            if not script:
                continue
            args = shlex.split(script)
            if len(args) != 2 or Path(args[1]).resolve() != Path(__file__).resolve():
                raise ValueError('The native CLI cannot execute this project\'s additional post-processing scripts')
        settings['post_process'] = []
        output = Path(directory) / (project.stem + '.cli.3mf')
        with zipfile.ZipFile(output, 'w') as target:
            for item in source.infolist():
                if item.filename == member:
                    target.writestr(copy.copy(item), json.dumps(settings, indent=2) + '\n')
                else:
                    with source.open(item) as src, target.open(copy.copy(item), 'w', force_zip64=True) as dest:
                        shutil.copyfileobj(src, dest)
    return output


def foundation_file(source, output, settings):
    """Emit scoped bridge-foundation cooling through the shared Rust provider."""
    return _rust_shared('cooling.foundation', input=str(Path(source).resolve()),
        output=str(Path(output).resolve()), settings=settings,
        policy=_rust_shared('cooling.foundation_policy'))


def apply_archive(path, project=None):
    """Package the processed native paths and their checksum without altering model meshes."""
    path = Path(path)
    original_hash = _digest(path)
    packaged_report = 'Metadata/hsm_cooling.json'
    with zipfile.ZipFile(path) as archive:
        if packaged_report in archive.namelist():
            result = json.loads(archive.read(packaged_report))
            return {**result, 'archive_sha256': original_hash, 'changed': False, 'already_processed': True}
    with zipfile.ZipFile(project or path) as profile:
        settings = json.loads(profile.read('Metadata/project_settings.config'))
    reports = []
    replacements = {}
    with tempfile.TemporaryDirectory(prefix='.cooling-', dir=path.parent) as scratch:
        scratch = Path(scratch)
        with zipfile.ZipFile(path) as archive:
            for member in archive.namelist():
                if not member.endswith('.gcode'):
                    continue
                source = scratch / Path(member).name
                with archive.open(member) as src, source.open('wb') as dest:
                    shutil.copyfileobj(src, dest)
                output = source.with_suffix('.processed.gcode')
                reading = foundation_file(source, output, settings)
                reading.update(member=member, input_gcode_sha256=_digest(source))
                if reading.get('changed') or reading.get('already_processed'):
                    processed = output if reading.get('changed') else source
                    reading['output_gcode_sha256'] = _digest(processed)
                    if reading.get('changed'):
                        replacements[member] = processed
                    replacements[member + '.md5'] = _digest(processed, 'md5').encode()
                    raw = path.parent / Path(member).name
                    if reading.get('changed') and raw.is_file() and _digest(raw) == reading['input_gcode_sha256']:
                        shutil.copyfile(processed, raw)
                reports.append(reading)
            added = sum(r.get('added_commanded_motion_seconds', 0.) for r in reports)
            result = {'input_archive_sha256': original_hash, 'changed': bool(replacements), 'members': reports,
                'added_commanded_motion_seconds': added,
                'estimate_scope': 'Native estimate plus the added constant-feed motion time; acceleration and fan spin-up are not simulated.'}
            if replacements and 'Metadata/slice_info.config' in archive.namelist():
                info = ET.fromstring(archive.read('Metadata/slice_info.config'))
                for plate in info.findall('plate'):
                    index = plate.find("metadata[@key='index']")
                    if index is None:
                        continue
                    seconds = sum(r.get('added_commanded_motion_seconds', 0.) for r in reports
                        if r['member'] == f"Metadata/plate_{index.get('value')}.gcode")
                    for field in plate.findall("metadata[@key='prediction']"):
                        field.set('value', str(math.ceil(float(field.get('value')) + seconds)))
                replacements['Metadata/slice_info.config'] = ET.tostring(info, encoding='utf-8', xml_declaration=True)
            if replacements:
                temporary = scratch / 'processed.3mf'
                with zipfile.ZipFile(temporary, 'w') as target:
                    for item in archive.infolist():
                        value = replacements.get(item.filename)
                        if isinstance(value, Path):
                            with value.open('rb') as src, target.open(copy.copy(item), 'w', force_zip64=True) as dest:
                                shutil.copyfileobj(src, dest)
                        elif value is None:
                            with archive.open(item) as src, target.open(copy.copy(item), 'w', force_zip64=True) as dest:
                                shutil.copyfileobj(src, dest)
                        else:
                            target.writestr(copy.copy(item), value)
                    target.writestr(packaged_report, json.dumps(result, indent=2) + '\n', compress_type=zipfile.ZIP_DEFLATED)
        if replacements:
            os.replace(temporary, path)
    result['archive_sha256'] = _digest(path)
    path.with_suffix('.cooling.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def apply_directory(directory, project):
    """Apply the shared cooling output stage to a native slice directory."""
    directory = Path(directory)
    reports = {p.name: apply_archive(p, project) for p in sorted(directory.glob('*.gcode.3mf'))}
    result_path = directory / 'result.json'
    if result_path.is_file():
        result = json.loads(result_path.read_text())
        for row in result.get('sliced_plates', []):
            increments = []
            for reading in reports.values():
                if not reading.get('changed'):
                    continue
                for member in reading['members']:
                    if member['member'] == f"Metadata/plate_{row['id']}.gcode":
                        increments.append(member.get('added_commanded_motion_seconds', 0.))
            row['total_predication'] += max(increments, default=0.)
        result_path.write_text(json.dumps(result, indent=2) + '\n')
    return reports


def _environment_settings():
    settings = {}
    for key in ['filament_settings_id', 'overhang_fan_speed', 'filament_bridge_speed', 'bridge_speed']:
        raw = os.environ.get('SLIC3R_' + key.upper(), '')
        try:
            value = json.loads(raw)
        except (ValueError, TypeError):
            delimiter = ';' if key == 'filament_settings_id' or ';' in raw else ','
            value = next(csv.reader([raw], delimiter=delimiter))
        settings[key] = value if isinstance(value, list) else [value]
    return settings


if __name__ == '__main__':
    source = Path(sys.argv[1])
    output = source.with_suffix(source.suffix + '.cooling')
    reading = foundation_file(source, output, _environment_settings())
    if reading.get('changed'):
        os.replace(output, source)
    elif output.exists():
        output.unlink()
    source.with_suffix(source.suffix + '.cooling.json').write_text(json.dumps(reading, indent=2) + '\n')
