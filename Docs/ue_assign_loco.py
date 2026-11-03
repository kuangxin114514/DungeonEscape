# -*- coding: utf-8 -*-
import unreal

folder = "/Game/Characters/Player/KayKit/Animations"
bs_path = folder + "/BS_KayKitLocomotion"
abp_path = folder + "/ABP_KayKitFromTP"
alias_path = "/Game/Mannequin/Character/Mesh/KayKitKnightSkelXXXXXX"
mesh_path = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight"
bp_path = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
mat_path = "/Game/Characters/Player/KayKit/Materials/M_KayKitKnight"
orig_skel_path = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton"

alias = unreal.EditorAssetLibrary.load_asset(alias_path)
orig_skel = unreal.EditorAssetLibrary.load_asset(orig_skel_path)
bs = unreal.EditorAssetLibrary.load_asset(bs_path)
abp = unreal.EditorAssetLibrary.load_asset(abp_path)
sk_mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)

unreal.log("BS skel={}".format(bs.get_editor_property("skeleton").get_path_name()))

# Ensure BS still has KayKit samples after reload
sd = bs.get_editor_property("sample_data")
unreal.log("samples n={}".format(len(sd)))
for i, s in enumerate(sd):
    anim = s.get_editor_property("animation")
    unreal.log("  sample{} anim={} rate={}".format(i, anim.get_name() if anim else None, s.get_editor_property("sample_rate") if False else "?"))
    try:
        # BlendSample: Animation, SampleValue, RateScale
        unreal.log("    value={} ratescale={}".format(s.get_editor_property("sample_value"), s.get_editor_property("rate_scale")))
    except Exception as e:
        unreal.log("    sample props ERR {}".format(e))

# Retarget / rebind KayKit locomotion+jump anims to alias skeleton so they match BS/ABP/mesh
anim_names = [
    "SK_KayKitKnight_Anim_Rig_Idle_Rig",
    "SK_KayKitKnight_Anim_Rig_Walking_A_Rig",
    "SK_KayKitKnight_Anim_Rig_Running_A_Rig",
    "SK_KayKitKnight_Anim_Rig_Jump_Idle_Rig",
    "SK_KayKitKnight_Anim_Rig_Jump_Start_Rig",
    "SK_KayKitKnight_Anim_Rig_Jump_Land_Rig",
    "SK_KayKitKnight_Anim_Rig_Jump_Full_Short_Rig",
    "SK_KayKitKnight_Anim_Rig_Jump_Full_Long_Rig",
]
mesh_folder = "/Game/Characters/Player/KayKit/Mesh"
for name in anim_names:
    path = mesh_folder + "/" + name
    if not unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.log("MISSING {}".format(name))
        continue
    anim = unreal.EditorAssetLibrary.load_asset(path)
    try:
        old = anim.get_editor_property("skeleton")
        anim.set_editor_property("skeleton", alias)
        unreal.log("anim {} skel {} -> alias".format(name, old.get_name() if old else None))
        unreal.EditorAssetLibrary.save_asset(path)
    except Exception as e:
        unreal.log("anim {} ERR {}".format(name, e))

# Point mesh to alias skeleton
try:
    oldm = sk_mesh.get_editor_property("skeleton")
    sk_mesh.set_editor_property("skeleton", alias)
    unreal.log("mesh skel {} -> alias".format(oldm.get_name() if oldm else None))
    # material on mesh
    mat = unreal.EditorAssetLibrary.load_asset(mat_path)
    try:
        mats = sk_mesh.get_editor_property("materials")
        unreal.log("mesh materials before={}".format(mats))
    except Exception as e:
        unreal.log("mats read ERR {}".format(e))
    try:
        # SkeletalMesh materials are SkeletalMaterial structs
        # Use set_material via AssetTools or EditorAssetLibrary
        sk_mesh.set_material(0, mat)
        unreal.log("set_material0 OK")
    except Exception as e:
        unreal.log("set_material ERR {}".format(e))
    unreal.EditorAssetLibrary.save_asset(mesh_path)
except Exception as e:
    unreal.log("mesh skel ERR {}".format(e))

