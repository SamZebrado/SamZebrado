#!/usr/bin/env python3
"""Reproducible source-fit pipeline and separate source-free parameter renderer."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
# Set before child imports to reproduce the original numerical execution context.
ENV = dict(os.environ, OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2')


def run(name, *args):
    subprocess.run([sys.executable, str(ROOT / 'src' / name), *map(str, args)], check=True, env=ENV)


def render(parameters, out):
    out.mkdir(parents=True, exist_ok=True)
    for name in ['render_from_parameters.py', 'render_shared.py']:
        run(name, '--work-dir', parameters, '--render-output', out)
    expected = parameters / 'expected_audio_sha256.json'
    if expected.exists():
        records = json.loads(expected.read_text())
        checks = {name: hashlib.sha256((out / name).read_bytes()).hexdigest() == digest
                  for name, digest in records.items()}
        (out / 'sha256_check.json').write_text(json.dumps(checks, indent=2) + '\n')
        if not all(checks.values()):
            raise SystemExit('Reference WAV SHA256 mismatch; inspect platform/numerical differences')
        print('Four reference WAV SHA256 checks passed', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    fit = sub.add_parser('fit', help='authorized input -> preprocessing -> v4/v5 fit -> audio -> page')
    fit.add_argument('--input', required=True, type=Path)
    fit.add_argument('--out', type=Path, default=Path('outputs/refit'))
    fit.add_argument('--intervals', type=Path, help='optional JSON active intervals; default entire input')
    fit.add_argument('--with-control', action='store_true', help='also fit shared timbre on the original v4 route')
    replay = sub.add_parser('render', help='saved parameters -> four synthetic WAVs -> page; no source audio')
    replay.add_argument('--parameters', type=Path, default=ROOT / 'parameters')
    replay.add_argument('--out', type=Path, default=Path('outputs/reference'))
    args = parser.parse_args()
    if args.command == 'fit':
        extra = ['--intervals', args.intervals] if args.intervals else []
        run('preprocess.py', '--input', args.input, '--work-dir', args.out, *extra)
        for name in ['fit_comparison.py', 'smooth_route.py', 'strict_smooth_route.py',
                     'merge_routes.py', 'fit_physical.py', 'evaluate.py']:
            run(name, '--work-dir', args.out)
        if args.with_control:
            run('fit_shared.py', '--work-dir', args.out)
        parameters = args.out
        audio = args.out / 'audio'
        page = args.out / 'site'
    else:
        parameters = args.parameters
        audio = args.out / 'audio'
        page = args.out / 'site'
    render(parameters, audio)
    run('export_demo.py', '--parameters', parameters, '--audio', audio, '--out', page)
    print(f'Done. Open {page / "index.html"} or serve that directory locally.', flush=True)


if __name__ == '__main__':
    main()
