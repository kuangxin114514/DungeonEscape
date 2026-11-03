# -*- coding: utf-8 -*-
from __future__ import print_function
import math, unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\diag_skel_face_t395b.txt"
lines=[]
def L(m):
    lines.append(str(m));
    try: unreal.log("T395b: "+str(m))
    except Exception: print(m)

def v3(v):
    return (float(v.x),float(v.y),float(v.z))
def yaw_of(dx,dy):
    return math.degrees(math.atan2(dy,dx))

worlds=[]
try:
    worlds=list(unreal.EditorLevelLibrary.get_pie_worlds(False) or [])
    L("pie_worlds=%d"%len(worlds))
except Exception as e:
    L("pie err "+str(e))
try:
    ew=unreal.EditorLevelLibrary.get_editor_world()
    L("editor_world=%s"%ew)
except Exception as e:
    L("ew err "+str(e))
try:
    gw=unreal.EditorLevelLibrary.get_game_world()
    L("game_world=%s"%gw)
    if gw and gw not in worlds: worlds.append(gw)
except Exception as e:
    L("gw err "+str(e))

# also all worlds via iterator
for o in unreal.ObjectIterator(unreal.World):
    try:
        pn=o.get_path_name()
    except Exception: continue
    if "UEDPIE" in pn or "Transient" in pn or "Map_" in pn:
        L("world_iter %s"%pn)
        if o not in worlds: worlds.append(o)

for world in worlds:
    L("== world %s =="%world)
    try:
        player=unreal.GameplayStatics.get_player_pawn(world,0)
    except Exception:
        player=None
    L("player=%s"%player)
    pl=player.get_actor_location() if player else None
    for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Pawn):
        try: cn=a.get_class().get_name()
        except Exception: continue
        if "Skeleton" not in cn: continue
        loc=a.get_actor_location(); fw=a.get_actor_forward_vector()
        mov=None
        try: mov=a.get_editor_property("character_movement")
        except Exception: pass
        vel=None; rry=None; ortm=None
        if mov:
            try: vel=mov.get_editor_property("velocity")
            except Exception: pass
            try:
                rr=mov.get_editor_property("rotation_rate"); rry=float(rr.yaw)
                ortm=mov.get_editor_property("orient_rotation_to_movement")
            except Exception: pass
        sm=None; mfw=None
        try:
            sm=a.get_editor_property("mesh"); mfw=sm.get_forward_vector()
        except Exception: pass
        L("pawn %s loc=%s yaw=%.1f fw=%s"%(a.get_name(),v3(loc),float(a.get_actor_rotation().yaw),v3(fw)))
        L("  vel=%s ortm=%s rry=%s"%(v3(vel) if vel else None, ortm, rry))
        L("  mfw=%s"% (v3(mfw) if mfw else None))
        if pl is not None:
            dx=float(pl.x)-float(loc.x); dy=float(pl.y)-float(loc.y)
            L("  toP angFw=%.1f angMesh=%.1f"%(yaw_of(float(fw.x),float(fw.y))-yaw_of(dx,dy),
                (yaw_of(float(mfw.x),float(mfw.y))-yaw_of(dx,dy)) if mfw else 0))
            if vel:
                vx,vy,_=v3(vel)
                if abs(vx)+abs(vy)>5:
                    L("  angVelToP=%.1f angFwVel=%.1f"%(yaw_of(vx,vy)-yaw_of(dx,dy), yaw_of(float(fw.x),float(fw.y))-yaw_of(vx,vy)))

open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("done")
