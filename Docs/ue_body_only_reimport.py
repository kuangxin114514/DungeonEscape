# -*- coding: utf-8 -*-
"""Reimport body-only SK (no helmet) + ensure M_KayKitKnight on SK/SM/BP. No SCS ctypes. Do NOT LoadMap."""
import unreal
import os

ROOT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape"
LOG = os.path.join(ROOT, "Docs", "ue_body_only_reimport.log")
FBX_BODY = os.path.join(ROOT, "RawAssets", "KayKitAdventurers", "fbx", "Knight_UE_Body.fbx")
FBX_SWORD = os.path.join(ROOT, "RawAssets", "KayKitAdventurers", "fbx", "SM_KayKitSword.fbx")
FBX_SHIELD = os.path.join(ROOT, "RawAssets", "KayKitAdventurers", "fbx", "SM_KayKitShield.fbx")

DEST = "/Game/Characters/Player/KayKit"
DEST_MESH = DEST + "/Mesh"
DEST_WEAP = DEST + "/Weapons"
DEST_MAT = DEST + "/Materials"
SK_PATH = DEST_MESH + "/SK_KayKitKnight"
SKEL_PATH = DEST_MESH + "/SK_KayKitKnight_Skeleton"
BP_PATH = DEST + "/BP_KayKitKnight"
MAT_PATH = DEST_MAT + "/M_KayKitKnight"
SWORD_PATH = DEST_WEAP + "/SM_KayKitSword"
SHIELD_PATH = DEST_WEAP + "/SM_KayKitShield"
IDLE_PATH = DEST_MESH + "/SK_KayKitKnight_Anim_Rig_Idle_Rig"

def flog(m):
    line = "BODYONLY: " + str(m)
    try: unreal.log(line)
    except Exception: pass
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def warn(m):
    line = "BODYONLY WARN: " + str(m)
    try: unreal.log_warning(line)
    except Exception: pass
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def save(a):
    if not a: return
    try: unreal.EditorAssetLibrary.save_loaded_asset(a, False)
    except Exception:
        try: unreal.EditorAssetLibrary.save_loaded_asset(a)
        except Exception as e: warn("save " + str(e))

def setp(obj, prop, val):
    try:
        obj.set_editor_property(prop, val)
        return True
    except Exception as e:
        warn("setp %s %s" % (prop, e))
        return False

def apply_mat_slots(asset, mat, n=16):
    if not asset or not mat:
        return 0
    applied = 0
    for i in range(n):
        try:
            asset.set_material(i, mat)
            applied += 1
        except Exception:
            break
    return applied

open(LOG, "w", encoding="utf-8").write("begin keep_plume_drop_cape_helmet\n")
flog("start")

mat = unreal.EditorAssetLibrary.load_asset(MAT_PATH)
skel = unreal.EditorAssetLibrary.load_asset(SKEL_PATH)
flog("mat=%s skel=%s" % (mat, skel))

# Reimport skeletal mesh onto existing skeleton
task = unreal.AssetImportTask()
task.filename = FBX_BODY
task.destination_path = DEST_MESH
task.destination_name = "SK_KayKitKnight"
task.replace_existing = True
task.automated = True
task.save = True

