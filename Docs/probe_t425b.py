# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\probe_t425b.txt"
py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0,py)
import shop_interact_runtime as sir
importlib.reload(sir)
lines=[]
def w(s):
    lines.append(str(s))
worlds=unreal.EditorLevelLibrary.get_pie_worlds(False)
pw=worlds[0] if worlds else None
w("level=%s"%unreal.GameplayStatics.get_current_level_name(pw, True))
w("path=%s"%pw.get_path_name())
w("is_dungeon=%s is_d2=%s is_d3=%s"%(sir._world_is_dungeon(pw), sir._world_is_dungeon2(pw), sir._world_is_dungeon3(pw)))
w("EXIT_RANGE=%s GATE_RANGE=%s"%(sir.EXIT_RANGE, sir.GATE_RANGE))
w("DUNGEON_LEVEL=%s resolve=%s"%(sir.DUNGEON_LEVEL, sir.resolve_dungeon_level()))
actors=unreal.GameplayStatics.get_all_actors_of_class(pw, unreal.Actor)
hits=[]
for a in actors:
    try:
        lab=str(a.get_actor_label())
    except Exception:
        lab=str(a.get_name())
    try:
        tags=[str(t) for t in list(a.tags)]
    except Exception:
        tags=[]
    name=str(a.get_name())
    blob="|".join([lab,name]+tags)
    keys=("HubReturn","DungeonExit","Gate","DungeonEntrance","ToDungeon","Stairs","HubGate","GateTrigger","HubExit")
    if any(k in blob for k in keys):
        loc=a.get_actor_location()
        hits.append((lab,name,tags,loc))
w("marker_count=%d"%len(hits))
for lab,name,tags,loc in hits:
    w("MARK lab=%s name=%s tags=%s loc=(%.0f,%.0f,%.0f)"%(lab,name,tags,loc.x,loc.y,loc.z))
    w("  is_hub=%s is_gate_lab=%s is_d2=%s is_d3=%s"%(
        sir._is_hub_return_marker(lab,tags),
        (("DungeonGate" in tags) or ("GateInteract" in tags) or ("HubGate" in lab) or ("GateTrigger" in lab) or ("DungeonEntrance" in lab) or lab.startswith("GateTrigger_")),
        sir._is_dungeon2_exit_marker(lab,tags),
        sir._is_dungeon3_exit_marker(lab,tags),
    ))
pc=unreal.GameplayStatics.get_player_controller(pw,0)
pawn=pc.get_controlled_pawn()
loc=pawn.get_actor_location()
w("pawn=(%.0f,%.0f,%.0f)"%(loc.x,loc.y,loc.z))
sk,title,gate,hub,d2,d3=sir.scan_near(pw, loc)
w("scan_at_pawn shop=%s title=%s gate=%s hub=%s d2=%s d3=%s"%(sk,title,gate,hub,d2,d3))
# also scan near each gate-like marker
for lab,name,tags,mloc in hits:
    sk,title,gate,hub,d2,d3=sir.scan_near(pw, mloc)
    w("scan_at_%s gate=%s hub=%s d2=%s d3=%s shop=%s"%(lab,gate,hub,d2,d3,sk))
open(OUT,"w",encoding="utf-8").write("\n".join(lines))
print("ok", len(lines))