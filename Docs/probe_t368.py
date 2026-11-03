# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_t368.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T368PROBE: "+str(m))
    except Exception: print(m)
# SystemLibrary methods containing line_trace
try:
    names=[n for n in dir(unreal.SystemLibrary) if "line_trace" in n.lower() or "LineTrace" in n]
    L("SystemLibrary line_trace: "+repr(names))
except Exception as e:
    L("SL dir "+str(e))
try:
    names=[n for n in dir(unreal.KismetSystemLibrary) if "line_trace" in n.lower() or "LineTrace" in n]
    L("KismetSystemLibrary line_trace: "+repr(names))
except Exception as e:
    L("KSL dir "+str(e))
# PIE world + skeleton sample
world=None
try:
    for w in unreal.EditorLevelLibrary.get_pie_world_context() and [] or []:
        pass
except Exception:
    pass
try:
    worlds=[]
    # try common helpers from runtime
    import sys
    sys.path.insert(0,r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python")
    import shop_interact_runtime as m
    world=m._pie_world()
    L("pie_world="+str(world))
except Exception as e:
    L("pie "+str(e)); world=None
if world:
    enemies=m._list_live_enemy_actors(world)
    L("enemy_count="+str(len(enemies)))
    for a in enemies[:3]:
        try:
            L("enemy name=%s class=%s"%(a.get_name(), a.get_class().get_name()))
        except Exception as e:
            L("ename "+str(e))
        try:
            L("is_character="+str(isinstance(a, unreal.Character)))
        except Exception as e:
            L("isinstance "+str(e))
        mesh=m._get_pawn_mesh(a)
        L("mesh="+str(mesh))
        try:
            cm=a.get_movement_component()
            L("move_comp="+str(cm)+" class="+str(cm.get_class().get_name() if cm else None))
        except Exception as e:
            L("move "+str(e))
        try:
            anim_mode=mesh.get_animation_mode() if mesh else None
            L("anim_mode="+str(anim_mode))
            anim_cls=mesh.get_editor_property("anim_class") if mesh else None
            L("anim_class="+str(anim_cls))
        except Exception as e:
            L("anim "+str(e))
# TraceTypeQuery
try:
    L("TraceTypeQuery attrs: "+repr([x for x in dir(unreal.TraceTypeQuery) if x.startswith("TRACE") or x.isupper()][:30]))
except Exception as e:
    L("TTQ "+str(e))
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
