# -*- coding: utf-8 -*-
"""Body SK: rename bones . -> _ for UE; skin weapons/cape/helmet; bone-local SMs."""
import bpy
import json
import os
import shutil
from mathutils import Matrix

GLB = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\KayKit-Character-Pack-Adventures-1.0-main\addons\kaykit_character_pack_adventures\Characters\gltf\Knight.glb"
TEX = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\KayKit-Character-Pack-Adventures-1.0-main\addons\kaykit_character_pack_adventures\Textures\knight_texture.png"
OUT_DIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\fbx"
OUT_BODY = os.path.join(OUT_DIR, "Knight_UE_Body.fbx")
OUT_SWORD = os.path.join(OUT_DIR, "SM_KayKitSword.fbx")
OUT_SHIELD = os.path.join(OUT_DIR, "SM_KayKitShield.fbx")
OUT_TEX = os.path.join(OUT_DIR, "knight_texture.png")
OUT_META = os.path.join(OUT_DIR, "kaykit_weapon_sockets.json")
LOG = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\export_knight_socket_weapons.log"

SCALE_TO_CM = 100.0
# After rename: dots become underscores
WEAPON_BONE = {"1H_Sword": "handslot_r", "Round_Shield": "handslot_l"}
EXTRA_SKIN = {"Knight_Cape": "chest", "Knight_Helmet": "head"}
KEEP_BODY_PREFIX = "Knight_"
KEEP_NAMES = set(WEAPON_BONE) | set(EXTRA_SKIN)

def wlog(msg):
    print(msg)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")

os.makedirs(OUT_DIR, exist_ok=True)
open(LOG, "w", encoding="utf-8").write("begin skin+underscore\n")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
arm = bpy.data.objects.get("Rig")
if not arm:
    raise RuntimeError("no Rig")

for o in list(bpy.data.objects):
    if o.type != "MESH":
        continue
    if o.name.startswith(KEEP_BODY_PREFIX) or o.name in KEEP_NAMES:
        continue
    wlog("REMOVE " + o.name)
    bpy.data.objects.remove(o, do_unlink=True)

def bone_world_matrix(arm_obj, bone_name):
    pb = arm_obj.pose.bones.get(bone_name)
    if not pb:
        raise RuntimeError("missing bone " + bone_name)
    return arm_obj.matrix_world @ pb.matrix

def rename_bones_dots_to_underscores(arm_obj):
    # UE FBX importer converts '.' -> '_' only; keep '-' so anim bone names match.
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="EDIT")
    renames = []
    for b in list(arm_obj.data.edit_bones):
        if "." in b.name:
            new = b.name.replace(".", "_")
            base = new
            n = 1
            existing = {eb.name for eb in arm_obj.data.edit_bones}
            while new in existing and new != b.name:
                new = "%s_%d" % (base, n); n += 1
            renames.append((b.name, new))
            b.name = new
    bpy.ops.object.mode_set(mode="OBJECT")
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        for vg in list(o.vertex_groups):
            if "." in vg.name:
                vg.name = vg.name.replace(".", "_")
    wlog("RENAMED_BONES " + str(renames[:20]) + ("..." if len(renames)>20 else ""))
    wlog("BONE_COUNT %d" % len(arm_obj.data.bones))
    wlog("HAS_handslot_r %s" % ("handslot_r" in [b.name for b in arm_obj.data.bones]))

def skin_to_bone(obj, arm_obj, bone_name):
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.update()
    mw = obj.matrix_world.copy()
    obj.parent = None
    obj.matrix_world = mw
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj.vertex_groups.clear()
    vg = obj.vertex_groups.new(name=bone_name)
    idxs = [v.index for v in obj.data.vertices]
    if idxs:
        vg.add(idxs, 1.0, "REPLACE")
    for m in list(obj.modifiers):
        obj.modifiers.remove(m)
    mod = obj.modifiers.new(name="Armature", type="ARMATURE")
    mod.object = arm_obj
    mod.use_vertex_groups = True
    obj.parent = arm_obj
    obj.parent_type = "OBJECT"
    obj.matrix_parent_inverse = arm_obj.matrix_world.inverted()
    obj.matrix_basis = Matrix.Identity(4)
    wlog("SKIN %s -> %s verts=%d" % (obj.name, bone_name, len(obj.data.vertices)))

def bake_to_bone_local(obj, arm_obj, bone_name):
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.update()
    mw = obj.matrix_world.copy()
    obj.parent = None
    obj.matrix_world = mw
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bone_inv = bone_world_matrix(arm_obj, bone_name).inverted()
    mesh = obj.data
    for v in mesh.vertices:
        v.co = bone_inv @ v.co
    mesh.update()
    obj.matrix_world = Matrix.Identity(4)
    obj.vertex_groups.clear()
    for m in list(obj.modifiers):
        obj.modifiers.remove(m)
    obj.parent = None
    wlog("BONE_LOCAL %s -> %s verts=%d" % (obj.name, bone_name, len(mesh.vertices)))

