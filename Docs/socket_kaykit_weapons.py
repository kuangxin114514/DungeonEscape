# -*- coding: utf-8 -*-
"""Reimport KayKit knight with skinned weapons; fresh skeleton (no junk previews); update BP."""
import unreal
import os

ROOT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape"
LOG = os.path.join(ROOT, "Docs", "ue_socket_weapons.log")
FBX_BODY = os.path.join(ROOT, "RawAssets", "KayKitAdventurers", "fbx", "Knight_UE_Body.fbx")
FBX_SWORD = os.path.join(ROOT, "RawAssets", "KayKitAdventurers", "fbx", "SM_KayKitSword.fbx")
FBX_SHIELD = os.path.join(ROOT, "RawAssets", "KayKitAdventurers", "fbx", "SM_KayKitShield.fbx")
TEX = os.path.join(ROOT, "RawAssets", "KayKitAdventurers", "fbx", "knight_texture.png")

DEST = "/Game/Characters/Player/KayKit"
DEST_MESH = DEST + "/Mesh"
DEST_WEAP = DEST + "/Weapons"
DEST_MAT = DEST + "/Materials"
DEST_TEX = DEST + "/Textures"
SK_PATH = DEST_MESH + "/SK_KayKitKnight"
SKEL_PATH = DEST_MESH + "/SK_KayKitKnight_Skeleton"
SKEL_POLLUTED = DEST_MESH + "/SK_KayKitKnight_Skeleton_Polluted"
BP_PATH = DEST + "/BP_KayKitKnight"
MAT_PATH = DEST_MAT + "/M_KayKitKnight"
SWORD_PATH = DEST_WEAP + "/SM_KayKitSword"
SHIELD_PATH = DEST_WEAP + "/SM_KayKitShield"
IDLE_PATH = DEST_MESH + "/SK_KayKitKnight_Anim_Rig_Idle_Rig"

def flog(m):
    line = "FIX: " + str(m)
    try: unreal.log(line)
    except Exception: pass
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def warn(m):
    line = "FIX WARN: " + str(m)
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

open(LOG, "w", encoding="utf-8").write("begin_skinned_fix2\n")
flog("start")

# Move polluted skeleton aside if still at SKEL_PATH
if unreal.EditorAssetLibrary.does_asset_exist(SKEL_PATH):
    # If Polluted already exists from prior partial run, leave SKEL_PATH alone only if it's the polluted one moved back... 
    # Check: if Polluted exists, SKEL_PATH might be missing (good) or recreated
    pass
elif unreal.EditorAssetLibrary.does_asset_exist(SKEL_POLLUTED):
    flog("polluted already aside")
else:
    flog("no skel at expected paths")

if unreal.EditorAssetLibrary.does_asset_exist(SKEL_PATH) and not unreal.EditorAssetLibrary.does_asset_exist(SKEL_POLLUTED):
    try:
        ok = unreal.EditorAssetLibrary.rename_asset(SKEL_PATH, SKEL_POLLUTED)
        flog("renamed skel -> Polluted ok=" + str(ok))
    except Exception as e:
        warn("rename skel " + str(e))

if unreal.EditorAssetLibrary.does_asset_exist(SK_PATH):
    try:
        unreal.EditorAssetLibrary.delete_asset(SK_PATH)
        flog("deleted old SK")
    except Exception as e:
        warn("del SK " + str(e))

for junk in ("1H_Sword", "Round_Shield", "Knight_Helmet", "1H_Sword_Offhand", "Badge_Shield",
             "2H_Sword", "Rectangle_Shield", "Spike_Shield"):
    p = DEST_MESH + "/" + junk
    if unreal.EditorAssetLibrary.does_asset_exist(p):
        try:
            unreal.EditorAssetLibrary.delete_asset(p)
            flog("del junk " + p)
        except Exception as e:
            warn("del junk " + junk + " " + str(e))

if not unreal.EditorAssetLibrary.does_asset_exist(DEST_TEX + "/knight_texture") and os.path.exists(TEX):
    task = unreal.AssetImportTask()
    task.filename = TEX
    task.destination_path = DEST_TEX
    task.destination_name = "knight_texture"
    task.replace_existing = True
    task.automated = True
    task.save = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    flog("imported tex")

mat = unreal.EditorAssetLibrary.load_asset(MAT_PATH)
flog("mat=" + str(mat))

# Import body
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
try:
    options.skeleton = None
except Exception:
    pass

