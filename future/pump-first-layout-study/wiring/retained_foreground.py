"""Unchanged native cable passages on the display and pump cartridge bulkhead."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3]

def passages():
 # Reading the recorded native datums avoids invoking the production CAD
 # assembly's import-time manual build while another study producer runs.
 return json.loads(Path(__file__).with_name('retained-foreground-passages.json').read_text())['passages']
