# -*- coding: utf-8 -*-
from __future__ import print_function
import unreal, importlib, sys
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\save_skel_focus_t395.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T395i: "+str(m))
    except Exception: print(m)

# save via loaded blueprint object
bp=None
for o in unreal.ObjectIterator(unreal.Blueprint):
    try:
        if o.get_name()=="BP_Enemy_Skeleton":
            bp=o; break
    except Exception: pass
L("bp=%s"%bp)
if bp:
    try:
        unreal.EditorAssetLibrary.save_loaded_asset(bp); L("save_loaded ok")
    except Exception as e:
        L("save_loaded "+str(e))
    try:
        unreal.EditorAssetLibrary.save_asset("/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"); L("save_asset ok")
    except Exception as e:
        L("save_asset "+str(e))

# ensure PIE instance has settings + try set focus now if player exists
world=None
try:
    pies=unreal.EditorLevelLibrary.get_pie_worlds(False)
    L("pies=%s"%pies)
    if pies: world=pies[0]
except Exception as e:
    L("pie "+str(e))
if world is None:
    # find UEDPIE world
    for o in unreal.ObjectIterator(unreal.World):
        try: pn=o.get_path_name()
        except Exception: continue
        if "UEDPIE" in pn:
            world=o; L("found "+pn); break
player=None
if world:
    try: player=unreal.GameplayStatics.get_player_pawn(world,0)
    except Exception: pass
L("player=%s"%player)
py=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python"
if py not in sys.path: sys.path.insert(0,py)
import skeleton_engine_ai as s
importlib.reload(s)
L("has_focus=%s ortm_line_check"%hasattr(s,"_set_focus_player"))
if world and player:
    for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character):
        try:
            if "Skeleton" not in a.get_class().get_name(): continue
        except Exception: continue
        s._ensure_move_settings(a)
        ctrl=s._get_ai_controller(a)
        L("skel %s ctrl=%s"%(a.get_name(), ctrl))
        if ctrl:
            s._set_focus_player(ctrl, player)
            L("focus set")
        try:
            mov=a.get_editor_property("character_movement")
            L("  ortm=%s ucdr=%s"%(mov.get_editor_property("orient_rotation_to_movement"), mov.get_editor_property("use_controller_desired_rotation")))
            fw=a.get_actor_forward_vector(); loc=a.get_actor_location(); pl=player.get_actor_location()
            import math
            def yaw(dx,dy): return math.degrees(math.atan2(dy,dx))
            ang=yaw(float(fw.x),float(fw.y))-yaw(float(pl.x)-float(loc.x), float(pl.y)-float(loc.y))
            L("  ang_fw_to_player=%.1f"%ang)
        except Exception as e:
            L("  diag "+str(e))

open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("done")
