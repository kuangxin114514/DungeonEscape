# -*- coding: utf-8 -*-
"""Import free KayKit Dungeon Remastered (OBJ) into Content/Environments/KayKitDungeon.
Does NOT spawn actors or modify Map_Hub / Map_Dungeon layout.
"""
import unreal
import os
import time

OBJ_DIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKit-Dungeon-Remastered-1.0-main\addons\kaykit_dungeon_remastered\Assets\obj"
TEX_SRC = os.path.join(OBJ_DIR, "dungeon_texture.png")
DEST = "/Game/Environments/KayKitDungeon"
DEST_TEX = DEST + "/Textures"
DEST_MAT = DEST + "/Materials"
DEST_MESH = DEST + "/Meshes"
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\import_kaykit_dungeon.txt"
IMPORT_SCALE = 100.0  # KayKit meters -> UE cm


def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)


def category_for(name):
    n = name.lower()
    if n.startswith("wall") or n.startswith("barrier"):
        return "Walls"
    if n.startswith("floor"):
        return "Floors"
    if n.startswith("stair") or n.startswith("stairs"):
        return "Stairs"
    if n.startswith("banner"):
        return "Banners"
    if n.startswith("door") or "doorway" in n:
        return "Doors"
    return "Props"


def write_out(lines):
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def import_texture():
    ensure_dir(DEST_TEX)
    dest_name = "T_KayKitDungeon_Atlas"
    full = DEST_TEX + "/" + dest_name
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        return unreal.EditorAssetLibrary.load_asset(full)
    task = unreal.AssetImportTask()
    task.filename = TEX_SRC
    task.destination_path = DEST_TEX
    task.destination_name = dest_name
    task.replace_existing = True
    task.automated = True
    task.save = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        return unreal.EditorAssetLibrary.load_asset(full)
    return None


def create_material(tex):
    ensure_dir(DEST_MAT)
    mat_path = DEST_MAT + "/M_KayKitDungeon"
    if unreal.EditorAssetLibrary.does_asset_exist(mat_path):
        return unreal.EditorAssetLibrary.load_asset(mat_path)
    # Create basic material asset
    factory = unreal.MaterialFactoryNew()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    mat = asset_tools.create_asset("M_KayKitDungeon", DEST_MAT, unreal.Material, factory)
    if not mat:
        return None
    try:
        # Create texture sample expression and connect to BaseColor
        tex_sample = unreal.MaterialEditingLibrary.create_material_expression(
            mat, unreal.MaterialExpressionTextureSample, -350, 0
        )
        tex_sample.texture = tex
        unreal.MaterialEditingLibrary.connect_material_property(
            tex_sample, "RGB", unreal.MaterialProperty.MP_BASE_COLOR
        )
        unreal.MaterialEditingLibrary.layout_material_expressions(mat)
        unreal.MaterialEditingLibrary.recompile_material(mat)
    except Exception as e:
        unreal.log_warning("mat connect: " + str(e))
    unreal.EditorAssetLibrary.save_asset(mat_path)
    return mat


def import_obj(abs_path, dest_path, asset_name):
    full = dest_path + "/" + asset_name
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        return unreal.EditorAssetLibrary.load_asset(full), "exists"
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
        sm.set_editor_property("import_uniform_scale", IMPORT_SCALE)
        try:
            sm.set_editor_property("convert_scene", True)
            sm.set_editor_property("force_front_x_axis", False)
        except Exception:
            pass
        options.set_editor_property("static_mesh_import_data", sm)
        task.options = options
    except Exception as e:
        unreal.log_warning("options: " + str(e))
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        return unreal.EditorAssetLibrary.load_asset(full), "imported"
    return None, "fail"


def apply_material(mesh, mat):
    if not mesh or not mat:
        return False
    try:
        # StaticMesh has set_material
        if hasattr(mesh, "set_material"):
            mesh.set_material(0, mat)
        else:
            # fallback via EditorAssetLibrary / StaticMeshEditorSubsystem
            try:
                sub = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
                # no direct set; use EditorAssetLibrary
            except Exception:
                pass
            # Use unreal.EditorStaticMeshLibrary if available
            try:
                unreal.EditorStaticMeshLibrary.set_lod_screen_sizes  # probe
            except Exception:
                pass
        unreal.EditorAssetLibrary.save_asset(mesh.get_path_name())
        return True
    except Exception as e:
        unreal.log_warning("mat assign " + str(e))
        return False


