# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\gi_gold5.txt"
lines=[]
def log(m):
    lines.append(str(m)); unreal.log("GI5: "+str(m))
paths=["/Game/Core/GI_DungeonGame","/Game/Blueprints/GI_DungeonGame","/Game/GI_DungeonGame","/Game/Game/GI_DungeonGame"]
found=None
for p in paths:
    if unreal.EditorAssetLibrary.does_asset_exist(p):
        found=p; break
if not found:
    # search
    try:
        assets=unreal.EditorAssetLibrary.list_assets("/Game", True, False)
        for a in assets:
            if "GI_Dungeon" in a or "DungeonGame" in a:
                lines.append("cand "+a)
                if a.endswith("GI_DungeonGame") or "/GI_DungeonGame." in a:
                    found=a.split(".")[0]
    except Exception as e:
        log("list "+str(e))
log("found="+str(found))
if found:
    unreal.EditorAssetLibrary.load_asset(found)
    cls=unreal.load_class(None, found+".GI_DungeonGame_C")
    if cls is None:
        # try common
        for suf in (".GI_DungeonGame_C", "_C"):
            cls=unreal.load_class(None, found+suf if not found.endswith("_C") else found)
            if cls: break
    log("cls="+str(cls))
    if cls:
        cdo=unreal.get_default_object(cls)
        log("cdo="+str(cdo))
        try:
            old=cdo.get_editor_property("Gold")
            log("old Gold="+str(old))
        except Exception as e:
            log("get Gold "+str(e)); old=None
        try:
            cdo.set_editor_property("Gold", 5)
            log("set Gold=5")
        except Exception as e:
            log("set Gold "+str(e))
        try:
            unreal.EditorAssetLibrary.save_asset(found)
            log("saved")
        except Exception as e:
            log("save "+str(e))
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE")
