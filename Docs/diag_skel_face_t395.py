# -*- coding: utf-8 -*-
from __future__ import print_function
import math, unreal
OUT=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\diag_skel_face_t395.txt"
lines=[]
def L(m):
    lines.append(str(m))
    try: unreal.log("T395: "+str(m))
    except Exception: print(m)

def v3(v):
    return (float(v.x),float(v.y),float(v.z))
def yaw_of(dx,dy):
    return math.degrees(math.atan2(dy,dx))

world=None
try:
    world=unreal.EditorLevelLibrary.get_game_world()
except Exception:
    world=None
if world is None:
    try: world=unreal.EditorLevelLibrary.get_editor_world()
    except Exception: world=None
L("world=%s"%world)

player=None
try:
    player=unreal.GameplayStatics.get_player_pawn(world,0)
except Exception as e:
    L("player err "+str(e))
L("player=%s"%player)
pl=None
if player:
    pl=player.get_actor_location()
    L("player loc %s yaw=%.1f"%(v3(pl), float(player.get_actor_rotation().yaw)))

# CDO check
BP="/Game/Characters/Enemies/Skeleton/BP_Enemy_Skeleton"
cls=unreal.EditorAssetLibrary.load_blueprint_class(BP)
cdo=unreal.get_default_object(cls)
cm=cdo.get_editor_property("character_movement")
rr=cm.get_editor_property("rotation_rate")
L("CDO rot_rate p=%.1f y=%.1f r=%.1f ortm=%s"%(float(rr.pitch),float(rr.yaw),float(rr.roll), cm.get_editor_property("orient_rotation_to_movement")))
mesh=cdo.get_editor_property("mesh")
mrr=mesh.get_editor_property("relative_rotation")
L("CDO mesh rel p=%.1f y=%.1f r=%.1f (not changing)"%(float(mrr.pitch),float(mrr.yaw),float(mrr.roll)))

for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Character):
    try:
        cn=a.get_class().get_name()
    except Exception:
        continue
    if "Skeleton" not in cn and "skeleton" not in cn:
        continue
    loc=a.get_actor_location()
    rot=a.get_actor_rotation()
    fw=a.get_actor_forward_vector()
    mov=a.get_editor_property("character_movement")
    vel=None
    try: vel=mov.get_editor_property("velocity")
    except Exception:
        try: vel=a.get_velocity()
        except Exception: vel=None
    rrate=mov.get_editor_property("rotation_rate")
    ortm=mov.get_editor_property("orient_rotation_to_movement")
    sm=a.get_editor_property("mesh")
    # mesh forward in world
    try:
        mfw=sm.get_forward_vector()
    except Exception:
        mfw=None
    try:
        mrr2=sm.get_editor_property("relative_rotation")
    except Exception:
        mrr2=None
    to_p=None
    ang_fw_to_p=None
    ang_vel_to_p=None
    ang_fw_vel=None
    if pl is not None:
        dx=float(pl.x)-float(loc.x); dy=float(pl.y)-float(loc.y)
        to_p=(dx,dy)
        ang_fw_to_p=yaw_of(float(fw.x),float(fw.y))-yaw_of(dx,dy)
    if vel is not None:
        vx,vy,vz=v3(vel)
        spd=math.sqrt(vx*vx+vy*vy)
        if spd>5 and pl is not None:
            ang_vel_to_p=yaw_of(vx,vy)-yaw_of(float(pl.x)-float(loc.x), float(pl.y)-float(loc.y))
            ang_fw_vel=yaw_of(float(fw.x),float(fw.y))-yaw_of(vx,vy)
    L("--- %s ---"%a.get_name())
    L("  loc=%s actor_yaw=%.1f fw=%s"%(v3(loc), float(rot.yaw), v3(fw)))
    L("  vel=%s ortm=%s rot_rate y=%.1f (p=%.1f)"%(v3(vel) if vel else None, ortm, float(rrate.yaw), float(rrate.pitch)))
    if mrr2 is not None:
        L("  mesh_rel y=%.1f mfw=%s"%(float(mrr2.yaw), v3(mfw) if mfw else None))
    if to_p is not None:
        L("  to_player_xy=%s ang_actorFw_vs_toPlayer=%.1f"%(to_p, ang_fw_to_p))
    if ang_vel_to_p is not None:
        L("  ang_vel_vs_toPlayer=%.1f ang_actorFw_vs_vel=%.1f"%(ang_vel_to_p, ang_fw_vel))
    if mfw is not None and pl is not None:
        ang_mfw_to_p=yaw_of(float(mfw.x),float(mfw.y))-yaw_of(float(pl.x)-float(loc.x), float(pl.y)-float(loc.y))
        L("  ang_meshFw_vs_toPlayer=%.1f"%ang_mfw_to_p)

open(OUT,"w",encoding="utf-8").write("\n".join(lines)+"\n")
print("done")
