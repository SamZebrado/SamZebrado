# v7 two-bank endpoint page

Buildless static Chinese page. Playback and full cross-bank motion precede terminology and method comparisons. Only v7 is added in this public increment. The existing v4/v5 page remains at `../`; v6 audio and its page are not published here.

## Public-safe assets

`data.json` whitelists mode IDs/nominal groups/fitted Hz, route and string geometry, fitted crossing strengths, per-bank parameter-rendered envelopes and aggregate initial-state envelopes, and audit/metric summaries. It omits source audio, source-derived envelopes, mode powers, and the coherent summed envelope (so it cannot accidentally be used as either bank's display).

The only audio is `v7_two_bank_shared_parameter_render.wav`: newly rendered from parameters, mono PCM16, 22,050 Hz, 1,050,127 samples. No original waveform is mixed into it.

## UI implementation

- Both maps use all 42 supplied geometry points, B 0–20 and A 26–46, not duplicated A-local animation. Analytic route endpoints are 4.5 and 36.5. The marker crosses the full interval continuously.
- There is no source in the spatial gap 20–26. Existing string ringing may continue during traversal. Recording-time gaps are a separate condition and silence the audio while motion continues.
- Each of B/A has six independent response groups. Bank choice selects `shared_B` or `shared_A` only. Aggregate `initial_state` has its own table column and is never assigned to a bank.
- Six bars and six rows are constructed once. Nominal h1–6 and h7–12 pages cover all 45 inherited mode IDs for each bank. Missing slots are zero, actual fitted Hz are displayed, and both banks share the same 0–0.6 amplitude scale.
- Candidate table contains first-stage scores. The selected candidate's refined 0.550716 result is separately labeled. Model freedom differs from the A-only v6 control.
- Inline help is collapsed initially; clicking expands normal document flow without covering plots. Keyboard Escape closes help.

## Validation

JS syntax and data assertions passed: 42 geometry points, 864 sorted crossings, 326 enabled modeled crossings, no source points in the spatial gap, 953×45 envelope frames for each displayed family. Browser QA status is recorded below after preview.

CUA Chrome QA passed on desktop and 390/320 px iframe layouts (content viewports 375/305 px with scrollbars): entry from parent, retained v6 and parent links, WAV metadata/play/pause and progressing clock, six bars/six rows stable across playback and bank/page changes, all 42 map points and string lines, spatial gap x=23.48 with zero highlighted triggers, recording-time gap with zero modal amplitudes and moving-route velocity, future path, inline mobile help and no horizontal page overflow. At 7 seconds D3 B/A amplitudes differed (0.00226 / 0.01611) while the separately displayed aggregate initial state stayed identical (0.00080), confirming bank-specific visualization. No app-origin warnings/errors in the final localhost-filtered console capture. The temporary QA harness was removed. Subjective listening quality and biological feasibility were not assessed.

## Case-specific exporter

This exporter supports only the validated case in this directory. The HTML results and geometry/count checks are case-specific, not automatically adapted to arbitrary new inputs or refits. Those require a new data/content audit and template changes.

## Rebuild from existing parameters (no refitting)

Keep this directory's HTML/CSS/JS, README and `build_page.py` together as the page template. Python 3 standard library is sufficient. The input directory must contain the final v7 `trajectory_visualization.json`, `metrics.json`, `audit.json`, and `v7_two_bank_shared_parameter_render.wav`.

Upstream sequence is: the old preprocessing and fit-comparison stages provide the inherited modal dictionary; run the v7 two-bank fit, then its independent parameter renderer, then the v7 audit/visualization stage. Only after those artifacts are available, run this exporter. The old `export_demo` is not compatible with v7. This page exporter does not run any upstream stage or read the source recording; existing validated parameters and rendered artifacts are sufficient.

```
python3 build_page.py --input-dir /path/to/final-v7-artifacts --output-dir /path/to/static/two-bank-endpoint
```

The CLI validates geometry, modes, crossings, frame dimensions and WAV format, strips non-whitelisted metadata, copies the page and single generated WAV, and writes the SHA-256 whitelist. It can refresh the current page directory, or build into a fresh directory. Existing unrelated output files are not deleted. Publish only the whitelist plus `safe-manifest.json`.
