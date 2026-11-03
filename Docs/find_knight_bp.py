# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, traceback
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\find_knight_bp.txt"
lines=[]
def L(m):
    lines.append(str(m)); 
    try: unreal.log("T330F: "+str(m))
    except Exception: print(m)
try:
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    ar.search_all_assets(True)
    for filt in ("BP_KayKitKnight", "KayKitKnight", "Sword_2H"):
        assets = ar.get_assets_by_class("Blueprint", True) if False else None
    # filter by path
    assets = ar.get_assets_by_path("/Game/Characters/Player/KayKit", True)
    L("assets under KayKit: %d" % len(assets or []))
    for a in assets or []:
        try:
            name = str(a.asset_name)
            path = str(a.object_path)
        except Exception:
            name=str(a); path=""
        if "BP_" in name or "Sword" in name:
            L("%s | %s | %s" % (name, path, a.asset_class))
    # try load variants
    for p in [
        "/Game/Characters/Player/KayKit/BP_KayKitKnight",
        "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight",
        "/Game/Characters/Player/KayKit/BP_KayKitKnight.BP_KayKitKnight_C",
    ]:
        a=None
        try: a=unreal.load_asset(p)
        except Exception as e: L("load %s err %s" % (p,e))
        L("load_asset %s -> %s" % (p, a))
except Exception as e:
    L("ERR "+str(e)); L(traceback.format_exc())
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE", OUT)
