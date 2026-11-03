# -*- coding: utf-8 -*-
import unreal

skel = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton")
idle = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle")
run = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Running_A")
walk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Walking_A")

# Try CDO / various bypasses for factory TargetSkeleton
factory_cdo = unreal.get_default_object(unreal.BlendSpaceFactory1D.static_class())
unreal.log("factory_cdo={}".format(factory_cdo))
for pn in ["TargetSkeleton","target_skeleton"]:
    try:
        factory_cdo.set_editor_property(pn, skel)
        unreal.log("CDO set {} OK".format(pn))
    except Exception as e:
        unreal.log("CDO set {} ERR {}".format(pn, e))

# Try AnimBlueprintFactory style property list on a new factory via get_editor_property Allow
f = unreal.BlendSpaceFactory1D()
# Some UE builds expose via set_editor_properties dict
try:
    f.set_editor_properties({"TargetSkeleton": skel})
    unreal.log("set_editor_properties OK")
except Exception as e:
    unreal.log("set_editor_properties ERR {}".format(e))

# Try create_asset_with_dialog? skip

# Check if Skeleton has set_preview_mesh / compatible
# Use AnimationLibrary finalize?

# Try: change skeleton via AssetRegistry / reimport data - no

# Approach: create empty AnimComposite or use AimOffset?

# Check BlendSpace1D methods for set_skeleton
bs_existing = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion")
unreal.log("existing bs={}".format(bs_existing))
if bs_existing:
    meths = [m for m in dir(bs_existing) if "kel" in m.lower() or "set_" in m.lower()]
    unreal.log("bs meths: "+",".join(meths[:50]))
    # try call_method SetSkeleton
    for m in ["SetSkeleton","set_skeleton","ReplaceSkeleton","replace_skeleton","SetPreviewSkeleton"]:
        try:
            unreal.log("call {} -> {}".format(m, bs_existing.call_method(m, (skel,))))
        except Exception as e:
            unreal.log("call {} ERR {}".format(m, e))

# Check AnimationEditorUtils / EditorScripting
names = [n for n in dir(unreal) if "Skeleton" in n or "BlendSpace" in n or "AnimationEditor" in n or "AnimEditor" in n]
unreal.log("names: "+",".join(names[:60]))

# Try duplicating AnimSequence onto KayKit skeleton by remap?
# Actually: UAnimSequence has skeleton read-only too usually

# IMPORTANT alternate path: use ABP with SequencePlayer only (Running),
# and drive play rate / which sequence from Character via SetAnimation
# by switching animation_data on mesh from Character EventTick -
# implement Tick in Python init_unreal runtime for editor PIE,
# AND also add a Blueprint-callable path.

# Check if we can add variables/nodes via SubobjectData - no

# Try factory create after setting protected via unreal.PythonObject
try:
    import json
    # inspect uobject flags
    unreal.log("f class={}".format(f.get_class()))
except Exception as e:
    unreal.log(str(e))

# Last idea: use EditorAssetLibrary.duplicate_asset of BS, then
# use Skeleton.compat / retarget so KayKit anims can be used on Mannequin BS?
# Animations must be same skeleton as BlendSpace.

# Retarget KayKit anims TO mannequin? Wrong direction.

# Retarget: set KayKit skeleton's Retarget Source / Rig to UE4 mannequin
# and use Animation Retarget Manager - still BS skeleton issue

# Try creating BlendSpace via AssetTools.create_asset while Skeleton is selected in content browser?
try:
    unreal.EditorAssetLibrary.sync_browser_to_objects(["/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton"])
except Exception as e:
    unreal.log("sync ERR {}".format(e))

f2 = unreal.BlendSpaceFactory1D()
f2.set_editor_property("edit_after_new", False)
path = "/Game/Characters/Player/KayKit/Animations"
name = "BS_KayKitLocomotion2"
full = path + "/" + name
if unreal.EditorAssetLibrary.does_asset_exist(full):
    unreal.EditorAssetLibrary.delete_asset(full)
asset = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, path, unreal.BlendSpace1D, f2)
unreal.log("create after sync -> {}".format(asset))

unreal.log("PROBE10_DONE")