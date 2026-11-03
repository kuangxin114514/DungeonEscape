# -*- coding: utf-8 -*-
import ast, shutil, re
p=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
shutil.copy2(p, p+".pre_t370")
t=open(p,encoding="utf-8").read()
if "T370_SKELETON_TUNE" not in t:
    t=t.replace("T368_SKELETON_AI:","T368_SKELETON_AI T370_SKELETON_TUNE:",1)

# constants
repls=[
("SKELETON_AGGRO_RANGE = 1000.0","SKELETON_AGGRO_RANGE = 600.0"),
("SKELETON_LOSE_RANGE = 1400.0","SKELETON_LOSE_RANGE = 900.0"),
("SKELETON_CHASE_SPEED = 380.0","SKELETON_CHASE_SPEED = 190.0"),
("SKELETON_ATTACK_COOLDOWN = 1.6","SKELETON_ATTACK_COOLDOWN = 1.05"),
("SKELETON_ATTACK_HIT_DELAY = 0.35","SKELETON_ATTACK_HIT_DELAY = 0.22"),
("SKELETON_ATTACK_RANGE = 180.0","SKELETON_ATTACK_RANGE = 200.0"),
]
for a,b in repls:
    if a not in t: raise SystemExit("missing "+a)
    t=t.replace(a,b,1)

# Prefer Walking for half-speed chase look; keep Running as fallback
old_run='''SKELETON_ANIM_RUN = (
    "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Running_A_Rig",
    "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Walking_A_Rig",
)'''
new_run='''SKELETON_ANIM_RUN = (
    "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Walking_A_Rig",
    "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Running_A_Rig",
)
# KayKit mesh often faces +Y while actor forward is +X; yaw offset stops "spin while chase".
SKELETON_FACE_YAW_OFFSET = -90.0'''
if old_run not in t: raise SystemExit("run anim block missing")
t=t.replace(old_run,new_run,1)

old_look='''def _look_at_xy(actor, target_loc):
    try:
        al = actor.get_actor_location()
        dx = float(target_loc.x) - float(al.x)
        dy = float(target_loc.y) - float(al.y)
        if (dx * dx + dy * dy) < 1.0:
            return
        import math
        yaw = math.degrees(math.atan2(dy, dx))
        actor.set_actor_rotation(unreal.Rotator(0.0, yaw, 0.0), False)
    except Exception:
        pass'''

new_look='''def _look_at_xy(actor, target_loc):
    """Face target in XY. Apply KayKit yaw offset; disable CMC orient-to-movement to avoid spin."""
    try:
        al = actor.get_actor_location()
        dx = float(target_loc.x) - float(al.x)
        dy = float(target_loc.y) - float(al.y)
        if (dx * dx + dy * dy) < 4.0:
            return
        import math
        yaw = math.degrees(math.atan2(dy, dx)) + float(SKELETON_FACE_YAW_OFFSET)
        # Avoid fighting CharacterMovement rotation every tick.
        try:
            if isinstance(actor, unreal.Character):
                mc = actor.get_movement_component()
                if mc is not None:
                    for prop, val in (
                        ("orient_rotation_to_movement", False),
                        ("use_controller_desired_rotation", False),
                    ):
                        try:
                            mc.set_editor_property(prop, val)
                        except Exception:
                            pass
                    try:
                        actor.set_editor_property("use_controller_rotation_yaw", False)
                    except Exception:
                        pass
        except Exception:
            pass
        # Only update when yaw changed enough (reduces jitter/spin)
        try:
            cur = actor.get_actor_rotation()
            cur_yaw = float(cur.yaw)
            diff = abs(((yaw - cur_yaw + 180.0) % 360.0) - 180.0)
            if diff < 3.0:
                return
        except Exception:
            pass
        actor.set_actor_rotation(unreal.Rotator(0.0, yaw, 0.0), False)
    except Exception:
        pass'''

if old_look not in t: raise SystemExit("look_at missing")
t=t.replace(old_look,new_look,1)

# Soften move: don't add_movement_input (CMC fights our set_actor_location+rotation)
old_move_assist='''    # Slate post-tick: CharacterMovement already ran, so drive with swept set_actor_location.
    # Still nudge max_walk_speed / add_movement_input as a soft assist if present.
    try:
        if isinstance(actor, unreal.Character):
            try:
                mc = actor.get_movement_component()
                if mc is not None:
                    try:
                        mc.set_editor_property("max_walk_speed", float(speed))
                    except Exception:
                        try:
                            mc.max_walk_speed = float(speed)
                        except Exception:
                            pass
            except Exception:
                pass
            try:
                actor.add_movement_input(unreal.Vector(dx / dist_xy, dy / dist_xy, 0.0), 1.0, False)
            except Exception:
                pass
    except Exception:
        pass'''

new_move_assist='''    # Slate post-tick: drive only with swept set_actor_location (no add_movement_input —
    # CMC orient-to-movement was spinning the mesh while we also set yaw).
    try:
        if isinstance(actor, unreal.Character):
            mc = actor.get_movement_component()
            if mc is not None:
                for prop, val in (
                    ("orient_rotation_to_movement", False),
                    ("use_controller_desired_rotation", False),
                    ("max_walk_speed", float(speed)),
                ):
                    try:
                        mc.set_editor_property(prop, val)
                    except Exception:
                        pass
    except Exception:
        pass'''

if old_move_assist not in t: raise SystemExit("move assist missing")
t=t.replace(old_move_assist,new_move_assist,1)

# Faster attack return: after attack window 0.9 -> 0.55 and prefer re-chase anim sooner
t=t.replace(
'''                if st.get("anim") == "attack" and (now - float(st.get("last_attack_t", 0.0))) > 0.9:
                    if st.get("anim") != "idle":
                        _skeleton_play_anim(enemy, "idle", True)''',
'''                if st.get("anim") == "attack" and (now - float(st.get("last_attack_t", 0.0))) > 0.55:
                    # Stay ready: face player; snap back to idle briefly until cooldown ends
                    if st.get("anim") != "idle":
                        _skeleton_play_anim(enemy, "idle", True)''',
1)

open(p,"w",encoding="utf-8").write(t)
ast.parse(t)
print("OK", "SKELETON_CHASE_SPEED = 190.0" in t, "SKELETON_AGGRO_RANGE = 600.0" in t, "SKELETON_FACE_YAW_OFFSET" in t)
