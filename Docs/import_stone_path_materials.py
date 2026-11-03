# -*- coding: utf-8 -*-
"""Import ambientCG medieval paving/cobblestone textures and create Materials.

HARD RULE: Import assets ONLY. Do NOT load Map_Hub, do NOT apply to any actor,
do NOT save any level. User will paint materials themselves.
"""
from __future__ import print_function
import unreal
import os
import traceback

RAW_ROOT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\Textures\StonePath"
DEST = "/Game/Environments/Materials/StonePath"
LOG_PATH = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\ue_stone_path_materials.log"

# Default UV tiling for path strips (user can change Constant in material)
TILING = 6.0
FALLBACK_ROUGHNESS = 0.85

# (folder_under_RAW, material_name, texture_prefix, label_note)
PACKS = [
    (
        "PavingStones037",
        "M_Cobblestone",
        "PavingStones037_1K-JPG",
        "medieval irregular cobblestone",
    ),
    (
        "PavingStones046",
        "M_StonePath",
        "PavingStones046_1K-JPG",
        "ordered stone paving path",
    ),
    (
        "PavingStones070",
        "M_PavingMedieval",
        "PavingStones070_1K-JPG",
        "worn medieval paving stones",
    ),
]

_log_lines = []


def log(msg):
    line = str(msg)
    _log_lines.append(line)
    try:
        unreal.log("STONEPATH: " + line)
    except Exception:
        print("STONEPATH: " + line)


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


def save(asset):
    if asset:
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(asset)
        except Exception as e:
            log("save fail: " + str(e))


def import_texture(abs_path, dest_name, srgb=True, is_normal=False):
    full = DEST + "/" + dest_name
    if not os.path.isfile(abs_path):
        log("MISSING " + abs_path)
        return None
    ensure_dir(DEST)
    task = unreal.AssetImportTask()
    task.filename = abs_path
    task.destination_path = DEST
    task.destination_name = dest_name
    task.replace_existing = True
    task.automated = True
    task.save = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    tex = None
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        tex = unreal.EditorAssetLibrary.load_asset(full)
    if not tex:
        log("import failed " + dest_name)
        return None
    try:
        if hasattr(tex, "set_editor_property"):
            try:
                tex.set_editor_property("srgb", bool(srgb))
            except Exception:
                pass
            if is_normal:
                try:
                    tex.set_editor_property(
                        "compression_settings",
                        unreal.TextureCompressionSettings.TC_NORMALMAP,
                    )
                except Exception:
                    pass
            elif not srgb:
                try:
                    tex.set_editor_property(
                        "compression_settings",
                        unreal.TextureCompressionSettings.TC_DEFAULT,
                    )
                except Exception:
                    pass
            save(tex)
    except Exception as e:
        log("tex props: " + str(e))
    log("imported " + full)
    return tex


