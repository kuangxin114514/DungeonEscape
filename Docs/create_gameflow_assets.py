import unreal

GAMEFLOW = "/Game/Core/GameFlow"

def ensure_dir(path):
    if not unreal.EditorAssetLibrary.does_directory_exist(path):
        unreal.EditorAssetLibrary.make_directory(path)

def create_bp(parent_class, name):
    asset_path = GAMEFLOW + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        unreal.log("Exists: " + asset_path)
        return unreal.load_asset(asset_path)
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("ParentClass", parent_class)
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    bp = asset_tools.create_asset(name, GAMEFLOW, None, factory)
    if bp:
        unreal.EditorAssetLibrary.save_loaded_asset(bp)
        unreal.log("Created: " + asset_path)
    else:
        unreal.log_error("Failed: " + name)
    return bp

def create_enum():
    name = "E_DungeonGameState"
    asset_path = GAMEFLOW + "/" + name
    if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        unreal.log("Exists: " + asset_path)
        return unreal.load_asset(asset_path)
    factory = unreal.EnumFactory()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    enum_asset = asset_tools.create_asset(name, GAMEFLOW, None, factory)
    if enum_asset:
        unreal.EditorAssetLibrary.save_loaded_asset(enum_asset)
        unreal.log("Created enum: " + asset_path)
    else:
        unreal.log_error("Failed enum")
    return enum_asset

ensure_dir(GAMEFLOW)
create_enum()
create_bp(unreal.GameInstance.static_class(), "GI_DungeonGame")
create_bp(unreal.GameModeBase.static_class(), "GM_Hub")
create_bp(unreal.GameModeBase.static_class(), "GM_Dungeon")
unreal.EditorAssetLibrary.save_directory(GAMEFLOW)
unreal.log("GameFlow assets done")
