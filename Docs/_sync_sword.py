import unreal
aes = unreal.AssetEditorSubsystem()
bp = unreal.load_asset("/Game/Characters/Player/KayKit/BP_KayKitKnight")
aes.open_editor_for_assets([bp])
sword = "/Game/Characters/Player/KayKit/SM_KayKitSword"
shield = "/Game/Characters/Player/KayKit/SM_KayKitShield"
# verify paths
for p in [sword, shield]:
    print(p, unreal.EditorAssetLibrary.does_asset_exist(p))
unreal.EditorAssetLibrary.sync_browser_to_objects([sword])
print("SYNCED_SWORD")