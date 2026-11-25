#!/usr/bin/env python3
"""News-image entry: the day's infographic ships with the repository.

The program copies the finished image to the output directory. It takes the
source path and output directory from arguments or environment, checks the
image's limits (PNG/JPEG under 1 MiB), and leaves every file world-readable
so the grader can collect the outputs.
"""
import argparse
import os
import shutil
import sys


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description="Copy the day's news image to the output directory")
    parser.add_argument("--input", default=os.environ.get("MAKEFUN_INPUT", os.path.join(here, "entry.png")))
    parser.add_argument("--output", default=os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    args = parser.parse_args()

    src = args.input
    if not os.path.isfile(src):
        print(f"entry: no image at {src}", file=sys.stderr)
        return 2

    with open(src, "rb") as fh:
        data = fh.read()
    if len(data) > 1_048_576:
        print(f"entry: {src} is {len(data)} bytes, over the 1 MiB cap", file=sys.stderr)
        return 2
    if not (data[:8] == b"\x89PNG\r\n\x1a\n" or data[:2] == b"\xff\xd8"):
        print(f"entry: {src} is neither a PNG nor a JPEG", file=sys.stderr)
        return 2

    out_dir = args.output
    os.makedirs(out_dir, mode=0o755, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    os.chmod(dst, 0o644)
    os.chmod(out_dir, 0o755)
    print(f"entry: wrote {dst} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
