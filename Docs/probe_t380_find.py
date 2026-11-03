# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_t380_find.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T380F: "+str(m))
    except Exception: print(m)
reg=unreal.AssetRegistryHelpers.get_asset_registry()
# search skeleton
for a in reg.get_assets_by_path("/Game", recursive=True):
    n=str(a.asset_name)
    p=str(a.package_name)
    if ("Skeleton" in n or "Skeleton" in p or "skel" in n.lower()) and ("Enemy" in p or "Enemies" in p or "Minion" in n or "Minion" in p or "BP_Enemy" in n):
        L("%s | %s | %s"%(a.asset_class, a.package_name, a.asset_name))
L("---ABP/AnimBP---")
for a in reg.get_assets_by_path("/Game", recursive=True):
    n=str(a.asset_name)
    if "AnimBP" in n or "ABP_" in n or str(a.asset_class)=="AnimBlueprint":
        L("%s | %s | %s"%(a.asset_class, a.package_name, a.asset_name))
L("---AIController---")
for a in reg.get_assets_by_path("/Game", recursive=True):
    n=str(a.asset_name)
    if "AIController" in n or n.startswith("AIC_") or "BT_" in n:
        L("%s | %s | %s"%(a.asset_class, a.package_name, a.asset_name))
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT,"lines",len(lines))
