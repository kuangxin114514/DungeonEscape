# -*- coding: utf-8 -*-
import unreal

alias_path = "/Game/Mannequin/Character/Mesh/KayKitKnightSkelXXXXXX"
orig_path = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton"
bs_path = "/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion"
abp_path = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP"
bp_path = "/Game/Characters/Player/KayKit/BP_KayKitKnight"
mesh_path = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight"
mat_path = "/Game/Characters/Player/KayKit/Materials/M_KayKitKnight"

# Save everything first
unreal.EditorAssetLibrary.save_directory("/Game/Characters/Player/KayKit")
unreal.EditorAssetLibrary.save_directory("/Game/Mannequin/Character/Mesh")

# Unload BS so rename is cleaner
bs = unreal.EditorAssetLibrary.load_asset(bs_path)
try:
    unreal.EditorLoadingAndSavingUtils.unload_packages([bs.get_outermost()])
    unreal.log("unloaded BS")
except Exception as e:
    unreal.log("unload BS ERR {}".format(e))

# Delete the duplicate alias skeleton (NOT the real kaykit one)
if unreal.EditorAssetLibrary.does_asset_exist(alias_path):
    # Make sure we are deleting the DUPLICATE under Mannequin, not orig
    alias_obj = unreal.EditorAssetLibrary.load_asset(alias_path)
    unreal.log("deleting alias {}".format(alias_obj.get_path_name()))
    ok = unreal.EditorAssetLibrary.delete_asset(alias_path)
    unreal.log("delete alias={}".format(ok))
else:
    unreal.log("alias missing already")

# Confirm orig still exists
unreal.log("orig exists={}".format(unreal.EditorAssetLibrary.does_asset_exist(orig_path)))

# Rename real KayKit skeleton to the 53-char Mannequin path BS already references
if unreal.EditorAssetLibrary.does_asset_exist(orig_path):
    ok = unreal.EditorAssetLibrary.rename_asset(orig_path, alias_path)
    unreal.log("rename orig->alias path OK={}".format(ok))
else:
    unreal.log("ORIG MISSING cannot rename")

# Check redirector / existence
unreal.log("alias exists now={}".format(unreal.EditorAssetLibrary.does_asset_exist(alias_path)))
unreal.log("orig exists now={}".format(unreal.EditorAssetLibrary.does_asset_exist(orig_path)))

# Reload BS from disk
bs = unreal.EditorAssetLibrary.load_asset(bs_path)
try:
    pkg = bs.get_outermost()
    unreal.EditorLoadingAndSavingUtils.reload_packages([pkg], unreal.ReloadPackagesInteractionMode.ASSUME_POSITIVE)
except Exception as e:
    unreal.log("reload ERR {}".format(e))

bs = unreal.EditorAssetLibrary.load_asset(bs_path)
skel = bs.get_editor_property("skeleton")
unreal.log("BS skel={}".format(skel.get_path_name() if skel else None))

# Load renamed skeleton
skel2 = unreal.EditorAssetLibrary.load_asset(alias_path)
unreal.log("renamed skel asset={}".format(skel2))

# Point ABP at renamed skeleton (same path)
abp = unreal.EditorAssetLibrary.load_asset(abp_path)
abp.set_editor_property("target_skeleton", skel2)
unreal.log("ABP target={}".format(abp.get_editor_property("target_skeleton").get_path_name()))
unreal.EditorAssetLibrary.save_asset(abp_path)

# Check mesh skeleton (should follow rename/redirector)
sk_mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
unreal.log("mesh skel={}".format(sk_mesh.get_editor_property("skeleton").get_path_name()))

# Re-assign AnimBP on character
bp_cls = unreal.EditorAssetLibrary.load_blueprint_class(bp_path)
cdo = unreal.get_default_object(bp_cls)
mesh_comp = cdo.get_editor_property("mesh")
abp_cls = unreal.EditorAssetLibrary.load_blueprint_class(abp_path)
mesh_comp.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
mesh_comp.set_editor_property("anim_class", abp_cls)
mesh_comp.set_editor_property("skeletal_mesh", sk_mesh)
mat = unreal.EditorAssetLibrary.load_asset(mat_path)
try:
    mesh_comp.set_editor_property("override_materials", [mat])
except Exception as e:
    unreal.log("mat ERR {}".format(e))
unreal.EditorAssetLibrary.save_asset(bp_path)

unreal.log("mode={} anim={}".format(mesh_comp.get_editor_property("animation_mode"), mesh_comp.get_editor_property("anim_class")))

# Verify samples
sd = bs.get_editor_property("sample_data")
for i, s in enumerate(sd):
    a = s.get_editor_property("animation")
    unreal.log("sample{}={}".format(i, a.get_name() if a else None))

# Check anim sequence skeletons still resolve
idle = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle_Rig")
unreal.log("idle skel={}".format(idle.get_editor_property("skeleton").get_path_name()))

unreal.log("RENAME_WIRE_DONE")