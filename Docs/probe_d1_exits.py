# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT = r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_d1_exits.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("ProbeD1: "+str(m))
    except Exception: print(m)

MAP="/Game/Maps/Dungeon/Map_Dungeon1"
unreal.EditorLoadingAndSavingUtils.load_map(MAP)
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    try:
        lab=a.get_actor_label() or ""
        cn=a.get_class().get_name()
        tags=list(a.get_editor_property("tags") or [])
    except Exception:
        continue
    key=(lab+" "+" ".join([str(t) for t in tags])+" "+cn).lower()
    if any(k in key for k in ("exit","hubreturn","dungeonexit","playerstart","skeleton","skel","enemy")) or "PlayerStart" in cn:
        loc=a.get_actor_location()
        L("%s | %s | tags=%s | (%.0f,%.0f,%.0f)" % (cn, lab, tags, loc.x, loc.y, loc.z))
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE", OUT)
