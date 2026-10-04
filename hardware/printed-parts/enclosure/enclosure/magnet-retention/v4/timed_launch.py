#!/usr/bin/env python3
"""Submit this frozen cartridge/cap trial once, inside its authorized time window."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import fcntl
import hashlib
import json
from pathlib import Path
import queue
import shutil
import sys
import time
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/bambu_send.py').is_file())
sys.path.insert(0, str(ROOT / 'tools'))
import bambu_printer
import bambu_send

PLAN = HERE / 'mark2-launch-plan.json'
RECEIPT = HERE / 'mark2-launch.json'


def now():
    return datetime.now(timezone.utc)


def save(path, data):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(path)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_bindings(plan):
    bindings = plan['bindings']
    for key in ('project', 'native_archive'):
        if sha(ROOT / bindings[key]) != bindings[key + '_sha256']:
            raise RuntimeError(f'{key} differs from the frozen review')
    with zipfile.ZipFile(ROOT / bindings['native_archive']) as archive:
        if hashlib.sha256(archive.read('Metadata/plate_1.gcode')).hexdigest() != bindings['gcode_sha256']:
            raise RuntimeError('G-code differs from the frozen review')
    for component in bindings['components']:
        for extension in ('stl', 'step'):
            source = HERE.parent.parent / f"enclosure-{component['part']}.{extension}"
            if sha(source) != component[f'source_{extension}_sha256']:
                raise RuntimeError(f"Current {component['part']} {extension} differs from the review")
    review = json.loads((HERE.parent / bindings['native_record']).read_text())
    if not review['native_checks_pass']:
        raise RuntimeError('Native checks do not pass')
    for key in ('native_archive_sha256', 'gcode_sha256', 'project_sha256'):
        if review[key] != bindings[key]:
            raise RuntimeError(f'Native review {key} differs from launch bindings')


def temperatures(status):
    def decode(packed):
        return {'actual_c': packed & 65535, 'target_c': packed >> 16}
    device = status.get('device', {})
    extruders = {str(item['id']): decode(item['temp'])
                 for item in device.get('extruder', {}).get('info', []) if 'temp' in item}
    chamber = device.get('ctc', {}).get('info', {}).get('temp')
    return {'extruders': extruders, 'bed_actual_c': status.get('bed_temper'),
            'bed_target_c': status.get('bed_target_temper'),
            'chamber': decode(chamber) if chamber is not None else None}


def observation(name, status):
    keys = ('task_id', 'job_id', 'subtask_name', 'gcode_file', 'print_type', 'gcode_state',
            'layer_num', 'total_layer_num', 'mc_percent', 'mc_remaining_time', 'print_error', 'hms')
    return {'printer': name, 'observed_at': now().isoformat(),
            **{key: status.get(key) for key in keys}, **temperatures(status)}


def read_both(printers):
    def read(name):
        with bambu_printer.Connection(printers[name], 12) as connection:
            return name, connection.status()
    with ThreadPoolExecutor(max_workers=2) as pool:
        return dict(pool.map(read, ('Mark2', 'H2C')))


def ready_mark2(status, plan):
    readiness = plan['operator_readiness']
    for field in ('task_id', 'job_id', 'subtask_name'):
        if str(status.get(field)) != str(readiness['bed_clear_after_' + field]):
            raise RuntimeError('Mark2 has changed jobs since the authorized bed-clear report; nothing sent')
    if status.get('gcode_state') not in ('IDLE', 'FINISH', 'FAILED'):
        raise RuntimeError(f"Mark2 is {status.get('gcode_state')}; no submission")
    if status.get('print_error') or status.get('hms') or bambu_send.manual_heat(status):
        raise RuntimeError('Mark2 reports a fault or an active manual heating/loading operation')
    spools = {str(item['id']): item for item in status.get('vir_slot', [])}
    if spools.get('254', {}).get('tray_type') != 'PET-CF':
        raise RuntimeError('Mark2 external left spool is not the reviewed PET-GF/PET-CF mapping')
    left = next((item for item in status.get('device', {}).get('nozzle', {}).get('info', [])
                 if item.get('id') == 1), {})
    if left.get('type') != 'HS01' or float(left.get('diameter', 0)) != 0.4:
        raise RuntimeError('Mark2 fixed left nozzle is not the reviewed hardened standard-flow 0.4 mm')


def deadline_allows(plan, when):
    timing = plan['timing']
    forecast = when + timedelta(seconds=timing['estimated_start_to_pause_seconds']
                                + timing['acceptance_allowance_seconds'])
    return forecast <= datetime.fromisoformat(timing['pause_cutoff_utc'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--dry-run', action='store_true')
    modes.add_argument('--launch', action='store_true')
    args = parser.parse_args()
    plan = json.loads(PLAN.read_text())
    verify_bindings(plan)
    if args.launch:
        if plan['state'] != 'scheduled_authorized' or plan.get('send_attempted'):
            raise RuntimeError('This plan is not awaiting an authorized first Send')
        if RECEIPT.exists() and json.loads(RECEIPT.read_text()).get('send_attempted'):
            raise RuntimeError('A Send is already recorded; do not submit again')
        if now() < datetime.fromisoformat(plan['timing']['prepare_not_before_utc']):
            raise RuntimeError('The scheduled preparation window has not opened; nothing sent')
        if not deadline_allows(plan, now()):
            plan.update(state='abandoned_deadline', abandoned_at=now().isoformat())
            save(PLAN, plan)
            raise RuntimeError('Forecast is later than the authorized magnet-pause cutoff; nothing sent')

    printers = bambu_printer.configured_printers()
    readings = read_both(printers)
    ready_mark2(readings['Mark2'], plan)
    preflight = {'observed_at': now().isoformat(), 'bindings_verified': True,
                 'readings': [observation(name, status) for name, status in readings.items()],
                 'send_attempted': False}
    original = ROOT / plan['bindings']['native_archive']
    imported = ROOT / '.cache/printer-control/cartridge-cap-v4-timed-import' / original.name
    imported.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(original, imported)
    bambu_send.SEND_ROUNDS = 1
    replies = []
    drain = bambu_send.Listener.drain

    def remember_replies(listener):
        heard = drain(listener)
        replies.extend(heard)
        return heard
    bambu_send.Listener.drain = remember_replies
    original_ax = bambu_send.ax
    peer_key = None
    peer_stable_since = time.monotonic()

    with (ROOT / '.cache/printer-control/bambu-print.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with bambu_printer.Connection(printers['H2C'], 12) as peer:
            peer.status()
            peer_key = tuple(peer.state['print'].get(k) for k in
                             ('task_id', 'job_id', 'subtask_name', 'gcode_state'))
            peer_stable_since = time.monotonic()

            def observe_peer():
                nonlocal peer_key, peer_stable_since
                while True:
                    try:
                        message = peer.messages.get_nowait()
                    except queue.Empty:
                        break
                    if isinstance(message, Exception):
                        raise message
                    if isinstance(message, dict):
                        bambu_printer.merge_status(peer.state, message)
                        current = peer.state.get('print', {})
                        key = tuple(current.get(k) for k in ('task_id', 'job_id', 'subtask_name', 'gcode_state'))
                        if key != peer_key or current.get('gcode_state') == 'PREPARE':
                            peer_key, peer_stable_since = key, time.monotonic()
                current = peer.state.get('print', {})
                key = tuple(current.get(k) for k in ('task_id', 'job_id', 'subtask_name', 'gcode_state'))
                if key != peer_key or current.get('gcode_state') == 'PREPARE':
                    peer_key, peer_stable_since = key, time.monotonic()
                return time.monotonic() - peer_stable_since

            def guarded_ax(*commands, **kwargs):
                if commands[:2] == ('press', 'confirm'):
                    target = datetime.fromisoformat(plan['timing']['target_acceptance_utc'])
                    target -= timedelta(seconds=plan['timing']['expected_send_to_acceptance_seconds'])
                    print('Send dialog ready; waiting for target time and 180 seconds of peer stability', flush=True)
                    while True:
                        stable = observe_peer()
                        if not deadline_allows(plan, now()):
                            raise RuntimeError('Magnet-pause cutoff cannot be met; nothing sent')
                        if now() >= target and stable >= plan['shared_circuit_spacing_seconds']:
                            break
                        time.sleep(1)
                    fresh = read_both(printers)
                    ready_mark2(fresh['Mark2'], plan)
                    peer.status()
                    if observe_peer() < plan['shared_circuit_spacing_seconds']:
                        raise RuntimeError('Peer start/resume changed during the final check; nothing sent')
                    verify_bindings(plan)
                    if not deadline_allows(plan, now()):
                        raise RuntimeError('Magnet-pause cutoff cannot be met; nothing sent')
                    if RECEIPT.exists() and json.loads(RECEIPT.read_text()).get('send_attempted'):
                        raise RuntimeError('A Send is already recorded; nothing more sent')
                    nodes = bambu_send.tree()
                    if bambu_send.selector(nodes) != 'Mark2' or bambu_send.tile(nodes)['label'] != 'Ext PET-CF':
                        raise RuntimeError('Final printer or external left filament mapping differs from the review')
                    if {k: v[0] for k, v in bambu_send.options(nodes).items()} != bambu_send.STANDING_OPTIONS:
                        raise RuntimeError('Final print options differ from the standing options')
                    confirm = bambu_send.find(nodes, role='AXButton', label='confirm')
                    if not confirm or not confirm[0]['enabled']:
                        raise RuntimeError('The final Send control is disabled; nothing sent')
                    stable = observe_peer()
                    if stable < plan['shared_circuit_spacing_seconds'] or not deadline_allows(plan, now()):
                        raise RuntimeError('Final startup spacing or pause deadline is not satisfied; nothing sent')
                    receipt = {'state': 'send_attempted_waiting_acceptance', 'send_attempted': True,
                               'send_count': 1, 'sent_at': now().isoformat(), 'bindings': plan['bindings'],
                               'before_send': [observation(name, status) for name, status in fresh.items()],
                               'peer_stable_seconds': stable, 'standing_options': bambu_send.STANDING_OPTIONS}
                    save(RECEIPT, receipt)
                    plan.update(state='send_attempted_waiting_acceptance', send_attempted=True,
                                sent_at=receipt['sent_at'])
                    save(PLAN, plan)
                return original_ax(*commands, **kwargs)

            if args.launch:
                bambu_send.ax = guarded_ax
            sys.argv = ['bambu_send.py', str(imported), 'Mark2', '--busy-wait', '0']
            if args.dry_run:
                sys.argv.append('--dry-run')
            try:
                bambu_send.main()
            except BaseException as error:
                if RECEIPT.exists() and json.loads(RECEIPT.read_text()).get('send_attempted'):
                    receipt = json.loads(RECEIPT.read_text())
                    receipt.update(state='acceptance_requires_review', failure=str(error), replies=replies)
                    save(RECEIPT, receipt)
                    plan.update(state='acceptance_requires_review')
                    save(PLAN, plan)
                elif bambu_send.dialog(bambu_send.tree(check=False)):
                    original_ax('press', 'cancel', '--role', 'AXButton', check=False)
                raise

    verify_bindings(plan)
    if args.dry_run:
        preflight.update(dialog_verified=True, standing_options=bambu_send.STANDING_OPTIONS)
        save(HERE / 'mark2-preflight.json', preflight)
        print('Preflight complete; no Send was pressed', flush=True)
        return
    accepted = read_both(printers)['Mark2']
    before_id = readings['Mark2'].get('task_id')
    if (accepted.get('subtask_name') != original.name or accepted.get('gcode_state') not in ('PREPARE', 'RUNNING')
            or not accepted.get('task_id') or accepted.get('task_id') == before_id or accepted.get('print_error')):
        raise RuntimeError('No verified new matching task; inspect the recorded Send without repeating it')
    receipt = json.loads(RECEIPT.read_text())
    receipt.update(state='accepted', task_id=accepted['task_id'], accepted_at=now().isoformat(),
                   acceptance=observation('Mark2', accepted), replies=replies,
                   project_file_reply_success=any(item.get('command') == 'project_file'
                                                  and str(item.get('result', '')).upper() == 'SUCCESS'
                                                  for item in replies),
                   estimated_pause_at=(now() + timedelta(seconds=plan['timing']['estimated_start_to_pause_seconds'])).isoformat())
    save(RECEIPT, receipt)
    plan.update(state='accepted', submitted=True, task_id=receipt['task_id'], accepted_at=receipt['accepted_at'])
    save(PLAN, plan)
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == '__main__':
    main()
