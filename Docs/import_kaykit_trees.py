# -*- coding: utf-8 -*-
"""Import KayKit Medieval Hexagon nature trees into Content Browser.

Does NOT load/modify Map_Hub or place any level actors.
Bake human-scale size into mesh via import_uniform_scale (fallback: pre-scale OBJ).
KayKit is Y-up: place with Rotator(roll=90, pitch=0, yaw=...).
"""
from __future__ import print_function
import unreal
import os
import shutil
import traceback

OBJ_DIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKit-Medieval-Hexagon-Pack-1.0-main\addons\kaykit_medieval_hexagon_pack\Assets\obj\decoration\nature"
TEMP_OBJ = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\_tmp_kaykit_trees_scaled"
DEST = "/Game/Environments/KayKitMedieval/Trees"
DEST_MAT = "/Game/Environments/KayKitMedieval/Buildings/M_KayKitMedieval"
LOG_PATH = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\ue_kaykit_trees.log"
SCALE_TXT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\KAYKIT_TREES_SCALE.txt"

# filename -> target world height cm (after Roll+90, former Y becomes up)
TREE_TARGETS = {
    "trees_A_small": 340.0,
    "trees_B_small": 340.0,
    "tree_single_A": 340.0,
    "tree_single_B": 340.0,
    "trees_A_medium": 600.0,
    "trees_B_medium": 600.0,
    "trees_A_large": 1050.0,
    "trees_B_large": 1050.0,
    "tree_single_A_cut": 100.0,
    "tree_single_B_cut": 100.0,
    "trees_A_cut": 90.0,
    "trees_B_cut": 90.0,
}

_log_lines = []


def log(msg):
    line = str(msg)
    _log_lines.append(line)
    try:
        unreal.log("KAYTREES: " + line)
    except Exception:
        print("KAYTREES: " + line)


def flush_log():
    try:
        with open(LOG_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(_log_lines) + "\n")
    except Exception as e:
        try:
            unreal.log_warning("log write fail: " + str(e))
        except Exception:
            pass


def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def mesh_size(mesh):
    if not mesh:
        return (0.001, 0.001, 0.001)
    try:
        bbox = mesh.get_bounding_box()
        sx = abs(bbox.max.x - bbox.min.x)
        sy = abs(bbox.max.y - bbox.min.y)
        sz = abs(bbox.max.z - bbox.min.z)
        return (max(sx, 0.001), max(sy, 0.001), max(sz, 0.001))
    except Exception as e:
        log("mesh_size fail: " + str(e))
        return (0.001, 0.001, 0.001)


def mesh_mins(mesh):
    bbox = mesh.get_bounding_box()
    return (bbox.min.x, bbox.min.y, bbox.min.z)


def height_axis_extent(mesh):
    """KayKit nature OBJs are Y-up: ALWAYS use Y as height (Roll+90 -> world Z).
    Cluster tiles are wider in X/Z than tall in Y — do not pick footprint axes."""
    sx, sy, sz = mesh_size(mesh)
    return "y", max(sy, 0.001)


def delete_if_exists(full):
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        try:
            unreal.EditorAssetLibrary.delete_asset(full)
            log("deleted " + full)
        except Exception as e:
            log("delete fail " + full + ": " + str(e))


def import_obj(abs_path, dest_path, asset_name, uniform_scale):
    full = dest_path + "/" + asset_name
    delete_if_exists(full)
    if not os.path.isfile(abs_path):
        log("MISSING file " + abs_path)
        return None
    task = unreal.AssetImportTask()
    task.filename = abs_path
    task.destination_path = dest_path
    task.destination_name = asset_name
    task.replace_existing = True
    task.automated = True
    task.save = True
    try:
        options = unreal.FbxImportUI()
        options.set_editor_property("automated_import_should_detect_type", False)
        options.set_editor_property("import_as_skeletal", False)
        options.set_editor_property("import_mesh", True)
        options.set_editor_property("import_materials", False)
        options.set_editor_property("import_textures", False)
        sm = unreal.FbxStaticMeshImportData()
        sm.set_editor_property("combine_meshes", True)
        sm.set_editor_property("auto_generate_collision", True)
        try:
            sm.set_editor_property("import_uniform_scale", float(uniform_scale))
        except Exception:
            pass
        # Match walls: keep Y-up; user places with Roll+90
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
    except Exception as e:
        log("options warn: " + str(e))
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        log("imported " + full + " scale=%.4f" % float(uniform_scale))
        return unreal.EditorAssetLibrary.load_asset(full)
    try:
        for a in unreal.EditorAssetLibrary.list_assets(dest_path, False, False):
            if asset_name.lower() in a.lower():
                log("found as " + a)
                return unreal.EditorAssetLibrary.load_asset(a)
    except Exception:
        pass
    log("IMPORT FAIL " + abs_path)
    return None


