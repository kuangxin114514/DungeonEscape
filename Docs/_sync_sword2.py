import unreal
aes = unreal.AssetEditorSubsystem()
bp = unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
aes.open_editor_for_assets([bp])
unreal.EditorAssetLibrary.sync_browser_to_objects(["/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword"])
print("OK")