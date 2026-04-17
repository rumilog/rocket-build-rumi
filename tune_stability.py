"""
Tune fin span until stability is in [1.0, 1.8] cal, then report final design.
Binary-search on span between 20mm and 90mm.
"""

import sys, json
from pathlib import Path

JAR = Path("C:/Users/rumiq/AppData/Local/OpenRocket/OpenRocket-23.09.jar")
ORK = Path("C:/Users/rumiq/Desktop/rocket-build-rumi/openrocket/H219T_sport.ork")

sys.path.insert(0, "C:/Users/rumiq/Desktop/RocketSmith/src")

from rocketsmith.openrocket.components import (
    delete_component, create_component, inspect_ork,
)

TARGET_MIN = 1.0
TARGET_MAX = 1.8

lo, hi = 0.020, 0.090  # span range in metres
best_span = None
best_stab = None

for iteration in range(12):
    span = (lo + hi) / 2.0

    # Replace fins with current span guess
    try:
        delete_component(ORK, "Fins", jar_path=JAR)
    except Exception:
        pass

    create_component(ORK, "fin-set", jar_path=JAR,
        parent_name="Fin Can",
        name="Fins",
        count=3,
        root_chord=0.120,
        tip_chord=0.050,
        span=round(span, 4),
        sweep=0.040,
        thickness=0.004,
    )

    info = inspect_ork(ORK, JAR)
    stab = info.get("stability_cal", 0.0)
    print(f"  iter {iteration+1:2d}: span={span*1000:.1f}mm -> {stab:.2f} cal")

    best_span = span
    best_stab = stab

    if TARGET_MIN <= stab <= TARGET_MAX:
        print(f"\nConverged at span={span*1000:.1f}mm, stability={stab:.2f} cal")
        break
    elif stab > TARGET_MAX:
        hi = span   # too stable → smaller fins
    else:
        lo = span   # not stable enough → bigger fins

print(f"\nFinal design:")
info = inspect_ork(ORK, JAR)
print(f"  CG:        {info['cg_x']*1000:.1f} mm from nose")
print(f"  CP:        {info['cp_x']*1000:.1f} mm from nose")
print(f"  Stability: {info['stability_cal']:.2f} cal")
print(f"  Fin span:  {best_span*1000:.1f} mm")

with open("/c/Users/rumiq/Desktop/rocket-build-rumi/openrocket/final_design.json", "w") as f:
    json.dump(info, f, indent=2, default=str)
print("\nSaved to openrocket/final_design.json")
