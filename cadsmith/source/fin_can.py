"""
Fin Can — base structural geometry.
Derived from: BodyTube:Fin Can, InnerTube:Motor Mount (fused as wall thickening),
              TrapezoidFinSet:Fins (fused as integrated fins)
Pass 1 (generate-structures): base shell only, no modifications.
Fore face at Z=0, aft end at Z=LENGTH_MM.
"""
import math
from build123d import (
    BuildPart, BuildSketch, BuildLine, Plane, Axis, Mode,
    Circle, Polyline, make_face, extrude, fillet, export_step,
    Pos, add,
)
from pathlib import Path

# --- Parameters (from manifest) ---
LENGTH_MM        = 400.0   # fin can body tube length
OD_MM            = 101.6   # outer diameter (4.0")
ID_MM            = 88.9    # inner diameter (3.5")
WALL_MM          = 6.35    # wall thickness (0.25")

# Motor mount region: 11" bore from aft
MOTOR_BORE_MM    = 41.7    # motor bore: 1.642" per spec
MOTOR_START_MM   = 120.6   # motor bore starts 120.6mm from fore (= 400 - 279.4mm)
MOTOR_END_MM     = 400.0   # motor bore ends at aft face

# Fin geometry
FIN_COUNT        = 3
ROOT_CHORD_MM    = 200.0
TIP_CHORD_MM     = 80.0
SPAN_MM          = 130.0
SWEEP_MM         = 60.0
FIN_THICK_MM     = 12.7    # DFAM-adjusted thickness for FDM structural strength
FIN_FILLET_MM    = 3.0
FIN_ROOT_INSET   = 1.0     # fin root penetrates wall by 1mm for fuse
FIN_Z_START      = 200.0   # fin root leading edge (relative to fin can fore)

# Shear pin clearance holes — fore end (outer part at recovery bay joint)
# Recovery bay coupler (inner) slides in at Z=0. Holes at Z=15 align with
# the heat inserts in the recovery bay coupler at its own Z=315 (AFT_SHEAR_Z).
SHEAR_PIN_ANGLES_DEG = [0, 90, 180, 270]
SHEAR_PIN_Z_MM       = 15.0   # from fore face
CLEARANCE_D_MM       = 2.6    # clearance for 2-56 pin shaft
CLEARANCE_DEPTH_MM   = 8.0    # through 6.35mm wall + margin

# Ejection gas baffle — aft face flush with motor bore start
BAFFLE_THICK        = 30.0   # baffle thickness in Z (unchanged)
BAFFLE_Z_START      = MOTOR_START_MM - BAFFLE_THICK  # fore face = 90.6mm, aft face = 120.6mm
BAFFLE_BOSS_R       = 22.0   # central boss radius (scaled for 4" bore)
BAFFLE_INNER_R      = ID_MM / 2  # leg outer radius = bore inner radius = 44.45mm
BAFFLE_LEG_W        = 14.0   # leg width (tangential direction)
BAFFLE_LEG_INNER_R  = BAFFLE_BOSS_R - 2.0  # legs overlap 2mm into boss for clean fusion
BAFFLE_HOLE_D       = 7.75   # per design spec

# --- Resolve output path ---
SCRIPT_DIR   = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
OUTPUT       = PROJECT_ROOT / "cadsmith" / "step" / "fin_can.step"

# ── Step 1: Body tube with local wall thickening ───────────────────────────────
# Outer shell: full solid cylinder
outer = extrude(Circle(OD_MM / 2), amount=LENGTH_MM)

# Fore bore (larger, general payload bore): Z=0 to Z=MOTOR_START_MM
fore_bore = extrude(Circle(ID_MM / 2), amount=MOTOR_START_MM)

# Motor bore (narrower): Z=MOTOR_START_MM to Z=MOTOR_END_MM
motor_bore_len = MOTOR_END_MM - MOTOR_START_MM
motor_bore = Pos(0, 0, MOTOR_START_MM) * extrude(Circle(MOTOR_BORE_MM / 2), amount=motor_bore_len)

body = outer - fore_bore - motor_bore

# ── Step 2: Integrated fins ────────────────────────────────────────────────────
# Fin root chord X uses inset so fin penetrates the wall (required for fillet)
root_x = OD_MM / 2 - FIN_ROOT_INSET    # 26.0mm
tip_x  = OD_MM / 2 + SPAN_MM           # 68.9mm

# Fin profile in XZ plane (Z measured from fin can fore face)
root_le_z = FIN_Z_START
root_te_z = FIN_Z_START + ROOT_CHORD_MM   # = 400.0 (aft end)
tip_le_z  = FIN_Z_START + SWEEP_MM        # = 320.0
tip_te_z  = tip_le_z + TIP_CHORD_MM       # = 370.0

