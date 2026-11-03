# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, shutil, os
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\dup_d3b_t422.txt"
lines=[]
def L(s):
    lines.append(str(s)); print(s)

# disk copy umap
src_dir=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Maps\Dungeon"
for fn in os.listdir(src_dir):
    if fn.startswith("Map_Dungeon2"):
        src=os.path.join(src_dir, fn)
        dst=os.path.join(src_dir, fn.replace("Map_Dungeon2","Map_Dungeon3"))
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
            L("copied %s -> %s"%(fn, os.path.basename(dst)))
        else:
            L("exists "+os.path.basename(dst))

# refresh asset registry
try:
    unreal.AssetRegistryHelpers.get_asset_registry().scan_paths_synchronous(["/Game/Maps/Dungeon"], True)
    L("scanned")
except Exception as e:
    L("scan ERR "+str(e))

dst="/Game/Maps/Dungeon/Map_Dungeon3"
L("dst exists=%s"%unreal.EditorAssetLibrary.does_asset_exist(dst))
# try load level
try:
    ok=unreal.EditorLoadingAndSavingUtils.load_map(dst)
    L("load_map="+str(ok))
except Exception as e:
    L("load_map ERR "+str(e))
    try:
        unreal.EditorLevelLibrary.load_level(dst)
        L("load_level ok")
    except Exception as e2:
        L("load_level ERR "+str(e2))

ps=None
try:
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        try:
            if isinstance(a, unreal.PlayerStart) or ("PlayerStart" in (a.get_name() or "")):
                ps=a; break
        except Exception:
            pass
except Exception as e:
    L("list ERR "+str(e))
if ps is None:
    try:
        ps=unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(-1180.0,0.0,120.0), unreal.Rotator(0,0,0))
        L("spawned PS "+str(ps))
    except Exception as e:
        L("spawn ERR "+str(e))
if ps is not None:
    try:
        ps.set_actor_label("Dungeon3_PlayerStart")
        L("PS labeled")
    except Exception as e:
        L("label ERR "+str(e))
try:
    unreal.EditorLevelLibrary.save_current_level()
    L("saved")
except Exception as e:
    L("save ERR "+str(e))
try:
    unreal.EditorLevelLibrary.load_level("/Game/Maps/Dungeon/Map_Dungeon2")
    L("back D2")
except Exception as e:
    L("back ERR "+str(e))
open(OUT,"w",encoding="utf-8").write("\n".join(lines))
