# -*- coding: utf-8 -*-
import unreal

folder = "/Game/Characters/Player/KayKit/Animations"
skel_path = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton"
unreal.EditorAssetLibrary.sync_browser_to_objects([skel_path])

name = "BS_KayKitLocomotion"
path = folder + "/" + name
if unreal.EditorAssetLibrary.does_asset_exist(path):
    unreal.EditorAssetLibrary.delete_asset(path)
    unreal.log("deleted old")

factory = unreal.BlendSpaceFactory1D()
tools = unreal.AssetToolsHelpers.get_asset_tools()
unreal.log("OPEN_DIALOG_NOW")
asset = tools.create_asset_with_dialog(name, folder, unreal.BlendSpace1D, factory)
unreal.log("DIALOG_RESULT={}".format(asset))
if asset:
    try:
        unreal.log("created_skel={}".format(asset.get_editor_property("skeleton")))
    except Exception as e:
        unreal.log("skel_read ERR {}".format(e))
    unreal.EditorAssetLibrary.save_asset(path)
unreal.log("DIALOG_DONE")