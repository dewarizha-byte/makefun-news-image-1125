#!/usr/bin/env python3
"""News-image entry: the day's infographic ships with the repo; this program copies it to /output."""
import os
import shutil

src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'entry.png')
out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
os.makedirs(out_dir, mode=0o755, exist_ok=True)
dst = os.path.join(out_dir, 'entry.png')
shutil.copyfile(src, dst)
os.chmod(dst, 0o644)
print(f"wrote {dst}")
