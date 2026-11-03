import unreal
unreal.EditorAssetLibrary.sync_browser_to_objects(["/Game/Characters/Player/KayKit/Weapons/SM_KayKitShield"])
bp=unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets([bp])
print("synced_shield")
