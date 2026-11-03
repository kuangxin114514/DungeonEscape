# -*- coding: utf-8 -*-
"""Export KayKit Knight for UE4.27: Z-up cm, weapons rigidly skinned to handslot bones."""
import bpy
import os
import shutil
from mathutils import Vector, Matrix

GLB = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\KayKit-Character-Pack-Adventures-1.0-main\addons\kaykit_character_pack_adventures\Characters\gltf\Knight.glb"
TEX = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\KayKit-Character-Pack-Adventures-1.0-main\addons\kaykit_character_pack_adventures\Textures\knight_texture.png"
OUT_DIR = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\RawAssets\KayKitAdventurers\fbx"
OUT_FBX = os.path.join(OUT_DIR, "Knight_UE.fbx")
OUT_TEX = os.path.join(OUT_DIR, "knight_texture.png")

KEEP_WEAPONS = {"1H_Sword", "Badge_Shield"}
SCALE_TO_CM = 100.0

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)

# Delete unused weapon meshes (keep body Knight_* + cape + chosen weapons)
for o in list(bpy.data.objects):
    if o.type == "MESH" and o.name not in KEEP_WEAPONS and not o.name.startswith("Knight_"):
        bpy.data.objects.remove(o, do_unlink=True)

arm = bpy.data.objects.get("Rig")
if not arm:
    raise RuntimeError("no Rig armature")

# Force weapons onto correct handslot bones if glTF used bone parenting under those slots
FORCE_BONE = {
    "1H_Sword": "handslot.r",
    "Badge_Shield": "handslot.l",
    "Knight_Cape": "chest",
}

def bone_parent_to_skinned(obj, arm_obj, bone_name=None):
    """Bake world transform into mesh, weight 100% to bone, armature-deform."""
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.update()

    # Prefer explicit bone, else current bone parent
    if bone_name is None:
        if obj.parent_type == "BONE" and obj.parent_bone:
            bone_name = obj.parent_bone
        else:
            bone_name = FORCE_BONE.get(obj.name)
    if not bone_name:
        return False
    if bone_name not in arm_obj.data.bones:
        print("MISSING_BONE", bone_name, "for", obj.name)
        return False

    # Visual world matrix while still parented
    mw = obj.matrix_world.copy()

    # Unparent keeping world
    obj.parent = None
    obj.matrix_world = mw
    bpy.context.view_layer.update()

    # Bake loc/rot/scale into mesh data (critical for UE bind pose)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Vertex groups: only the target bone
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
    mod.use_deform_preserve_volume = False

    # Parent under armature; keep baked world verts
    obj.parent = arm_obj
    obj.parent_type = "OBJECT"
    obj.matrix_parent_inverse = arm_obj.matrix_world.inverted()
    obj.matrix_basis = Matrix.Identity(4)
    print("SKINNED", obj.name, "->", bone_name, "verts", len(idxs))
    return True

# Skin bone-parented meshes + force weapons/cape
for o in list(bpy.data.objects):
    if o.type != "MESH":
        continue
    target = FORCE_BONE.get(o.name)
    if o.parent_type == "BONE" or target:
        bone_parent_to_skinned(o, arm, target)

# Ensure body meshes have armature mod + parent
for o in bpy.data.objects:
    if o.type != "MESH":
        continue
    if not any(m.type == "ARMATURE" for m in o.modifiers):
        m = o.modifiers.new(name="Armature", type="ARMATURE")
        m.object = arm
    if o.parent != arm:
        mw = o.matrix_world.copy()
        o.parent = arm
        o.parent_type = "OBJECT"
        o.matrix_world = mw

# Scale whole armature hierarchy to cm, then apply on armature only
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
arm.scale = (SCALE_TO_CM, SCALE_TO_CM, SCALE_TO_CM)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# After armature scale-apply, child meshes may have residual scale — apply theirs too
for o in list(bpy.data.objects):
    if o.type != "MESH":
        continue
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    # Temporarily clear parent to apply cleanly, then re-parent
    mw = o.matrix_world.copy()
    parent = o.parent
    o.parent = None
    o.matrix_world = mw
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if parent:
        o.parent = parent
        o.parent_type = "OBJECT"
        o.matrix_parent_inverse = parent.matrix_world.inverted()
        o.matrix_basis = Matrix.Identity(4)

meshes = [o for o in bpy.data.objects if o.type == "MESH"]
print("EXPORT meshes=", [m.name for m in meshes], "anims=", len(bpy.data.actions))

# Verify weights on sword
sw = bpy.data.objects.get("1H_Sword")
if sw:
    print("SWORD_GROUPS", [g.name for g in sw.vertex_groups], "parent", sw.parent.name if sw.parent else None)
    # Approximate sword center vs handslot.r head
    bpy.context.view_layer.update()
    center = Vector((0, 0, 0))
    for v in sw.data.vertices:
        center += sw.matrix_world @ v.co
    center /= max(len(sw.data.vertices), 1)
    pb = arm.pose.bones.get("handslot.r")
    if pb:
        hand_world = arm.matrix_world @ pb.matrix @ Vector((0, 0, 0))
        print("SWORD_CENTER", list(center), "HANDSLOT", list(hand_world), "DIST", (center - hand_world).length)

os.makedirs(OUT_DIR, exist_ok=True)
try:
    shutil.copy2(TEX, OUT_TEX)
except Exception as e:
    print("tex copy", e)

bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
for m in meshes:
    m.select_set(True)
bpy.context.view_layer.objects.active = arm

bpy.ops.export_scene.fbx(
    filepath=OUT_FBX,
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

mn = Vector((1e9, 1e9, 1e9))
mx = Vector((-1e9, -1e9, -1e9))
for o in meshes:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c)
        mn = Vector((min(mn.x, w.x), min(mn.y, w.y), min(mn.z, w.z)))
        mx = Vector((max(mx.x, w.x), max(mx.y, w.y), max(mx.z, w.z)))
print("READY_UE_FBX", OUT_FBX, "size", list(mx - mn), "actions", len(bpy.data.actions))
