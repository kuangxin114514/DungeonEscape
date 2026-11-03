# -*- coding: utf-8 -*-
import unreal

skel = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton")
idle = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Idle_Rig")
walk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Walking_A_Rig")
run = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_Running_A_Rig")
folder = "/Game/Characters/Player/KayKit/Animations"

src = "/Game/Mannequin/Animations/ThirdPerson_IdleRun_2D"
dst = folder + "/BS_KayKitLocomotion2D"
if unreal.EditorAssetLibrary.does_asset_exist(dst):
    unreal.EditorAssetLibrary.delete_asset(dst)

bs = unreal.EditorAssetLibrary.duplicate_asset(src, dst)
unreal.log("dup={}".format(bs))
if not bs:
    unreal.log("DUP_FAIL")
else:
    unreal.log("before skel={}".format(bs.get_editor_property("skeleton")))
    # Try every way to set skeleton
    for m in ["SetSkeleton", "set_skeleton", "ReplaceSkeleton", "SetPreviewSkeleton"]:
        try:
            r = bs.call_method(m, (skel,))
            unreal.log("call {} => {}".format(m, r))
        except Exception as e:
            unreal.log("call {} ERR {}".format(m, e))
    for prop in ["skeleton", "Skeleton", "preview_skeleton", "PreviewSkeleton", "target_skeleton"]:
        try:
            bs.set_editor_property(prop, skel)
            unreal.log("set {} OK".format(prop))
        except Exception as e:
            unreal.log("set {} ERR {}".format(prop, e))
    unreal.log("after skel={}".format(bs.get_editor_property("skeleton")))

    # Inspect sample API
    methods = [m for m in dir(bs) if not m.startswith("_")]
    unreal.log("bs methods: {}".format(methods))
    for m in methods:
        if "sample" in m.lower() or "blend" in m.lower() or "grid" in m.lower() or "axis" in m.lower() or "add" in m.lower():
            unreal.log("interesting {}".format(m))

    # Try add_sample / get_samples
    for m in ["add_sample", "AddSample", "delete_all_samples", "DeleteAllSamples", "get_number_of_samples", "GetNumberOfSamples"]:
        if hasattr(bs, m):
            unreal.log("HAS attr {}".format(m))
        try:
            r = bs.call_method(m)
            unreal.log("call empty {} => {}".format(m, r))
        except Exception as e:
            unreal.log("call empty {} ERR {}".format(m, e))

    # BlendSpaceBase API via unreal.BlendSpace
    unreal.log("BlendSpace dir sample: {}".format([m for m in dir(unreal.BlendSpace) if "sample" in m.lower() or "Sample" in m or "axis" in m.lower()]))

unreal.log("SETSKEL_DONE")