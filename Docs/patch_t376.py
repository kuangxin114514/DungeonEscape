# -*- coding: utf-8 -*-
import ast, shutil
p=r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Content\Python\shop_interact_runtime.py"
shutil.copy2(p, p+".pre_t376")
t=open(p,encoding="utf-8").read()
if "T376_STABLE_FACE" not in t:
    t=t.replace("T375_FACE_NO_FLIP:","T375_FACE_NO_FLIP T376_STABLE_FACE:",1)

# Authored mesh yaw 270; actor needs +90 so run faces move dir
t=t.replace(
"SKELETON_FACE_YAW_OFFSET = 0.0  # mesh rel yaw forced to 0\nSKELETON_MESH_REL_YAW = 0.0",
"SKELETON_FACE_YAW_OFFSET = 90.0  # mesh rel yaw 270 => actor yaw = atan2+90 to face run forward\nSKELETON_MESH_REL_YAW = 270.0",
1)

# Rewrite face + disable + move for stability
start=t.find("def _skeleton_force_upright(actor):")
end=t.find("def _has_line_of_sight(world, enemy, pawn):")
if start<0 or end<0: raise SystemExit("markers")

new=r'''def _skeleton_force_upright(actor):
    if actor is None:
        return
    try:
        cur = actor.get_actor_rotation()
        if abs(float(cur.pitch)) < 0.25 and abs(float(cur.roll)) < 0.25:
            return
        actor.set_actor_rotation(unreal.Rotator(0.0, float(cur.yaw), 0.0), False)
    except Exception:
        pass


def _skeleton_face_target(actor, target_loc):
    """Face player; only update when yaw delta is meaningful (stops micro-spin)."""
    if actor is None or target_loc is None:
        return
    try:
        al = actor.get_actor_location()
        dx = float(target_loc.x) - float(al.x)
        dy = float(target_loc.y) - float(al.y)
        if (dx * dx + dy * dy) < 4.0:
            _skeleton_force_upright(actor)
            return
        import math
        yaw = math.degrees(math.atan2(dy, dx)) + float(SKELETON_FACE_YAW_OFFSET)
        cur = actor.get_actor_rotation()
        cur_yaw = float(cur.yaw)
        diff = abs(((yaw - cur_yaw + 180.0) % 360.0) - 180.0)
        # Always fix tumble; only turn when needed
        if diff < 8.0 and abs(float(cur.pitch)) < 0.5 and abs(float(cur.roll)) < 0.5:
            return
        actor.set_actor_rotation(unreal.Rotator(0.0, float(yaw), 0.0), False)
    except Exception:
        _skeleton_force_upright(actor)


def _skeleton_disable_physics_flip(actor, force=False):
    """Run once per AI state (or force). Avoid per-frame mesh writes that cause spin/pop."""
    if actor is None:
        return None
    st = None
    try:
        st = _skeleton_ai_state(actor)
        if (not force) and st.get("phys_locked"):
            return None
    except Exception:
        st = None
    try:
        ctrl = actor.get_controller()
        if ctrl is not None:
            try:
                ctrl.stop_movement()
            except Exception:
                pass
            try:
                if "AIController" in ctrl.get_class().get_name():
                    ctrl.unpossess()
            except Exception:
                pass
    except Exception:
        pass
    for prop, val in (
        ("use_controller_rotation_yaw", False),
        ("use_controller_rotation_pitch", False),
        ("use_controller_rotation_roll", False),
    ):
        try:
            actor.set_editor_property(prop, val)
        except Exception:
            pass
    mc = None
    try:
        if isinstance(actor, unreal.Character):
            mc = actor.get_movement_component()
    except Exception:
        mc = None
    if mc is not None:
        for prop, val in (
            ("orient_rotation_to_movement", False),
            ("use_controller_desired_rotation", False),
            ("enable_physics_interaction", False),
            ("b_enable_physics_interaction", False),
            ("push_force_factor", 0.0),
            ("initial_push_force_factor", 0.0),
        ):
            try:
                mc.set_editor_property(prop, val)
            except Exception:
                pass
    mesh = None
    try:
        mesh = _get_pawn_mesh(actor)
    except Exception:
        mesh = None
    if mesh is not None:
        try:
            mesh.set_simulate_physics(False)
        except Exception:
            pass
        try:
            mesh.set_all_bodies_simulate_physics(False)
        except Exception:
            pass
        try:
            mesh.set_collision_enabled(unreal.CollisionEnabled.QUERY_ONLY)
        except Exception:
            pass
        try:
            mesh.set_editor_property(
                "relative_rotation",
                unreal.Rotator(0.0, float(SKELETON_MESH_REL_YAW), 0.0),
            )
        except Exception:
            pass
        try:
            mesh.set_editor_property(
                "root_motion_mode",
                unreal.RootMotionMode.NO_ROOT_MOTION_EXTRACTION,
            )
        except Exception:
            pass
    if st is not None:
        st["phys_locked"] = True
    return mc


def _skeleton_prepare_move(actor):
    return _skeleton_disable_physics_flip(actor, force=False)


def _look_at_xy(actor, target_loc):
    _skeleton_disable_physics_flip(actor, force=False)
    _skeleton_face_target(actor, target_loc)


def _move_actor_toward(actor, target_loc, speed, dt):
    """Move then face player (stable yaw). Keep run anim playing — do not retouch mesh every step."""
    try:
        al = actor.get_actor_location()
    except Exception:
        return 99999.0
    dx = float(target_loc.x) - float(al.x)
    dy = float(target_loc.y) - float(al.y)
    dist_xy = (dx * dx + dy * dy) ** 0.5
    _skeleton_disable_physics_flip(actor, force=False)
    if dist_xy < 1.0:
        _skeleton_face_target(actor, target_loc)
        return dist_xy
    # Face FIRST so movement direction matches facing, then slide
    _skeleton_face_target(actor, target_loc)
    step = float(speed) * float(dt)
    if step > dist_xy:
        step = dist_xy
    nx = float(al.x) + dx / dist_xy * step
    ny = float(al.y) + dy / dist_xy * step
    nz = float(al.z)
    try:
        actor.set_actor_location(unreal.Vector(nx, ny, nz), True, False)
    except Exception:
        try:
            actor.set_actor_location(unreal.Vector(nx, ny, nz), False, True)
        except Exception as e:
            _log("T376 move fail " + str(e))
    # Re-assert upright facing after sweep (collision can tumble)
    _skeleton_face_target(actor, target_loc)
    try:
        al2 = actor.get_actor_location()
        dx2 = float(target_loc.x) - float(al2.x)
        dy2 = float(target_loc.y) - float(al2.y)
        return (dx2 * dx2 + dy2 * dy2) ** 0.5
    except Exception:
        return dist_xy


'''
t=t[:start]+new+t[end:]

# Add phys_locked to state dict
t=t.replace(
'''            "in_melee_since": 0.0,    # when first entered attack range (0=not in melee)
            "spawn_loc": spawn,
            "aggro": False,
        }''',
'''            "in_melee_since": 0.0,    # when first entered attack range (0=not in melee)
            "spawn_loc": spawn,
            "aggro": False,
            "phys_locked": False,
        }''',
1)

# Aggroed block: don't call disable every frame with mesh write — face only
t=t.replace(
'''        # Aggroed — always face player + kill any tumble from collision
        _skeleton_disable_physics_flip(enemy)
        _skeleton_face_target(enemy, pl)
        if dist <= float(SKELETON_ATTACK_RANGE):''',
'''        # Aggroed — face player (physics lock is once-per-actor)
        _skeleton_disable_physics_flip(enemy, force=False)
        _skeleton_face_target(enemy, pl)
        if dist <= float(SKELETON_ATTACK_RANGE):''',
1)

open(p,"w",encoding="utf-8").write(t)
ast.parse(t)
print("OK", "SKELETON_FACE_YAW_OFFSET = 90.0" in t, "SKELETON_MESH_REL_YAW = 270.0" in t, "phys_locked" in t)