def write_scaled_obj(src_path, dst_path, scale):
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    src_mtl = os.path.splitext(src_path)[0] + ".mtl"
    if os.path.isfile(src_mtl):
        shutil.copy2(src_mtl, os.path.splitext(dst_path)[0] + ".mtl")
    out_lines = []
    with open(src_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                if len(parts) >= 4:
                    x = float(parts[1]) * scale
                    y = float(parts[2]) * scale
                    z = float(parts[3]) * scale
                    rest = " ".join(parts[4:]) if len(parts) > 4 else ""
                    if rest:
                        out_lines.append("v %.6f %.6f %.6f %s\n" % (x, y, z, rest))
                    else:
                        out_lines.append("v %.6f %.6f %.6f\n" % (x, y, z))
                else:
                    out_lines.append(line)
            else:
                out_lines.append(line)
    with open(dst_path, "w", encoding="utf-8") as f:
        f.writelines(out_lines)


def apply_build_scale(mesh, scale):
    try:
        bs = unreal.EditorStaticMeshLibrary.get_lod_build_settings(mesh, 0)
        bs.set_editor_property("build_scale_3d", unreal.Vector(scale, scale, scale))
        unreal.EditorStaticMeshLibrary.set_lod_build_settings(mesh, 0, bs)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh)
        return True
    except Exception as e:
        log("build_scale fail: " + str(e))
        return False


def resolve_material():
    candidates = [
        DEST_MAT,
        "/Game/Environments/KayKitMedieval/Buildings/hexagons_medieval",
        "/Game/Environments/KayKitMedieval/Walls/hexagons_medieval",
        "/Game/Environments/KayKitMedieval/Walls/M_KayKitWall",
    ]
    for p in candidates:
        if unreal.EditorAssetLibrary.does_asset_exist(p):
            log("using material " + p)
            return unreal.EditorAssetLibrary.load_asset(p)
    log("WARN no material found")
    return None


def assign_mat(mesh, mat):
    if not mesh or not mat:
        return
    try:
        mesh.set_material(0, mat)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    except Exception as e:
        log("set_material fail: " + str(e))