fin_profile = [
    (root_x, root_le_z),  # root leading edge
    (tip_x,  tip_le_z),   # tip leading edge
    (tip_x,  tip_te_z),   # tip trailing edge
    (root_x, root_te_z),  # root trailing edge
]

# Build single fin in XZ plane, extruded in Y
with BuildPart() as single_fin_part:
    with BuildSketch(Plane.XZ):
        with BuildLine():
            Polyline(*fin_profile, close=True)
        make_face()
    extrude(amount=FIN_THICK_MM / 2, both=True)

fin_shape = single_fin_part.part

# Polar array: 3 fins at 120° spacing
with BuildPart() as all_fins_part:
    for i in range(FIN_COUNT):
        add(fin_shape.rotate(Axis.Z, i * (360.0 / FIN_COUNT)))

all_fins = all_fins_part.part

# ── Step 3: Fuse fins into body + baffle ──────────────────────────────────────
with BuildPart() as airframe:
    add(body)
    add(all_fins)

    # ── Baffle: central boss ──────────────────────────────────────────────────
    with BuildSketch(Plane.XY.offset(BAFFLE_Z_START)):
        Circle(BAFFLE_BOSS_R)
    extrude(amount=BAFFLE_THICK)

    # ── Baffle: 3 radial legs ─────────────────────────────────────────────────
    for theta_deg in [0, 120, 240]:
        theta  = math.radians(theta_deg)
        cos_t  = math.cos(theta)
        sin_t  = math.sin(theta)
        half_w = BAFFLE_LEG_W / 2
        p1 = (BAFFLE_LEG_INNER_R * cos_t - half_w * sin_t,
              BAFFLE_LEG_INNER_R * sin_t + half_w * cos_t)
        p2 = (BAFFLE_LEG_INNER_R * cos_t + half_w * sin_t,
              BAFFLE_LEG_INNER_R * sin_t - half_w * cos_t)
        p3 = (BAFFLE_INNER_R * cos_t + half_w * sin_t,
              BAFFLE_INNER_R * sin_t - half_w * cos_t)
        p4 = (BAFFLE_INNER_R * cos_t - half_w * sin_t,
              BAFFLE_INNER_R * sin_t + half_w * cos_t)
        with BuildSketch(Plane.XY.offset(BAFFLE_Z_START)):
            with BuildLine():
                Polyline(p1, p2, p3, p4, close=True)
            make_face()
        extrude(amount=BAFFLE_THICK)

    # ── Baffle: eyebolt pilot hole through boss ───────────────────────────────
    with BuildSketch(Plane.XY.offset(BAFFLE_Z_START)):
        Circle(BAFFLE_HOLE_D / 2)
    extrude(amount=BAFFLE_THICK, mode=Mode.SUBTRACT)

    # ── Step 4: Shear pin clearance holes through fore outer wall ─────────────────
    R_outer = OD_MM / 2   # = 27mm
    for deg in SHEAR_PIN_ANGLES_DEG:
        rad   = math.radians(deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        plane = Plane(
            origin=(cos_a * R_outer, sin_a * R_outer, SHEAR_PIN_Z_MM),
            z_dir=(-cos_a, -sin_a, 0),
        )
        with BuildSketch(plane):
            Circle(CLEARANCE_D_MM / 2)
        extrude(amount=CLEARANCE_DEPTH_MM, mode=Mode.SUBTRACT)

# ── Step 5: Fin root fillets ───────────────────────────────────────────────────
if FIN_FILLET_MM > 0:
    body_r = OD_MM / 2
    z_parallel_edges = airframe.edges().filter_by(Axis.Z)
    fin_root_edges = [
        e for e in z_parallel_edges
        if abs(math.sqrt(e.center().X**2 + e.center().Y**2) - body_r) < 0.5
        and 0.1 < e.center().Z < root_te_z
        and 1.0 < e.length < ROOT_CHORD_MM
    ]
    max_feasible = min(FIN_THICK_MM / 2 * 0.9, 3.0)
    applied = min(FIN_FILLET_MM, max_feasible)
    if applied < FIN_FILLET_MM:
        print(f"[fillet] clamped {FIN_FILLET_MM} -> {applied} mm")
    print(f"[fillet] selected {len(fin_root_edges)} edges, trying r={applied}")
    if fin_root_edges:
        # Try progressively smaller radii until OCC accepts
        for r in [applied, applied * 0.75, applied * 0.5, applied * 0.25]:
            try:
                fillet(fin_root_edges, radius=r)
                print(f"[fillet] success at r={r}")
                break
            except ValueError:
                print(f"[fillet] r={r} failed, trying smaller")
        else:
            print("[fillet] all radii failed, skipping fillets")

# --- Export ---
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
export_step(airframe.part, str(OUTPUT))
print(f"Exported: {OUTPUT}")
