# -*- coding: utf-8 -*-
"""T227d: place exit markers at screenshot corridor + SM_stairs; confirm runtime."""
from __future__ import print_function
import unreal, shutil, os, sys

OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_t227_attack_hub_exit.txt"
SRC = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\shop_interact_runtime_v15.py"
DST = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
DUNGEON = "/Game/Maps/Dungeon/Map_Dungeon"
HUB = "/Game/Maps/Hub/Map_Hub"
lines=[]
def L(m):
    lines.append(str(m)); unreal.log("T227d: "+str(m))
def flush():
    open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")

def ensure_marker(label, loc):
    marker=None
    for a in unreal.EditorLevelLibrary.get_all_level_actors():
        try:
            if (a.get_actor_label() or "") == label:
                marker=a; break
        except Exception:
            pass
    if marker is None:
        marker = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, loc, unreal.Rotator(0,0,0))
        L("spawn "+label)
    else:
        L("reuse "+label)
    try: marker.set_actor_label(label)
    except Exception: pass
    try: marker.set_actor_location(loc, False, True)
    except Exception:
        try: marker.set_actor_location(loc, False, False)
        except Exception as e: L("loc "+str(e))
    try: marker.set_editor_property("tags", ["HubReturn", "DungeonExit"])
    except Exception as e: L("tags "+str(e))
    try:
        cube = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube")
        smc = marker.static_mesh_component
        if cube: smc.set_editor_property("static_mesh", cube)
        smc.set_editor_property("relative_scale3d", unreal.Vector(0.5, 0.5, 0.5))
        try: smc.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        except Exception: pass
    except Exception as e:
        L("mesh "+str(e))
    L("%s @ (%.1f,%.1f,%.1f)" % (label, loc.x, loc.y, loc.z))
    return marker

def main():
    L("=== T227d ===")
    shutil.copyfile(SRC, DST)
    shutil.copyfile(SRC, r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\shop_interact_runtime.py")
    py_dir = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
    if py_dir not in sys.path: sys.path.insert(0, py_dir)
    if "shop_interact_runtime" in sys.modules:
        del sys.modules["shop_interact_runtime"]
    import shop_interact_runtime as mod
    mod.bootstrap()
    L("runtime ok V=%s" % ("V15b" if "V15b" in open(DST,encoding="utf-8",errors="ignore").read() else "?"))

    unreal.EditorLoadingAndSavingUtils.load_map(DUNGEON)
    # 1) Screenshot corridor near selected wall (130,-840) — place in corridor walkway
    ensure_marker("DungeonExit_HubReturn", unreal.Vector(130.0, -700.0, 140.0))
    # 2) Actual SM_stairs east
    ensure_marker("DungeonExit_HubReturn_Stairs", unreal.Vector(1280.0, -80.0, 140.0))
    # 3) Spawn-side wide stairs (PlayerStart area)
    ensure_marker("DungeonExit_HubReturn_Wide", unreal.Vector(-1500.0, -40.0, 140.0))
    unreal.EditorLevelLibrary.save_current_level()
    L("dungeon saved")
    unreal.EditorLoadingAndSavingUtils.load_map(HUB)
    L("hub restored")
    mod.bootstrap()
    L("=== DONE ===")
    L("Markers: corridor(130,-700) | SM_stairs(1280,-80) | wide(-1500,-40); range=380; LMB=Chop")
    flush()
main()