def main():
    log("=== KAYKIT TREES IMPORT START ===")
    log("NOTE: do not touch Map_Hub; content-only import")
    ensure_dir(DEST)
    mat = resolve_material()

    results = []  # dicts for scale sidecar

    for name, target_h in TREE_TARGETS.items():
        src = os.path.join(OBJ_DIR, name + ".obj")
        if not os.path.isfile(src):
            log("SKIP missing " + src)
            results.append({"name": name, "ok": False, "err": "missing"})
            continue
        try:
            # Pass 1: probe at scale 1.0
            mesh = import_obj(src, DEST, name, 1.0)
            if not mesh:
                results.append({"name": name, "ok": False, "err": "probe import fail"})
                continue
            sx, sy, sz = mesh_size(mesh)
            axis, native_h = height_axis_extent(mesh)
            log("%s probe size=%.4f,%.4f,%.4f height_axis=%s native_h=%.4f target=%.1f" % (
                name, sx, sy, sz, axis, native_h, target_h))
            if native_h < 0.01:
                native_h = 1.0
            S = target_h / native_h
            # Sanity clamp for KayKit meter-ish units
            if S < 20.0:
                log("WARN %s S=%.2f too small; bumping" % (name, S))
                S = 20.0
            if S > 2000.0:
                log("WARN %s S=%.2f too large; clamping" % (name, S))
                S = 2000.0
            log("%s computed S=%.4f" % (name, S))

            # Pass 2: reimport with uniform scale baked
            mesh = import_obj(src, DEST, name, S)
            bake = "import_uniform_scale"
            if not mesh:
                results.append({"name": name, "ok": False, "err": "scaled import fail"})
                continue
            sx2, sy2, sz2 = mesh_size(mesh)
            axis2, h2 = height_axis_extent(mesh)
            log("%s after uniform_scale size=%.2f,%.2f,%.2f h_axis=%s h=%.2f" % (
                name, sx2, sy2, sz2, axis2, h2))

            # If import_uniform_scale ignored, try BuildScale then pre-scale OBJ
            if h2 < target_h * 0.5:
                log("%s still small; trying BuildScale3D x%.1f" % (name, S))
                if apply_build_scale(mesh, S):
                    # Reload / re-measure — build scale may not change get_bounding_box until rebuild
                    sx2, sy2, sz2 = mesh_size(mesh)
                    axis2, h2 = height_axis_extent(mesh)
                    bake = "build_scale_3d"
                    log("%s after build_scale size=%.2f,%.2f,%.2f h=%.2f" % (name, sx2, sy2, sz2, h2))

            if h2 < target_h * 0.5:
                log("%s FALLBACK pre-scale OBJ vertices x%.1f" % (name, S))
                bake = "prescale_obj_vertices"
                if os.path.isdir(TEMP_OBJ):
                    # only clear this file's outputs
                    pass
                os.makedirs(TEMP_OBJ, exist_ok=True)
                dst = os.path.join(TEMP_OBJ, name + ".obj")
                write_scaled_obj(src, dst, S)
                mesh = import_obj(dst, DEST, name, 1.0)
                if mesh:
                    sx2, sy2, sz2 = mesh_size(mesh)
                    axis2, h2 = height_axis_extent(mesh)
                    log("%s after prescale size=%.2f,%.2f,%.2f h=%.2f" % (name, sx2, sy2, sz2, h2))

            assign_mat(mesh, mat)
            unreal.EditorAssetLibrary.save_loaded_asset(mesh)
            full = DEST + "/" + name
            rec = {
                "name": name,
                "ok": True,
                "path": full,
                "native_h": native_h,
                "height_axis": axis,
                "S": S,
                "bake": bake,
                "final_size": (sx2, sy2, sz2),
                "final_h": h2,
                "target_h": target_h,
                "spawn_rot": "Rotator(roll=90, pitch=0, yaw=...)",
                "recommended_Scale3D": 1.0 if h2 >= target_h * 0.5 else (target_h / max(h2, 0.01)),
            }
            results.append(rec)
            log("OK %s path=%s final_h=%.1f bake=%s Scale3D=%.3f" % (
                name, full, h2, bake, rec["recommended_Scale3D"]))
        except Exception as e:
            log("ERR %s: %s" % (name, e))
            log(traceback.format_exc())
            results.append({"name": name, "ok": False, "err": str(e)})

    # Sidecar scale notes
    try:
        lines = [
            "KayKit Trees — place with Roll=90 (Y-up OBJ). Do not auto-spawn on Map_Hub.",
            "Asset path prefix: /Game/Environments/KayKitMedieval/Trees/",
            "",
        ]
        for r in results:
            if not r.get("ok"):
                lines.append("%s FAIL %s" % (r.get("name"), r.get("err")))
                continue
            fs = r["final_size"]
            lines.append(
                "%s | path=%s | native_h=%.4f(%s) S=%.2f bake=%s | final_bbox=%.1fx%.1fx%.1f final_h=%.1f (target %.0f) | Scale3D=%.3f | %s"
                % (r["name"], r["path"], r["native_h"], r["height_axis"], r["S"], r["bake"],
                   fs[0], fs[1], fs[2], r["final_h"], r["target_h"],
                   r["recommended_Scale3D"], r["spawn_rot"])
            )
        with open(SCALE_TXT, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        log("wrote " + SCALE_TXT)
    except Exception as e:
        log("scale txt fail: " + str(e))

    try:
        unreal.EditorAssetLibrary.save_directory("/Game/Environments/KayKitMedieval")
    except Exception as e:
        log("save_directory: " + str(e))

    ok_n = sum(1 for r in results if r.get("ok"))
    log("=== KAYKIT TREES DONE ok=%d/%d ===" % (ok_n, len(TREE_TARGETS)))
    flush_log()
    return 0


try:
    main()
except Exception as e:
    log("FATAL: " + str(e))
    log(traceback.format_exc())
    flush_log()
    raise
