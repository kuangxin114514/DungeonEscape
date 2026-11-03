# -*- coding: utf-8 -*-
"""Import ambientCG Grass001 textures, create M_Grass with tiling, apply ONLY to HubFloor_Ground.

HARD RULE: Do not move/delete/rescale/re-material any Map_Hub buildings, walls, shops, markers.
Only touch HubFloor_Ground (or Floor / Hub_Floor labels).
"""
from __future__ import print_function
import unreal
import os
import traceback

HUB_MAP = "/Game/Maps/Hub/Map_Hub"
RAW_DIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\Textures\Grass"
DEST = "/Game/Environments/Materials/Grass"
DEST_TEX = DEST  # textures live beside material
LOG_PATH = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\ue_grass_material.log"

TILING = 30.0  # UV scale for ~60m courtyard
ROUGHNESS = 0.9

COLOR_SRC = os.path.join(RAW_DIR, "Grass001_1K-JPG_Color.jpg")
ROUGH_SRC = os.path.join(RAW_DIR, "Grass001_1K-JPG_Roughness.jpg")
NORMAL_SRC = os.path.join(RAW_DIR, "Grass001_1K-JPG_NormalDX.jpg")

T_COLOR = "T_Grass"
T_ROUGH = "T_Grass_Roughness"
T_NORMAL = "T_Grass_Normal"
M_NAME = "M_Grass"

FLOOR_LABELS = ("HubFloor_Ground", "Floor", "Hub_Floor")

_log_lines = []


def log(msg):
    line = str(msg)
    _log_lines.append(line)
    try:
        unreal.log("GRASS: " + line)
    except Exception:
        print("GRASS: " + line)


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


def import_texture(abs_path, dest_name, srgb=True):
    full = DEST_TEX + "/" + dest_name
    if not os.path.isfile(abs_path):
        log("MISSING " + abs_path)
        return None
    ensure_dir(DEST_TEX)
    # reimport if exists
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        log("reimport existing " + full)
    task = unreal.AssetImportTask()
    task.filename = abs_path
    task.destination_path = DEST_TEX
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
        # Texture2D sRGB / compression
        if hasattr(tex, "set_editor_property"):
            try:
                tex.set_editor_property("srgb", bool(srgb))
            except Exception:
                pass
            if not srgb:
                try:
                    tex.set_editor_property(
                        "compression_settings",
                        unreal.TextureCompressionSettings.TC_DEFAULT,
                    )
                except Exception:
                    pass
                # Normal map compression if this is normal
                if "Normal" in dest_name:
                    try:
                        tex.set_editor_property(
                            "compression_settings",
                            unreal.TextureCompressionSettings.TC_NORMALMAP,
                        )
                    except Exception:
                        pass
            save(tex)
    except Exception as e:
        log("tex props: " + str(e))
    log("imported " + full)
    return tex


def make_material(tex_color, tex_rough, tex_normal):
    ensure_dir(DEST)
    full = DEST + "/" + M_NAME
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        log("deleting old " + full)
        unreal.EditorAssetLibrary.delete_asset(full)
    factory = unreal.MaterialFactoryNew()
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        M_NAME, DEST, unreal.Material, factory
    )
    if not mat:
        log("material create FAILED")
        return None
    try:
        mel = unreal.MaterialEditingLibrary
        # UV = TexCoord * TILING
        texcoord = mel.create_material_expression(
            mat, unreal.MaterialExpressionTextureCoordinate, -600, 0
        )
        mul = mel.create_material_expression(
            mat, unreal.MaterialExpressionMultiply, -400, 0
        )
        const_tile = mel.create_material_expression(
            mat, unreal.MaterialExpressionConstant, -600, 120
        )
        const_tile.set_editor_property("r", float(TILING))
        mel.connect_material_expressions(texcoord, "", mul, "A")
        mel.connect_material_expressions(const_tile, "", mul, "B")

        # BaseColor sample
        ts = mel.create_material_expression(
            mat, unreal.MaterialExpressionTextureSample, -200, 0
        )
        if tex_color:
            ts.set_editor_property("texture", tex_color)
        mel.connect_material_expressions(mul, "", ts, "UVs")
        mel.connect_material_property(ts, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)

        # Roughness: prefer map R channel, else constant
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
            const_r.set_editor_property("r", float(ROUGHNESS))
            mel.connect_material_property(
                const_r, "", unreal.MaterialProperty.MP_ROUGHNESS
            )

        # Normal
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
        log("wired M_Grass tiling=%.1f" % TILING)
    except Exception as e:
        log("material wire FAIL: " + str(e))
        log(traceback.format_exc())
    save(mat)
    log("material=" + full)
    return unreal.EditorAssetLibrary.load_asset(full)


