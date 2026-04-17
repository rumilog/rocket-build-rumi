"""
Build a 54mm sport rocket designed for the AeroTech H219T-14A motor.
Motor: 38mm dia, 155mm long, 234.56 Ns, 224N avg thrust.
Airframe: 54mm OD, two-body design (recovery + fin can), ogive nose.
"""

import sys
import json
from pathlib import Path

JAR = Path("C:/Users/rumiq/AppData/Local/OpenRocket/OpenRocket-23.09.jar")
ORK = Path("C:/Users/rumiq/Desktop/rocket-build-rumi/openrocket/H219T_sport.ork")
ORK.parent.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, "C:/Users/rumiq/Desktop/RocketSmith/src")

from rocketsmith.openrocket.components import new_ork, create_component, read_components
from rocketsmith.openrocket.simulation import create_simulation, run_simulation

# ── 1. New file ────────────────────────────────────────────────────────────────
print("Creating .ork file...")
new_ork(name="H219T Sport", output_path=ORK, jar_path=JAR)

# ── 2. Nose cone ───────────────────────────────────────────────────────────────
# Ogive, 54mm OD, 220mm long (4-caliber nose for good drag coefficient)
print("Adding nose cone...")
create_component(ORK, "nose-cone", jar_path=JAR,
    name="Nose Cone",
    shape="ogive",
    length=0.220,
    diameter=0.054,
    thickness=0.002,
)

# ── 3. Recovery body tube ──────────────────────────────────────────────────────
# Upper section — holds parachute, 54mm OD, 300mm long
print("Adding recovery body tube...")
create_component(ORK, "body-tube", jar_path=JAR,
    name="Recovery Bay",
    length=0.300,
    diameter=0.054,
    thickness=0.002,
)

# ── 4. Parachute (inside recovery bay) ────────────────────────────────────────
# 18" chute, Cd=1.5 — good for a ~1kg rocket
print("Adding parachute...")
create_component(ORK, "parachute", jar_path=JAR,
    parent_name="Recovery Bay",
    name="Main Chute",
    diameter=0.457,  # 18 inches
    cd=1.5,
)

# ── 5. Fin can / motor section ─────────────────────────────────────────────────
# Lower body tube, 54mm OD, 400mm long
print("Adding fin can body tube...")
create_component(ORK, "body-tube", jar_path=JAR,
    name="Fin Can",
    length=0.400,
    diameter=0.054,
    thickness=0.002,
)

# ── 6. Motor mount (inner tube) ───────────────────────────────────────────────
# 38mm OD motor mount, 165mm long (10mm longer than H219T at 155mm)
# Positioned at aft end of fin can
print("Adding motor mount...")
create_component(ORK, "inner-tube", jar_path=JAR,
    parent_name="Fin Can",
    name="Motor Mount",
    length=0.165,
    diameter=0.038,
    thickness=0.001,
    motor_mount=True,
    axial_offset_m=0.400 - 0.165,
    axial_offset_method="top",
)

# ── 7. Trapezoidal fin set ─────────────────────────────────────────────────────
# 3 fins: root=120mm, tip=50mm, span=90mm, sweep=40mm
# Large enough to push CP well aft of CG
print("Adding fin set...")
create_component(ORK, "fin-set", jar_path=JAR,
    parent_name="Fin Can",
    name="Fins",
    count=3,
    root_chord=0.120,
    tip_chord=0.050,
    span=0.090,
    sweep=0.040,
    thickness=0.004,
)

# ── 8. Read component tree ─────────────────────────────────────────────────────
print("\nComponent tree:")
tree = read_components(ORK)
print(json.dumps(tree, indent=2, default=str))

# ── 9. Flight simulation ───────────────────────────────────────────────────────
# JVM is still alive from component creation — safe to call simulation now
from rocketsmith.openrocket.simulation import create_simulation, run_simulation

print("\nCreating flight config (H219T)...")
sim = create_simulation(
    ORK, JAR,
    motor_designation="H219T",
    sim_name="H219T-14A",
    mount_name="Motor Mount",
    launch_rod_length_m=1.83,  # 6-foot rod for an H motor
)
print("Sim created:", json.dumps(sim, indent=2, default=str))

print("\nRunning simulation...")
flights = run_simulation(ORK, JAR)
FLIGHTS_OUT = Path("C:/Users/rumiq/Desktop/rocket-build-rumi/openrocket/flights")
FLIGHTS_OUT.mkdir(parents=True, exist_ok=True)

from orhelper import FlightDataType
for f in flights:
    alt = f.timeseries.get(FlightDataType.TYPE_ALTITUDE, [])
    vel = f.timeseries.get(FlightDataType.TYPE_VELOCITY_TOTAL, [])
    accel = f.timeseries.get(FlightDataType.TYPE_ACCELERATION_TOTAL, [])
    max_alt = float(max(alt)) if len(alt) else 0.0
    max_vel = float(max(vel)) if len(vel) else 0.0
    max_acc = float(max(accel)) if len(accel) else 0.0
    print(f"  [{f.name}]")
    print(f"    Apogee:    {max_alt:.1f} m ({max_alt*3.281:.0f} ft)")
    print(f"    Stability: min={f.min_stability_cal}, max={f.max_stability_cal} cal")
    print(f"    Max vel:   {max_vel:.1f} m/s ({max_vel/340:.2f} Mach)")
    print(f"    Max accel: {max_acc:.1f} m/s²")
    # Save summary
    flight_json = FLIGHTS_OUT / f"{f.name.replace(' ', '_')}.json"
    summary = {
        "name": f.name,
        "max_altitude_m": max_alt,
        "max_altitude_ft": max_alt * 3.281,
        "max_velocity_ms": max_vel,
        "max_velocity_mach": max_vel / 340,
        "max_acceleration_ms2": max_acc,
        "min_stability_cal": f.min_stability_cal,
        "max_stability_cal": f.max_stability_cal,
    }
    with open(flight_json, "w") as fp:
        json.dump(summary, fp, indent=2)
    print(f"    Saved:     {flight_json}")
