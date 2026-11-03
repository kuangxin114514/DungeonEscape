import unreal
asset = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
if asset:
    unreal.AssetEditorSubsystem().open_editor_for_assets([asset])
    unreal.log("OPENED SK_KayKitKnight")
else:
    unreal.log_error("MISSING SK_KayKitKnight")
