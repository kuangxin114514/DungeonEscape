# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\fix_lights_t430.txt"
lines=[]
def L(s):
    lines.append(str(s)); print(s)

world=unreal.EditorLevelLibrary.get_editor_world()
L("world="+str(world.get_path_name() if world else None))
n=0
for a in unreal.EditorLevelLibrary.get_all_level_actors():
    if not isinstance(a, unreal.PointLight):
        continue
    try:
        comp=a.light_component
        comp.set_editor_property("mobility", unreal.ComponentMobility.MOVABLE)
        name=a.get_actor_label() if hasattr(a,"get_actor_label") else a.get_name()
        L("movable: "+str(name))
        n+=1
    except Exception as e:
        L("ERR "+str(a.get_name())+" "+str(e))
try:
    ws=world.get_world_settings()
    ws.set_editor_property("force_no_precomputed_lighting", True)
    L("ForceNoPrecomputedLighting=True")
except Exception as e:
    L("ws ERR "+str(e))
try:
    unreal.EditorLevelLibrary.save_current_level()
    L("saved")
except Exception as e:
    L("save ERR "+str(e))
L("fixed_point_lights=%d"%n)
open(OUT,"w",encoding="utf-8").write("\n".join(lines))
