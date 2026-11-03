# -*- coding: utf-8 -*-
import unreal
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_t227_corridor.txt"
lines=[]
def L(m):
    lines.append(str(m)); unreal.log("P227c: "+str(m))
unreal.EditorLoadingAndSavingUtils.load_map("/Game/Maps/Dungeon/Map_Dungeon")
# dump all actors sorted by Y then X
rows=[]
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    try:
        lab=a.get_actor_label() or a.get_name() or ""
        loc=a.get_actor_location()
        cn=a.get_class().get_name()
    except Exception:
        continue
    mesh=""
    try:
        smc=a.static_mesh_component
        if smc:
            sm=smc.get_editor_property("static_mesh")
            if sm: mesh=sm.get_name()
    except Exception:
        pass
    rows.append((loc.y, loc.x, loc.z, lab, mesh, cn))
rows.sort()
L("ALL actors by Y:")
for y,x,z,lab,mesh,cn in rows:
    L("  y=%.0f x=%.0f z=%.0f %s/%s [%s]" % (y,x,z,lab,mesh,cn))
# KayKit stair mesh assets available
assets=unreal.EditorAssetLibrary.list_assets("/Game/Environments/KayKitDungeon/Meshes", True, False)
stairs=[p for p in assets if "stair" in p.lower()]
L("stair meshes in pack: %d" % len(stairs))
for p in stairs:
    L("  "+p)
unreal.EditorLoadingAndSavingUtils.load_map("/Game/Maps/Hub/Map_Hub")
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("DONE")