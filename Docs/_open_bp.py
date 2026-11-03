# -*- coding: utf-8 -*-
import unreal
bp = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
aes.open_editor_for_assets([bp])
unreal.EditorAssetLibrary.sync_browser_to_objects(["/Game/Characters/Player/KayKit/BP_KayKitKnight"])
print("OPENED")