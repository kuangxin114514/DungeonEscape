# -*- coding: utf-8 -*-
import ast, shutil
p=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
shutil.copy2(p, p+".pre_t372")
t=open(p,encoding="utf-8").read()
if "T372_SKEL_FACE_RUN" not in t:
    t=t.replace("T370_SKELETON_TUNE:","T370_SKELETON_TUNE T372_SKEL_FACE_RUN:",1)

# Restore Running as primary
old_run='''SKELETON_ANIM_RUN = (
    "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Walking_A_Rig",
    "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Running_A_Rig",
)
# KayKit mesh often faces +Y while actor forward is +X; yaw offset stops "spin while chase".
SKELETON_FACE_YAW_OFFSET = -90.0'''
new_run='''SKELETON_ANIM_RUN = (
    "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Running_A_Rig",
    "/Game/Characters/Enemies/Skeleton/Animations/SK_SkeletonMinion_Rig_Walking_A_Rig",
)
# Mesh CharacterMesh0 already has relative yaw ~270 on BP; do NOT double-offset actor yaw.
SKELETON_FACE_YAW_OFFSET = 0.0
SKELETON_MESH_REL_YAW = 270.0
SKELETON_ATTACK_WINDUP = 0.5  # seconds in melee before first swing'''
if old_run not in t:
    raise SystemExit("run block missing:\n"+repr(t[t.find("SKELETON_ANIM_RUN"):t.find("SKELETON_ANIM_RUN")+400]))
t=t.replace(old_run,new_run,1)

# Replace _look_at_xy entirely with safer version
start=t.find("def _look_at_xy(actor, target_loc):")
end=t.find("def _move_actor_toward(actor, target_loc, speed, dt):")
if start<0 or end<0: raise SystemExit("look/move markers missing")
new_look='''def _look_at_xy(actor, target_loc):
    """Face target in XY only (keep pitch/roll). Offset 0 — BP mesh already yaw 270."""
    try:
        al = actor.get_actor_location()
        dx = float(target_loc.x) - float(al.x)
        dy = float(target_loc.y) - float(al.y)
        if (dx * dx + dy * dy) < 16.0:
            return
        import math
        yaw = math.degrees(math.atan2(dy, dx)) + float(SKELETON_FACE_YAW_OFFSET)
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
        # Keep mesh relative yaw stable (KayKit)
        try:
            mesh = _get_pawn_mesh(actor)
            if mesh is not None:
                try:
                    rr = mesh.get_editor_property("relative_rotation")
                    want = float(SKELETON_MESH_REL_YAW)
                    if abs(float(rr.yaw) - want) > 1.0 or abs(float(rr.pitch)) > 1.0 or abs(float(rr.roll)) > 1.0:
                        mesh.set_editor_property(
                            "relative_rotation",
                            unreal.Rotator(0.0, want, 0.0),
                        )
                except Exception:
                    pass
        except Exception:
            pass
        try:
            cur = actor.get_actor_rotation()
            cur_yaw = float(cur.yaw)
            diff = abs(((yaw - cur_yaw + 180.0) % 360.0) - 180.0)
            if diff < 5.0:
                return
            # Preserve pitch/roll — never zero them (avoids tumble/"上下转")
            actor.set_actor_rotation(
                unreal.Rotator(float(cur.pitch), float(yaw), float(cur.roll)),
                False,
            )
        except Exception:
            actor.set_actor_rotation(unreal.Rotator(0.0, yaw, 0.0), False)
    except Exception:
        pass


'''
t=t[:start]+new_look+t[end:]

# Add in_melee_since to state dict
old_st='''        st = {
            "state": "idle",          # idle|chase|attack
            "anim": None,             # idle|run|attack
            "last_attack_t": 0.0,
            "attack_hit_due": 0.0,    # when to apply pending damage (0=none)
            "spawn_loc": spawn,
            "aggro": False,
        }'''
new_st='''        st = {
            "state": "idle",          # idle|chase|attack
            "anim": None,             # idle|run|attack
            "last_attack_t": 0.0,
            "attack_hit_due": 0.0,    # when to apply pending damage (0=none)
            "in_melee_since": 0.0,    # when first entered attack range (0=not in melee)
            "spawn_loc": spawn,
            "aggro": False,
        }'''
if old_st not in t: raise SystemExit("state dict missing")
t=t.replace(old_st,new_st,1)

# Patch attack branch: require windup 0.5s after entering melee
# Find the attack block in update_skeleton_ai
old_atk='''        if dist <= float(SKELETON_ATTACK_RANGE):
            # Attack if cooldown ready
            if (now - float(st.get("last_attack_t", 0.0))) >= float(SKELETON_ATTACK_COOLDOWN):
                st["state"] = "attack"
                st["last_attack_t"] = now
                st["attack_hit_due"] = now + float(SKELETON_ATTACK_HIT_DELAY)
                _look_at_xy(enemy, pl)
                _skeleton_play_anim(enemy, "attack", False)
            else:
                # Hold in place facing player; keep last attack anim or idle stance
                st["state"] = "attack" if st.get("anim") == "attack" else "chase"
                _look_at_xy(enemy, pl)
                # After attack anim finishes, show idle/run briefly — if not mid-attack window, play idle-ish
                if st.get("anim") == "attack" and (now - float(st.get("last_attack_t", 0.0))) > 0.55:
                    # Stay ready: face player; snap back to idle briefly until cooldown ends
                    if st.get("anim") != "idle":
                        _skeleton_play_anim(enemy, "idle", True)
        else:
            st["state"] = "chase"
            _move_actor_toward(enemy, pl, SKELETON_CHASE_SPEED, dt)
            if st.get("anim") != "run":
                _skeleton_play_anim(enemy, "run", True)'''

