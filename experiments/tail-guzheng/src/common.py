"""Shared CLI for the preserved research scripts; no private path defaults."""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace


def settings():
    parser = argparse.ArgumentParser()
    parser.add_argument('--work-dir', type=Path, default=Path('outputs'))
    parser.add_argument('--render-output', type=Path)
    args = parser.parse_args()
    config_file = args.work_dir / 'config.json'
    config = json.loads(config_file.read_text()) if config_file.exists() else {}
    return SimpleNamespace(**vars(args), active_intervals=config.get('active_intervals'))
