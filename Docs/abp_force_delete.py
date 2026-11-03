# -*- coding: utf-8 -*-
import unreal
import time

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\abp_force_delete_result.txt"
lines = []
def L(m):
    lines.append(str(m))
def flush():
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")

aes = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
paths = [
    "/Game/Characters/Player/KayKit/Animations/ABP_KayKitFromTP_BROKEN",
    "/Game/Characters/Player/KayKit/Animations/ABP_KayKitKnight_Probe_BROKEN",
]
assets = []
for p in paths:
    if unreal.EditorAssetLibrary.does_asset_exist(p):
        a = unreal.EditorAssetLibrary.load_asset(p)
        L("loaded {} type={}".format(p, a.get_class().get_name() if a else None))
        try:
            aes.close_all_editors_for_asset(a)
        except Exception as e:
            L("close {}".format(e))
        if a:
            assets.append(a)

# Try delete_loaded_assets
try:
    ok = unreal.EditorAssetLibrary.delete_loaded_assets(assets)
    L("delete_loaded_assets -> {}".format(ok))
except Exception as e:
    L("delete_loaded_assets ERR {}".format(e))

# Try AssetTools delete
try:
    at = unreal.AssetToolsHelpers.get_asset_tools()
    L("asset_tools={}".format(at))
except Exception as e:
    L("asset_tools ERR {}".format(e))

# ObjectTools via unreal.load_object / force
try:
    # In UE4.27 python, ObjectTools may be available as unreal.ObjectTools? 
    names = [n for n in dir(unreal) if "elete" in n.lower() or "ObjectTools" in n]
    L("delete_apis={}".format(names[:40]))
except Exception as e:
    L("dir ERR {}".format(e))

# Try consolidating/replacing with loco then delete
loco = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion")
for a in list(assets):
    p = a.get_path_name().split(".")[0]
    L("still exists after loaded delete? {} = {}".format(p, unreal.EditorAssetLibrary.does_asset_exist(p)))

# Soft: mark for GC by renaming out of Animations then deleting
for p in paths:
    if unreal.EditorAssetLibrary.does_asset_exist(p):
        dest = p + "_TO_DELETE"
        if unreal.EditorAssetLibrary.does_asset_exist(dest):
            unreal.EditorAssetLibrary.delete_asset(dest)
        ok = unreal.EditorAssetLibrary.rename_asset(p, dest)
        L("rename {} -> {} = {}".format(p, dest, ok))
        if unreal.EditorAssetLibrary.does_asset_exist(dest):
            # unload via save package none
            try:
                a2 = unreal.EditorAssetLibrary.load_asset(dest)
                aes.close_all_editors_for_asset(a2)
            except Exception:
                pass
            ok2 = unreal.EditorAssetLibrary.delete_asset(dest)
            L("delete renamed {} -> {}".format(dest, ok2))
            # try delete_loaded
            if unreal.EditorAssetLibrary.does_asset_exist(dest):
                a2 = unreal.EditorAssetLibrary.load_asset(dest)
                try:
                    ok3 = unreal.EditorAssetLibrary.delete_loaded_assets([a2])
                    L("delete_loaded renamed -> {}".format(ok3))
                except Exception as e:
                    L("delete_loaded renamed ERR {}".format(e))

# Final list
assets_left = unreal.EditorAssetLibrary.list_assets("/Game/Characters/Player/KayKit/Animations", recursive=False)
L("left={}".format([a for a in assets_left if "BROKEN" in a or "TO_DELETE" in a or "FromTP" in a or "Probe" in a]))
L("DONE")
flush()