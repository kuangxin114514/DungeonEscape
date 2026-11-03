# -*- coding: utf-8 -*-
import unreal

folder = "/Game/Characters/Player/KayKit/Animations"
unreal.EditorAssetLibrary.make_directory(folder)
paths = unreal.EditorAssetLibrary.list_assets(folder, True, False)
unreal.log("ASSETS: {}".format(paths))

# Delete bad Mannequin-skeleton BS if present so we can recreate
bad = folder + "/BS_KayKitLocomotion"
if unreal.EditorAssetLibrary.does_asset_exist(bad):
    bs = unreal.EditorAssetLibrary.load_asset(bad)
    try:
        sk = bs.get_editor_property("skeleton")
        unreal.log("existing BS skeleton={}".format(sk.get_path_name() if sk else None))
        if sk and "Mannequin" in sk.get_path_name():
            unreal.EditorAssetLibrary.delete_asset(bad)
            unreal.log("deleted bad BS")
    except Exception as e:
        unreal.log("bs check ERR {}".format(e))

# Sync browser to folder
try:
    unreal.EditorAssetLibrary.sync_browser_to_objects([folder])
except Exception as e:
    try:
        # alternate API
        unreal.AssetRegistryHelpers.get_asset_registry()
        editors = unreal.AssetToolsHelpers.get_asset_tools()
        unreal.log("sync alt err {}".format(e))
    except Exception as e2:
        unreal.log("sync ERR {} / {}".format(e, e2))

# Focus content browser via console?
world = unreal.EditorLevelLibrary.get_editor_world()
unreal.SystemLibrary.execute_console_command(world, "ContentBrowser.FocusSearch")

# Set Character mesh to use ABP temporarily? Keep SingleNode until BS ready.
# Confirm run/idle/walk paths (_Rig preferred if exist)
for name in ["Idle_Rig","Idle","Running_A_Rig","Running_A","Walking_A_Rig","Walking_A"]:
    p = "/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_" + name.replace("_Rig","") 
# list matching
all_mesh = unreal.EditorAssetLibrary.list_assets("/Game/Characters/Player/KayKit/Mesh", False, False)
anims = [p for p in all_mesh if "Idle" in p or "Running" in p or "Walking" in p]
unreal.log("LOCO_ANIMS: {}".format(anims))

# Open ABP so user/UI can see it - don't assign yet
abp = "/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight"
if unreal.EditorAssetLibrary.does_asset_exist(abp):
    unreal.EditorLoadingAndSavingUtils.load_map  # noop keep
    try:
        ss = unreal.AssetEditorSubsystem()
    except Exception:
        ss = None
    try:
        # UE4.27: AssetEditorSubsystem might be unreal.get_editor_subsystem
        aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem) if hasattr(unreal, "get_editor_subsystem") else None
        unreal.log("aes={}".format(aes))
        if aes:
            aes.open_editor_for_assets([unreal.EditorAssetLibrary.load_asset(abp)])
            unreal.log("opened ABP")
    except Exception as e:
        unreal.log("open abp ERR {}".format(e))

unreal.log("PREP_DONE")