sko = options.skeletal_mesh_import_data
for prop, val in (
    ("import_meshes_in_bone_hierarchy", False),
    ("ImportMeshesInBoneHierarchy", False),
    ("use_t0_as_ref_pose", True),
    ("preserve_smoothing_groups", True),
    ("import_morph_targets", False),
    ("update_skeleton_reference_pose", False),
    ("convert_scene", True),
    ("force_front_x_axis", False),
    ("transform_vertex_to_absolute", True),
):
    setp(sko, prop, val)

# Log sko props containing mesh/bone
flog("sko props: " + str([a for a in dir(sko) if "mesh" in a.lower() or "bone" in a.lower() or "hier" in a.lower()]))

task.options = options
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
flog("imported body paths=" + str(list(task.imported_object_paths) if task.imported_object_paths else None))

sk = unreal.EditorAssetLibrary.load_asset(SK_PATH)
skel = unreal.EditorAssetLibrary.load_asset(SKEL_PATH)
if not skel:
    for p in unreal.EditorAssetLibrary.list_assets(DEST_MESH, False, False):
        base = p.split(".")[0]
        if base.endswith("_Skeleton") and "Polluted" not in base and "OLD" not in base:
            skel = unreal.EditorAssetLibrary.load_asset(base)
            flog("found skel " + base)
            break
flog("sk=" + str(sk) + " skel=" + str(skel))

if sk:
    nverts = None
    for meth in ("get_num_vertices", "get_num_verts"):
        if hasattr(sk, meth):
            try:
                nverts = getattr(sk, meth)(0)
                break
            except Exception as e:
                warn(meth + " " + str(e))
    flog("num_vertices lod0=" + str(nverts))
    # Try imported bounds / lod models via python
    try:
        flog("sk attrs sample " + str([a for a in dir(sk) if "vert" in a.lower() or "lod" in a.lower() or "section" in a.lower()][:40]))
    except Exception:
        pass
    if mat:
        for i in range(16):
            try: sk.set_material(i, mat)
            except Exception: break
        flog("mat applied")
    save(sk)
save(skel)

for old_path in (SKEL_POLLUTED, DEST_MESH + "/SK_KayKitKnight_Skeleton_OLD"):
    if skel and unreal.EditorAssetLibrary.does_asset_exist(old_path):
        old = unreal.EditorAssetLibrary.load_asset(old_path)
        if old:
            try:
                ok = unreal.EditorAssetLibrary.consolidate_assets(skel, [old])
                flog("consolidate " + old_path + " -> " + str(ok))
            except Exception as e:
                warn("consolidate " + old_path + " " + str(e))

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
    flog("import SM " + dest_name + " -> " + str(a))
    if a and mat:
        for i in range(8):
            try: a.set_material(i, mat)
            except Exception: break
        save(a)
    return a

sword = import_sm(FBX_SWORD, "SM_KayKitSword", DEST_WEAP)
shield = import_sm(FBX_SHIELD, "SM_KayKitShield", DEST_WEAP)

# Probe / clear preview on new skel
if skel:
    for attr in dir(skel):
        if "preview" in attr.lower() or "attach" in attr.lower():
            flog("skel attr " + attr)
    for prop in ("preview_attached_asset_container", "PreviewAttachedAssetContainer"):
        try:
            c = skel.get_editor_property(prop)
            flog("got " + prop + " = " + str(c) + " dir=" + str([a for a in dir(c) if not a.startswith("_")][:30]))
            for ap in ("attached_objects", "AttachedObjects", "attached_actors", "AttachedActors"):
                try:
                    c.set_editor_property(ap, unreal.Map(str, unreal.SoftObjectPath) if False else {})
                    flog("cleared " + ap)
                except Exception as e:
                    warn("clear " + ap + " " + str(e))
        except Exception as e:
            warn(prop + " " + str(e))
    save(skel)

# BP CDO
idle = unreal.EditorAssetLibrary.load_asset(IDLE_PATH)
sk = unreal.EditorAssetLibrary.load_asset(SK_PATH)
try:
    cls = unreal.load_class(None, BP_PATH + ".BP_KayKitKnight_C")
    cdo = unreal.get_default_object(cls)
    mesh = cdo.get_editor_property("mesh")
    mesh.set_editor_property("skeletal_mesh", sk)
    mesh.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    rot = unreal.Rotator(); rot.pitch = 0; rot.yaw = -90; rot.roll = 0
    mesh.set_editor_property("relative_rotation", rot)
    mesh.set_editor_property("relative_scale3d", unreal.Vector(0.75, 0.75, 0.75))
    mesh.set_editor_property("relative_location", unreal.Vector(0, 0, -90))
    if idle:
        try: mesh.set_animation(idle)
        except Exception:
            try: mesh.override_animation_data(idle, True, True, 0.0, 1.0)
            except Exception as e: warn("idle " + str(e))
    flog("bp cdo ok")
