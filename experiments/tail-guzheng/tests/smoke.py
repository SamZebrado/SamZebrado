"""Synthetic, non-private end-to-end test; no original recording or saved analysis needed."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import numpy as np
from scipy.io import wavfile
ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='tail_guzheng_smoke_') as temp:
    root = Path(temp)
    sr = 44100
    t = np.arange(4 * sr) / sr
    audio = np.zeros(len(t))
    # Six known pitches, nonoverlapping scan order and repeated decay/attack excitation.
    for index, midi in enumerate([50, 52, 54, 57, 59, 62] * 2):
        onset = .1 + index * .30
        u = np.maximum(t - onset, 0)
        gate = t >= onset
        f = 440 * 2 ** ((midi - 69) / 12)
        for harmonic, amplitude in [(1, .10), (2, .025), (3, .012)]:
            audio += gate * amplitude * (1 - np.exp(-u / .004)) * np.exp(-u / .3) * np.sin(2 * np.pi * f * harmonic * u)
    source = root / 'synthetic_stereo_44100.wav'
    wavfile.write(source, sr, np.stack([audio, audio * .9], axis=1).astype(np.float32))
    work = root / 'result'
    subprocess.run([sys.executable, str(ROOT / 'pipeline.py'), 'fit', '--input', str(source), '--out', str(work)], check=True,
                   env=dict(os.environ, OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2'))
    config = json.loads((work / 'config.json').read_text())
    assert config['sample_rate'] == 22050 and config['samples'] == 88200
    assert config['input_sample_rate'] == 44100
    for name in ['strict_full.wav', 'relaxed_full.wav', 'strict_shared_full.wav', 'relaxed_shared_full.wav']:
        rate, data = wavfile.read(work / 'audio' / name)
        assert rate == 22050 and data.shape == (88200,) and data.dtype == np.int16
        assert np.max(abs(data.astype(float))) > 0
        assert (work / 'site/assets' / name).read_bytes() == (work / 'audio' / name).read_bytes()
    html = (work / 'site/index.html').read_text()
    assert '__DATA__' not in html and 'v5_strict' in html
    meta = json.loads((work / 'v5/physical/shared_metadata.json').read_text())
    assert all(meta['families'][f]['shared_response_real_coefficients'] > 0 for f in ['strict', 'relaxed'])
    # Parameter-only route succeeds even after removing all input/analysis dependencies.
    import shutil
    clean = root / 'params_only'
    for folder, names in [('v4', ['comparison_parameters.json', 'strict_coefficients.json', 'relaxed_coefficients.json', 'playback_gains.json']),
                          ('v5/physical', ['shared_metadata.json', 'strict_shared_parameters.json', 'relaxed_shared_parameters.json', 'metrics.json'])]:
        (clean / folder).mkdir(parents=True, exist_ok=True)
        for name in names:
            shutil.copyfile(work / folder / name, clean / folder / name)
    replay = root / 'replay'
    subprocess.run([sys.executable, str(ROOT / 'pipeline.py'), 'render', '--parameters', str(clean), '--out', str(replay)], check=True)
    for audio_file in (work / 'audio').glob('*full.wav'):
        assert audio_file.read_bytes() == (replay / 'audio' / audio_file.name).read_bytes()
    print('SMOKE PASS: stereo float 44100 -> mono PCM16 22050 -> v4 -> two v5 routes -> merge -> shared fit -> gain -> 4 WAVs -> page -> isolated parameter-only rerender')
    print('Synthetic in-sample metrics:', (work / 'fit_metrics.json').read_text())
