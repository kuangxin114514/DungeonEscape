# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, os, traceback
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\import_square_shield.txt"
DEST="/Game/Characters/Player/KayKit/Weapons"
MAT="/Game/Characters/Player/KayKit/Materials/M_KayKitKnight"
JOBS=[
 (r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\fbx\SM_KayKitShield_Square.fbx","SM_KayKitShield_Square"),
 (r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\fbx\SM_KayKitShield_Square_Color.fbx","SM_KayKitShield_Square_Color"),
]
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("ImportSqShield: "+str(m))
    except Exception: print(m)

def setp(obj, prop, val):
    try:
        obj.set_editor_property(prop, val); return True
    except Exception as e:
        L("setp %s fail %s"%(prop,e)); return False

def import_sm(fbx, dest_name):
    if not os.path.isfile(fbx):
        L("MISSING "+fbx); return None
    t=unreal.AssetImportTask()
    t.filename=fbx
    t.destination_path=DEST
    t.destination_name=dest_name
    t.replace_existing=True
    t.automated=True
    t.save=True
    ui=unreal.FbxImportUI()
    setp(ui,"import_mesh",True)
    setp(ui,"import_as_skeletal",False)
    setp(ui,"import_animations",False)
    setp(ui,"import_materials",False)
    setp(ui,"import_textures",False)
    setp(ui,"mesh_type_to_import",unreal.FBXImportType.FBXIT_STATIC_MESH)
    try:
        smd=ui.static_mesh_import_data
        setp(smd,"combine_meshes",True)
        setp(smd,"auto_generate_collision",True)
    except Exception as e:
        L("smd "+str(e))
    t.options=ui
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
    path=DEST+"/"+dest_name
    asset=unreal.EditorAssetLibrary.load_asset(path)
    L("imported %s -> %s"%(dest_name, asset))
    return asset

def assign_mat(sm, mat):
    if not sm or not mat: return
    try:
        mats=sm.static_materials
        n=len(mats) if mats is not None else 0
    except Exception:
        n=0
    for i in range(max(1,n)):
        try: sm.set_material(i, mat)
        except Exception: pass
    try: unreal.EditorAssetLibrary.save_loaded_asset(sm)
    except Exception: pass
    L("mat ok %s slots=%s"%(sm.get_name(), n))

try:
    if not unreal.EditorAssetLibrary.does_directory_exist(DEST):
        unreal.EditorAssetLibrary.make_directory(DEST)
    mat=unreal.EditorAssetLibrary.load_asset(MAT)
    L("mat=%s"%mat)
    square=None
    for fbx,name in JOBS:
        sm=import_sm(fbx,name)
        assign_mat(sm, mat)
        if name=="SM_KayKitShield_Square":
            square=sm
    # stamp onto Shield1 BP
    bp_path="/Game/Characters/Player/KayKit/BP_KayKitKnight_Shield1"
    unreal.load_asset(bp_path)
    changed=0
    for o in unreal.ObjectIterator(unreal.StaticMeshComponent):
        try: pn=o.get_path_name()
        except Exception: continue
        if "BP_KayKitKnight_Shield1" not in pn or "GEN_VARIABLE" not in pn: continue
        nm=o.get_name()
        try: sm=o.get_editor_property("static_mesh")
        except Exception: sm=None
        sname=sm.get_name() if sm else ""
        if ("StaticMesh1" in nm) or ("Shield" in sname) or ("shield" in nm.lower()):
            try:
                o.set_editor_property("static_mesh", square)
                changed+=1
                L("BP set %s -> %s"%(nm, square.get_name() if square else None))
            except Exception as e:
                L("BP set fail "+str(e))
    try:
        unreal.EditorAssetLibrary.save_asset(bp_path); L("bp saved")
    except Exception as e:
        L("bp save "+str(e))
    L("changed=%d"%changed)
except Exception as e:
    L("ERR "+str(e)); L(traceback.format_exc())
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
