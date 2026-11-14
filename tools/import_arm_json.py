#!/usr/bin/env python3
"""Convert an old-stack data/arm.json into an arm.yaml profile snippet.

The old calibration was:
    "COM": "COM5",
    "servo-angle": [[scale, offset], ...]   # per channel
    "prev-servo":  [90, ...]

Usage:
    python3 tools/import_arm_json.py path/to/arm.json
then paste the printed joints over the matching profile in arm.yaml
(and set its port). Joint limits are not in arm.json — they were set
interactively in angle.py — so limits stay at whatever arm.yaml has.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from uroarm import load_profile

NAMES = load_profile("uroarm").joint_names  # channel order 0..5


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    with open(sys.argv[1]) as f:
        params = json.load(f)

    print(f"    port: {params.get('COM')!r}   # was \"COM\" in arm.json — use the /dev path on Linux/macOS")
    print("    joints:")
    for ch, (scale, offset) in enumerate(params["servo-angle"]):
        print(
            f"      - {{ name: {NAMES[ch]}, channel: {ch}, servo: TBD,"
            f" scale: {scale}, offset_deg: {offset}, limit_deg: [-90, 90], pulse_us: [600, 2400] }}"
        )


if __name__ == "__main__":
    main()
