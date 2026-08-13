#!/usr/bin/env python3
"""Save the exact Python/pip environment after a successful reproduction run."""
from pathlib import Path
import platform
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
out = root / 'requirements-reproduced.txt'
freeze = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'], text=True)
out.write_text(f'# Python {platform.python_version()}\n' + freeze, encoding='utf-8')
print(f'Saved {out}')