def make_material(mat_name, tex_color, tex_rough, tex_normal, tiling=TILING):
    ensure_dir(DEST)
    full = DEST + "/" + mat_name
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        log("deleting old " + full)
        unreal.EditorAssetLibrary.delete_asset(full)
    factory = unreal.MaterialFactoryNew()
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        mat_name, DEST, unreal.Material, factory
    )
    if not mat:
        log("material create FAILED " + mat_name)
        return None
    try:
        mel = unreal.MaterialEditingLibrary
        texcoord = mel.create_material_expression(
            mat, unreal.MaterialExpressionTextureCoordinate, -600, 0
        )
        mul = mel.create_material_expression(
            mat, unreal.MaterialExpressionMultiply, -400, 0
        )
        const_tile = mel.create_material_expression(
            mat, unreal.MaterialExpressionConstant, -600, 120
        )
        const_tile.set_editor_property("r", float(tiling))
        mel.connect_material_expressions(texcoord, "", mul, "A")
        mel.connect_material_expressions(const_tile, "", mul, "B")

        ts = mel.create_material_expression(
            mat, unreal.MaterialExpressionTextureSample, -200, 0
        )
        if tex_color:
            ts.set_editor_property("texture", tex_color)
        mel.connect_material_expressions(mul, "", ts, "UVs")
        mel.connect_material_property(ts, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)

        if tex_rough:
            ts_r = mel.create_material_expression(
                mat, unreal.MaterialExpressionTextureSample, -200, 250
            )
            ts_r.set_editor_property("texture", tex_rough)
            try:
                ts_r.set_editor_property(
                    "sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR
                )
            except Exception:
                pass
            mel.connect_material_expressions(mul, "", ts_r, "UVs")
            mel.connect_material_property(ts_r, "R", unreal.MaterialProperty.MP_ROUGHNESS)
        else:
            const_r = mel.create_material_expression(
                mat, unreal.MaterialExpressionConstant, -200, 250
            )
            const_r.set_editor_property("r", float(FALLBACK_ROUGHNESS))
            mel.connect_material_property(
                const_r, "", unreal.MaterialProperty.MP_ROUGHNESS
            )

        if tex_normal:
            ts_n = mel.create_material_expression(
                mat, unreal.MaterialExpressionTextureSample, -200, 450
            )
            ts_n.set_editor_property("texture", tex_normal)
            try:
                ts_n.set_editor_property(
                    "sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL
                )
            except Exception:
                pass
            mel.connect_material_expressions(mul, "", ts_n, "UVs")
            mel.connect_material_property(
                ts_n, "RGB", unreal.MaterialProperty.MP_NORMAL
            )

        mel.recompile_material(mat)
        log("wired %s tiling=%.1f" % (mat_name, tiling))
    except Exception as e:
        log("material wire FAIL %s: %s" % (mat_name, e))
        log(traceback.format_exc())
    save(mat)
    log("material=" + full)
    return unreal.EditorAssetLibrary.load_asset(full)


def process_pack(folder, mat_name, prefix, note):
    log("--- pack %s -> %s (%s) ---" % (folder, mat_name, note))
    raw = os.path.join(RAW_ROOT, folder)
    color_src = os.path.join(raw, prefix + "_Color.jpg")
    rough_src = os.path.join(raw, prefix + "_Roughness.jpg")
    normal_src = os.path.join(raw, prefix + "_NormalDX.jpg")

    # Texture names: T_<MatSuffix>_Color etc.
    suffix = mat_name[2:] if mat_name.startswith("M_") else mat_name
    t_color_name = "T_" + suffix + "_Color"
    t_rough_name = "T_" + suffix + "_Roughness"
    t_normal_name = "T_" + suffix + "_Normal"

    tex_c = import_texture(color_src, t_color_name, srgb=True, is_normal=False)
    tex_r = import_texture(rough_src, t_rough_name, srgb=False, is_normal=False)
    tex_n = import_texture(normal_src, t_normal_name, srgb=False, is_normal=True)
    mat = make_material(mat_name, tex_c, tex_r, tex_n, TILING)
    return {
        "material": DEST + "/" + mat_name if mat else None,
        "color": DEST + "/" + t_color_name if tex_c else None,
        "roughness": DEST + "/" + t_rough_name if tex_r else None,
        "normal": DEST + "/" + t_normal_name if tex_n else None,
        "note": note,
        "source": "ambientCG " + folder + " (CC0)",
    }


def main():
    log("=== import_stone_path_materials start ===")
    log("DEST=" + DEST)
    log("TILING=" + str(TILING))
    log("NO_LEVEL_EDIT=True (will not load/save Map_Hub or apply to actors)")
    ensure_dir(DEST)
    results = []
    for folder, mat_name, prefix, note in PACKS:
        try:
            results.append(process_pack(folder, mat_name, prefix, note))
        except Exception as e:
            log("pack FAIL %s: %s" % (folder, e))
            log(traceback.format_exc())
    try:
        unreal.EditorAssetLibrary.save_directory(DEST, True, True)
        log("saved assets under " + DEST)
    except Exception as e:
        log("save dir fail: " + str(e))

    log("=== SUMMARY (Content Browser paths) ===")
    for r in results:
        log("MATERIAL %s  # %s | %s" % (r.get("material"), r.get("note"), r.get("source")))
        log("  Color      %s" % r.get("color"))
        log("  Roughness  %s" % r.get("roughness"))
        log("  Normal     %s" % r.get("normal"))
    log("=== done ===")
    flush_log()


main()
