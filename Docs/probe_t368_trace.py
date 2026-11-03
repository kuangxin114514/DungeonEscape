# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, inspect
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_t368_trace.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log(str(m))
    except Exception: print(m)
try:
    L(str(unreal.SystemLibrary.line_trace_single.__doc__))
except Exception as e:
    L("doc "+str(e))
try:
    L("sig="+str(inspect.signature(unreal.SystemLibrary.line_trace_single)))
except Exception as e:
    L("sig "+str(e))
try:
    L("new_doc="+str(unreal.SystemLibrary.line_trace_single_new.__doc__))
except Exception as e:
    L("new "+str(e))
try:
    L("HitResult attrs sample: blocking_hit,actor in dir? "+str(hasattr(unreal.HitResult(),"blocking_hit"))+" "+str([a for a in dir(unreal.HitResult) if "block" in a.lower() or a in ("actor","component","time","distance")][:20]))
except Exception as e:
    L("hr "+str(e))
# Character methods
try:
    L("Character add_movement: "+str(hasattr(unreal.Character,"add_movement_input")))
    L("Actor set_actor_location: "+str(hasattr(unreal.Actor,"set_actor_location")))
    L("Actor set_actor_rotation: "+str(hasattr(unreal.Actor,"set_actor_rotation")))
except Exception as e:
    L("char "+str(e))
# DrawDebugTrace
try:
    L("DrawDebugTrace: "+str([x for x in dir(unreal.DrawDebugTrace) if not x.startswith("_")][:20]))
except Exception as e:
    L("ddt "+str(e))
open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("WROTE",OUT)
