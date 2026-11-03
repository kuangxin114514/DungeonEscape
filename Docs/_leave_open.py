import unreal
bp=unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets([bp])
unreal.EditorAssetLibrary.sync_browser_to_objects([
 "/Game/Characters/Player/KayKit/Weapons/SM_KayKitSword",
 "/Game/Characters/Player/KayKit/Weapons/SM_KayKitShield",
])
print("BP_OPEN_VIEWPORT_READY")