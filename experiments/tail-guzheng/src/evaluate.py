"""Compute same-recording scalar-gain waveform scores; never copy source into a demo."""
import json
import numpy as np
from scipy.io import wavfile
from common import settings
cfg = settings()
rate, pcm = wavfile.read(cfg.work_dir / 'input.wav')
x = pcm.astype(float) / 32768
results = {}
for version, folder, suffix in [('v4', 'v4', ''), ('v5', 'v5/physical', '_shared')]:
    metrics = {}
    for family in ['strict', 'relaxed']:
        y = np.load(cfg.work_dir / folder / f'{family}{suffix}_raw.npy')
        power = float(y @ y)
        gain = float(x @ y / power) if power > 0 else 0.0
        error = float(np.linalg.norm(x - gain * y) / np.linalg.norm(x))
        corr = float(np.corrcoef(x, y)[0, 1]) if np.std(y) > 0 else None
        metrics[family] = {'gain': gain, 'waveform_NRMSE': error, 'correlation': corr,
                           'snr_db': float(-20 * np.log10(max(error, 1e-300)))}
    results[version] = metrics
    if version == 'v4':
        dest = cfg.work_dir / folder / 'playback_gains.json'
        dest.write_text(json.dumps({k: v['gain'] for k, v in metrics.items()}, indent=2) + '\n')
    else:
        (cfg.work_dir / folder / 'metrics.json').write_text(json.dumps(metrics, indent=2) + '\n')
(cfg.work_dir / 'fit_metrics.json').write_text(json.dumps(results, indent=2, allow_nan=False) + '\n')
print(json.dumps(results, indent=2))