# The file may have slightly different comment encoding - read actual segment
idx=t.find("        if dist <= float(SKELETON_ATTACK_RANGE):")
idx2=t.find("\n\ndef _purge_dead_skeleton_ai_keys", idx)
if idx<0 or idx2<0:
    raise SystemExit("attack branch markers missing %s %s"%(idx,idx2))
new_atk='''        if dist <= float(SKELETON_ATTACK_RANGE):
            # Windup: must stay in melee 0.5s before first swing (and between swings still respect cooldown)
            if float(st.get("in_melee_since", 0.0) or 0.0) <= 0.0:
                st["in_melee_since"] = now
            windup_ok = (now - float(st["in_melee_since"])) >= float(SKELETON_ATTACK_WINDUP)
            if windup_ok and (now - float(st.get("last_attack_t", 0.0))) >= float(SKELETON_ATTACK_COOLDOWN):
                st["state"] = "attack"
                st["last_attack_t"] = now
                st["attack_hit_due"] = now + float(SKELETON_ATTACK_HIT_DELAY)
                _look_at_xy(enemy, pl)
                _skeleton_play_anim(enemy, "attack", False)
            else:
                # Hold / face while waiting for windup or cooldown
                st["state"] = "attack" if st.get("anim") == "attack" else "chase"
                _look_at_xy(enemy, pl)
                if st.get("anim") == "attack" and (now - float(st.get("last_attack_t", 0.0))) > 0.55:
                    if st.get("anim") != "idle":
                        _skeleton_play_anim(enemy, "idle", True)
                elif st.get("anim") not in ("idle", "attack"):
                    _skeleton_play_anim(enemy, "idle", True)
        else:
            st["in_melee_since"] = 0.0
            st["state"] = "chase"
            _move_actor_toward(enemy, pl, SKELETON_CHASE_SPEED, dt)
            if st.get("anim") != "run":
                _skeleton_play_anim(enemy, "run", True)
'''
t=t[:idx]+new_atk+t[idx2:]

# Also clear in_melee_since when losing aggro / idle
t=t.replace(
'''            if st["state"] != "idle" or st.get("aggro"):
                st["state"] = "idle"
                st["aggro"] = False
                st["attack_hit_due"] = 0.0
                if st.get("anim") != "idle":
                    _skeleton_play_anim(enemy, "idle", True)''',
'''            if st["state"] != "idle" or st.get("aggro"):
                st["state"] = "idle"
                st["aggro"] = False
                st["attack_hit_due"] = 0.0
                st["in_melee_since"] = 0.0
                if st.get("anim") != "idle":
                    _skeleton_play_anim(enemy, "idle", True)''',
1)
t=t.replace(
'''            if st["state"] != "idle":
                st["state"] = "idle"
                st["attack_hit_due"] = 0.0
            if st.get("anim") != "idle":
                _skeleton_play_anim(enemy, "idle", True)
            continue
        # Aggroed''',
'''            if st["state"] != "idle":
                st["state"] = "idle"
                st["attack_hit_due"] = 0.0
                st["in_melee_since"] = 0.0
            if st.get("anim") != "idle":
                _skeleton_play_anim(enemy, "idle", True)
            continue
        # Aggroed''',
1)

# Improve run anim play: force re-apply if somehow not Running sequence
# In _skeleton_play_anim after success, set play rate 1.0 for run
old_play_end='''    st = _skeleton_ai_state(actor)
    st["anim"] = kind
    return True'''
new_play_end='''    try:
        if kind == "run":
            # Keep run looping at normal rate
            try:
                mesh.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
            except Exception:
                pass
            try:
                mesh.override_animation_data(seq, True, True, 0.0, 1.0)
            except Exception:
                pass
    except Exception:
        pass
    st = _skeleton_ai_state(actor)
    st["anim"] = kind
    return True'''
# only replace first occurrence inside skeleton play - there may be similar elsewhere
# find within _skeleton_play_anim
ps=t.find("def _skeleton_play_anim(actor, kind, looping):")
pe=t.find("def _look_at_xy(actor, target_loc):")
if ps<0 or pe<0: raise SystemExit("play/look markers")
chunk=t[ps:pe]
if old_play_end not in chunk: raise SystemExit("play end missing in chunk")
chunk=chunk.replace(old_play_end,new_play_end,1)
t=t[:ps]+chunk+t[pe:]

open(p,"w",encoding="utf-8").write(t)
ast.parse(t)
print("OK")
print("offset", "SKELETON_FACE_YAW_OFFSET = 0.0" in t)
print("windup", "SKELETON_ATTACK_WINDUP = 0.5" in t)
print("run first", t[t.find("SKELETON_ANIM_RUN"):t.find("SKELETON_ANIM_RUN")+200])