# ABP target skeleton -> alias
try:
    abp.set_editor_property("target_skeleton", alias)
    unreal.log("ABP target -> alias")
except Exception as e:
    unreal.log("ABP skel ERR {}".format(e))

# Ensure jump SequencePlayers use KayKit jump (already done) + proper start/land if possible
EdGraphNode = unreal.load_class(None, "/Script/Engine.EdGraphNode")
jump_idle = unreal.EditorAssetLibrary.load_asset(mesh_folder + "/SK_KayKitKnight_Anim_Rig_Jump_Idle_Rig")
jump_start = unreal.EditorAssetLibrary.load_asset(mesh_folder + "/SK_KayKitKnight_Anim_Rig_Jump_Start_Rig")
jump_land = unreal.EditorAssetLibrary.load_asset(mesh_folder + "/SK_KayKitKnight_Anim_Rig_Jump_Land_Rig")
for obj in unreal.ObjectIterator(EdGraphNode):
    p = obj.get_path_name()
    if "ABP_KayKitFromTP" not in p:
        continue
    if obj.get_class().get_name() != "AnimGraphNode_SequencePlayer":
        continue
    try:
        node = obj.get_editor_property("Node")
        seq = node.get_editor_property("sequence")
        nm = obj.get_name()
        # Heuristic: keep Jump_Idle for loop; try assign start/land by node index names
        unreal.log("SP {} -> {}".format(nm, seq.get_name() if seq else None))
    except Exception as e:
        unreal.log("SP ERR {}".format(e))

# Compile-ish: save ABP
unreal.EditorAssetLibrary.save_asset(abp_path)

# Assign AnimBP to character CDO mesh
bp_cls = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
cdo = unreal.get_default_object(bp_cls)
mesh_comp = cdo.get_editor_property("mesh")

abp_cls = unreal.EditorAssetLibrary.load_blueprint_class(abp_path)
unreal.log("abp_cls={}".format(abp_cls))

mesh_comp.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
mesh_comp.set_editor_property("anim_class", abp_cls)
mesh_comp.set_editor_property("skeletal_mesh", sk_mesh)

# Materials on component
mat = unreal.EditorAssetLibrary.load_asset(mat_path)
try:
    mesh_comp.set_editor_property("override_materials", [mat])
    unreal.log("override_materials OK")
except Exception as e:
    unreal.log("override_materials ERR {}".format(e))

# Verify sword/shield static mesh components still present on SCS or CDO
# BP may use components via GetComponents
try:
    comps = cdo.get_components_by_class(unreal.StaticMeshComponent.static_class())
    unreal.log("static mesh comps={}".format([c.get_name() for c in comps]))
except Exception as e:
    unreal.log("comps ERR {}".format(e))

unreal.log("mode={} anim_class={}".format(
    mesh_comp.get_editor_property("animation_mode"),
    mesh_comp.get_editor_property("anim_class")))

# Save BP
ok = unreal.EditorAssetLibrary.save_asset(bp_path)
unreal.log("save bp={}".format(ok))

# GM_Hub default pawn check + set if needed
gm_path = "/Game/Core/GameFlow/GM_Hub"
if unreal.EditorAssetLibrary.does_asset_exist(gm_path):
    gm_cls = unreal.EditorAssetLibrary.load_blueprint_class(gm_path)
    gm_cdo = unreal.get_default_object(gm_cls)
    pawn = gm_cdo.get_editor_property("default_pawn_class")
    unreal.log("GM_Hub default_pawn={}".format(pawn))
    if pawn is None or "KayKit" not in str(pawn):
        gm_cdo.set_editor_property("default_pawn_class", bp_cls)
        unreal.EditorAssetLibrary.save_asset(gm_path)
        unreal.log("GM_Hub pawn set to BP_KayKitKnight")

# Final consistency check
unreal.log("FINAL mesh.skel={}".format(sk_mesh.get_editor_property("skeleton").get_path_name()))
unreal.log("FINAL abp.target={}".format(abp.get_editor_property("target_skeleton").get_path_name()))
unreal.log("FINAL bs.skel={}".format(bs.get_editor_property("skeleton").get_path_name()))
unreal.log("ASSIGN_DONE")