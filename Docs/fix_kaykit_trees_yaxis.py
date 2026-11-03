# -*- coding: utf-8 -*-
"""Re-bake KayKit cluster trees using Y as height (Y-up). Quiet logs to avoid remote JSON blowup."""
from __future__ import print_function
import unreal
import os

OBJ_DIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKit-Medieval-Hexagon-Pack-1.0-main\addons\kaykit_medieval_hexagon_pack\Assets\obj\decoration\nature"
DEST = "/Game/Environments/KayKitMedieval/Trees"
MAT = "/Game/Environments/KayKitMedieval/Buildings/M_KayKitMedieval"
LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\ue_kaykit_trees.log"
SCALE_TXT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\KAYKIT_TREES_SCALE.txt"

# Force Y height (KayKit Y-up). name -> target_cm
FIX = {
    "trees_A_small": 340.0,
    "trees_B_small": 340.0,
    "trees_A_medium": 600.0,
    "trees_B_medium": 600.0,
    "trees_A_large": 1050.0,
    "trees_B_large": 1050.0,
}

# Already-correct singles/cuts (keep as-is in sidecar)
KEEP = {
    "tree_single_A": (340.0, 284.17, (163.1, 340.0, 155.4)),
    "tree_single_B": (340.0, 280.37, (192.0, 340.0, 201.9)),
    "tree_single_A_cut": (100.0, 302.81, (51.4, 100.0, 49.0)),
    "tree_single_B_cut": (100.0, 422.57, (76.4, 100.0, 80.3)),
    "trees_A_cut": (90.0, 429.23, (714.1, 90.0, 723.1)),
    "trees_B_cut": (90.0, 519.67, (728.6, 90.0, 759.0)),
}

lines = []

def log(msg):
    lines.append(str(msg))


def mesh_size(mesh):
    bb = mesh.get_bounding_box()
    return (
        abs(bb.max.x - bb.min.x),
        abs(bb.max.y - bb.min.y),
        abs(bb.max.z - bb.min.z),
    )


def import_obj(abs_path, dest_path, asset_name, uniform_scale):
    full = dest_path + "/" + asset_name
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        unreal.EditorAssetLibrary.delete_asset(full)
    task = unreal.AssetImportTask()
    task.filename = abs_path
    task.destination_path = dest_path
    task.destination_name = asset_name
    task.replace_existing = True
    task.automated = True
    task.save = True
    options = unreal.FbxImportUI()
    options.set_editor_property("automated_import_should_detect_type", False)
    options.set_editor_property("import_as_skeletal", False)
    options.set_editor_property("import_mesh", True)
    options.set_editor_property("import_materials", False)
    options.set_editor_property("import_textures", False)
    sm = unreal.FbxStaticMeshImportData()
    sm.set_editor_property("combine_meshes", True)
    sm.set_editor_property("auto_generate_collision", True)
    sm.set_editor_property("import_uniform_scale", float(uniform_scale))
    try:
        sm.set_editor_property("convert_scene", False)
    except Exception:
        pass
    try:
        sm.set_editor_property("force_front_x_axis", False)
    except Exception:
        pass
    options.set_editor_property("static_mesh_import_data", sm)
    task.options = options
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        return unreal.EditorAssetLibrary.load_asset(full)
    return None


mat = None
if unreal.EditorAssetLibrary.does_asset_exist(MAT):
    mat = unreal.EditorAssetLibrary.load_asset(MAT)

log("=== KAYKIT TREES Y-AXIS FIX ===")
results = []

for name, target in FIX.items():
    src = os.path.join(OBJ_DIR, name + ".obj")
    # probe at 1.0
    mesh = import_obj(src, DEST, name, 1.0)
    if not mesh:
        log("FAIL probe " + name)
        continue
    sx, sy, sz = mesh_size(mesh)
    native_y = max(sy, 0.001)
    S = target / native_y
    log("%s probe Y=%.4f S=%.4f (was wrong axis before)" % (name, native_y, S))
    mesh = import_obj(src, DEST, name, S)
    if not mesh:
        log("FAIL scaled " + name)
        continue
    sx, sy, sz = mesh_size(mesh)
    if mat:
        try:
            mesh.set_material(0, mat)
        except Exception:
            pass
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    log("OK %s final=%.1f,%.1f,%.1f Yh=%.1f" % (name, sx, sy, sz, sy))
    results.append((name, native_y, S, sx, sy, sz, target))

# write sidecar + append log (file only, minimal unreal.log)
out = [
    "KayKit Trees — place with Roll=90 (Y-up OBJ). Content-only; Map_Hub untouched.",
    "Asset path prefix: /Game/Environments/KayKitMedieval/Trees/",
    "Height axis = mesh Y (becomes world Z after Roll 90). Scale3D=1.0 after bake.",
    "",
]
for name, native_y, S, sx, sy, sz, target in results:
    out.append(
        "%s | /Game/Environments/KayKitMedieval/Trees/%s | native_Y=%.4f S=%.2f | final_bbox=%.1fx%.1fx%.1f world_height~%.1f (target %.0f) | Scale3D=1.0 | Rotator(roll=90,pitch=0,yaw=...)"
        % (name, name, native_y, S, sx, sy, sz, sy, target)
    )
for name, (target, S, bbox) in KEEP.items():
    out.append(
        "%s | /Game/Environments/KayKitMedieval/Trees/%s | S=%.2f | final_bbox=%.1fx%.1fx%.1f world_height~%.1f (target %.0f) | Scale3D=1.0 | Rotator(roll=90,pitch=0,yaw=...)"
        % (name, name, S, bbox[0], bbox[1], bbox[2], bbox[1], target)
    )

with open(SCALE_TXT, "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")
with open(LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n\n" + "\n".join(out) + "\n")

try:
    unreal.EditorAssetLibrary.save_directory(DEST)
except Exception:
    pass

# one short line for remote JSON
unreal.log("KAYTREES_FIX_DONE n=%d" % len(results))
print("KAYTREES_FIX_DONE n=%d" % len(results))