"""Observe acceptance of a single CUA Send; this script does not send a print."""
from datetime import datetime, timezone
from pathlib import Path
import json
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/bambu_print.py').is_file())
STEM = '2026-10-25-sculpted-cover-front-overlap-black-left04-z004-mark2'
sys.path.insert(0, str(ROOT / 'tools'))
from bambu_print import PrinterWatch, accepted, archive_details, verify_spools
from bambu_printer import configured_printers

archive = HERE / (STEM + '.gcode.3mf')
details = archive_details(archive)
keys = ['job_id', 'subtask_name', 'gcode_state', 'print_error', 'hms', 'layer_num',
        'total_layer_num', 'mc_remaining_time', 'mc_percent', 'nozzle_temper',
        'nozzle_target_temper', 'bed_temper', 'bed_target_temper']
with PrinterWatch(configured_printers()['Mark2']) as watch:
    verify_spools(details, watch.reading)
    print('Watching Mark2 for the new cover task; no print command issued by observer.', flush=True)
    end = time.monotonic() + 180
    while time.monotonic() < end:
        watch.drain(1)
        if watch.reply and watch.reply.get('result') not in ('SUCCESS', 'success'):
            raise RuntimeError(f'Print command rejected: {watch.reply}')
        if accepted(watch.initial, watch.reading, archive.name):
            receipt = {'printer': 'Mark2', 'observed_at_utc': datetime.now(timezone.utc).isoformat(),
                **{k: watch.reading.get(k) for k in keys}, 'archive': details,
                'previous_job_id': str(watch.initial.get('job_id')),
                'send_method': 'Bambu Connect CUA; one Send click', 'send_click_count': 1,
                'launch_options': {'Timelapse': 'On', 'Auto bed leveling': 'On',
                    'Flow dynamic calibration': 'Auto', 'Nozzle Offset Calibration': 'Auto'},
                'external_spool_mapping': {'left': 254, 'type': 'PET-CF', 'colour': '161616FF'},
                'selected_plate': 'Textured PEI Plate',
                'shared_circuit': {'peer': 'Mark1', 'peer_task_id': '1374272357',
                    'peer_accepted_at_utc': '2026-10-25T16:39:30.598475+00:00',
                    'peer_already_running_observed_at_utc': '2026-10-25T16:49:15.227860+00:00',
                    'required_spacing_seconds': 180},
                'command_reply': watch.reply, 'events': watch.events,
                'authorization_quote': 'Please print your recommended faucet display cover on mark2, the bed is clear and ready.'}
            (HERE / 'launch.json').write_text(json.dumps(receipt, indent=2) + '\n')
            print(json.dumps(receipt, indent=2), flush=True)
            break
    else:
        raise TimeoutError('No new matching Mark2 task observed; do not repeat Send without checking the app and printer.')