def assign_mat_via_slots(mesh, mat):
    """Force material on slot 0 for StaticMesh."""
    try:
        mats = mesh.static_materials
        if mats is None or len(mats) == 0:
            slot = unreal.StaticMaterial()
            slot.set_editor_property("material_interface", mat)
            slot.set_editor_property("material_slot_name", "DefaultMaterial")
            mesh.set_editor_property("static_materials", [slot])
        else:
            # rebuild list with slot0 = mat
            new_list = []
            for i, sm in enumerate(mats):
                if i == 0:
                    sm.set_editor_property("material_interface", mat)
                new_list.append(sm)
            mesh.set_editor_property("static_materials", new_list)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh)
        return True
    except Exception as e:
        unreal.log_warning("slot assign: " + str(e))
        return False


def main():
    t0 = time.time()
    lines = []
    lines.append("KAYKIT_DUNGEON_IMPORT start")
    lines.append("OBJ_DIR=" + OBJ_DIR)
    if not os.path.isdir(OBJ_DIR):
        lines.append("ERROR missing OBJ_DIR")
        write_out(lines)
        return

    ensure_dir(DEST)
    ensure_dir(DEST_MESH)
    for sub in ("Walls", "Floors", "Stairs", "Banners", "Doors", "Props"):
        ensure_dir(DEST_MESH + "/" + sub)

    tex = import_texture()
    lines.append("texture=" + ("ok" if tex else "FAIL"))
    mat = create_material(tex) if tex else None
    lines.append("material=" + ("ok" if mat else "FAIL"))

    objs = sorted([f for f in os.listdir(OBJ_DIR) if f.lower().endswith(".obj")])
    lines.append("obj_files=" + str(len(objs)))

    ok = 0
    exist = 0
    fail = 0
    fail_names = []
    by_cat = {}

    # Import in batches to keep editor responsive
    for i, fname in enumerate(objs):
        name = os.path.splitext(fname)[0]
        cat = category_for(name)
        dest_path = DEST_MESH + "/" + cat
        asset_name = "SM_" + name
        mesh, status = import_obj(os.path.join(OBJ_DIR, fname), dest_path, asset_name)
        by_cat[cat] = by_cat.get(cat, 0) + (1 if mesh else 0)
        if status == "imported":
            ok += 1
            if mat:
                assign_mat_via_slots(mesh, mat)
        elif status == "exists":
            exist += 1
            if mat:
                assign_mat_via_slots(mesh, mat)
        else:
            fail += 1
            fail_names.append(fname)
        if (i + 1) % 40 == 0:
            unreal.log("KAYKIT_DUNGEON progress %d/%d" % (i + 1, len(objs)))

    lines.append("imported_new=" + str(ok))
    lines.append("already_existed=" + str(exist))
    lines.append("failed=" + str(fail))
    lines.append("by_category=" + str(by_cat))
    if fail_names:
        lines.append("fail_list=" + ",".join(fail_names[:30]))
    # Sample asset check
    sample = DEST_MESH + "/Walls/SM_wall"
    lines.append("sample_wall_exists=" + str(unreal.EditorAssetLibrary.does_asset_exist(sample)))
    # Count StaticMeshes under dest
    assets = unreal.EditorAssetLibrary.list_assets(DEST, recursive=True, include_folder=False)
    sm_count = 0
    for a in assets:
        try:
            if unreal.EditorAssetLibrary.find_asset_data(a).asset_class == "StaticMesh":
                sm_count += 1
        except Exception:
            if "/Meshes/" in a:
                sm_count += 1
    lines.append("staticmesh_under_dest=" + str(sm_count))
    lines.append("elapsed_s=" + str(round(time.time() - t0, 1)))
    lines.append("DEST=" + DEST)
    lines.append("READY_FOR_DRAG=1" if sm_count > 0 else "READY_FOR_DRAG=0")
    lines.append("KAYKIT_DUNGEON_IMPORT done")
    write_out(lines)
    for L in lines:
        unreal.log(L)


main()