options = unreal.FbxImportUI()
setp(options, "import_mesh", True)
setp(options, "import_as_skeletal", True)
setp(options, "import_animations", False)
setp(options, "import_materials", False)
setp(options, "import_textures", False)
setp(options, "create_physics_asset", False)
setp(options, "mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
if skel:
    try:
        options.skeleton = skel
        flog("bound existing skeleton")
    except Exception as e:
        warn("set skeleton " + str(e))

sko = options.skeletal_mesh_import_data
for prop, val in (
    ("import_meshes_in_bone_hierarchy", False),
    ("use_t0_as_ref_pose", True),
    ("preserve_smoothing_groups", True),
    ("import_morph_targets", False),
    ("update_skeleton_reference_pose", False),
    ("convert_scene", True),
    ("force_front_x_axis", False),
    ("transform_vertex_to_absolute", True),
):
    setp(sko, prop, val)

task.options = options
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
flog("imported body paths=%s" % (list(task.imported_object_paths) if task.imported_object_paths else None))

sk = unreal.EditorAssetLibrary.load_asset(SK_PATH)
flog("sk=%s" % sk)
nverts = None
if sk:
    for meth in ("get_num_vertices", "get_num_verts"):
        if hasattr(sk, meth):
            try:
                nverts = getattr(sk, meth)(0)
                break
            except Exception as e:
                warn(meth + " " + str(e))
    flog("num_vertices lod0=%s" % nverts)
    n = apply_mat_slots(sk, mat)
    flog("sk mat slots applied=%d" % n)
    save(sk)

def import_sm(fbx, dest_name, dest_path):
    full = dest_path + "/" + dest_name
    t = unreal.AssetImportTask()
    t.filename = fbx
    t.destination_path = dest_path
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
    smd = ui.static_mesh_import_data
    setp(smd, "combine_meshes", True)
    setp(smd, "auto_generate_collision", False)
    t.options = ui
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
    a = unreal.EditorAssetLibrary.load_asset(full)
    flog("import SM %s -> %s" % (dest_name, a))
    if a and mat:
        n = apply_mat_slots(a, mat, 8)
        flog("SM %s mat slots=%d" % (dest_name, n))
        save(a)
    return a

sword = import_sm(FBX_SWORD, "SM_KayKitSword", DEST_WEAP)
shield = import_sm(FBX_SHIELD, "SM_KayKitShield", DEST_WEAP)

# Refresh BP CDO mesh + materials (no SCS mutation)
idle = unreal.EditorAssetLibrary.load_asset(IDLE_PATH)
sk = unreal.EditorAssetLibrary.load_asset(SK_PATH)
try:
    cls = unreal.load_class(None, BP_PATH + ".BP_KayKitKnight_C")
    cdo = unreal.get_default_object(cls)
    mesh = cdo.get_editor_property("mesh")
    mesh.set_editor_property("skeletal_mesh", sk)
    flog("bp mesh refreshed")
    if mat:
        for i in range(16):
            try:
                mesh.set_material(i, mat)
            except Exception:
                break
        flog("bp CharacterMesh0 materials set")
    if idle:
        try: mesh.override_animation_data(idle, True, True, 0.0, 1.0)
        except Exception as e: warn("idle " + str(e))
    # Also paint any StaticMesh components on CDO that use sword/shield assets
    try:
        comps = cdo.get_components_by_class(unreal.StaticMeshComponent)
        for comp in comps:
            try:
                sm = comp.get_editor_property("static_mesh")
            except Exception:
                sm = None
            name = ""
            try:
                name = str(sm.get_name()) if sm else ""
            except Exception:
                name = ""
            if sm and mat and (("Sword" in name) or ("Shield" in name) or ("KayKit" in name)):
                for i in range(8):
                    try:
                        comp.set_material(i, mat)
                    except Exception:
                        break
                flog("bp SMC mat set on " + name)
    except Exception as e:
        warn("bp smc mats " + str(e))
except Exception as e:
    warn("bp cdo " + str(e))

bp = unreal.EditorAssetLibrary.load_asset(BP_PATH)
save(bp)
save(sk)
save(sword)
save(shield)
try:
    unreal.EditorAssetLibrary.save_directory(DEST, False, True)
except Exception as e:
    warn("save_dir " + str(e))

# Re-open BP editor so mesh refresh shows
try:
    aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
    aes.open_editor_for_assets([bp])
    flog("reopened bp editor")
except Exception as e:
    warn("reopen " + str(e))

flog("DONE keep_plume_drop_cape verts_expect~3772 got=%s sword=%s shield=%s" % (nverts, bool(sword), bool(shield)))
print("BODYONLY_KEEP_PLUME_DROP_CAPE_DONE")