def load_hub():
    try:
        unreal.EditorLoadingAndSavingUtils.load_map(HUB_MAP)
        log("loaded " + HUB_MAP)
        return True
    except Exception as e:
        log("load_map fail: " + str(e))
        # maybe already open
        try:
            world = unreal.EditorLevelLibrary.get_editor_world()
            log("using current world " + str(world))
            return True
        except Exception as e2:
            log("no world: " + str(e2))
            return False


def is_floor_actor(actor):
    try:
        lab = actor.get_actor_label()
    except Exception:
        lab = ""
    if lab in FLOOR_LABELS or (lab and lab.startswith("HubFloor_")):
        return True
    return False


def apply_to_floor_only(mat):
    if not mat:
        log("no mat to apply")
        return False
    actors = []
    try:
        actors = unreal.EditorLevelLibrary.get_all_level_actors()
    except Exception as e:
        log("get actors fail: " + str(e))
        return False

    applied = 0
    skipped_buildings = 0
    floor_found = []
    for a in actors:
        try:
            lab = a.get_actor_label()
        except Exception:
            lab = "?"
        if not is_floor_actor(a):
            # never touch walls/buildings/shops
            if lab.startswith(("HubWall_", "HubCorner_", "HubGate_", "HubShop_",
                               "HubMarker_", "HubLabel_", "HubMed_", "HubEnv_",
                               "HubKay_", "HubPlaceholder_")):
                skipped_buildings += 1
            continue
        floor_found.append(lab)
        # StaticMeshActor path
        try:
            smc = a.static_mesh_component
        except Exception:
            smc = None
        if smc is None:
            try:
                smc = a.get_component_by_class(unreal.StaticMeshComponent)
            except Exception:
                smc = None
        if smc is None:
            log("floor actor has no SMC: " + lab)
            continue
        try:
            # set all material slots on the floor mesh component only
            num = 1
            try:
                num = smc.get_num_materials()
            except Exception:
                pass
            for i in range(max(1, int(num))):
                smc.set_material(i, mat)
            applied += 1
            log("applied M_Grass to " + lab + " slots=" + str(num))
        except Exception as e:
            log("apply fail " + lab + ": " + str(e))

    log("floors_found=" + str(floor_found))
    log("applied_count=" + str(applied))
    log("skipped_buildingish_labels=" + str(skipped_buildings))
    return applied > 0


def save_map():
    try:
        unreal.EditorLevelLibrary.save_current_level()
        log("saved current level")
    except Exception as e:
        log("save level fail: " + str(e))
    try:
        unreal.EditorAssetLibrary.save_directory(DEST, True, True)
        log("saved assets under " + DEST)
    except Exception as e:
        log("save dir fail: " + str(e))


def main():
    log("=== import_grass_material start ===")
    log("TILING=" + str(TILING))
    tex_c = import_texture(COLOR_SRC, T_COLOR, srgb=True)
    tex_r = import_texture(ROUGH_SRC, T_ROUGH, srgb=False)
    tex_n = import_texture(NORMAL_SRC, T_NORMAL, srgb=False)
    mat = make_material(tex_c, tex_r, tex_n)
    if not load_hub():
        log("ABORT: could not load hub")
        flush_log()
        return
    ok = apply_to_floor_only(mat)
    if ok:
        save_map()
    else:
        log("WARN: floor not found or apply failed; assets still saved")
        save(mat)
        try:
            unreal.EditorAssetLibrary.save_directory(DEST, True, True)
        except Exception:
            pass
    log("=== done ok=%s ===" % ok)
    flush_log()


main()