except Exception as e:
    warn("bp cdo " + str(e))

# Child BP attempt
tools = unreal.AssetToolsHelpers.get_asset_tools()
CHILD_PATH = DEST + "/BP_KayKitKnightArmed"
CHILD_NAME = "BP_KayKitKnightArmed"
parent_cls = unreal.load_class(None, BP_PATH + ".BP_KayKitKnight_C")
if parent_cls:
    if unreal.EditorAssetLibrary.does_asset_exist(CHILD_PATH):
        try: unreal.EditorAssetLibrary.delete_asset(CHILD_PATH)
        except Exception: pass
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", parent_cls)
    bp = tools.create_asset(CHILD_NAME, DEST, unreal.Blueprint, factory)
    flog("child bp " + str(bp))
    if bp:
        save(bp)
        scs = None
        try:
            scs = bp.get_editor_property("simple_construction_script")
            flog("child scs=" + str(scs))
        except Exception as e:
            warn("scs get " + str(e))
        if not scs:
            try:
                scs = unreal.new_object(unreal.load_class(None, "/Script/Engine.SimpleConstructionScript"), bp, "SimpleConstructionScript")
                try: bp.set_editor_property("simple_construction_script", scs)
                except Exception as e: warn("set scs " + str(e))
                flog("new scs " + str(scs))
            except Exception as e:
                warn("new scs " + str(e))
        if scs and sword and shield:
            for varname, sm_asset, bone in (("SwordMesh", sword, "handslot_r"), ("ShieldMesh", shield, "handslot_l")):
                try:
                    node = scs.create_node(unreal.StaticMeshComponent, varname)
                    flog("node " + varname + " " + str(node))
                except Exception as e:
                    warn("node " + varname + " " + str(e))
                    node = None
                if not node: continue
                for prop, val in (("parent_component_or_variable_name", "Mesh"), ("parent_socket_name", bone)):
                    setp(node, prop, val)
                tmpl = None
                try: tmpl = node.get_editor_property("component_template")
                except Exception: pass
                if tmpl is None:
                    try:
                        tmpl = unreal.new_object(unreal.StaticMeshComponent, node, varname + "_GEN_VARIABLE")
                        setp(node, "component_template", tmpl)
                    except Exception as e:
                        warn("tmpl " + str(e))
                if tmpl:
                    setp(tmpl, "static_mesh", sm_asset)
                    setp(tmpl, "relative_location", unreal.Vector(0, 0, 0))
                    r0 = unreal.Rotator(); r0.pitch=0; r0.yaw=0; r0.roll=0
                    setp(tmpl, "relative_rotation", r0)
                    setp(tmpl, "relative_scale3d", unreal.Vector(1, 1, 1))
                    flog("tmpl ok " + varname)
            save(bp)
            try:
                unreal.BlueprintEditorLibrary.compile_blueprint(bp)
                flog("compiled")
            except Exception as e:
                warn("compile " + str(e))

# Verify assets
for name in ("1H_Sword", "Round_Shield", "Knight_Helmet", "1H_Sword_Offhand", "Badge_Shield"):
    flog("Mesh/" + name + "=" + str(unreal.EditorAssetLibrary.does_asset_exist(DEST_MESH + "/" + name)))

# Hex-less verify: read skeleton package for preview names via load
if skel:
    # After fresh import, polluted names should be gone from THIS asset
    flog("skel path=" + skel.get_path_name())

idle = unreal.EditorAssetLibrary.load_asset(IDLE_PATH)
if idle:
    try: flog("idle.skeleton=" + str(idle.get_editor_property("skeleton")))
    except Exception as e: warn("idle " + str(e))

for p in (SK_PATH, SKEL_PATH, SWORD_PATH, SHIELD_PATH, BP_PATH, CHILD_PATH, MAT_PATH):
    save(unreal.EditorAssetLibrary.load_asset(p))
try:
    unreal.EditorAssetLibrary.save_directory(DEST, False, True)
    flog("saved_dir")
except Exception as e:
    warn("save_dir " + str(e))

flog("DONE")