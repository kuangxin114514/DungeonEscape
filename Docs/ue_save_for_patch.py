# -*- coding: utf-8 -*-
import unreal
# Force save and unload references by GC
bs_path = "/Game/Characters/Player/KayKit/Animations/BS_KayKitLocomotion"
unreal.EditorAssetLibrary.save_asset(bs_path)
# Close editors
try:
    aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
    aes.close_all_editors()
    unreal.log("closed editors")
except Exception as e:
    unreal.log("close ERR {}".format(e))
unreal.EditorAssetLibrary.save_directory("/Game/Characters/Player/KayKit/Animations")
unreal.log("SAVED_FOR_PATCH")