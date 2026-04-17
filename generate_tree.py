"""
Generate component_tree.json from the .ork file, then annotate with DFAM rules.
"""

import sys, json
from pathlib import Path

JAR = Path("C:/Users/rumiq/AppData/Local/OpenRocket/OpenRocket-23.09.jar")
ORK = Path("C:/Users/rumiq/Desktop/rocket-build-rumi/openrocket/H219T_sport.ork")
PROJECT = Path("C:/Users/rumiq/Desktop/rocket-build-rumi")

sys.path.insert(0, "C:/Users/rumiq/Desktop/RocketSmith/src")

# ── 1. Generate component_tree.json ───────────────────────────────────────────
from rocketsmith.openrocket.generate_tree import generate_tree

print("Generating component tree...")
tree, ascii_art = generate_tree(rocket_file_path=ORK, project_dir=PROJECT, jar_path=JAR)

tree_path = PROJECT / "gui" / "component_tree.json"
tree_path.parent.mkdir(parents=True, exist_ok=True)
tree_path.write_text(tree.model_dump_json(indent=2), encoding="utf-8")
print(f"Written to: {tree_path}")
print(ascii_art.encode("ascii", errors="replace").decode("ascii"))

# ── 2. Apply DFAM rules ────────────────────────────────────────────────────────
from rocketsmith.manufacturing.dfam import annotate_dfam
from rocketsmith.manufacturing.models import ComponentTree

print("\nApplying DFAM rules (additive, fins fused, coupler fused)...")
annotated = annotate_dfam(tree, fusion_overrides=None)
tree_path.write_text(annotated.model_dump_json(indent=2), encoding="utf-8")

# ── 3. Report ──────────────────────────────────────────────────────────────────
data = json.loads(tree_path.read_text(encoding="utf-8"))
print("\nParts to print:")
for part in data.get("parts", []):
    print(f"  - {part['name']}  (from: {part['derived_from']})")

print("\nSkipped:")
for s in data.get("skipped_components", []):
    print(f"  - {s['name']}: {s['reason']}")

print("\nDecisions:")
for d in data.get("decisions", []):
    print(f"  - {d['decision']}: {d['chosen']} ({d['reason']})")
