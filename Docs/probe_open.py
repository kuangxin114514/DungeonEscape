# -*- coding: utf-8 -*-
import unreal, json
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_open.json"
tools = unreal.AssetToolsHelpers.get_asset_tools()
r = {
 "tools": [a for a in dir(tools) if not a.startswith("_")],
 "eal": [a for a in dir(unreal.EditorAssetLibrary) if "open" in a.lower() or "edit" in a.lower() or "sync" in a.lower() or "load" in a.lower()],
 "has_AssetEditorSubsystem": hasattr(unreal, "AssetEditorSubsystem"),
 "has_AssetEditorToolkit": hasattr(unreal, "AssetEditorToolkit"),
 "unreal_open": [a for a in dir(unreal) if "Editor" in a and ("Asset" in a or "Toolkit" in a or "Subsystem" in a)],
}
# Try open via LevelEditorSubsystem / load
for name in ("open_editor_for_assets","OpenEditorForAssets"):
    r["has_"+name] = hasattr(tools, name)
# Bones on skeleton via reference skeleton?
skel = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Skeleton")
sk = unreal.EditorAssetLibrary.load_asset("/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight")
r["skel_dir_bone"] = [a for a in dir(skel) if not a.startswith("_")][:80]
r["sk_dir"] = [a for a in dir(sk) if not a.startswith("_")][:80]
# Try get reference skeleton bone names via python method
for meth in ("get_all_socket_names","GetAllSocketNames"):
    if hasattr(sk, meth):
        try: r[meth]=list(getattr(sk,meth)())
        except Exception as e: r[meth]=str(e)

with open(OUT,"w",encoding="utf-8") as f: json.dump(r,f,indent=2,default=str)
print("OPEN_DONE")