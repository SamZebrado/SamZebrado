"""Convert a user-authorized WAV to mono PCM16, 22050 Hz, without trimming time."""
import argparse
import json
import math
from pathlib import Path
import numpy as np
from scipy import signal
from scipy.io import wavfile


def prepare(source, work, intervals=None):
    rate, raw = wavfile.read(source)
    if raw.ndim not in (1, 2) or raw.size == 0:
        raise ValueError('Expected a nonempty mono or multichannel WAV')
    if raw.dtype.kind == 'u':
        audio = (raw.astype(float) - 128) / 128
    elif raw.dtype.kind == 'i':
        audio = raw.astype(float) / float(2 ** (raw.dtype.itemsize * 8 - 1))
    elif raw.dtype.kind == 'f':
        audio = raw.astype(float)
    else:
        raise ValueError('Unsupported WAV sample format')
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    if not np.isfinite(audio).all():
        raise ValueError('Non-finite input samples')
    if rate != 22050:
        factor = math.gcd(int(rate), 22050)
        audio = signal.resample_poly(audio, 22050 // factor, int(rate) // factor)
    duration = len(audio) / 22050
    if duration < .5:
        raise ValueError('Use at least 0.5 seconds of audio')
    if np.max(abs(audio)) == 0:
        raise ValueError('Silent input has no identifiable fitting target')
    active = intervals if intervals is not None else [[0.0, duration]]
    previous = -1.0
    for pair in active:
        if len(pair) != 2 or not (0 <= pair[0] < pair[1] <= duration + 1e-9) or pair[0] < previous or pair[1] - pair[0] < .04:
            raise ValueError('Intervals must be sorted, disjoint, in range, and >=40 ms')
        previous = pair[1]
    if not active:
        raise ValueError('At least one active interval is required')
    work.mkdir(parents=True, exist_ok=True)
    if (work / 'input.wav').exists() or (work / 'config.json').exists():
        raise FileExistsError('Choose a new output directory; existing analysis is not overwritten')
    clipped = int(np.count_nonzero((audio < -1) | (audio >= 1)))
    pcm = np.clip(np.rint(audio * 32768), -32768, 32767).astype(np.int16)
    wavfile.write(work / 'input.wav', 22050, pcm)
    config = {'sample_rate': 22050, 'samples': len(pcm), 'active_intervals': active,
              'preprocessing': 'Channel mean; polyphase resample; PCM16 quantization; no trimming, denoising or source separation',
              'input_sample_rate': int(rate), 'clipped_samples': clipped}
    (work / 'config.json').write_text(json.dumps(config, indent=2) + '\n')
    return config


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--work-dir', type=Path, default=Path('outputs'))
    parser.add_argument('--intervals', type=Path, help='JSON list of [start, end] in seconds')
    args = parser.parse_args()
    prepare(args.input, args.work_dir, json.loads(args.intervals.read_text()) if args.intervals else None)
