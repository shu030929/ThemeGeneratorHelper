#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*.py'
PYTHONPATH=src python -m makeetheme ios examples/theme.json --out dist/example.ktheme
PYTHONPATH=src python -m makeetheme android-res examples/theme.json --out dist/example-android-resources.zip
python - <<'PY'
from pathlib import Path
assert Path('dist/example.ktheme').exists()
assert Path('dist/example-android-resources.zip').exists()
print('checks passed')
PY
