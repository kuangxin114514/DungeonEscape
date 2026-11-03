# -*- coding: utf-8 -*-
import unreal
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_t227.txt"
lines=[]
def L(m):
    lines.append(str(m)); unreal.log("P227: "+str(m))
try:
    w = unreal.EditorLevelLibrary.get_editor_world()
    L("editor_world="+str(w)+" path="+str(w.get_path_name() if w else None))
except Exception as e:
    L("editor_world err "+str(e))
try:
    pies = unreal.EditorLevelLibrary.get_pie_worlds(False)
    L("pie="+str(pies))
except Exception as e:
    L("pie err "+str(e))
for p in [
"/Game/Maps/Dungeon/Map_Dungeon",
"/Game/Characters/Player/KayKit/BP_KayKitKnight",
"/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_1H_Melee_Attack_Chop_Rig",
"/Game/Characters/Player/KayKit/Mesh/SK_KayKitKnight_Anim_Rig_1H_Melee_Attack_Chop",
"/Game/Characters/Player/KayKit/Animations/ABP_KayKitLocomotion",
]:
    L("exists %s -> %s" % (p, unreal.EditorAssetLibrary.does_asset_exist(p)))
    try:
        a = unreal.EditorAssetLibrary.load_asset(p)
        L("  load="+str(a))
    except Exception as e:
        L("  load err "+str(e))
# list chop-like
try:
    assets = unreal.EditorAssetLibrary.list_assets("/Game/Characters/Player/KayKit", True, False)
    chops=[x for x in assets if "Chop" in x or "ABP_" in x or "BP_KayKit" in x]
    L("listed=%d chop/abp/bp=%d" % (len(assets), len(chops)))
    for x in chops[:40]:
        L("  "+x)
except Exception as e:
    L("list err "+str(e))
# maps
try:
    maps = unreal.EditorAssetLibrary.list_assets("/Game/Maps", True, False)
    L("maps="+str(maps))
except Exception as e:
    L("maps err "+str(e))
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("PROBE_DONE")
