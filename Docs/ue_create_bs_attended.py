# -*- coding: utf-8 -*-
import unreal

skel = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton")
idle = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle_Rig")
walk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Walking_A_Rig")
run = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Running_A_Rig")
folder = "/Game/Characters/Player/KayKit/Animations"

# 1) Try SetSkeleton / set skeleton on duplicated mannequin BS
src = "/Game/Mannequin/Animations/ThirdPerson_IdleRun_2D"
# Prefer 1D if we can duplicate a 1D - check mannequin for BlendSpace1D
man_anims = unreal.EditorAssetLibrary.list_assets("/Game/Mannequin/Animations", False, False)
unreal.log("man_anims={}".format(man_anims))

# Duplicate ThirdPerson IdleRun as starting point? It's BlendSpace (2D). We need BlendSpace1D.
# Create via factory without skeleton -> fails. Try call_method on factory.

factory = unreal.BlendSpaceFactory1D()
for m in ["SetTargetSkeleton","set_target_skeleton","SetSkeleton","FactoryCreateNew"]:
    try:
        r = factory.call_method(m, (skel,))
        unreal.log("factory.call_method({})={}".format(m, r))
    except Exception as e:
        unreal.log("factory.call_method({}) ERR {}".format(m, e))

# Try create blank then SetSkeleton on asset via call_method
# First duplicate any existing BlendSpace1D from engine
engine_bs = None
# Search loaded BlendSpace1D
for obj in unreal.ObjectIterator(unreal.BlendSpace1D):
    unreal.log("found BS1D {}".format(obj.get_path_name()))
    engine_bs = obj
    break

# Duplicate mannequin-related: create new empty by duplicating previous deleted - recreate from ThirdPerson by converting?
# Try: create asset with factory when TargetSkeleton set via CDO
cdo = unreal.get_default_object(unreal.BlendSpaceFactory1D.static_class())
unreal.log("CDO={}".format(cdo))
for prop in ["TargetSkeleton","target_skeleton"]:
    try:
        cdo.set_editor_property(prop, skel)
        unreal.log("CDO.{} SET".format(prop))
    except Exception as e:
        unreal.log("CDO.{} ERR {}".format(prop, e))

# Try creating AnimMontage via right-click equivalent - AnimationLibrary?
# Duplicate Idle as montage using AssetTools.rename / duplicate then change class? Impossible.

# Try AnimSequence -> create montage through editor subsystem action
try:
    aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
except Exception:
    aes = None

# ATTENDED dialog create
name = "BS_KayKitLocomotion"
path = folder + "/" + name
if unreal.EditorAssetLibrary.does_asset_exist(path):
    unreal.EditorAssetLibrary.delete_asset(path)

tools = unreal.AssetToolsHelpers.get_asset_tools()
unreal.log("OPEN_ATTENDED_DIALOG")
asset = tools.create_asset_with_dialog(name, folder, unreal.BlendSpace1D, unreal.BlendSpaceFactory1D())
unreal.log("RESULT={}".format(asset))
if asset:
    unreal.log("skel={}".format(asset.get_editor_property("skeleton")))
    unreal.EditorAssetLibrary.save_asset(path)
unreal.log("ATTENDED_DONE")