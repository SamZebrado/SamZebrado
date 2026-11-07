"""Explicitly reproduce the final v5 combination of two separately fitted paths."""
import json
import shutil
from common import settings
cfg = settings()
root = cfg.work_dir / 'v5'
strict = json.loads((root / 'strict_smooth_event_parameters.json').read_text())
relaxed = json.loads((root / 'smooth_event_parameters.json').read_text())
strict['families']['relaxed'] = {
    'contact_events': [event for event in relaxed['families']['relaxed']['contact_events']
                       if event['string_index'] in [5, 6, 7, 8, 9, 10]]}
strict['geometry']['two_fit_routes'] = (
    'Strict forbids a sounded traversal of strings outside the six tested source notes; '
    'optional-contact route may traverse those coordinates with contact lifted. '
    'Both preserve all 42 ordered points.')
(root / 'physical_event_parameters.json').write_text(json.dumps(strict, indent=2) + '\n')
shutil.copyfile(root / 'smooth_routing.npz', root / 'relaxed_smooth_routing.npz')
