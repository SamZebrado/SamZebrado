#!/usr/bin/env python3
"""Rebuild THIS validated v7 case from its existing artifacts; never refit or generically adapt new cases."""
import argparse
import hashlib
import json
import shutil
import wave
from pathlib import Path

PAGE_FILES = ['index.html', 'style.css', 'app.js', 'README.md', 'build_page.py']
AUDIO_FILE = 'v7_two_bank_shared_parameter_render.wav'

def build(input_dir, output_dir):
    source = Path(input_dir).resolve()
    destination = Path(output_dir).resolve()
    templates = Path(__file__).resolve().parent
    load = lambda name: json.loads((source / name).read_text(encoding='utf-8'))
    visual = load('trajectory_visualization.json')
    metrics, audit = load('metrics.json'), load('audit.json')
    if visual.get('version') != 'v7_two_bank_endpoint_sweeps':
        raise ValueError('Expected v7_two_bank_endpoint_sweeps artifacts.')
    families = visual['modal_amplitude_frames']['families']
    # Whitelist bank envelopes and aggregate initial state; omit coherent summed
    # envelope, source powers, source hash, source audio, and all raw analysis.
    frames = {key: visual['modal_amplitude_frames'][key]
              for key in ['frame_rate_Hz', 'time', 'definition']}
    frames['families'] = {key: families[key]
                         for key in ['shared_B', 'shared_A', 'initial_state']}
    result = {
        'version': 'v7',
        'duration': visual['metadata']['duration'],
        'activeIntervals': visual['metadata']['active_intervals'],
        'modes': [{'id': i, 'string': mode['j'], 'harmonic': mode['h'], 'hz': mode['f']}
                  for i, mode in enumerate(visual['metadata']['modes'])],
        'route': {key: visual['analytic_route'][key]
                  for key in ['endpoints', 'endpoint_times', 'start_endpoint', 'string_geometry']},
        'crossings': [{key: event[key] for key in [
            'time', 'half_cycle', 'direction', 'coordinate', 'note_index',
            'bank', 'enabled', 'strength', 'status']}
            for event in visual['candidate_crossings']],
        'frames': frames, 'metrics': metrics, 'audit': audit,
    }
    assert len(result['modes']) == 45
    assert len(result['route']['string_geometry']) == 42
    assert len(result['crossings']) == 864
    assert sum(event['enabled'] for event in result['crossings']) == 326
    assert all(not 20 < point['coordinate'] < 26 for point in result['route']['string_geometry'])
    times = [event['time'] for event in result['crossings']]
    assert times == sorted(times)
    assert frames['frame_rate_Hz'] == 20
    assert len(frames['time']) == 953
    for family in frames['families'].values():
        assert family['mode_ids'] == list(range(45))
        assert len(family['amplitudes']) == 953
        assert all(len(row) == 45 for row in family['amplitudes'])
    with wave.open(str(source / AUDIO_FILE)) as wav:
        assert (wav.getnframes(), wav.getframerate(), wav.getnchannels(), wav.getsampwidth()) == (1050127, 22050, 1, 2)
    destination.mkdir(parents=True, exist_ok=True)
    for filename in PAGE_FILES:
        origin, target = templates / filename, destination / filename
        if origin != target:
            shutil.copyfile(origin, target)
    if source / AUDIO_FILE != destination / AUDIO_FILE:
        shutil.copyfile(source / AUDIO_FILE, destination / AUDIO_FILE)
    (destination / 'data.json').write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    filenames = ['index.html', 'style.css', 'app.js', 'data.json', AUDIO_FILE, 'README.md', 'build_page.py']
    manifest = {
        'scope': 'v7 two-bank parameter-only comparison',
        'contains_source_audio': False, 'contains_source_envelopes': False,
        'files': [{'path': filename,
                   'bytes': (destination / filename).stat().st_size,
                   'sha256': hashlib.sha256((destination / filename).read_bytes()).hexdigest()}
                  for filename in filenames],
    }
    (destination / 'safe-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Built {len(filenames) + 1} files in {destination}; parameter-only assets validated. No fitting performed.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', required=True, help='Directory containing final v7 visualization, metrics, audit and parameter-rendered WAV.')
    parser.add_argument('--output-dir', required=True, help='Static output directory. Unrelated files are never removed.')
    args = parser.parse_args()
    build(args.input_dir, args.output_dir)
