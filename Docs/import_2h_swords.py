# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, os, traceback

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\import_2h_swords.txt"
DEST = "/Game/Characters/Player/KayKit/Weapons"
MAT = "/Game/Characters/Player/KayKit/Materials/M_KayKitKnight"
JOBS = [
    (r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\fbx\SM_KayKitSword_2H.fbx", "SM_KayKitSword_2H"),
    (r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\fbx\SM_KayKitSword_2H_Color.fbx", "SM_KayKitSword_2H_Color"),
]
lines = []

def L(m):
    lines.append(str(m))
    try: unreal.log("Import2H: " + str(m))
    except Exception: print(m)

def setp(obj, prop, val):
    try:
        obj.set_editor_property(prop, val)
        return True
    except Exception as e:
        L("setp %s fail %s" % (prop, e))
        return False

def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)
        L("mkdir " + path)

def import_sm(fbx, dest_name):
    if not os.path.isfile(fbx):
        L("MISSING " + fbx)
        return None
    t = unreal.AssetImportTask()
    t.filename = fbx
    t.destination_path = DEST
    t.destination_name = dest_name
    t.replace_existing = True
    t.automated = True
    t.save = True
    ui = unreal.FbxImportUI()
    setp(ui, "import_mesh", True)
    setp(ui, "import_as_skeletal", False)
    setp(ui, "import_animations", False)
    setp(ui, "import_materials", False)
    setp(ui, "import_textures", False)
    setp(ui, "mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
    setp(ui, "static_mesh_import_data", ui.static_mesh_import_data)
    try:
        smd = ui.static_mesh_import_data
        setp(smd, "combine_meshes", True)
        setp(smd, "auto_generate_collision", True)
        setp(smd, "normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
    except Exception as e:
        L("smd " + str(e))
    t.options = ui
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
    path = DEST + "/" + dest_name
    asset = unreal.EditorAssetLibrary.load_asset(path)
    L("imported %s -> %s exists=%s" % (dest_name, path, asset is not None))
    return asset

def assign_mat(sm, mat):
    if not sm or not mat:
        return
    try:
        mats = sm.static_materials
        n = len(mats) if mats is not None else 0
    except Exception:
        n = 0
    L("%s slots=%s" % (sm.get_name(), n))
    try:
        # UE4: set material by index
        for i in range(max(1, n)):
            try:
                sm.set_material(i, mat)
            except Exception:
                pass
        # also via static_materials array if needed
        try:
            arr = sm.get_editor_property("static_materials")
            if arr and len(arr) > 0:
                for i in range(len(arr)):
                    slot = arr[i]
                    try:
                        slot.set_editor_property("material_interface", mat)
                    except Exception:
                        try:
                            slot.material_interface = mat
                        except Exception:
                            pass
                sm.set_editor_property("static_materials", arr)
        except Exception as e:
            L("static_materials " + str(e))
        unreal.EditorAssetLibrary.save_loaded_asset(sm)
        L("mat assigned " + sm.get_name())
    except Exception as e:
        L("assign fail " + str(e))
        L(traceback.format_exc())

def main():
    L("BEGIN")
    ensure_dir(DEST)
    mat = unreal.EditorAssetLibrary.load_asset(MAT)
    L("mat=" + str(mat))
    for fbx, name in JOBS:
        sm = import_sm(fbx, name)
        assign_mat(sm, mat)
        path = DEST + "/" + name
        L("final exists=%s" % unreal.EditorAssetLibrary.does_asset_exist(path))
    # list weapons folder
    try:
        assets = unreal.EditorAssetLibrary.list_assets(DEST, True, False)
        for a in assets:
            if "Sword" in a:
                L("list " + a)
    except Exception as e:
        L("list " + str(e))
    L("DONE")
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("WROTE", OUT)

try:
    main()
except Exception as e:
    L("FATAL " + str(e))
    L(traceback.format_exc())
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