# Scale armature first
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
arm.scale = (SCALE_TO_CM, SCALE_TO_CM, SCALE_TO_CM)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Apply residual mesh scales
for o in list(bpy.data.objects):
    if o.type != "MESH":
        continue
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    mw = o.matrix_world.copy()
    parent, ptype, pbone = o.parent, o.parent_type, o.parent_bone
    o.parent = None
    o.matrix_world = mw
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if parent:
        o.parent = parent
        o.parent_type = ptype
        if ptype == "BONE":
            o.parent_bone = pbone
        else:
            o.matrix_parent_inverse = parent.matrix_world.inverted()
            o.matrix_basis = Matrix.Identity(4)

# Rename bones BEFORE skinning weapons
rename_bones_dots_to_underscores(arm)

# Static SM copies
weapon_exports = []
for obj_name, bone in WEAPON_BONE.items():
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        wlog("MISSING_WEAPON " + obj_name)
        continue
    dup = obj.copy()
    dup.data = obj.data.copy()
    bpy.context.collection.objects.link(dup)
    dup.name = obj_name + "_Static"
    bake_to_bone_local(dup, arm, bone)
    weapon_exports.append((dup, bone, OUT_SWORD if "Sword" in obj_name else OUT_SHIELD))

for obj_name, bone in WEAPON_BONE.items():
    obj = bpy.data.objects.get(obj_name)
    if obj:
        skin_to_bone(obj, arm, bone)
for obj_name, bone in EXTRA_SKIN.items():
    obj = bpy.data.objects.get(obj_name)
    if obj:
        skin_to_bone(obj, arm, bone)
    else:
        wlog("MISSING_EXTRA " + obj_name)

for o in bpy.data.objects:
    if o.type != "MESH" or o.name.endswith("_Static"):
        continue
    if not any(m.type == "ARMATURE" for m in o.modifiers):
        m = o.modifiers.new(name="Armature", type="ARMATURE")
        m.object = arm
    if o.parent != arm:
        mw = o.matrix_world.copy()
        o.parent = arm
        o.parent_type = "OBJECT"
        o.matrix_world = mw

try:
    shutil.copy2(TEX, OUT_TEX)
except Exception as e:
    wlog("tex " + str(e))

body_meshes = [o for o in bpy.data.objects if o.type == "MESH" and not o.name.endswith("_Static")]
total_verts = sum(len(m.data.vertices) for m in body_meshes)
wlog("BODY_MESHES " + str([m.name for m in body_meshes]))
wlog("WEAPON_VG " + str([(m.name, [vg.name for vg in m.vertex_groups]) for m in body_meshes if m.name in WEAPON_BONE or m.name in EXTRA_SKIN]))
wlog("TOTAL_VERTS %d" % total_verts)

bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
for m in body_meshes:
    m.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.export_scene.fbx(
    filepath=OUT_BODY,
    use_selection=True,
    object_types={"ARMATURE", "MESH"},
    use_mesh_modifiers=True,
    mesh_smooth_type="FACE",
    add_leaf_bones=False,
    primary_bone_axis="Y",
    secondary_bone_axis="X",
    armature_nodetype="NULL",
    bake_anim=True,
    bake_anim_use_all_bones=True,
    bake_anim_use_nla_strips=True,
    bake_anim_use_all_actions=True,
    bake_anim_force_startend_keying=True,
    bake_anim_step=1.0,
    bake_anim_simplify_factor=0.0,
    path_mode="COPY",
    embed_textures=False,
    axis_forward="-Y",
    axis_up="Z",
    apply_unit_scale=True,
    apply_scale_options="FBX_SCALE_ALL",
)
wlog("EXPORTED_BODY " + OUT_BODY)

for dup, bone, path in weapon_exports:
    bpy.ops.object.select_all(action="DESELECT")
    dup.select_set(True)
    bpy.context.view_layer.objects.active = dup
    bpy.ops.export_scene.fbx(
        filepath=path,
        use_selection=True,
        object_types={"MESH"},
        use_mesh_modifiers=True,
        mesh_smooth_type="FACE",
        add_leaf_bones=False,
        bake_anim=False,
        path_mode="COPY",
        embed_textures=False,
        axis_forward="-Y",
        axis_up="Z",
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_ALL",
    )
    wlog("EXPORTED_SM " + path + " bone=" + bone)

meta = {"sockets": {"sword": {"bone_ue": "handslot_r"}, "shield": {"bone_ue": "handslot_l"}}, "mode": "skinned_underscore"}
with open(OUT_META, "w", encoding="utf-8") as f:
    json.dump(meta, f, indent=2)
wlog("DONE")